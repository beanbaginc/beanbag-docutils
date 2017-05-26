"""Sphinx extension to enhance intersphinx support.

This fixes some reference issues with :rst:role:`option` (see
https://github.com/sphinx-doc/sphinx/pull/3769 for the equivalent upstream
fix).

It also introduces a ``.. default-intersphinx::`` directive that allows for
specifying one or more intersphinx set prefixes that should be tried if a
reference could not be found. For example::

    .. default-intersphinx:: myapp1.5 python

    :ref:`some-reference`

This does affect the process by which missing references are located. If an
unprefixed reference is used, it will only match if the prefix is in the list
above, which differs from the default behavior of looking through all
intersphinx mappings.


Setup
=====

This extension must be added to ``exetnsions`` in :file:`conf.py` after the
:py:mod:`sphinx.ext.intersphinx` extension is added. For example::

    extensions = [
        ...
        'sphinx.ext.intersphinx',
        'beanbag_docutils.sphinx.ext.intersphinx',
        ...
    ]
"""

from __future__ import unicode_literals

import re

import six
from sphinx.errors import ExtensionError
from sphinx.ext import intersphinx
from sphinx.util.compat import Directive


class DefaultIntersphinx(Directive):
    """Specifies one or more default intersphinx sets to use."""

    required_arguments = 1
    optional_arguments = 100

    SPLIT_RE = re.compile(r',\s*')

    def run(self):
        """Run the directive.

        Returns:
            list:
            An empty list, always.
        """
        env = self.state.document.settings.env
        env.metadata[env.docname]['default-intersphinx-prefixes'] = \
            self.arguments

        return []


def _on_missing_reference(app, env, node, contnode):
    """Handler for missing references.

    This will attempt to fix references to options and then attempt to
    apply default intersphinx prefixes (if needed) before resolving a
    reference using intersphinx.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application processing the document.

        env (sphinx.environment.BuildEnvironment):
            The environment for this doc build.

        node (sphinx.addnodes.pending_xref):
            The pending reference to resolve.

        contnode (docutils.nodes.literal):
            The context for the reference.

    Returns:
        list:
        The list of any reference nodes, as created by intersphinx.
    """
    orig_target = node['reftarget']
    target = orig_target
    domain = node.get('refdomain')

    # See if we're referencing a std:option. Sphinx (as of 1.6.1) does not
    # properly link these. A pull request has been opened to fix this
    # (https://github.com/sphinx-doc/sphinx/pull/3769). Until we can make
    # use of that, we're including the workaround here.
    if domain == 'std' and node['reftype'] == 'option':
        # Options are stored in the inventory as "program-name.--option".
        # In order to look up the option, the target will need to be
        # converted to this format.
        #
        # Ideally, we'd be able to utilize the same logic as found in
        # StandardDomain._resolve_option_xref, but we don't have any
        # information on the progoptions data stored there. Instead, we
        # try to determine if the target already has a program name or
        # an intersphinx doc set and normalize the contents to match the
        # option reference name format.
        i = target.rfind(' ')

        if i != -1:
            # The option target contains a program name and an option
            # name. We can easily normalize this to be in
            # <progname>.<option> format.
            target = '%s.%s' % (target[:i], target[i + 1:])
            target = target.replace(' ', '-')
        else:
            # Since a space was not found, and a program name is needed
            # to complete the reference, we'll see if a ".. program::"
            # has been set in this file. If so, we'll put that into the
            # target name (being careful to consider any intersphinx doc
            # set name that may be prefixed).
            progname = node.get('std:program')

            if progname:
                if ':' in target:
                    setname, newtarget = target.split(':', 1)
                    target = '%s:%s.%s' % (setname, progname, newtarget)
                else:
                    target = '%s.%s' % (progname, target)

    if ':' not in target:
        prefixes = \
            env.metadata[env.docname].get('default-intersphinx-prefixes')

        if prefixes:
            # Try all supported prefixes in order. These are the only allowed
            # to be inferred.
            for prefix in prefixes:
                old_content = contnode[0]
                node['reftarget'] = '%s:%s' % (prefix, target)
                result = intersphinx.missing_reference(app, env, node,
                                                       contnode)

                if result:
                    return result

                # Couldn't find it. Go back to the original target and try
                # again.
                node['reftarget'] = orig_target
                contnode[0] = old_content

            return None

    return intersphinx.missing_reference(app, env, node, contnode)


def setup(app):
    """Set up the Sphinx extension.

    This listens for the events needed to handle missing references, and
    registers directives.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application building the docs.
    """
    app.add_directive('default-intersphinx', DefaultIntersphinx)

    # Disconnect the other intersphinx listener. We're going to override it.
    listeners = app.events.listeners.get('missing-reference', {})

    for listener_id, callback in six.iteritems(listeners):
        if callback == intersphinx.missing_reference:
            del listeners[listener_id]
            break
    else:
        raise ExtensionError('beanbag_docutils.sphinx.ext.intersphinx_utils '
                             'must come after sphinx.ext.intersphinx')

    app.connect('missing-reference', _on_missing_reference)
