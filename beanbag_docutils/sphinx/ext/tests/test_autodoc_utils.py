"""Unit tests for beanbag_docutils.sphinx.ext.autodoc_utils."""

from __future__ import unicode_literals

import six

from beanbag_docutils.sphinx.ext import autodoc_utils
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

    def bar(self):
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
        autodoc_utils.__name__,
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

    def test_with_wildcard_exclude_with_defaults(self):
        """Testing autodoc_excludes with wildcard (*) exclude list with
        defaults
        """
        doc = '\n'.join([
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass2.__name__),
            '',
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass2.__name__),
        ])

        rendered = self.render_doc(doc)

        self.assertIn('foo', rendered)

    def test_with_wildcard_exclude_added_to_defaults(self):
        """Testing autodoc_excludes with wildcard (*) exclude list added to
        defaults
        """
        doc = '\n'.join([
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass1.__name__),
            '',
            '.. autoclass:: %s.%s' % (DocClass2.__module__,
                                      DocClass2.__name__),
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

    def test_with_class_attr_exclude(self):
        """Testing autodoc_excludes with class exclude list"""
        docclass1_path = '%s.%s' % (DocClass1.__module__, DocClass1.__name__)

        doc = '\n'.join([
            '.. autoclass:: %s' % docclass1_path,
            '',
            '.. autoclass:: %s.%s' % (DocClass2.__module__,
                                      DocClass2.__name__),
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

    def test_with_class_attr_exclude_with_defaults(self):
        """Testing autodoc_excludes with class exclude list with defaults"""
        docclass1_path = '%s.%s' % (DocClass1.__module__, DocClass1.__name__)

        doc = '\n'.join([
            '.. autoclass:: %s' % docclass1_path,
            '',
            '.. autoclass:: %s.%s' % (DocClass2.__module__,
                                      DocClass2.__name__),
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

    def test_with_class_attr_exclude_and_added_to_defaults(self):
        """Testing autodoc_excludes with class exclude list and added with
        defaults
        """
        docclass1_path = '%s.%s' % (DocClass1.__module__, DocClass1.__name__)

        doc = '\n'.join([
            '.. autoclass:: %s' % docclass1_path,
            '',
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass2.__name__),
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

    def test_with_empty_excludes(self):
        """Testing autodoc_excludes with empty excludes"""
        doc = '\n'.join([
            '.. autoclass:: %s.%s' % (DocClass1.__module__,
                                      DocClass1.__name__),
            '',
            '.. autoclass:: %s.%s' % (DocClass2.__module__,
                                      DocClass2.__name__),
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

    def test_with_deprecated(self):
        """Testing autodoc_excludes with __deprecated__ in module"""
        rendered = self.render_doc('.. automodule:: %s\n' % __name__)

        self.assertIn('AutoDocExcludesTests', rendered)
        self.assertNotIn('DeprecatedModule', rendered)


class BeanbagDocstringTests(SphinxExtTestCase):
    """Unit tests for BeanbagDocstring."""

    extensions = [
        autodoc_utils.__name__,
    ]

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
                ':type arg1: :class:`str`\n'
                ':param arg2: Description of arg2.\n'
                ':type arg2: :class:`foo.bar.abc.def.ghi`, *optional*\n'
                ':param \\*args: Description of args.\n'
                ':type \\*args: :class:`tuple`\n'
                ':param \\*\\*kwargs: Description of kwargs.\n'
                ':type \\*\\*kwargs: :class:`dict`\n'
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
            ':Context: :class:`dict` -- Description of the context.\n'
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
                '   Description of the deprecation.\n'
            )
        )

    def test_deprecated_section_with_version_and_lists(self):
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

    def test_keys(self):
        """Testing Beanbag docstring with Keys section"""
        self.assertEqual(
            self._render_docstring(
                'Keys:\n'
                '    key1 (str):\n'
                '        Description 1\n'
                '\n'
                '    key2 (dict):\n'
                '        Description 2\n'
                '\n'
                '    key3 (int, optional):\n'
                '        Description 3\n'
            ),
            (
                ':Keys: * **key1** (:class:`str`) -- Description 1\n'
                '       * **key2** (:class:`dict`) -- Description 2\n'
                '       * **key3** (:class:`int`, *optional*)'
                ' -- Description 3\n'
            ))

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
                ':Model Attributes: * **attr1** (:class:`dict`)'
                ' -- Description of attr1\n'
                '                   * **attr2** (:class:`foo.bar.baz`)'
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
                ':Option Args: * **attr1** (:class:`dict`)'
                ' -- Description of attr1\n'
                '              * **attr2** (:class:`foo.bar.baz`, *optional*)'
                ' -- Description of attr2\n'
            )
        )

    def test_tuple(self):
        """Testing Beanbag docstring with Tuple section"""
        self.assertEqual(
            self._render_docstring(
                'Tuple:\n'
                '    0 (str):\n'
                '        Description 1\n'
                '\n'
                '    1 (dict):\n'
                '        Description 2\n'
                '\n'
                '    2 (int, optional):\n'
                '        Description 3\n'
            ),
            (
                ':Tuple: * **0** (:class:`str`) -- Description 1\n'
                '        * **1** (:class:`dict`) -- Description 2\n'
                '        * **2** (:class:`int`, *optional*) -- Description 3\n'
            ))

    def test_type_section(self):
        """Testing Beanbag docstring with Type section"""
        self.assertEqual(
            self._render_docstring(
                'Type:\n'
                '    dict\n'
            ),
            ':Type: :class:`dict`\n'
        )

    def test_type_section_with_description(self):
        """Testing Beanbag docstring with Type section with description"""
        self.assertEqual(
            self._render_docstring(
                'Type:\n'
                '    dict:\n'
                '    Description.\n'
            ),
            ':Type: :class:`dict` -- Description.\n'
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
                '   Description of the addition.\n'
            )
        )

    def test_version_added_section_with_lists(self):
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
                '   Description of the change.\n'
            )
        )

    def test_version_changed_section_with_lists(self):
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

    def _render_docstring(self, content):
        """Render a Beanbag docstring to ReST.

        Args:
            content (unicode):
                The docstring content to render.

        Returns:
            unicode:
            The resulting ReStructuredText.
        """
        with self.with_sphinx_env() as ctx:
            return six.text_type(BeanbagDocstring(content,
                                                  config=ctx['config']))


__autodoc_excludes__ = ['IgnoredModule']
__deprecated__ = ['DeprecatedModule']
