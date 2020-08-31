"""Unit tests for beanbag_docutils.sphinx.ext.autodoc_utils."""

from __future__ import unicode_literals

import six

from beanbag_docutils.sphinx.ext.autodoc_utils import BeanbagDocstring
from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


# A series of modules used to test autodoc exclusions.
class IgnoredModule(object):
    pass


class DeprecatedModule(object):
    pass


class DocClass1(object):
    def foo(self):
        pass


class DocClass2(object):
    def foo(self):
        pass


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
        'sphinx.ext.autodoc',
        'sphinx.ext.napoleon',
        'beanbag_docutils.sphinx.ext.autodoc_utils',
    ]

    def test_with_autodoc_excludes(self):
        """Testing autodoc_excludes with __autodoc_excludes__ in module"""
        rendered = self.render_doc('.. automodule:: %s\n' % __name__)

        self.assertIn('AutoDocExcludesTests', rendered)
        self.assertNotIn('IgnoredModule', rendered)

    def test_with_wildcard_exclude(self):
        """Testing autodoc_excludes with wildcard (*) exclude list"""
        doc = '\n'.join([
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass2.__name__),
            '',
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass2.__name__),
        ])

        # Make sure our attributes are here by default.
        rendered = self.render_doc(doc)

        self.assertIn('__dict__', rendered)
        self.assertIn('foo', rendered)
        self.assertIn('__module__', rendered)

        # Now exclude them.
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

    def test_with_class_attr_exclude(self):
        """Testing autodoc_excludes with class exclude list"""
        docclass1_path = '%s.%s' % (DocClass1.__module__, DocClass1.__name__)

        doc = '\n'.join([
            '.. autoclass:: %s' % docclass1_path,
            '',
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass2.__name__),
        ])

        # Make sure the attributes on these classes are here by default.
        rendered = self.render_doc(doc)

        self.assertIn('DocClass1.__dict__', rendered)
        self.assertIn('DocClass1.__module__', rendered)
        self.assertIn('DocClass1.foo', rendered)
        self.assertIn('DocClass2.__dict__', rendered)
        self.assertIn('DocClass2.__module__', rendered)
        self.assertIn('DocClass2.foo', rendered)

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
        self.assertNotIn('DocClass1.__dict__', rendered)
        self.assertNotIn('DocClass1.foo', rendered)
        self.assertIn('DocClass2.__module__', rendered)
        self.assertNotIn('DocClass2.__dict__', rendered)
        self.assertNotIn('DocClass2.foo', rendered)

    def test_with_deprecated(self):
        """Testing autodoc_excludes with __deprecated__ in module"""
        rendered = self.render_doc('.. automodule:: %s\n' % __name__)

        self.assertIn('AutoDocExcludesTests', rendered)
        self.assertNotIn('DeprecatedModule', rendered)


class BeanbagDocstringTests(SphinxExtTestCase):
    """Unit tests for BeanbagDocstring."""

    def test_args_section(self):
        """Testing Beanbag docstring with Args section"""
        self.assertEqual(
            self._render_docstring(
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
            ),
            (
                ':param arg1: Description of arg1.\n'
                ':type arg1: str\n'
                ':param arg2: Description of arg2.\n'
                ':type arg2: foo.bar.abc.def.ghi, optional\n'
                ':param \\*args: Description of args.\n'
                ':type \\*args: tuple\n'
                ':param \\*\\*kwargs: Description of kwargs.\n'
                ':type \\*\\*kwargs: dict\n'
            )
        )

    def test_context_section_with_description(self):
        """Testing Beanbag docstring with Context section with description"""
        self.assertEqual(
            self._render_docstring(
                'Context:\n'
                '    Description of the context.\n'
            ),
            ':Context: Description of the context.\n'
        )

    def test_context_section_with_type(self):
        """Testing Beanbag docstring with Context section with type"""
        self.assertEqual(
            self._render_docstring(
                'Context:\n'
                '    dict\n'
            ),
            ':Context: dict\n'
        )

    def test_context_section_with_type_and_description(self):
        """Testing Beanbag docstring with Context section with type and
        description
        """
        self.assertEqual(
            self._render_docstring(
                'Context:\n'
                '    dict:\n'
                '    Description of the context.\n'
            ),
            ':Context: *dict* -- Description of the context.\n'
        )

    def test_deprecated_section_with_version(self):
        """Testing Beanbag docstring with Deprecated section with version"""
        self.assertEqual(
            self._render_docstring(
                'Deprecated:\n'
                '    2.0\n'
            ),
            '.. deprecated:: 2.0\n\n'
        )

    def test_deprecated_section_with_version_and_description(self):
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
                '    Description of the deprecation.\n'
            )
        )

    def test_model_attributes(self):
        """Testing Beanbag docstring with Model Attributes section"""
        self.assertEqual(
            self._render_docstring(
                'Model Attributes:\n'
                '    attr1 (dict):\n'
                '        Description of attr1\n'
                '\n'
                '    attr2 (foo.bar\n'
                '           .baz):\n'
                '        Description of attr2\n'
            ),
            (
                ':Model Attributes: * **attr1** (*dict*)'
                ' -- Description of attr1\n'
                '                   * **attr2** (*foo.bar.baz*)'
                ' -- Description of attr2\n'
            )
        )

    def test_option_args(self):
        """Testing Beanbag docstring with Option Args section"""
        self.assertEqual(
            self._render_docstring(
                'Option Args:\n'
                '    attr1 (dict):\n'
                '        Description of attr1\n'
                '\n'
                '    attr2 (foo.bar\n'
                '           .baz,\n'
                '           optional):\n'
                '        Description of attr2\n'
            ),
            (
                ':Option Args: * **attr1** (*dict*)'
                ' -- Description of attr1\n'
                '              * **attr2** (*foo.bar.baz, optional*)'
                ' -- Description of attr2\n'
            )
        )

    def test_version_added_section_with_version(self):
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

    def test_version_added_section_with_version_and_description(self):
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
                '    Description of the addition.\n'
            )
        )

    def test_version_changed_section(self):
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
                '    Description of the change.\n'
            )
        )

    def _render_docstring(self, content):
        """Render a Beanbag docstring to ReST.

        Args:
            content (unicode):
                The docstring content to render.

        Returns:
            unicode:
            The resulting ReStructuredText.
        """
        return six.text_type(BeanbagDocstring(content))


__autodoc_excludes__ = ['IgnoredModule']
__deprecated__ = ['DeprecatedModule']
