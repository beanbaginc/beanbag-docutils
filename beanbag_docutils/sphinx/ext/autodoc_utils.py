"""Sphinx extension to add utilities for autodoc.

This enhances autodoc support for Beanbag's docstring format and to allow for
excluding content from docs.


Beanbag's Docstrings
====================

By setting ``napoleon_beanbag_docstring = True`` in :file:`conf.py`, and
turning off ``napoleon_google_docstring``, Beanbag's docstring format can be
used.

This works just like the Google docstring format, but with a few additions:

* A new ``Context:`` section to describe what happens within the context of a
  context manager (including the variable).

* New ``Model Attributes:`` and ``Option Args:`` sections for defining the
  attributes on a model or the options in a dictionary when using JavaScript.

* Parsing improvements to allow for wrapping argument types across lines,
  which is useful when you have long module paths that won't fit on one line.

This requires the ``sphinx.ext.napoleon`` module to be loaded.


Excluding Content
=================

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

To use this, add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.autodoc_utils',
        ...
    ]

If you want to use the Beanbag docstring format, you'll need:

    extensions = [
        ...
        'sphinx.ext.napoleon',
        'beanbag_docutils.sphinx.ext.autodoc_utils',
        ...
    ]

    napoleon_beanbag_docstring = True
    napoleon_google_docstring = False


Configuration
=============

``autodoc_excludes``:
    Optional global exclusions to apply, as shown above.

``napoleon_beanbag_docstring``::
    Enable parsing of the Beanbag docstring format.
"""

from __future__ import unicode_literals

import re
import sys

from sphinx.ext.napoleon.docstring import GoogleDocstring


class BeanbagDocstring(GoogleDocstring):
    """Docstring parser for the Beanbag documentation.

    This is based on the Google docstring format used by Napoleon, but with
    a few additions:

    * Support for describing contexts in a context manager (using the
      ``Context:`` section, which works like ``Returns`` or ``Yields``).

    * ``Model Attributes:`` and ``Option Args:`` argument sections.

    * Parsing improvements for arguments to allow for wrapping across lines,
      for long module paths.
    """

    partial_typed_arg_start_re = \
        re.compile(r'\s*(.+?)\s*\(\s*(.*[^\s]+)\s*[^:)]*$')
    partial_typed_arg_end_re = re.compile(r'\s*(.+?)\s*\):$')

    extra_returns_sections = [
        ('context', 'Context'),
    ]

    extra_fields_sections = [
        ('model attributes', 'Model Attributes'),
        ('option args', 'Option Args'),
    ]

    MAX_PARTIAL_TYPED_ARG_LINES = 3

    def __init__(self, *args, **kwargs):
        """Initialize the parser.

        Args:
            *args (tuple):
                Positional arguments for the parent.

            **kwargs (dict):
                Keyword arguments for the parent.
        """
        super(BeanbagDocstring, self).__init__(*args, **kwargs)

        for keyword, label in self.extra_returns_sections:
            self.register_returns_section(keyword, label)

        for keyword, label in self.extra_fields_sections:
            self.register_fields_section(keyword, label)

        self._parse(True)

    def register_returns_section(self, keyword, label):
        """Register a Returns-like section with the given keyword and label.

        Args:
            keyword (unicode):
                The keyword used in the docs.

            label (unicode):
                The label outputted in the section.
        """
        self._sections[keyword] = lambda *args: \
            self._format_fields(label, self._consume_returns_section())

    def register_fields_section(self, keyword, label):
        """Register a fields section with the given keyword and label.

        Args:
            keyword (unicode):
                The keyword used in the docs.

            label (unicode):
                The label outputted in the section.
        """
        self._sections[keyword] = lambda *args: \
            self._format_fields(label, self._consume_fields())

    def _parse(self, parse=False):
        """Parse the docstring.

        By default (when called from the parent class), this won't do anything.
        It requires passing ``True`` in order to parse. This is there to
        prevent the parent class from prematurely parsing before all sections
        are rendered.

        Args:
            parse (bool, optional):
                Set whether the parsing should actually happen.
        """
        if parse:
            super(BeanbagDocstring, self)._parse()

    def _consume_field(self, parse_type=True, *args, **kwargs):
        """Parse a field line and return the field's information.

        This enhances the default version from Napoleon to allow for attribute
        types that wrap across multiple lines.

        Args:
            parse_type (bool, optional):
                Whether to parse type information.

            *args (tuple):
                Position arguments to pass to the paren method.

            **kwargs (dict):
                Keyword arguments to pass to the paren method.

        Returns:
            tuple:
            Information on the field. The format is dependent on the parent
            method.
        """
        if parse_type:
            lines = self._line_iter.peek(1)
            m = self.partial_typed_arg_start_re.match(lines[0])

            if m:
                result = None

                for i in range(1, self.MAX_PARTIAL_TYPED_ARG_LINES):
                    # See if there's an ending part anywhere.
                    lines = self._line_iter.peek(i + 1)

                    m = self.partial_typed_arg_start_re.match(lines[i])

                    if m:
                        # We're in a new typed arg. Bail.
                        break

                    m = self.partial_typed_arg_end_re.match(lines[i])

                    if m:
                        result = '%s%s' % (
                            lines[0],
                            ''.join(line.strip() for line in lines[1:])
                        )
                        break

                if result:
                    # Consume those lines so they're not processed again.
                    self._line_iter.next(len(lines))

                    # Insert the new resulting line in the line cache for
                    # processing.
                    self._line_iter._cache.appendleft(result)

        return super(BeanbagDocstring, self)._consume_field(parse_type,
                                                            *args, **kwargs)


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


def _process_docstring(app, what, name, obj, options, lines):
    """Process a docstring.

    If Beanbag docstrings are enabled, this will parse them and replace the
    docstring lines.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application.

        what (unicode):
            The type of thing owning the docstring.

        name (unicode):
            The name of the thing owning the docstring.

        obj (object):
            The object owning the docstring.

        options (dict):
            Options passed to this handler.

        lines (list of unicode):
            The lines to process.
    """
    if app.config['napoleon_beanbag_docstring']:
        docstring = BeanbagDocstring(lines, app.config, app, what, name, obj,
                                     options)
        lines[:] = docstring.lines()[:]


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
    app.add_config_value('napoleon_beanbag_docstring', False, True)

    app.connect(b'autodoc-skip-member', _filter_members)
    app.connect(b'autodoc-process-docstring', _process_docstring)
