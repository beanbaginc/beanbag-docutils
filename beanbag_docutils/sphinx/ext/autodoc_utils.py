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
            '__annotations__',
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


Better Documentation for Inherited TypedDicts
=============================================

.. versionadded:: 3.0

When a TypedDict inherits from another, the actual MRO is flattened, leaving
any attributes that come from the parent classes without docstrings/comments in
the generated documentation. Including ``autodoc_utils`` will automatically fix
these to scan the original base classes when docs are missing for some members.

This uses ``__orig_bases__``, which was added for TypedDict in Python 3.11. If
using this with older versions of Python,
:py:class:`typing_extensions.TypedDict` should be used instead.


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

from __future__ import annotations

import re
import sys
from inspect import isclass
from typing import TYPE_CHECKING, TypedDict

from sphinx import version_info
from sphinx.ext.autodoc import AttributeDocumenter, ClassDocumenter
from sphinx.ext.napoleon.docstring import GoogleDocstring
from sphinx.pycode import ModuleAnalyzer

from beanbag_docutils import get_version_string

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing import Any

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.ext.autodoc import ObjectMember, Options
    from sphinx.util.typing import ExtensionMetadata
    from typing_extensions import NotRequired

try:
    from sphinx.ext.napoleon.docstring import _convert_type_spec
except ImportError:
    if TYPE_CHECKING:
        assert False
    else:
        def _convert_type_spec(
            type_part: str,
            type_aliases: Mapping[str, str],
        ) -> str:
            try:
                return type_aliases[type_part]
            except KeyError:
                if type_part == 'None':
                    return ':obj:`None`'
                else:
                    return f':class:`{type_part}`'


class ReturnsSectionOptions(TypedDict):
    """Options for registering a "Returns"-like section.

    Version Added:
        3.0
    """

    #: Whether the type is required, and assumed to be the first line.
    require_type: NotRequired[bool]


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

    extra_returns_sections: Sequence[
        tuple[str, str, ReturnsSectionOptions]
    ] = [
        ('context', 'Context', {}),
        ('type', 'Type', {
            'require_type': True,
        }),
    ]

    extra_fields_sections: Sequence[tuple[str, str]] = [
        ('keys', 'Keys'),
        ('model attributes', 'Model Attributes'),
        ('option args', 'Option Args'),
        ('tuple', 'Tuple'),
    ]

    extra_version_info_sections: Sequence[tuple[str, str]] = [
        ('deprecated', 'deprecated'),
        ('version added', 'versionadded'),
        ('version changed', 'versionchanged'),
    ]

    MAX_PARTIAL_TYPED_ARG_LINES = 3

    COMMA_RE = re.compile(r',\s*')

    # Type is ignored here because some type checkers get annoyed at comparing
    # tuple[Literal[], ...].
    _USES_LINES_DEQUE = (version_info[:2] >= (5, 1))  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the parser.

        Args:
            *args (tuple):
                Positional arguments for the parent.

            **kwargs (dict):
                Keyword arguments for the parent.
        """
        super().__init__(*args, **kwargs)

        for keyword, label, options in self.extra_returns_sections:
            self.register_returns_section(
                keyword, label, options)

        for keyword, label in self.extra_fields_sections:
            self.register_fields_section(keyword, label)

        for keyword, admonition in self.extra_version_info_sections:
            self.register_version_info_section(keyword, admonition)

        self._parse(True)

    def register_returns_section(
        self,
        keyword: str,
        label: str,
        options: (ReturnsSectionOptions | None) = None,
    ) -> None:
        """Register a Returns-like section with the given keyword and label.

        Args:
            keyword (str):
                The keyword used in the docs.

            label (str):
                The label outputted in the section.

            options (ReturnsSectionOptions, optional):
                Options for the registration.

                Version Added:
                    2.0
        """
        if options is None:
            options = {}

        self._sections[keyword] = lambda *args: \
            self._format_fields(
                label,
                self._consume_returns_section(**options))

    def register_fields_section(
        self,
        keyword: str,
        label: str,
    ) -> None:
        """Register a fields section with the given keyword and label.

        Args:
            keyword (str):
                The keyword used in the docs.

            label (str):
                The label outputted in the section.
        """
        self._sections[keyword] = lambda *args: \
            self._format_fields(label, self._consume_fields())

    def register_version_info_section(
        self,
        keyword: str,
        admonition: str,
    ) -> None:
        """Register a version section with the given keyword and admonition.

        Args:
            keyword (str):
                The keyword used in the docs.

            admonition (str):
                The admonition to use for the section.
        """
        self._sections[keyword] = lambda *args: \
            self._format_admonition_with_params(
                admonition,
                self._consume_to_next_section())

    def _format_admonition_with_params(
        self,
        admonition: str,
        lines: list[str],
    ) -> list[str]:
        """Format an admonition section with the first line as a parameter.

        Args:
            admonition (str):
                The admonition name.

            lines (list of str):
                The list of lines to format.

        Returns:
            list of str:
            The resulting list of lines.
        """
        lines = self._strip_empty(lines)

        if lines:
            param_line = lines[0].strip()

            if param_line.endswith(':'):
                param_line = param_line[:-1]

            return [
                f'.. {admonition}:: {param_line}',
                '',
                *self._indent(self._dedent(lines[1:]), 3),
                '',
            ]
        else:
            return [f'.. {admonition}::', '']

    def _parse(
        self,
        parse: bool = False,
    ) -> None:
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
            super()._parse()

    def _consume_field(
        self,
        parse_type: bool = True,
        *args,
        **kwargs,
    ) -> tuple[str, Any, list[str]]:
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

                    if not isinstance(lines[i], str):
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

        name, type_str, desc = super()._consume_field(
            parse_type, *args, **kwargs)

        return (name, self.make_type_reference(type_str), desc)

    def _consume_returns_section(
        self,
        *args,
        require_type: bool = False,
        **kwargs,
    ) -> list[tuple[str, str, list[str]]]:
        """Consume a returns section, converting and handling types.

        This enhances the default version from Napoleon to allow for
        return-like sections lacking a description, and to intelligently
        process type references.

        Version Added:
            2.0:
            This is the first release to override this functionality.

        Args:
            *args (tuple):
                Position arguments to pass to the paren method.

            require_type (bool, optional):
                Whether to assume the first line is a type.

            **kwargs (dict):
                Keyword arguments to pass to the paren method.

        Returns:
            tuple:
            Information on the field. The format is dependent on the parent
            method.
        """
        if require_type:
            lines = self.peek_lines(1)

            if lines:
                param_line = lines[0].rstrip()

                if not param_line.endswith(':'):
                    self.consume_lines(1)
                    self.queue_line(f'{param_line}:')

        nodes = super()._consume_returns_section(
            *args, **kwargs)

        return [
            (name, self.make_type_reference(type_str), desc)
            for name, type_str, desc in nodes
        ]

    def peek_lines(
        self,
        num_lines: int = 1,
    ) -> list[str]:
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
            # Sphinx < 5.1. Type is ignored because _line_iter doesn't exist in
            # current versions.
            return self._line_iter.peek(num_lines)  # type: ignore

    def consume_lines(
        self,
        num_lines: int,
    ) -> None:
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
            for _i in range(num_lines):
                self._lines.popleft()
        else:
            # Sphinx < 5.1. Type is ignored because _line_iter doesn't exist in
            # current versions.
            self._line_iter.next(num_lines)  # type: ignore

    def queue_line(
        self,
        line: str,
    ) -> None:
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
            self._line_iter._cache.appendleft(line)  # type: ignore

    def make_type_reference(
        self,
        type_str: str,
    ) -> str:
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
            type_str (str):
                The string to parse and create references from.

        Returns:
            str:
            The new string.
        """
        if not type_str:
            return type_str

        type_aliases = \
            getattr(self._config, 'napoleon_type_aliases', None) or {}
        parts = type_str.split(',')
        type_parts = []

        for type_part in parts[0].split(' '):
            if type_part not in {'of', 'or'}:
                type_part = _convert_type_spec(type_part, type_aliases)

            type_parts.append(type_part)

        new_parts = [' '.join(type_parts)]

        if len(parts) > 1:
            new_parts += [
                f' *{_part.strip()}*'
                for _part in parts[1:]
            ]

        return ','.join(new_parts)


def _filter_members(
    app: Sphinx,
    what: str,
    name: str,
    obj: Any,
    skip: bool,
    options: Options,
) -> bool:
    """Filter members out of the documentation.

    This will look up the name in the ``autodoc_excludes`` table under the
    ``what`` and under ``'*'`` keys. If an entry is listed, it will be
    excluded from the documentation.

    It will also skip modules listed in ``__deprecated__`` in the documented
    module.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register roles and configuration on.

        what (str):
            The type of thing being filtered (one of ``attribute``, ``class``,
            ``exception``, ``function``, ``method``, or ``module``).

        name (str):
            The name of the object to look up in the filter lists.

        obj (object):
            The object that may be filtered.

        skip (bool):
            Whether the filter will be skipped if this handler doesn't
            return a different value.

        options (sphinx.ext.autodoc.Options):
            Options given to the autodoc directive.

    Returns:
        bool:
        Whether the member will be skipped.
    """
    module_name = app.env.temp_data.get('autodoc:module')

    if not module_name:
        return False

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


def _process_docstring(
    app: Sphinx,
    what: str,
    name: str,
    obj: Any,
    options: Options,
    lines: list[str],
) -> None:
    """Process a docstring.

    If Beanbag docstrings are enabled, this will parse them and replace the
    docstring lines.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application.

        what (str):
            The type of thing owning the docstring.

        name (str):
            The name of the thing owning the docstring.

        obj (object):
            The object owning the docstring.

        options (sphinx.ext.autodoc.Options):
            Options passed to this handler.

        lines (list of str):
            The lines to process.
    """
    if app.config['napoleon_beanbag_docstring']:
        docstring = BeanbagDocstring(lines, app.config, app, what, name, obj,
                                     options)
        lines[:] = docstring.lines()[:]


def _replace_config_default(
    config: Config,
    name: str,
    new_default: Any,
) -> None:
    """Replace a default Sphinx configuration value.

    This provides compatibility with multiple versions of Sphinx.

    Args:
        config (sphinx.config.Config):
            The configuration to modify.

        name (str):
            The name of the configuration option.

        new_default (object):
            The new default value for the configuration option.
    """
    config_values = config.values
    value = config_values[name]

    del config_values[name]

    if isinstance(value, tuple):
        # Sphinx <= 7.2
        rebuild, types = value[1:]
    else:
        # Sphinx >= 7.3
        rebuild = value.rebuild
        types = value.valid_types

    config.add(name=name,
               default=new_default,
               rebuild=rebuild,
               types=types)


def _on_config_inited(
    app: Sphinx,
    config: Config,
) -> None:
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
        _replace_config_default(config, 'autodoc_member_order', 'bysource')
        _replace_config_default(config, 'autoclass_content', 'class')

        config.autodoc_default_options = dict({
            'members': True,
            'special-members': True,
            'undoc-members': True,
            'show-inheritance': True,
        }, **(config.autodoc_default_options or {}))

    # Register type aliases.
    new_type_aliases = {}

    if 'python' in config.intersphinx_mapping:
        python_intersphinx = config.intersphinx_mapping['python'][0]

        if python_intersphinx is not None:
            if python_intersphinx.startswith('https://docs.python.org/2'):
                # Python 2
                #
                # Note that 'list' does not have corresponding type
                # documentation in Python 2.
                new_type_aliases.update({
                    'tuple': ':py:func:`tuple <tuple>`',
                    'unicode': ':py:func:`unicode <unicode>`',
                })
            else:
                # Python 3
                new_type_aliases.update({
                    'list': ':py:class:`list`',
                    'tuple': ':py:class:`tuple`',
                    'unicode': ':py:class:`str <str>`',
                })

    if new_type_aliases:
        if config.napoleon_type_aliases is None:
            config.napoleon_type_aliases = new_type_aliases.copy()
        else:
            config.napoleon_type_aliases.update(new_type_aliases)

        if 'autodoc_type_aliases' in config:
            config.autodoc_type_aliases.update(new_type_aliases)

    # Update autodoc_excludes to include defaults if requested.
    #
    # We'll also ensure all lists are sets, to make processing faster.
    if config.autodoc_excludes.get('__defaults__'):
        new_autodoc_excludes = {
            '*': {
                '__annotations__',
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
            for key, value in config.autodoc_excludes.items()
            if key not in {'*', '__defaults__'}
        })
    else:
        new_autodoc_excludes = {
            key: set(value)
            for key, value in config.autodoc_excludes.items()
            if key != '__defaults__'
        }

    config.autodoc_excludes = new_autodoc_excludes


#: A cache of docstrings which were extracted for inherited TypedDicts.
#:
#: Version Added:
#:     3.0
_found_docstrings: dict[tuple[type, str], Sequence[str]] = {}


class BeanbagClassDocumenter(ClassDocumenter):
    """A ClassDocumenter that handles docstrings for inherited TypedDicts.

    When a TypedDict inherits from another, the MRO is flattened so the class
    inherits directly from :py:class:`dict`, making it so Sphinx can't find
    docstrings/comments for attributes that come from parent classes. This
    class will iterate up the ``__orig_bases__`` chain in order to find
    docstrings in parent classes.

    The docstrings are returned here (in case any custom templates are using
    the loaded member data), and also cached in :py:data:`_found_docstrings`,
    which is used by :py:class:`BeanbagAttributeDocumenter` to actually output
    the documentation for the attributes.

    Version Added:
        3.0
    """

    def get_object_members(
        self,
        want_all: bool,
    ) -> tuple[bool, list[ObjectMember]]:
        """Get members for the class.

        Args:
            want_all (bool):
                Whether to get all members for the class.

        Returns:
            tuple:
            A 2-tuple of:

            Tuple:
                0 (bool):
                    Whether to check if the item is actually in the module. In
                    effect this will always be ``False``.

                1 (list of sphinx.ext.autodoc.ObjectMember):
                    The list of members to document.
        """
        check, members = super().get_object_members(want_all)

        obj = self.object

        if not isclass(obj) or not issubclass(obj, dict):
            return check, members

        if orig_bases := getattr(obj, '__orig_bases__', None):
            for member in members:
                name = member.__name__

                if (member.docstring is None and not
                    name.startswith('__')):
                    docstring = self._get_inherited_docstring(
                        name, orig_bases)

                    if docstring:
                        _found_docstrings[obj, name] = docstring
                        member.docstring = '\n'.join(docstring)

        return check, members

    def _get_inherited_docstring(
        self,
        name: str,
        orig_bases: Sequence[type],
    ) -> Sequence[str] | None:
        """Get the docstring for an inherited attribute.

        Args:
            name (str):
                The name of the attribute.

            orig_bases (list of type):
                The list of original bases to search for the docstring.

        Returns:
            list of str:
            The docstring of the attribute, split into lines.
        """
        for orig_base in orig_bases:
            analyzer = ModuleAnalyzer.for_module(orig_base.__module__)
            analyzer.analyze()

            docs = analyzer.attr_docs.get((orig_base.__name__, name))

            if docs is not None:
                return docs

        # If we didn't find it, go through the bases again and see if any of
        # those are themselves inherited TypedDicts.
        for orig_base in orig_bases:
            if new_orig_bases := getattr(orig_base, '__orig_bases__', None):
                docs = self._get_inherited_docstring(name, new_orig_bases)

                if docs:
                    return docs

        return None


class BeanbagAttributeDocumenter(AttributeDocumenter):
    """An AttributeDocumenter that handles docstrings for inherited TypedDicts.

    Version Added:
        3.0
    """

    def get_attribute_comment(
        self,
        parent: Any,
        attrname: str,
    ) -> list[str] | None:
        """Return the comment for the attribute.

        Args:
            parent (type):
                The parent class of the attribute.

            attrname (str):
                The name of the attribute.

        Returns:
            list of str:
            The docstring/doc comment of the attribute, split into lines.
        """
        comment = super().get_attribute_comment(parent, attrname)

        if comment is None:
            comment = _found_docstrings.get((parent, attrname))

        return comment


def setup(
    app: Sphinx,
) -> ExtensionMetadata:
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

    app.add_config_value('use_beanbag_autodoc_defaults', True, 'env')
    app.add_config_value('autodoc_excludes', {'__defaults__':
                                              True}, 'env')
    app.add_config_value('napoleon_beanbag_docstring', True, 'env')

    app.connect('autodoc-skip-member', _filter_members)
    app.connect('autodoc-process-docstring', _process_docstring)
    app.connect('config-inited', _on_config_inited)

    app.add_autodocumenter(BeanbagAttributeDocumenter, override=True)
    app.add_autodocumenter(BeanbagClassDocumenter, override=True)

    return {
        'version': get_version_string(),
        'parallel_read_safe': True,
    }
