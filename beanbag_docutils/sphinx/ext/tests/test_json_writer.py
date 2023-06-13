"""Unit tests for beanbag_docutils.sphinx.ext.json_writer.

Version Added:
    2.2
"""

import json
import os

from beanbag_docutils.sphinx.ext import json_writer
from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


class JsonWriterTests(SphinxExtTestCase):
    extensions = [
        json_writer.__name__,
    ]

    def test_anchors_html(self):
        """Testing json_writer with anchors_html"""
        data = json.loads(self.render_doc(
            '==========\n'
            'Page Title\n'
            '==========\n'
            '\n'
            '.. _section-1::\n'
            'Section 1\n'
            '=========\n'
            '\n'
            '.. _section-1-2::\n'
            'Section 1.2\n'
            '---------\n'
            '\n'
            '.. _section-2::\n'
            'Section 2\n'
            '=========\n',
            builder_name='json'))

        self.assertEqual(
            data.get('anchors_html'),
            '<ul>\n'
            '<li><a class="reference internal" href="#section-1">Section 1</a>'
            '<ul>\n'
            '<li><a class="reference internal" href="#section-1-2">Section 1.2'
            '</a></li>\n'
            '</ul>\n'
            '</li>\n'
            '<li><a class="reference internal" href="#section-2">Section 2</a>'
            '</li>\n'
            '</ul>\n'
        )

    def test_anchors_html_with_no_sections(self):
        """Testing json_writer with anchors_html with no sections"""
        data = json.loads(self.render_doc(
            '==========\n'
            'Page Title\n'
            '==========\n',
            builder_name='json'))

        self.assertIn('anchors_html', data)
        self.assertIsNone(data.get('anchors_html'))

    def test_toc(self):
        """Testing json_writer with toc"""
        files = {
            'contents.rst': '',
            'index.rst': (
                '========\n'
                'Top Page\n'
                '========\n'
                '\n'
                '.. toctree::\n'
                '\n'
                '   page1\n'
                '   page2\n'
            ),
            'page1.rst': (
                '======\n'
                'Page 1\n'
                '======\n'
                '\n'
                '.. toctree::\n'
                '\n'
                '   page1.1\n'
            ),
            'page1.1.rst': (
                '========\n'
                'Page 1.1\n'
                '========\n'
            ),
            'page2.rst': (
                '======\n'
                'Page 2\n'
                '======\n'
            ),
        }

        with self.rendered_docs(files=files,
                                builder_name='json') as build_dir:
            with open(os.path.join(build_dir, 'globalcontext.json'),
                      'r') as fp:
                global_context = json.load(fp)

            self.assertIn('toc', global_context)
            self.assertEqual(global_context['toc'], [
                {
                    'docname': 'index',
                    'title': 'Top Page',
                    'items': [
                        {
                            'docname': 'page1',
                            'title': 'Page 1',
                            'items': [
                                {
                                    'docname': 'page1.1',
                                    'title': 'Page 1.1',
                                },
                            ],
                        },
                        {
                            'docname': 'page2',
                            'title': 'Page 2',
                        },
                    ],
                },
            ])

    def test_toc_with_no_children(self):
        """Testing json_writer with toc and no children"""
        files = {
            'contents.rst': '',
            'index.rst': (
                '========\n'
                'Top Page\n'
                '========\n'
                '\n'
                '.. toctree::\n'
                '\n'
                '   page1\n'
                '   page2\n'
            ),
        }

        with self.rendered_docs(files=files,
                                builder_name='json') as build_dir:
            with open(os.path.join(build_dir, 'globalcontext.json'),
                      'r') as fp:
                global_context = json.load(fp)

            self.assertIn('toc', global_context)
            self.assertEqual(global_context['toc'], [
                {
                    'docname': 'index',
                    'title': 'Top Page',
                },
            ])

    def test_toc_with_doc_root_page(self):
        """Testing json_writer with toc and doc_root page (no index.rst)"""
        files = {
            'contents.rst': (
                '========\n'
                'Top Page\n'
                '========\n'
                '\n'
                '.. toctree::\n'
                '\n'
                '   page1\n'
                '   page2\n'
            ),
        }

        with self.rendered_docs(files=files,
                                builder_name='json') as build_dir:
            with open(os.path.join(build_dir, 'globalcontext.json'),
                      'r') as fp:
                global_context = json.load(fp)

            self.assertIn('toc', global_context)
            self.assertEqual(global_context['toc'], [
                {
                    'docname': 'contents',
                    'title': 'Top Page',
                },
            ])
