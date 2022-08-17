"""Sphinx extension to link to source code on GitHub.

This links to source code for modules, classes, etc. to the correct line on
GitHub. This prevents having to bundle the source code along with the
documentation, and better ties everything together.


Setup
=====

To use this, you'll need to import the module and define your own
:py:func:`linkcode_resolve` in your :file:`conf.py`::

    from beanbag_docutils.sphinx.ext.github import github_linkcode_resolve

    extensions = [
        ...
        'sphinx.ext.linkcode',
        ...
    ]

    def linkcode_resolve(domain, info):
        return github_linkcode_resolve(
            domain=domain,
            info=info,
            allowed_module_names=['mymodule'],
            github_org_id='myorg',
            github_repo_id='myrepo',
            branch='master',
            source_prefix='src/')

``source_prefix`` and ``allowed_module_names`` are optional. See the
docs for :py:func:`github_linkcode_resolve` for more information.
"""

from __future__ import unicode_literals

import ast
import inspect
import logging
import re
import subprocess
import sys

import six


logger = logging.getLogger(__name__)


GIT_BRANCH_CONTAINS_RE = re.compile(r'^\s*([^\s]+)\s+([0-9a-f]+)\s.*')

# We'll store 5 items in the AST cache by default. This will ensure that we
# don't re-parse the same tree any more often than we have to, and leave
# room for some parallel processing if needed.
_AST_CACHE_MAX_SIZE = 5


_head_ref = None
_ast_cache = []


def _run_git(cmd):
    """Run git with the given arguments, returning the output.

    Args:
        cmd (list of unicode):
            A list of arguments to pass to :command:`git`.

    Returns:
        bytes:
        The resulting output from the command.

    Raises:
        subprocess.CalledProcessError:
            Error calling into git.
    """
    p = subprocess.Popen(['git'] + cmd, stdout=subprocess.PIPE)
    output, error = p.communicate()
    ret_code = p.poll()

    if ret_code:
        raise subprocess.CalledProcessError(ret_code, 'git')

    assert isinstance(output, bytes)

    return output


def _git_get_nearest_tracking_branch(merge_base, remote='origin'):
    """Return the nearest tracking branch for the given Git repository.

    Args:
        merge_base (unicode):
            The merge base used to locate the nearest tracking branch.

        remote (origin, optional):
            The remote name.

    Returns:
        unicode:
        The nearest tracking branch, or ``None`` if not found.
    """
    try:
        _run_git(['fetch', 'origin', '%s:%s' % (merge_base, merge_base)])
    except Exception:
        # Ignore, as we may already have this. Hopefully it won't fail later.
        pass

    lines = _run_git(['branch', '-rv', '--contains', merge_base]).splitlines()

    remote_prefix = '%s/' % remote
    best_distance = None
    best_ref_name = None

    for line in lines:
        m = GIT_BRANCH_CONTAINS_RE.match(line.decode('utf-8').strip())

        if m:
            ref_name = m.group(1)
            sha = m.group(2)

            if (ref_name.startswith(remote_prefix) and
                not ref_name.endswith('/HEAD')):

                distance = len(_run_git(['log',
                                         '--pretty=format:%H',
                                         '...%s' % sha]).splitlines())

                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_ref_name = ref_name

    if best_ref_name and best_ref_name.startswith(remote_prefix):
        # Strip away the remote.
        best_ref_name = best_ref_name[len(remote_prefix):]

    return best_ref_name


def _get_git_doc_ref(branch):
    """Return the commit SHA used for linking to source code on GitHub.

    The commit SHA will be cached for future lookups.

    Args:
        branch (unicode):
            The branch to use as a merge base.

    Returns:
        unicode:
        The commit SHA used for any links, if found, or ``None`` if not.
    """
    global _head_ref

    if not _head_ref:
        try:
            tracking_branch = _git_get_nearest_tracking_branch(branch)
            _head_ref = _run_git(['rev-parse', tracking_branch]).strip()

            if isinstance(_head_ref, bytes):
                _head_ref = _head_ref.decode('utf-8')
        except subprocess.CalledProcessError:
            _head_ref = None

    return _head_ref


def _find_path_in_ast_nodes(nodes, path):
    """Return an AST node for an object path, if found.

    This walks the AST tree, guided by the given identifier path, trying to
    locate the referenced identifier.

    If a node represented by the path can be found, the node will be returned.

    Version Added:
        2.0

    Args:
        nodes (list or ast.AST):
            The list of nodes or the AST object to walk.

        path (list of unicode):
            The identifier path.

    Returns:
        ast.Node:
        The node, if found, or ``None`` if not found.
    """
    name = path[0]

    if not isinstance(nodes, list):
        nodes = ast.iter_child_nodes(nodes)

    for node in nodes:
        # If this is an explicit assignment, check to see if any of the
        # targets of the assignment is the path we're looking for.
        if isinstance(node, ast.Assign):
            target_names = {
                getattr(_target, 'id', None)
                for _target in node.targets
            }

            if name in target_names:
                # We found it. We're done.
                #
                # Note that there might be more items in path, but if so,
                # then we're documenting something like a namedtuple() that
                # got code-injected. There isn't likely to be any code to
                # link to beyond this.
                return node

        # If this is anything else, see if it has the next name in the path.
        if hasattr(node, 'name') and node.name == name:
            if len(path) > 1:
                # This is a match, but we have more to process. Recurse.
                return _find_path_in_ast_nodes(node.body, path[1:])
            else:
                # This was the last part we needed. Return the node.
                return node

    return None


def _find_ast_node_for_path(module, path):
    """Return the AST node for an object path, if found.

    Version Added:
        2.0

    Args:
        module (module):
            The module in which to begin the search.

        path (unicode):
            The ``.``-delimited path to the node.

    Returns:
        ast.Node:
        The resulting node, if found, or ``None`` if not found.
    """
    global _ast_cache

    tree = None

    # See if we already have a parsed AST in cache.
    for _tree, _module in _ast_cache:
        if _module is module:
            tree = _tree
            break

    if tree is None:
        # We don't have one in cache, so build it and push the last item
        # out of cache.
        try:
            lines = inspect.findsource(module)[0]
            tree = ast.parse(''.join(lines))
            _ast_cache = (
                [(module, tree)] +
                _ast_cache[:_AST_CACHE_MAX_SIZE - 1]
            )
        except Exception as e:
            logger.exception('Failed to parse AST tree for %r: %s',
                             module, e)
            return None

    try:
        return _find_path_in_ast_nodes(tree, path)
    except Exception as e:
        logger.exception('Failed to look up object %s: %s',
                         '.'.join(path), e)
        return None


def github_linkcode_resolve(domain, info, github_org_id, github_repo_id,
                            branch, source_prefix='', allowed_module_names=[]):
    """Return a link to the source on GitHub for the given autodoc info.

    This takes some basic information on the GitHub project, branch, and
    what modules are considered acceptable, and generates a link to the
    approprite line on the GitHub repository browser for the class, function,
    variable, or other object.

    Args:
        domain (unicode):
            The autodoc domain being processed. This only accepts "py", and
            comes from the original :py:func:`linkcode_resolve` call.

        info (dict):
            Information on the item being linked to. This comes from the
            original :py:func:`linkcode_resolve` call.

        github_org_id (unicode):
            The GitHub organization ID.

        github_repo_id (unicode):
            The GitHub repository ID.

        branch (unicode):
            The branch used as a merge base to find the appropriate commit
            to link to. Callers may want to compute this off of the version
            number of the project, or some other information.

        source_prefix (unicode, optional):
            A prefix for any linked filename, in case the module is not at
            the top of the source tree.

        allowed_module_names (list of unicode, optional):
            The list of top-level module names considered valid for links.
            If provided, links will only be generated if residing somewhere
            in one of the provided module names.
    """
    module_name = info['module']

    if (domain != 'py' or
        not module_name or
        (allowed_module_names and
         module_name.split('.')[0] not in allowed_module_names)):
        # These aren't the modules you're looking for.
        return None

    # Grab the name of the source file.
    filename = module_name.replace('.', '/') + '.py'

    # Grab the module referenced in the docs.
    submod = sys.modules.get(module_name)

    if submod is None:
        return None

    # Split that, trying to find the module at the very tail of the module
    # path.
    node = _find_ast_node_for_path(submod, info['fullname'].split('.'))

    if node is None:
        return None

    # Build a reference for the line number in GitHub.
    linespec = '#L%d' % node.lineno

    # Get the branch/tag/commit to link to.
    ref = _get_git_doc_ref(branch) or branch
    assert isinstance(ref, six.text_type)

    return ('https://github.com/%s/%s/blob/%s/%s%s%s'
            % (github_org_id, github_repo_id, ref, source_prefix,
               filename, linespec))


def clear_github_linkcode_caches():
    """Clear the internal caches for GitHub code linking.

    This is primarily intended for unit tests.

    Version Added:
        2.0
    """
    global _head_ref, _ast_cache

    _head_ref = None
    _ast_cache = []
