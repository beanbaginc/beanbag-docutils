"""Base test case support for Sphinx extensions."""

import os
from contextlib import contextmanager
from unittest import TestCase
from typing import Dict, Iterator

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
    def with_sphinx_env(self, config={}, builder_name='html'):
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
            app = TestApp(buildername=builder_name,
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

    @contextmanager
    def rendered_docs(
        self,
        files={},            # type: Dict
        config={},           # type: Dict
        builder_name='html'  # type: str
    ):  # type: (...) -> Iterator[str]
        """Render ReST documents and yield the directory for processing.

        This will set up a Sphinx environment, based on the extensions and
        configuration provided by the consumer, and perform a render of the
        given ReST files. The caller can then inspect the files within the
        environment.

        Version Added:
            2.2

        Args:
            files (dict):
                A mapping of filenames and contents to write.

                All contents are byte strings.

            config (dict, optional):
                Additional configuration to set for the render.

            builder_name (unicode, optional):
                The name of the builder to use.

        Context:
            unicode:
        """
        with self.with_sphinx_env(config=config,
                                  builder_name=builder_name) as ctx:
            srcdir = ctx['srcdir']

            old_cwd = os.getcwd()
            os.chdir(srcdir)

            try:
                for path, contents in files.items():
                    dirname = os.path.dirname(path)

                    if dirname and not os.path.exists(dirname):
                        os.makedirs(dirname)

                    if isinstance(contents, bytes):
                        with open(path, 'wb') as fp:
                            fp.write(contents)
                    else:
                        assert isinstance(contents, str)

                        with open(path, 'w') as fp:
                            fp.write(contents)

                app = ctx['app']
                app.build()

                yield str(app.outdir)
            finally:
                os.chdir(old_cwd)

    def render_doc(
        self,
        doc_content: str,
        config={},
        builder_name='html',
        extra_files={}
    ):  # type: (...) -> str
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

            builder_name (unicode, optional):
                The name of the builder to use.

            extra_files (dict):
                A mapping of extra filenames and contents to write.

        Returns:
            unicode:
            The rendered content.

        Raises:
            ValueError:
                ``builder_name`` wasn't a valid value.
        """
        if builder_name == 'html':
            out_filename = 'contents.html'
        elif builder_name == 'json':
            out_filename = 'contents.fjson'
        else:
            raise ValueError('"%s" is not a supported builder name'
                             % builder_name)

        files = {
            'contents.rst': doc_content,
        }
        files.update(extra_files)

        with self.rendered_docs(files=files,
                                config=config,
                                builder_name=builder_name) as build_dir:
            with open(os.path.join(build_dir, out_filename), 'r') as fp:
                return fp.read().strip()
