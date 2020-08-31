"""Unit tests for beanbag_docutils.sphinx.ext.http_role."""

from __future__ import unicode_literals

from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase


class HttpRoleTests(SphinxExtTestCase):
    """Unit tests for HTTP roles."""

    extensions = [
        'beanbag_docutils.sphinx.ext.http_role',
    ]

    def test_http_status_codes_format(self):
        """Testing http-status-codes-format directive with :http:`...` role"""
        self.assertEqual(
            self.render_doc(
                '.. http-status-codes-format:: HTTP Code %(code)s\n'
                '\n'
                'This is :http:`404`.'
            ),
            (
                '<p>This is <a class="reference external"'
                ' href="https://wikipedia.org/wiki/List_of_HTTP_status_codes'
                '#404">HTTP Code 404</a>.</p>'
            )
        )

    def test_http_role(self):
        """Testing :http:`...` role"""
        self.assertEqual(
            self.render_doc('This is :http:`404`.'),
            (
                '<p>This is <a class="reference external"'
                ' href="https://wikipedia.org/wiki/List_of_HTTP_status_codes'
                '#404">HTTP 404 Not Found</a>.</p>'
            )
        )

    def test_http_role_with_http_status_codes_format(self):
        """Testing :http:`...` role with custom http_status_codes_format"""
        self.assertEqual(
            self.render_doc(
                'This is :http:`404`.',
                config={
                    'http_status_codes_format': 'HTTP Code %(code)s',
                }),
            (
                '<p>This is <a class="reference external"'
                ' href="https://wikipedia.org/wiki/List_of_HTTP_status_codes'
                '#404">HTTP Code 404</a>.</p>'
            )
        )

    def test_http_role_with_http_status_codes_url(self):
        """Testing :http:`...` role with custom http_status_codes_url"""
        self.assertEqual(
            self.render_doc(
                'This is :http:`404`.',
                config={
                    'http_status_codes_url': 'https://example.com/http/%s',
                }),
            (
                '<p>This is <a class="reference external"'
                ' href="https://example.com/http/404">HTTP 404 Not Found</a>.'
                '</p>'
            )
        )
