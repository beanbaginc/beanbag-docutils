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


Configuration
=============

``retina_suffixes``:
    A list of suffix identifiers for Retina images. Each of these go after
    the filename and before the extension. This defaults to ``['@2x', '@3x']``.
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
    suffixes = app.config['retina_suffixes']
    retina_images = []

    for full_path, (docnames, filename) in env.images.iteritems():
        base, ext = os.path.splitext(full_path)

        for suffix in suffixes:
            src_retina_path = '%s%s%s' % (base, suffix, ext)

            if os.path.exists(src_retina_path):
                base, ext = os.path.splitext(filename)
                dest_retina_name = '%s%s%s' % (base, suffix, ext)

                retina_images += [
                    (docname, src_retina_path, dest_retina_name)
                    for docname in docnames
                ]

    for docname, src_path, dest_name in retina_images:
        # Emulate add_file(), but give greater control over the filenames.
        # Ideally we wouldn't dive into internals of _existing, but we should
        # be able to adjust this easily enough for any changes that may be
        # made.
        env.images[src_path] = (set([docname]), dest_name)
        env.images._existing.add(dest_name)


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
    suffixes = app.config['retina_suffixes']
    new_images = {}

    for full_path, basename in app.builder.images.iteritems():
        base, ext = os.path.splitext(full_path)

        for suffix in suffixes:
            retina_path = '%s%s%s' % (base, suffix, ext)

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
    app.add_config_value('retina_suffixes', ['@2x', '@3x'], True)

    app.connect(b'env-updated', add_high_dpi_images)
    app.connect(b'html-collect-pages', collect_pages)
