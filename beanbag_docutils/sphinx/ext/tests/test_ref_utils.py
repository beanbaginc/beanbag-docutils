"""Unit tests for beanbag_docutils.sphinx.ext.ref_utils."""

from __future__ import unicode_literals

from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


class RefUtilsTests(SphinxExtTestCase):
    """Unit tests for reference role utilities."""

    extensions = [
        'beanbag_docutils.sphinx.ext.ref_utils',
    ]

    def test_ref_break_for_javascript(self):
        """Testing ref_utils reference line break for JavaScript references"""
        rendered = self.render_doc(
            '.. js:function:: abc.def.myfunc\n'
            '\n'
            '   Description.\n'
            '\n'
            'Link to :js:class:`abc.def\n'
            '.myfunc`.'
        )

        self.assertIn(
            '<a class="reference internal" href="#abc.def.myfunc"'
            ' title="abc.def.myfunc">',
            rendered)

    def test_ref_break_for_python(self):
        """Testing ref_utils reference line break for Python references"""
        rendered = self.render_doc(
            '.. py:function:: abc.def.myfunc\n'
            '\n'
            '   Description.\n'
            '\n'
            'Link to :py:class:`abc.def\n'
            '.myfunc`.'
        )

        self.assertIn(
            '<a class="reference internal" href="#abc.def.myfunc"'
            ' title="abc.def.myfunc">',
            rendered)
