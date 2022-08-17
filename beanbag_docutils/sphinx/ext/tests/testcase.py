"""Base test case support for Sphinx extensions."""

from __future__ import unicode_literals

import os
import shutil
import tempfile
from contextlib import contextmanager
from unittest import TestCase

from sphinx_testing.util import TestApp, docutils_namespace

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

    @contextmanager
    def with_sphinx_env(self, config={}):
        """Run within a Sphinx environment.

        Version Added:
            1.10

        Args:
            config (dict, optional):
                Additional configuration to set for phinx.

        Context:
            dict:
            A dictionary containing:

            Keys:
                app (sphinx.application.Sphinx):
                    The Sphinx application that was set up.

                config (sphinx.config.Config):
                    The Sphinx configuration object.

                srcdir (unicode):
                    The location to place ReST source files in.
        """
        new_config = {
            'extensions': self.extensions,
            'html_theme': 'test',
            'html_theme_path': [_theme_path],
        }
        new_config.update(self.config)
        new_config.update(config)

        with docutils_namespace():
            app = TestApp(buildername='html',
                          create_new_srcdir=True,
                          copy_srcdir_to_tmpdir=False,
                          confoverrides=new_config)

            try:
                yield {
                    'app': app,
                    'config': app.config,
                    'srcdir': app.srcdir,
                }
            finally:
                app.cleanup()

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
        with self.with_sphinx_env(config=config) as ctx:
            with open(os.path.join(ctx['srcdir'], 'contents.rst'), 'w') as fp:
                fp.write(doc_content)

            app = ctx['app']
            app.build()

            with open(app.outdir / 'contents.html', 'r') as fp:
                return fp.read().strip()
