"""Unit tests for beanbag_docutils.sphinx.ext.extlinks."""

from __future__ import unicode_literals

from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


class ExtLinksTests(SphinxExtTestCase):
    """Unit tests for extlinks."""

    config = {
        'extlinks': {
            'bug': ('https://bugs.example.com/%s?#main', 'bug'),
        },
    }

    extensions = [
        'beanbag_docutils.sphinx.ext.extlinks',
    ]

    def test_extlink_with_anchor(self):
        """Testing :<extlink>:`...` role with mapped URL containing anchor"""
        self.assertEqual(
            self.render_doc(':bug:`123`'),
            '<p><a class="reference external"'
            ' href="https://bugs.example.com/123?#main">bug123</a></p>')
