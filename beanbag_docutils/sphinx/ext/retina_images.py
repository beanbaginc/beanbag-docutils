"""Sphinx extension for Retina images.

This extension goes through all the images Sphinx will provide in _images and
checks if Retina versions are available. If there are any, they will be copied
as well.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.retina_images',
        ...
    ]
"""

from __future__ import unicode_literals

import os


def add_high_dpi_images(app, env):
    """Add high-DPI images to the list of bundled images.

    Any image that has a "@2x" version will be included in the output
    directory for the docs.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register roles and configuration on.

        env (sphinx.environment.BuildEnvironment):
            The build environment for the generated docs.
    """
    retina_images = []

    for full_path, (docnames, filename) in env.images.iteritems():
        base, ext = os.path.splitext(full_path)
        retina_path = base + '@2x' + ext

        if os.path.exists(retina_path):
            retina_images += [
                (docname, retina_path)
                for docname in docnames
            ]

    for docname, path in retina_images:
        env.images.add_file(docname, path)


def collect_pages(app):
    """Collect high-DPI images for use in HTML pages.

    This will go through the images referenced in a document for an HTML page
    and add any high-DPI versions previously found in
    :py:func:`add_high_dpi_images` to the list of images to collect for the
    page.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register roles and configuration on.

    Returns:
        list:
        An empty list (indicating no additional HTML pages are collected).
    """
    new_images = {}

    for full_path, basename in app.builder.images.iteritems():
        base, ext = os.path.splitext(full_path)
        retina_path = base + '@2x' + ext

        if retina_path in app.env.images:
            new_images[retina_path] = app.env.images[retina_path][1]

    app.builder.images.update(new_images)

    return []


def setup(app):
    """Set up the Sphinx extension.

    This listens for the events needed to collect and bundle high-DPI
    images.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to listen to events on.
    """
    app.connect(b'env-updated', add_high_dpi_images)
    app.connect(b'html-collect-pages', collect_pages)
