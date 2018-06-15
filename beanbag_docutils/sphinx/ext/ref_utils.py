"""Sphinx extension to improve references.

This enhances references, allowing both Python and JavaScript references to
break paths (like ``foo.bar.MyClass``) across multiple lines.


Setup
=====

To use this, add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.ref_utils',
        ...
    ]
"""

from __future__ import unicode_literals

import re

from sphinx.domains.javascript import JSXRefRole
from sphinx.domains.python import PyXRefRole


WS_RE = re.compile(r'\s+')


def _process_link(orig_process_link, role, *args, **kwargs):
    """Process a link, stripping away all whitespace from targets.

    Args:
        orig_process_link (callable):
            The original function used to process a link for the role.

        role (sphinx.roles.XRefRole):
            The role instance being processed.

        *args (tuple):
            Positional arguments to pass to the original function.

        **kwargs (dict):
            Keyword arguments to pass to the original function.

    Returns:
        tuple:
        A tuple of ``(title, target)``.
    """
    title, target = orig_process_link(role, *args, **kwargs)

    return title, WS_RE.sub('', target)


def setup(app):
    """Set up the Sphinx extension.

    This alters some behavior for the Python domain, allowing newlines in
    references.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to extend.
    """
    def _setup_ref_role(role):
        orig_process_link = role.process_link
        role.process_link = \
            lambda *args, **kwargs: \
            _process_link(orig_process_link, *args, **kwargs)

    for role in (JSXRefRole, PyXRefRole):
        _setup_ref_role(role)
