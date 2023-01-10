"""Unit tests for beanbag_docutils.sphinx.ext.extlinks."""

from sphinx import version_info as sphinx_version_info

from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


if sphinx_version_info[:2] >= (4, 0):
    _bug_caption = 'bug%s'
else:
    _bug_caption = 'bug'


class ExtLinksTests(SphinxExtTestCase):
    """Unit tests for extlinks."""

    config = {
        'extlinks': {
            'bug': ('https://bugs.example.com/%s?#main', _bug_caption),
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
