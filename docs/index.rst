beanbag-docutils
================

This is a set of extensions to the Sphinx_ ReStructuredText_-based
documentation system used by `our products`_ to help generate better
documentation

Amongst other enhancements, this package offers:

* A parser for the `Beanbag docstring format`_ (a variation on the `Google
  docstring format`_), which we use for Python and JavaScript documentation
* Enhancements for Sphinx's intersphinx_ system to provide per-page
  intersphinx resolution options (useful for pages, such as release notes,
  that need to link to different versions of the same docs, such as Django_ or
  Python)
* Enhancements to ReStructuredText references to let a reference name span
  lines (useful for long Python/JavaScript module/class names)
* Linking code references to GitHub documentation
* High-DPI image embedding
* A role for HTTP status codes
* Access to document-defined metadata in a structured form when parsing
  documents


.. _Beanbag docstring format:
   https://www.notion.so/reviewboard/Standard-Documentation-Format-4388f594d86547cc949b365cda3cf391
.. _Django: https://www.djangoproject.com/
.. _Google docstring format:
   https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings
.. _intersphinx:
   https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
.. _our products: https://www.beanbaginc.com/
.. _ReStructuredText:
   https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html
.. _Sphinx: https://www.sphinx-doc.org/


Installation
============

It's very easy to get going. Just install ``beanbag-docutils`` like so:

.. code-block:: shell

   $ pip install beanbag-docutils

We like to place ours in a :file:`doc-requirements.txt` file in each of our
repositories, and use:

.. code-block:: shell

   $ pip install -r doc-requirements.txt


Sphinx Extensions
=================

The following extensions are provided:

:py:mod:`~beanbag_docutils.sphinx.ext.autodoc_utils`
    * Enables parsing of the `Beanbag docstring format`_ for Python.
    * Advanced options for defining excluded and deprecated classes/functions
      to skip, either in a Sphinx project's :file:`conf.py` or directly in the
      Python modules.

:py:mod:`~beanbag_docutils.sphinx.ext.collect_files`
    * Allows arbitrary supplemental files to be "collected" along with any of
      your documentation.

:py:mod:`~beanbag_docutils.sphinx.ext.django_utils`
    * Roles and directives for describing Django-related concepts in your
      documentation.
    * Automatic support for resolving "lazy" localized strings, so they
      appear correctly.

:py:mod:`~beanbag_docutils.sphinx.ext.extlinks`
    * An improved version of Sphinx's own :py:mod:`sphinx.ext.extlinks` that
      supports anchors in the string passed to the role (e.g.,
      ``:myext:`name#anchor```).

:py:mod:`~beanbag_docutils.sphinx.ext.github`
    * Provides links to the appropriate versions of the tree in GitHub for any
      source code references, instead of bundling copies of the source code
      with the documentation.

:py:mod:`~beanbag_docutils.sphinx.ext.http_role`
    * Provides a :rst:role:`http` role for specifying HTTP status codes and
      linking them to useful documentation.

:py:mod:`~beanbag_docutils.sphinx.ext.image_srcsets`
    * Drop-in support for generating ``<img srcset="...">`` images using the
      built-in :rst:dir:`image` directive. Appropriate images can be
      automatically determined or manually specified.

:py:mod:`~beanbag_docutils.sphinx.ext.intersphinx_utils`
    * Allows individual documentation pages to specify which intersphinx_
      mappings should be used if multiple mappings contained the same
      reference. Useful for having, say, different release notes pages linking
      to different versions of Python or Django_ documentation.

:py:mod:`~beanbag_docutils.sphinx.ext.metadata`
    * Extracts metadata from :rst:dir:`meta` directives into the document's
      metadata, allowing tools or custom doc rendering platforms to access it.

    .. versionadded:: 2.2

:py:mod:`~beanbag_docutils.sphinx.ext.ref_utils`
    * Allows Python and JavaScript references to span multiple lines, in
      case of very long class or module paths.

:py:mod:`~beanbag_docutils.sphinx.ext.retina_images`
    * Collects all high-DPI versions of images (e.g., any with a ``@2x``
      in the filename) for the resulting documentation.


See Also
========

.. toctree::
   :hidden:

   coderef/index

.. toctree::
   :maxdepth: 2

   releasenotes/index

* Other Projects:

  * `Review Board`_ - Our extensible open source code review product.

  * RBCommons_ - Our Review Board SaaS.

  * `Django Evolution`_ - Advanced schema migration for Django, compatible with
    Django's migrations.

  * Djblets_ - A set of utilities and infrastructure for Django-based projects.

  * kgb_ - Function spies for Python unit tests.

  * RBTools_ - Command line tools for Review Board and RBCommons.


.. _Django Evolution: https://django-evolution.readthedocs.io/
.. _Djblets: https://github.com/djblets/djblets/
.. _kgb: https://github.com/beanbaginc/kgb/
.. _RBCommons: https://www.rbcommons.com/
.. _RBTools: https://github.com/reviewboard/rbtools/
.. _Review Board: https://www.reviewboard.org/
