"""Unit tests for beanbag_docutils.sphinx.ext.image_srcsets."""

from beanbag_docutils.sphinx.ext import image_srcsets
from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


class ImageTests(SphinxExtTestCase):
    """Unit tests for image."""

    extensions = [
        image_srcsets.__name__,
    ]

    def test_with_html(self):
        """Testing image with HTML"""
        rendered = self.render_doc(
            '.. image:: path/to/image.png\n'
        )

        self.assertEqual(
            rendered,
            '<img alt="path/to/image.png" src="path/to/image.png" />')

    def test_with_html_and_srcset(self):
        """Testing image-srcset with HTML and srcset"""
        rendered = self.render_doc(
            '.. image:: path/to/image.png\n'
            '   :sources: 2x path/to/image@2x.png\n'
            '             3x path/to/image@3x.png\n'
        )

        self.assertEqual(
            rendered,
            '<img srcset="_images/image.png 1x, _images/image%402x.png 2x,'
            ' _images/image%403x.png 3x" alt="_images/image.png"'
            ' src="_images/image.png" />')

    def test_with_html_and_srcset_files(self):
        """Testing image-srcset with HTML and srcset @-based files"""
        rendered = self.render_doc(
            '.. image:: my/images/image.png\n',
            extra_files={
                'my/images/image.png': b'',
                'my/images/image@2x.png': b'',
                'my/images/image@3x.png': b'',
                'my/images/image@4x.png': b'',
            })

        self.assertEqual(
            rendered,
            '<img srcset="_images/image.png 1x, _images/image%402x.png 2x,'
            ' _images/image%403x.png 3x, _images/image%404x.png 4x"'
            ' alt="_images/image.png" src="_images/image.png" />')
