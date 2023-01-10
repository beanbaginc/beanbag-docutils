"""Sphinx extension for srcsets in images.

.. versionadded:: 2.1


This extension adds a ``sources`` option to the standard image directives,
enabling responsive image support via srcsets.

These are specified a bit differently from ``<img srcset="...">`` values.
The descriptor goes first, and a comma between entries is optional (a blank
line can be used instead). For example:

.. code-block:: rst

   .. image:: path/to/file.png
      :sources: 2x path/to/file@2x.png
                3x path/to/file@3x.png
                100w path/to/file@100w.png
                200h path/to/file@200h.png

If ``sources`` is not explicitly provided, but files with those standard
``@``-based suffixes exist alongside the referenced main image, they'll
automatically be used to define the srcsets of the image. The ``1x`` entry is
also automatically inserted based on the main image.

If relying on the default of scanning for srcset images, this becomes a
zero-configuration, drop-in solution for all Sphinx documentation codebases.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.image_srcsets',
        ...
    ]
"""

from __future__ import unicode_literals

import os
import posixpath
import re
from collections import OrderedDict
from glob import glob
from typing import Dict

import six
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.images import Image
from six.moves.urllib.parse import quote as urllib_quote
from sphinx.application import Sphinx
from sphinx.util.i18n import search_image_for_language


def _get_srcsets(
    node  # type: nodes.image
):  # type: (...) -> Dict[str, str]
    """Return a normalized version of all srcsets for an image node.

    This will convert a ``sources`` option to a dictionary mapping descriptors
    (such as ``2x``, ``100w``, etc.) to URLs.

    These will be cached for future lookup.

    Args:
        node (docutils.nodes.image):
            The image node to retrieve sources from.

    Returns:
        dict:
        The mapping of descriptors to URLs.
    """
    try:
        norm_srcsets = node.attributes['_srcsets']
    except KeyError:
        srcset = node.attributes.get('sources')
        norm_srcsets = OrderedDict()

        if srcset:
            norm_srcsets['1x'] = node.attributes['uri']

            for source in re.split(r',|\n+', srcset):
                source = source.strip()

                if source:
                    descriptor, url = source.split(' ', 1)
                    norm_srcsets[descriptor.strip()] = url.strip()

        node.attributes['_srcsets'] = norm_srcsets

    return norm_srcsets


def _visit_image_html(
    self,
    node   # type: nodes.image
):  # type: (...) -> None
    """Process an Image node.

    This will update the HTML of the image node with a ``srcsets=`` attribute
    if srcsets are needed.

    Args:
        node (docutils.nodes.image):
            The image node to process.
    """
    # Use the default logic to build the image tag, since it's non-trivial.
    type(self).visit_image(self, node)

    images = self.builder.env.images
    base_images_path = self.builder.imgpath
    srcsets = _get_srcsets(node)

    if srcsets:
        last_tag = self.body[-1]
        assert last_tag.startswith('<img ')

        self.body[-1] = (
            '<img srcset="%s" %s' % (
                ', '.join(
                    '%s %s' % (
                        posixpath.join(base_images_path,
                                       urllib_quote(images[url][1])),
                        source)
                    for source, url in six.iteritems(srcsets)
                ),
                last_tag[len('<img '):],
            )
        )


def collect_srcsets(
    app,     # type: Sphinx
    doctree  # type: nodes.document
):  # type: (...) -> None
    """Collect all images referenced by image nodes or scanned in directories.

    This will collect any explicit values defined via our ``sources`` option
    for image directives. If ``sources`` is not specified, but there are files
    in the directory with ``@2x``, ``@3x``, ``@100w`` ``@100h``, etc.
    descriptors, those will be collected instead and associated with the image.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application being run.

        doctree (docutils.nodes.document):
            The document tree being processed.
    """
    env = app.env
    images = env.images
    docname = env.docname

    if hasattr(doctree, 'findall'):
        # This is the modern way of finding nodes.
        findall = doctree.findall
    else:
        # This is pending deprecation in docutils.
        findall = doctree.traverse

    for node in findall(nodes.image):
        srcsets = _get_srcsets(node)

        if not srcsets:
            image_path = search_image_for_language(node['uri'], env)
            rel_image_path, abs_image_path = env.relfn2path(
                search_image_for_language(node['uri'], env),
                docname)
            base_filename, ext = os.path.splitext(image_path)
            candidates = glob('%s@*%s' % (base_filename, ext))

            if candidates:
                srcsets['1x'] = node['uri']

                pattern = re.compile(r'%s@(\d+[xwh])%s'
                                     % (re.escape(base_filename),
                                        re.escape(ext)))

                for candidate in sorted(candidates):
                    m = pattern.match(candidate)

                    if m:
                        descriptor = m.group(1)

                        if descriptor not in srcsets:
                            srcsets[descriptor] = candidate

        for descriptor, image_path in list(six.iteritems(srcsets)):
            image_path = env.relfn2path(
                search_image_for_language(image_path, env),
                docname)[0]

            env.dependencies[docname].add(image_path)
            images.add_file(docname, image_path)


def setup(
    app  # type: Sphinx
):  # type: (...) -> None
    """Set up the Sphinx extension.

    This listens for the events needed to collect and bundle images for
    srcsets, and update the resulting HTML to specify them.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application being run.
    """
    Image.option_spec['sources'] = directives.unchanged

    app.add_node(nodes.image,
                 html=(_visit_image_html, None),
                 override=True)

    app.connect('doctree-read', collect_srcsets)
