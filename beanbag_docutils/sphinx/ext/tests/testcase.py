"""Base test case support for Sphinx extensions."""

from __future__ import unicode_literals

import os
import shutil
import tempfile
from unittest import TestCase

from sphinx_testing import with_app

import beanbag_docutils


_theme_path = os.path.abspath(os.path.join(beanbag_docutils.__file__,
                                           '..', '..', 'tests', 'sphinx',
                                           'themes'))


class SphinxExtTestCase(TestCase):
    """Base class for test cases for Sphinx extensions.

    This provides common functionality for setting up and rendering a ReST
    document to a content-only HTML string.
    """

    #: Class-wide configuration for the renders.
    config = {}

    #: A list of extensions required for the tests.
    extensions = []

    maxDiff = 1000000

    def render_doc(self, doc_content, config={}):
        """Render a ReST document to a string.

        This will set up a Sphinx environment, based on the extensions and
        configuration provided by the consumer, and perform a render of the
        given ReST content. The resulting string will be a rendered version
        of just that content.

        Args:
            doc_content (unicode):
                The ReST content to render.

            config (dict, optional):
                Additional configuration to set for the render.

        Returns:
            unicode:
            The rendered content.
        """
        srcdir = tempfile.mkdtemp(suffix='beanbag-docutils-tests.')

        # This file needs to be present, even if it's blank.
        with open(os.path.join(srcdir, 'conf.py'), 'w') as fp:
            pass

        with open(os.path.join(srcdir, 'contents.rst'), 'w') as fp:
            fp.write(doc_content)

        new_config = {
          'extensions': self.extensions,
          'html_theme': 'test',
          'html_theme_path': [_theme_path],
        }
        new_config.update(self.config)
        new_config.update(config)

        @with_app(buildername='html', srcdir=srcdir,
                  copy_srcdir_to_tmpdir=False, confoverrides=new_config)
        def _render(app, status, warning):
            app.build()

            result = (app.outdir / 'contents.html').read_text().strip()

            if isinstance(result, bytes):
                result = result.decode('utf-8')

            return result

        try:
            return _render()
        finally:
            shutil.rmtree(srcdir)
