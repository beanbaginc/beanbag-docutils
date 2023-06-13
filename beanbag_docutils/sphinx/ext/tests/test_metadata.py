# coding: utf-8
"""Unit tests for beanbag_docutils.sphinx.ext.metadata.

Version Added:
    2.2
"""

import json
from unittest import SkipTest

from docutils import nodes, __version__ as DOCUTILS_VERSION

from beanbag_docutils.sphinx.ext import metadata
from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


class MetadataTests(SphinxExtTestCase):
    """Unit tests for the metadata extension."""

    extensions = [
        metadata.__name__,
    ]

    @classmethod
    def setUpClass(cls):
        super(MetadataTests, cls).setUpClass()

        if not hasattr(nodes, 'meta'):
            raise SkipTest('Not supported on docutils %s' % DOCUTILS_VERSION)

    def test_with_single_value(self):
        """Testing metadata extension with single value for key"""
        data = json.loads(self.render_doc(
            '.. meta::\n'
            '   :my_key: my value!\n',
            builder_name='json'
        ))

        self.assertEqual(
            data.get('meta'),
            {
                'my_key': {
                    'content': 'my value!',
                },
            })

    def test_with_multiple_values(self):
        """Testing metadata extension with multiple values for key"""
        data = json.loads(self.render_doc(
            '.. meta::\n'
            '   :description lang=en: hi!\n'
            '   :description lang=ja: こんにちは\n',
            builder_name='json'
        ))

        self.assertEqual(
            data.get('meta'),
            {
                'description': [
                    {
                        'content': 'hi!',
                        'lang': 'en',
                    },
                    {
                        'content': 'こんにちは',
                        'lang': 'ja',
                    },
                ],
            })
