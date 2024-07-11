"""Sphinx extension for extracting metadata for the page.

.. versionadded:: 2.2


This extension extracts any :rst:dir:`meta` information (useful for content
like page descriptions for social media) and extracts their information into
the document's top-level metadata.

This metadata can then be used when building sites or tools that process the
page's compiled documentation (when not simply relying on the generated HTML).

The metadata will be available in the document's ``meta`` information, keyed
off by the name used in the :rst:dir:`meta` directive, the content, and any
other attributes provided.

If multiple pieces of metadata exist for the same key, the information will be
assembled into a list under that key. Otherwise, the information will be
assigned directly to the key.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.metadata',
        ...
    ]
"""

from typing import Any, Dict, TYPE_CHECKING

from docutils import nodes, __version__ as DOCUTILS_VERSION
from sphinx.errors import ExtensionError

from beanbag_docutils import VERSION

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def _on_doctree_read(
    app,     # type: Sphinx
    doctree  # type: nodes.document
):  # type: (...) -> None
    """Extract any doc-defined metadata into the compiled page information.

    This will go through any :rst:dir:`meta` nodes, pulling out attributes
    and storing them in the metadata for the document.

    Version Added:
        2.2

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application being run.

        doctree (docutils.nodes.document):
            The document tree being processed.
    """
    metadata = {}  # type: Dict[str, Any]
    env = app.env

    if hasattr(doctree, 'findall'):
        # This is the modern way of finding nodes.
        findall = doctree.findall
    else:
        # This is pending deprecation in docutils.
        findall = doctree.traverse
        assert False

    for node in findall(nodes.meta):
        if not node.hasattr('name'):
            continue

        name = node['name']
        meta_attrs = dict(node.non_default_attributes())
        del meta_attrs['name']

        metadata.setdefault(name, []).append(meta_attrs)

    # Register all the new metadata.
    docname = env.docname
    doc_metadata = env.metadata[docname]

    for key, values in metadata.items():
        if len(values) == 1:
            doc_metadata[key] = values[0]
        else:
            doc_metadata[key] = values


def setup(
    app  # type: Sphinx
):  # type: (...) -> Dict
    """Set up the Sphinx extension.

    This listens for the event needed to process the document tree for
    metadata extraction.

    Version Added:
        2.2

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application being run.
    """
    if not hasattr(nodes, 'meta'):
        raise ExtensionError('beanbag_docutils.sphinx.ext does not support '
                             'docutils %s'
                             % DOCUTILS_VERSION)

    app.connect('doctree-read', _on_doctree_read)

    return {
        'version': VERSION,
    }
