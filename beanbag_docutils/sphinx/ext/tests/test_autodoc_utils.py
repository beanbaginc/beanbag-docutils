"""Unit tests for beanbag_docutils.sphinx.ext.autodoc_utils."""

from __future__ import annotations

from sphinx import version_info as sphinx_version_info
from typing_extensions import TypedDict

from beanbag_docutils.sphinx.ext import autodoc_utils
from beanbag_docutils.sphinx.ext.autodoc_utils import BeanbagDocstring
from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


# A series of modules used to test autodoc exclusions.
class IgnoredModule:  # noqa
    pass


class DeprecatedModule:  # noqa
    pass


class DocClass1:  # noqa
    def foo(self):  # noqa
        pass

    def bar(self):  # noqa
        pass


class DocClass2:  # noqa
    def foo(self):  # noqa
        pass


# Classes for testing TypedDict inheritance.
class BaseTypedDict(TypedDict):
    """Base TypedDict class."""

    #: Base field with documentation.
    base_field: str


# Test classes for documenting actual behavior vs expected behavior.
class InheritedTypedDict(BaseTypedDict):
    """Inherited TypedDict class."""

    #: Inherited field with documentation.
    inherited_field: int

    #: Another field with documentation.
    another_field: str


class AutoDocExcludesTests(SphinxExtTestCase):
    """Unit tests for autodoc_excludes setting."""

    config = {
        'autoclass_content': 'class',
        'autodoc_default_options': {
            'members': None,
            'member-order': 'bysource',
            'special-members': None,
            'undoc-members': None,
        },
    }

    extensions = [
        autodoc_utils.__name__,
    ]

    def test_with_autodoc_excludes(self) -> None:
        """Testing autodoc_excludes with __autodoc_excludes__ in module"""
        rendered = self.render_doc(f'.. automodule:: {__name__}\n')

        self.assertIn('AutoDocExcludesTests', rendered)
        self.assertNotIn('IgnoredModule', rendered)

    def test_with_wildcard_exclude(self) -> None:
        """Testing autodoc_excludes with wildcard (*) exclude list"""
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        rendered = self.render_doc(
            doc,
            config={
                'autodoc_excludes': {
                    '*': ['__dict__', 'foo'],
                },
            }
        )

        self.assertNotIn('__dict__', rendered)
        self.assertNotIn('foo', rendered)
        self.assertIn('__module__', rendered)

    def test_with_wildcard_exclude_with_defaults(self) -> None:
        """Testing autodoc_excludes with wildcard (*) exclude list with
        defaults
        """
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        rendered = self.render_doc(doc)

        self.assertIn('foo', rendered)

    def test_with_wildcard_exclude_added_to_defaults(self) -> None:
        """Testing autodoc_excludes with wildcard (*) exclude list added to
        defaults
        """
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        rendered = self.render_doc(
            doc,
            config={
                'autodoc_excludes': {
                    '__defaults__': True,
                    '*': ['foo'],
                },
            }
        )

        self.assertNotIn('__dict__', rendered)
        self.assertNotIn('foo', rendered)
        self.assertNotIn('__module__', rendered)

    def test_with_class_attr_exclude(self) -> None:
        """Testing autodoc_excludes with class exclude list"""
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        # Now exclude them.
        rendered = self.render_doc(
            doc,
            config={
                'autodoc_excludes': {
                    'class': ['__dict__', 'foo'],
                },
            }
        )

        self.assertIn('DocClass1.__module__', rendered)
        self.assertIn('DocClass2.__module__', rendered)
        self.assertIn('DocClass1.bar', rendered)
        self.assertNotIn('DocClass1.__dict__', rendered)
        self.assertNotIn('DocClass1.foo', rendered)
        self.assertNotIn('DocClass2.__dict__', rendered)
        self.assertNotIn('DocClass2.foo', rendered)

    def test_with_class_attr_exclude_with_defaults(self) -> None:
        """Testing autodoc_excludes with class exclude list with defaults"""
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        # Make sure the attributes on these classes are here by default.
        rendered = self.render_doc(doc)

        self.assertIn('DocClass1.foo', rendered)
        self.assertIn('DocClass1.bar', rendered)
        self.assertIn('DocClass2.foo', rendered)
        self.assertNotIn('DocClass1.__dict__', rendered)
        self.assertNotIn('DocClass1.__module__', rendered)
        self.assertNotIn('DocClass2.__dict__', rendered)
        self.assertNotIn('DocClass2.__module__', rendered)

    def test_with_class_attr_exclude_and_added_to_defaults(self) -> None:
        """Testing autodoc_excludes with class exclude list and added with
        defaults
        """
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        # Now exclude them.
        rendered = self.render_doc(
            doc,
            config={
                'autodoc_excludes': {
                    '__defaults__': True,
                    'class': ['foo'],
                },
            }
        )

        self.assertIn('DocClass1.bar', rendered)
        self.assertNotIn('DocClass1.__module__', rendered)
        self.assertNotIn('DocClass1.__dict__', rendered)
        self.assertNotIn('DocClass1.foo', rendered)
        self.assertNotIn('DocClass2.__module__', rendered)
        self.assertNotIn('DocClass2.__dict__', rendered)
        self.assertNotIn('DocClass2.foo', rendered)

    def test_with_empty_excludes(self) -> None:
        """Testing autodoc_excludes with empty excludes"""
        doc = '\n'.join([
            f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}',
            '',
            f'.. autoclass:: {DocClass2.__module__}.{DocClass2.__name__}',
        ])

        # Make sure some our attributes are here by default.
        rendered = self.render_doc(
            doc,
            config={
                'autodoc_excludes': {},
            })

        self.assertIn('__dict__', rendered)
        self.assertIn('foo', rendered)
        self.assertIn('__module__', rendered)
        self.assertIn('DocClass1.__module__', rendered)

    def test_with_deprecated(self) -> None:
        """Testing autodoc_excludes with __deprecated__ in module"""
        rendered = self.render_doc(f'.. automodule:: {__name__}\n')

        self.assertIn('AutoDocExcludesTests', rendered)
        self.assertNotIn('DeprecatedModule', rendered)


class BeanbagDocstringTests(SphinxExtTestCase):
    """Unit tests for BeanbagDocstring."""

    extensions = [
        autodoc_utils.__name__,
    ]

    def test_args_section(self) -> None:
        """Testing Beanbag docstring with Args section"""
        rendered = self._render_docstring(
            'Args:\n'
            '   arg1 (str):\n'
            '       Description of arg1.\n'
            '\n'
            '   arg2 (foo.bar.abc\n'
            '         .def.ghi,\n'
            '         optional):\n'
            '       Description of arg2.\n'
            '\n'
            '   *args (tuple):\n'
            '       Description of args.\n'
            '\n'
            '   **kwargs (dict):\n'
            '       Description of kwargs.\n'
        )

        # Type is ignored here because some type checkers get annoyed at
        # comparing tuple[Literal[], ...].
        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(
                rendered,
                ':param arg1: Description of arg1.\n'
                ':type arg1: :py:class:`str`\n'
                ':param arg2: Description of arg2.\n'
                ':type arg2: :py:class:`foo.bar.abc.def.ghi`, *optional*\n'
                ':param \\*args: Description of args.\n'
                ':type \\*args: :py:class:`tuple`\n'
                ':param \\*\\*kwargs: Description of kwargs.\n'
                ':type \\*\\*kwargs: :py:class:`dict`\n')
        else:
            self.assertEqual(
                rendered,
                ':param arg1: Description of arg1.\n'
                ':type arg1: :class:`str`\n'
                ':param arg2: Description of arg2.\n'
                ':type arg2: :class:`foo.bar.abc.def.ghi`, *optional*\n'
                ':param \\*args: Description of args.\n'
                ':type \\*args: :class:`tuple`\n'
                ':param \\*\\*kwargs: Description of kwargs.\n'
                ':type \\*\\*kwargs: :class:`dict`\n')

    def test_context_section_with_description(self) -> None:
        """Testing Beanbag docstring with Context section with description"""
        self.assertEqual(
            self._render_docstring(
                'Context:\n'
                '    Description of the context.\n'
            ),
            ':Context: Description of the context.\n'
        )

    def test_context_section_with_type(self) -> None:
        """Testing Beanbag docstring with Context section with type"""
        self.assertEqual(
            self._render_docstring(
                'Context:\n'
                '    dict\n'
            ),
            ':Context: dict\n'
        )

    def test_context_section_with_type_and_description(self) -> None:
        """Testing Beanbag docstring with Context section with type and
        description
        """
        rendered = self._render_docstring(
            'Context:\n'
            '    dict:\n'
            '    Description of the context.\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(
                rendered,
                ':Context: :py:class:`dict` -- Description of the context.\n')
        else:
            self.assertEqual(
                rendered,
                ':Context: :class:`dict` -- Description of the context.\n')

    def test_deprecated_section_with_version(self) -> None:
        """Testing Beanbag docstring with Deprecated section with version"""
        self.assertEqual(
            self._render_docstring(
                'Deprecated:\n'
                '    2.0\n'
            ),
            '.. deprecated:: 2.0\n\n'
        )

    def test_deprecated_section_with_version_and_description(self) -> None:
        """Testing Beanbag docstring with Deprecated section with version and
        description
        """
        self.assertEqual(
            self._render_docstring(
                'Deprecated:\n'
                '    2.0:\n'
                '    Description of the deprecation.\n'
            ),
            (
                '.. deprecated:: 2.0\n'
                '\n'
                '   Description of the deprecation.\n'
            )
        )

    def test_deprecated_section_with_version_and_lists(self) -> None:
        """Testing Beanbag docstring with Deprecated section with lists"""
        self.assertEqual(
            self._render_docstring(
                'Deprecated:\n'
                '    2.0:\n'
                '    * This is item one and it\n'
                '      wraps across multiple\n'
                '      lines\n'
                '\n'
                '    * And this is item 2.\n'
                '      Still multiple lines.\n'
            ),
            (
                '.. deprecated:: 2.0\n'
                '\n'
                '   * This is item one and it\n'
                '     wraps across multiple\n'
                '     lines\n'
                '   \n'
                '   * And this is item 2.\n'
                '     Still multiple lines.\n'
            )
        )

    def test_keys(self) -> None:
        """Testing Beanbag docstring with Keys section"""
        rendered = self._render_docstring(
            'Keys:\n'
            '    key1 (str):\n'
            '        Description 1\n'
            '\n'
            '    key2 (dict):\n'
            '        Description 2\n'
            '\n'
            '    key3 (int, optional):\n'
            '        Description 3\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(
                rendered,
                ':Keys: * **key1** (:py:class:`str`) -- Description 1\n'
                '       * **key2** (:py:class:`dict`) -- Description 2\n'
                '       * **key3** (:py:class:`int`, *optional*)'
                ' -- Description 3\n')
        else:
            self.assertEqual(
                rendered,
                ':Keys: * **key1** (:class:`str`) -- Description 1\n'
                '       * **key2** (:class:`dict`) -- Description 2\n'
                '       * **key3** (:class:`int`, *optional*)'
                ' -- Description 3\n')

    def test_model_attributes(self) -> None:
        """Testing Beanbag docstring with Model Attributes section"""
        rendered = self._render_docstring(
            'Model Attributes:\n'
            '    attr1 (dict):\n'
            '        Description of attr1\n'
            '\n'
            '    attr2 (foo.bar\n'
            '           .baz):\n'
            '        Description of attr2\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(
                rendered,
                ':Model Attributes: * **attr1** (:py:class:`dict`)'
                ' -- Description of attr1\n'
                '                   * **attr2** (:py:class:`foo.bar.baz`)'
                ' -- Description of attr2\n')
        else:
            self.assertEqual(
                rendered,
                ':Model Attributes: * **attr1** (:class:`dict`)'
                ' -- Description of attr1\n'
                '                   * **attr2** (:class:`foo.bar.baz`)'
                ' -- Description of attr2\n')

    def test_option_args(self) -> None:
        """Testing Beanbag docstring with Option Args section"""
        rendered = self._render_docstring(
            'Option Args:\n'
            '    attr1 (dict):\n'
            '        Description of attr1\n'
            '\n'
            '    attr2 (foo.bar\n'
            '           .baz,\n'
            '           optional):\n'
            '        Description of attr2\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(
                rendered,
                ':Option Args: * **attr1** (:py:class:`dict`)'
                ' -- Description of attr1\n'
                '              * **attr2** (:py:class:`foo.bar.baz`,'
                ' *optional*) -- Description of attr2\n')
        else:
            self.assertEqual(
                rendered,
                ':Option Args: * **attr1** (:class:`dict`)'
                ' -- Description of attr1\n'
                '              * **attr2** (:class:`foo.bar.baz`, *optional*)'
                ' -- Description of attr2\n')

    def test_tuple(self) -> None:
        """Testing Beanbag docstring with Tuple section"""
        rendered = self._render_docstring(
            'Tuple:\n'
            '    0 (str):\n'
            '        Description 1\n'
            '\n'
            '    1 (dict):\n'
            '        Description 2\n'
            '\n'
            '    2 (int, optional):\n'
            '        Description 3\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(
                rendered,
                ':Tuple: * **0** (:py:class:`str`) -- Description 1\n'
                '        * **1** (:py:class:`dict`) -- Description 2\n'
                '        * **2** (:py:class:`int`, *optional*) -- '
                'Description 3\n')
        else:
            self.assertEqual(
                rendered,
                ':Tuple: * **0** (:class:`str`) -- Description 1\n'
                '        * **1** (:class:`dict`) -- Description 2\n'
                '        * **2** (:class:`int`, *optional*) -- '
                'Description 3\n')

    def test_type_section(self) -> None:
        """Testing Beanbag docstring with Type section"""
        rendered = self._render_docstring(
            'Type:\n'
            '    dict\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(rendered, ':Type: :py:class:`dict`\n')
        else:
            self.assertEqual(rendered, ':Type: :class:`dict`\n')

    def test_type_section_with_description(self) -> None:
        """Testing Beanbag docstring with Type section with description"""
        rendered = self._render_docstring(
            'Type:\n'
            '    dict:\n'
            '    Description.\n'
        )

        if sphinx_version_info[:2] >= (7, 2):  # type:ignore
            self.assertEqual(rendered,
                             ':Type: :py:class:`dict` -- Description.\n')
        else:
            self.assertEqual(rendered,
                             ':Type: :class:`dict` -- Description.\n')

    def test_version_added_section_with_version(self) -> None:
        """Testing Beanbag docstring with Version Added section with version"""
        self.assertEqual(
            self._render_docstring(
                'Version Added:\n'
                '    2.0\n'
            ),
            (
                '.. versionadded:: 2.0\n'
                '\n'
            )
        )

    def test_version_added_section_with_version_and_description(self) -> None:
        """Testing Beanbag docstring with Version Added section with version
        and description
        """
        self.assertEqual(
            self._render_docstring(
                'Version Added:\n'
                '    2.0:\n'
                '    Description of the addition.\n'
            ),
            (
                '.. versionadded:: 2.0\n'
                '\n'
                '   Description of the addition.\n'
            )
        )

    def test_version_added_section_with_lists(self) -> None:
        """Testing Beanbag docstring with Version Added section with lists"""
        self.assertEqual(
            self._render_docstring(
                'Version Added:\n'
                '    2.0:\n'
                '    * This is item one and it\n'
                '      wraps across multiple\n'
                '      lines\n'
                '\n'
                '    * And this is item 2.\n'
                '      Still multiple lines.\n'
            ),
            (
                '.. versionadded:: 2.0\n'
                '\n'
                '   * This is item one and it\n'
                '     wraps across multiple\n'
                '     lines\n'
                '   \n'
                '   * And this is item 2.\n'
                '     Still multiple lines.\n'
            )
        )

    def test_version_changed_section(self) -> None:
        """Testing Beanbag docstring with Version Changed section"""
        self.assertEqual(
            self._render_docstring(
                'Version Changed:\n'
                '    2.0:\n'
                '    Description of the change.\n'
            ),
            (
                '.. versionchanged:: 2.0\n'
                '\n'
                '   Description of the change.\n'
            )
        )

    def test_version_changed_section_with_lists(self) -> None:
        """Testing Beanbag docstring with Version Changed section with lists"""
        self.assertEqual(
            self._render_docstring(
                'Version Changed:\n'
                '    2.0:\n'
                '    * This is item one and it\n'
                '      wraps across multiple\n'
                '      lines\n'
                '\n'
                '    * And this is item 2.\n'
                '      Still multiple lines.\n'
            ),
            (
                '.. versionchanged:: 2.0\n'
                '\n'
                '   * This is item one and it\n'
                '     wraps across multiple\n'
                '     lines\n'
                '   \n'
                '   * And this is item 2.\n'
                '     Still multiple lines.\n'
            )
        )

    def _render_docstring(
        self,
        content: str,
    ) -> str:
        """Render a Beanbag docstring to ReST.

        Args:
            content (str):
                The docstring content to render.

        Returns:
            str:
            The resulting ReStructuredText.
        """
        with self.with_sphinx_env() as ctx:
            return str(BeanbagDocstring(content, config=ctx['config']))


class TypedDictInheritanceTests(SphinxExtTestCase):
    """Unit tests for TypedDict inheritance feature."""

    extensions = [
        autodoc_utils.__name__,
    ]

    def test_base_typeddict_docstrings(self) -> None:
        """Testing base TypedDict documentation (no inheritance)"""
        doc = (
            f'.. autoclass:: {BaseTypedDict.__module__}.'
            f'{BaseTypedDict.__name__}'
        )

        rendered = self.render_doc(doc)

        # Check that the class itself is documented.
        self.assertIn('BaseTypedDict', rendered)
        self.assertIn('Base TypedDict class.', rendered)

        # Check that attributes are documented.
        self.assertIn('base_field', rendered)
        self.assertIn('Base field with documentation.', rendered)

    def test_inherited_typeddict_docstrings(self) -> None:
        """Testing inherited TypedDict documentation"""
        doc = (
            f'.. autoclass:: {InheritedTypedDict.__module__}.'
            f'{InheritedTypedDict.__name__}'
        )

        rendered = self.render_doc(doc)

        # Check that the class itself is documented.
        self.assertIn('InheritedTypedDict', rendered)
        self.assertIn('Inherited TypedDict class.', rendered)

        # Check that attributes in the inherited class are documented.
        self.assertIn('inherited_field', rendered)
        self.assertIn('Inherited field with documentation.', rendered)
        self.assertIn('another_field', rendered)
        self.assertIn('Another field with documentation.', rendered)

        # Check that attributes which come from the parent class are
        # documented.
        self.assertIn('base_field', rendered)
        self.assertIn('Base field with documentation.', rendered)

    def test_non_typeddict_class_unchanged(self) -> None:
        """Testing that non-TypedDict classes are unaffected"""
        doc = f'.. autoclass:: {DocClass1.__module__}.{DocClass1.__name__}'

        rendered = self.render_doc(doc)

        # Check that regular classes still work normally.
        self.assertIn('DocClass1', rendered)
        self.assertIn('foo', rendered)
        self.assertIn('bar', rendered)

    def test_beanbag_class_documenter_dict_subclass_check(self) -> None:
        """Testing BeanbagClassDocumenter properly checks for dict subclasses
        """
        # Test that TypedDict is recognized as dict subclass.
        self.assertTrue(issubclass(BaseTypedDict, dict))

        # Test that regular classes are not dict subclasses.
        self.assertFalse(issubclass(DocClass1, dict))


__autodoc_excludes__ = ['IgnoredModule']
__deprecated__ = ['DeprecatedModule']
