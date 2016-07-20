"""Sphinx extension to add utilities for autodoc.

A module can define top-level ``__autodoc_excludes__`` or ``__deprecated__``
lists. These are in the same format as ``__all__``, in that they take a list of
strings for top-level classes, functions, and variables. Anything listed here
will be excluded from any autodoc code.

``__autodoc_excludes__`` is particularly handy when documenting an
:file:`__init__.py` that imports contents from a submodule and re-exports it in
``__all__``. In this case, autodoc would normally output documentation both in
:file:`__init__.py` and the submodule, but that can be avoided by setting::

    __autodoc_excludes = __all__

Excludes can also be defined globally, filtered by the type of object the
docstring would belong to. See the documentation for autodoc-skip-member_ for
more information. You can configure this in :file:`conf.py` by doing::

    autodoc_excludes = {
        # Applies to modules, classes, and anything else.
        '*': [
            '__dict__',
            '__doc__',
            '__module__',
            '__weakref__',
        ],
        'class': [
            # Useful for Django models.
            'DoesNotExist',
            'MultipleObjectsReturned',
            'objects',

            # Useful forms.
            'base_fields',
            'media',
        ],
    }

That's just an example, but a useful one for Django users.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.autodoc_utils',
        ...
    ]


Configuration
=============

``autodoc_excludes``:
    Optional global exclusions to apply, as shown above.
"""

from __future__ import unicode_literals

import sys


def _filter_members(app, what, name, obj, skip, options):
    """Filter members out of the documentation.

    This will look up the name in the ``autodoc_excludes`` table under the
    ``what`` and under ``'*'`` keys. If an entry is listed, it will be
    excluded from the documentation.

    It will also skip modules listed in ``__deprecated__`` in the documented
    module.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register roles and configuration on.

        what (unicode):
            The type of thing being filtered (one of ``attribute``, ``class``,
            ``exception``, ``function``, ``method``, or ``module``).

        name (unicode):
            The name of the object to look up in the filter lists.

        obj (object):
            The object that may be filtered.

        skip (bool):
            Whether the filter will be skipped if this handler doesn't
            return a different value.

        options (object):
            Options given to the autodoc directive.

    Returns:
        bool:
        Whether the member will be skipped.
    """
    module_name = app.env.temp_data['autodoc:module']
    module = sys.modules[module_name]

    # Check if the module itself is excluding this from the docs.
    module_excludes = set(getattr(module, '__autodoc_excludes__', []))

    if name in module_excludes:
        return True

    # Check if this appears in the global list of excludes.
    global_excludes = app.config['autodoc_excludes']

    for key in (what, '*'):
        if key in global_excludes and name in global_excludes.get(key, []):
            return True

    # Check if this appears in the list of deprecated objects.
    if name in getattr(module, '__deprecated__', []):
        return True

    return skip


def setup(app):
    """Set up the Sphinx extension.

    This sets up the configuration and event handlers needed for enhancing
    auto-doc support.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register configuration and listen to
            events on.
    """
    app.add_config_value('autodoc_excludes', {}, True)
    app.connect(b'autodoc-skip-member', _filter_members)
