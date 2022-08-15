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

* New ``Deprecated:``, ``Version Added:``, and ``Version Changed:`` sections
  for defining version-related information.

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

By default, ``autodoc_excludes`` is set to::

    autodoc_excludes = {
        # Applies to modules, classes, and anything else.
        '*': [
            '__dict__',
            '__doc__',
            '__module__',
            '__weakref__',
        ],
    }

If overriding, you can set ``'__defaults__': True`` to merge your changes in
with these defaults.

.. versionchanged:: 2.0
   Changed from a default of an empty dictionary, and added the
   ``__defaults__`` option.


.. _autodoc-skip-member:
   http://www.sphinx-doc.org/en/stable/ext/autodoc.html#event-autodoc-skip-member


Setup
=====

.. versionchanged:: 2.0
   Improved setup by enabling other default extensions and options when
   enabling this extension.


To use this, add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.autodoc_utils',
        ...
    ]

This will automatically enable the :py:mod:`sphinx.ext.autodoc`,
:py:mod:`sphinx.ext.intersphinx`, and :py:mod:`sphinx.ext.napoleon` extensions,
and enable the following autodoc options::

    autodoc_member_order = 'bysource'
    autoclass_content = 'class'
    autodoc_default_options = {
        'members': True,
        'special-members': True,
        'undoc-members': True,
        'show-inheritance': True,
    }

These default options can be turned off by setting
``use_beanbag_autodoc_defaults=False``.


Configuration
=============

``autodoc_excludes``
    Optional global exclusions to apply, as shown above.

``napoleon_beanbag_docstring``
    Set whether the Beanbag docstring format should be used.

    This is the default as of ``beanbag-docutils`` 2.0.

``use_beanbag_autodoc_defaults``
    Set whether autodoc defaults should be used.

    .. versionadded:: 2.0
"""

from __future__ import unicode_literals

import re
import sys

import six
from sphinx import version_info
from sphinx.ext.napoleon.docstring import GoogleDocstring, _convert_type_spec

from beanbag_docutils import VERSION


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
        ('context', 'Context', {}),
        ('type', 'Type', {
            'require_type': True,
        }),
    ]

    extra_fields_sections = [
        ('keys', 'Keys'),
        ('model attributes', 'Model Attributes'),
        ('option args', 'Option Args'),
        ('tuple', 'Tuple'),
    ]

    extra_version_info_sections = [
        ('deprecated', 'deprecated'),
        ('version added', 'versionadded'),
        ('version changed', 'versionchanged'),
    ]

    MAX_PARTIAL_TYPED_ARG_LINES = 3

    COMMA_RE = re.compile(r',\s*')

    _USES_LINES_DEQUE = (version_info[:2] >= (5, 1))

    def __init__(self, *args, **kwargs):
        """Initialize the parser.

        Args:
            *args (tuple):
                Positional arguments for the parent.

            **kwargs (dict):
                Keyword arguments for the parent.
        """
        super(BeanbagDocstring, self).__init__(*args, **kwargs)

        for keyword, label, options in self.extra_returns_sections:
            self.register_returns_section(keyword, label, options)

        for keyword, label in self.extra_fields_sections:
            self.register_fields_section(keyword, label)

        for keyword, admonition in self.extra_version_info_sections:
            self.register_version_info_section(keyword, admonition)

        self._parse(True)

    def register_returns_section(self, keyword, label, options={}):
        """Register a Returns-like section with the given keyword and label.

        Args:
            keyword (unicode):
                The keyword used in the docs.

            label (unicode):
                The label outputted in the section.

            options (dict, optional):
                Options for the registration.

                This accepts:

                Keys:
                    require_type (bool, optional):
                        Whether the type is required, and assumed to be the
                        first line.

                Version Added:
                    2.0
        """
        self._sections[keyword] = lambda *args: \
            self._format_fields(
                label,
                self._consume_returns_section(**options))

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

    def register_version_info_section(self, keyword, admonition):
        """Register a version section with the given keyword and admonition.

        Args:
            keyword (unicode):
                The keyword used in the docs.

            admonition (unicode):
                The admonition to use for the section.
        """
        self._sections[keyword] = lambda *args: \
            self._format_admonition_with_params(
                admonition,
                self._consume_to_next_section())

    def _format_admonition_with_params(self, admonition, lines):
        """Format an admonition section with the first line as a parameter.

        Args:
            admonition (unicode):
                The admonition name.

            lines (list of unicode):
                The list of lines to format.

        Returns:
            list of unicode:
            The resulting list of lines.
        """
        lines = self._strip_empty(lines)

        if lines:
            param_line = lines[0].strip()

            if param_line.endswith(':'):
                param_line = param_line[:-1]

            return (
                ['.. %s:: %s' % (admonition, param_line), ''] +
                self._indent(self._dedent(lines[1:]), 3) + ['']
            )
        else:
            return ['.. %s::' % admonition, '']

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
            lines = self.peek_lines()
            m = self.partial_typed_arg_start_re.match(lines[0])

            if m:
                result = None

                for i in range(1, self.MAX_PARTIAL_TYPED_ARG_LINES):
                    # See if there's an ending part anywhere.
                    lines = self.peek_lines(i + 1)

                    if not isinstance(lines[i], six.string_types):
                        # We're past the strings and into something else.
                        # Bail.
                        break

                    m = self.partial_typed_arg_start_re.match(lines[i])

                    if m:
                        # We're in a new typed arg. Bail.
                        break

                    m = self.partial_typed_arg_end_re.match(lines[i])

                    if m:
                        # We need to rebuild the string based on the lines
                        # we've determined for the field. We have to be
                        # careful to join them in such a way where we have
                        # a space in-between if separating words, but not if
                        # separating parts of a class name.
                        parts = []
                        prev_line = None

                        for line in lines:
                            norm_line = line.strip()

                            if norm_line and prev_line is not None:
                                if (norm_line.startswith('.') or
                                    prev_line.endswith('.')):
                                    line = norm_line
                                else:
                                    parts.append(' ')

                            parts.append(line)
                            prev_line = norm_line

                        result = ''.join(parts)

                        if ',' in result:
                            result = ', '.join(self.COMMA_RE.split(result))

                        break

                if result:
                    # Consume those lines so they're not processed again.
                    self.consume_lines(len(lines))

                    # Insert the new resulting line in the line cache for
                    # processing.
                    self.queue_line(result)

        name, type_str, desc = super(BeanbagDocstring, self)._consume_field(
            parse_type, *args, **kwargs)

        return (name, self.make_type_reference(type_str), desc)

    def _consume_returns_section(self, *args, **kwargs):
        """Consume a returns section, converting and handling types.

        This enhances the default version from Napoleon to allow for
        return-like sections lacking a description, and to intelligently
        process type references.

        Version Added:
            2.0:
            This is the first release to override this functionality.

        Args:
            require_type (bool, optional):
                Whether to assume the first line is a type.

            *args (tuple):
                Position arguments to pass to the paren method.

            **kwargs (dict):
                Keyword arguments to pass to the paren method.

        Returns:
            tuple:
            Information on the field. The format is dependent on the parent
            method.
        """
        if kwargs.pop('require_type', False):
            lines = self.peek_lines(1)

            if lines:
                param_line = lines[0].rstrip()

                if not param_line.endswith(':'):
                    self.consume_lines(1)
                    self.queue_line('%s:' % param_line)

        nodes = super(BeanbagDocstring, self)._consume_returns_section(
            *args, **kwargs)

        return [
            (name, self.make_type_reference(type_str), desc)
            for name, type_str, desc in nodes
        ]

    def peek_lines(self, num_lines=1):
        """Return the specified number of lines without consuming them.

        Version Added:
            1.9

        Args:
            num_lines (int, optional):
                The number of lines to return.

        Returns:
            list of str:
            The resulting lines.
        """
        if self._USES_LINES_DEQUE:
            # Sphinx >= 5.1
            lines = self._lines

            return [
                lines.get(i)
                for i in range(num_lines)
            ]
        else:
            # Sphinx < 5.1
            return self._line_iter.peek(num_lines)

    def consume_lines(self, num_lines):
        """Consume the specified number of lines.

        This will ensure that these lines are not processed any further.

        Version Added:
            1.9

        Args:
            num_lines (int, optional):
                The number of lines to consume.
        """
        if self._USES_LINES_DEQUE:
            # Sphinx >= 5.1
            for i in range(num_lines):
                self._lines.popleft()
        else:
            # Sphinx < 5.1
            self._line_iter.next(num_lines)

    def queue_line(self, line):
        """Queue a line for processing.

        This will place the line at the beginning of the processing queue.

        Version Added:
            1.9

        Args:
            line (str):
                The line to queue.
        """
        if self._USES_LINES_DEQUE:
            # Sphinx >= 5.1
            self._lines.appendleft(line)
        else:
            # Sphinx < 5.1
            self._line_iter._cache.appendleft(line)

    def make_type_reference(self, type_str):
        """Create references to types in a type string.

        This will parse the string, separating out a type from zero or more
        suffixes (like ``, optional``).

        The type will be further parsed into a space-separated tokens. Each
        of those will be set as a reference, allowing Sphinx to try to link
        it. The exceptions are the words "of" and "or", which we use to
        list optional types.

        The suffixes are each formatted with emphasis.

        Version Added:
            2.0

        Args:
            type_str (unicode):
                The string to parse and create references from.

        Returns:
            unicode:
            The new string.
        """
        if not type_str:
            return type_str

        type_aliases = self._config.napoleon_type_aliases or {}
        parts = type_str.split(',')
        type_parts = []

        for type_part in parts[0].split(' '):
            if type_part not in ('of', 'or'):
                type_part = _convert_type_spec(type_part, type_aliases)

            type_parts.append(type_part)

        new_parts = [' '.join(type_parts)]

        if len(parts) > 1:
            new_parts += [
                r' *%s*' % _part.strip()
                for _part in parts[1:]
            ]

        return ','.join(new_parts)


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
    module_name = app.env.temp_data.get('autodoc:module')

    if not module_name:
        return

    module = sys.modules[module_name]

    # Check if the module itself is excluding this from the docs.
    module_excludes = getattr(module, '__autodoc_excludes__', [])

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


def _on_config_inited(app, config):
    """Override default configuration settings for Napoleon.

    This will ensure that some of our defaults take place for Beanbag
    docstring rendering.

    Version Added:
        2.0

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to override configuration on.

        config (sphinx.config.Config):
            The Sphinx configuration to override.
    """
    if config.use_beanbag_autodoc_defaults:
        # Turn off competing docstring parsers.
        config.napoleon_google_docstring = False
        config.napoleon_numpy_docstring = False

        # Force this off so that we can handle this ourselves when consuming a
        # field.
        config.napoleon_preprocess_types = False

        # Change some defaults.
        config.values['autodoc_member_order'] = \
            ('bysource',) + config.values['autodoc_member_order'][1:]
        config.values['autoclass_content'] = \
            ('class',) + config.values['autoclass_content'][1:]

        config.autodoc_default_options = dict({
            'members': True,
            'special-members': True,
            'undoc-members': True,
            'show-inheritance': True,
        }, **(config.autodoc_default_options or {}))

    # Register type aliases.
    if config.napoleon_type_aliases is None:
        config.napoleon_type_aliases = {}

    if 'python' in config.intersphinx_mapping:
        python_intersphinx = config.intersphinx_mapping['python'][0]

        if python_intersphinx is not None:
            if python_intersphinx.startswith('https://docs.python.org/2'):
                # Python 2
                #
                # Note that 'list' does not have corresponding type
                # documentation in Python 2.
                config.napoleon_type_aliases.update({
                    'tuple': ':py:func:`tuple <tuple>`',
                    'unicode': ':py:func:`unicode <unicode>`',
                })
            else:
                # Python 3
                config.napoleon_type_aliases.update({
                    'list': ':py:class:`list`',
                    'tuple': ':py:class:`tuple`',
                    'unicode': ':py:class:`unicode <str>`',
                })

    # Update autodoc_excludes to include defaults if requested.
    #
    # We'll also ensure all lists are sets, to make processing faster.
    if config.autodoc_excludes.get('__defaults__'):
        new_autodoc_excludes = {
            '*': {
                '__dict__',
                '__doc__',
                '__module__',
                '__weakref__',
            },
        }

        if '*' in config.autodoc_excludes:
            new_autodoc_excludes['*'].update(config.autodoc_excludes['*'])

        new_autodoc_excludes.update({
            key: set(value)
            for key, value in six.iteritems(config.autodoc_excludes)
            if key not in ('*', '__defaults__')
        })
    else:
        new_autodoc_excludes = {
            key: set(value)
            for key, value in six.iteritems(config.autodoc_excludes)
            if key != '__defaults__'
        }

    config.autodoc_excludes = new_autodoc_excludes


def setup(app):
    """Set up the Sphinx extension.

    This sets up the configuration and event handlers needed for enhancing
    auto-doc support.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register configuration and listen to
            events on.
    """
    app.setup_extension('sphinx.ext.autodoc')
    app.setup_extension('sphinx.ext.intersphinx')
    app.setup_extension('sphinx.ext.napoleon')

    app.add_config_value('use_beanbag_autodoc_defaults', True, True)
    app.add_config_value('autodoc_excludes', {'__defaults__': True}, True)
    app.add_config_value('napoleon_beanbag_docstring', True, True)

    app.connect('autodoc-skip-member', _filter_members)
    app.connect('autodoc-process-docstring', _process_docstring)
    app.connect('config-inited', _on_config_inited)

    return {
        'version': VERSION,
        'parallel_read_safe': True,
    }
