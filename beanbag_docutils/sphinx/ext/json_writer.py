"""Sphinx extension offering an enhanced JSON document builder.

When enabled, the JSON builder provided by
:pypi:`sphinxcontrib-serializinghtml` will be augmented with:

1. A ``toc`` key in :file:`globalcontext.json` containing a structured
   Table of Contents for the site.

2. An ``anchors_html`` in the page's context containing HTML-rendered anchors
   for the page, without the page title being included.


Setup
=====

To use this, add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.json_writer',
        ...
    ]

This will automatically enable the :py:mod:`sphinxcontrib.serializinghtml`
extension and set the appropriate overrides.

You can then build the JSON documentation using the ``json`` builder.


Table of Contents Structure
===========================

The ``toc`` key in :file:`globalcontext.json` contains a list of dictionaries
containing:

Keys:
   docname (str):
       The name of the document.

   title (str):
       The document title.

   items (list, optional):
       The list of child documents under this page in the tree. This uses
       this same structure.


This will start with the ``index.rst`` at the top of the project, if it exists.
If it does not, it will fall back to the configured Sphinx root document
(configured by ``root_doc``).


Anchors Structure
=================

Anchors are stored in a ``.fjson`` page's ``anchors_html`` key. This will be
pre-rendered HTML, following the form of the normal ``toc`` key. For example:

.. code-block:: html

    <ul>
     <li><a class="reference internal" href="#section1">Section 1</a></li>
     <li><a class="reference internal" href="#section2">Section 2</a><ul>
      <li><a class="reference internal" href="#section2.1">Section 2.1</a></li>
      <li><a class="reference internal" href="#section2.2">Section 2.2</a></li>
      ...
     </ul></li>
     ...
    </ul>

"""

from typing import Any, Dict, List, TYPE_CHECKING

from sphinx.environment.adapters.toctree import TocTree

from beanbag_docutils import VERSION

try:
    from sphinx.builders.html import JSONHTMLBuilder
    has_native_json_builder = True
except ImportError:
    from sphinxcontrib.serializinghtml import JSONHTMLBuilder
    has_native_json_builder = False

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class JSONBuilder(JSONHTMLBuilder):
    """Sphinx builder for JSON files.

    This specializes :py:mod:`sphinxcontrib.serializinghtml.JSONHTMLBuilder`,
    adding additional state for a structured Table of Contents, available
    in :file:`glboalcontext.json`.

    Version Added:
        2.2
    """

    def handle_finish(self):  # type: (...) -> None
        """Handle finishing the build for all the docs."""
        env = self.env
        toc = None

        for name in ('index', getattr(env.config, 'root_doc', 'contents')):
            if name and name in env.titles:
                toc = self._build_toc([name])
                break

        self.globalcontext['toc'] = toc

        super(JSONBuilder, self).handle_finish()

    def _build_toc(
        self,
        docnames,  # type: List[str]
    ):  # type: (...) -> List[Dict[str, Any]]
        """Build the Table of Contents for a given level

        This will iterate through ``docnames`` and produce entries for each,
        recursively building for any child documents.

        Args:
            docnames (list of str):
                The list of document names on this level.

        Returns:
            list of dict:
            The list of Table of Contents entries for this level.
        """
        env = self.env
        toc = []  # type: List[Dict[str, Any]]

        for docname in docnames:
            toc_info = {
                'docname': docname,
                'title': str(env.titles[docname].children[0]),
            }  # type: Dict[str, Any]

            children = env.toctree_includes.get(docname, [])

            if children:
                toc_info['items'] = self._build_toc(children)

            toc.append(toc_info)

        return toc


def _on_html_page_context(
    app,           # type: Sphinx
    pagename,      # type: str
    templatename,  # type: str
    ctx,           # type: Dict
    event_arg      # type: Any
):  # type: (...) -> None
    """Gather information for the page.

    This will generate the ``anchors_html`` for a page and set it in the
    context. This may be ``None`` if a Table of Contents is not present.

    Version Added:
        2.2

    Args:
        app (sphinx.application.Sphinx):
            The current Sphinx application.

        pagename (str):
            The name of the page.

        templatename (str, unused):
            The template being used to render the page.

        ctx (dict):
            The context to populate.

        event_arg (object, unused):
            An unused event argument from the caller.
    """
    builder = app.builder
    toc = TocTree(app.env).get_toc_for(pagename, builder)
    anchors_html = None

    children = toc.children

    if len(children) > 0:
        toc_top = children[0]
        anchors_node = None

        if len(toc_top.children) > 1:
            anchors_node = toc_top.children[1]
        elif len(children) > 1:
            anchors_node = children[1]

        if anchors_node is not None:
            anchors_html = builder.render_partial(anchors_node)['fragment']

    ctx['anchors_html'] = anchors_html


def setup(app):
    """Set up the Sphinx extension.

    This sets up the configuration and event handlers needed for the JSON
    writer extension.

    Version Added:
        2.2

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register configuration and listen to
            events on.
    """
    if not has_native_json_builder:
        app.setup_extension('sphinxcontrib.serializinghtml')

    app.add_builder(JSONBuilder, override=True)

    app.connect('html-page-context', _on_html_page_context)

    return {
        'version': VERSION,
    }
