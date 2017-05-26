=====================
Beanbag Doc Utilities
=====================

This is a collection of utilities to help with generating documentation for
Beanbag-related products, including:

* `Review Board`_ - Our widely-used open source code review product.
* RBCommons_ - Our Review Board SaaS.
* Djblets_ - A set of utilities and infrastructure for Django-based projects.
* RBTools_ - Command line tools for Review Board and RBCommons.


.. _Review Board: https://www.reviewboard.org/
.. _RBCommons: https://www.rbcommons.com/
.. _Djblets: https://github.com/djblets/djblets/
.. _RBTools: https://github.com/reviewboard/rbtools/


Sphinx Extensions
=================

We use Sphinx_ for our documentation, and have a number of extensions to help
with the generation of docs.


.. _Sphinx: http://www.sphinx-doc.org/


autodoc_utils
-------------

Enhances autodoc support for Beanbag's docstring format and to allow for
excluding content from docs.


Beanbag's Docstrings
~~~~~~~~~~~~~~~~~~~~

By setting ``napoleon_beanbag_docstring = True`` in :file:`conf.py`, and
turning off ``napoleon_google_docstring``, Beanbag's docstring format can be
used.

This works just like the Google docstring format, but with a few additions:

* A new ``Context:`` section to describe what happens within the context of a
  context manager (including the variable).

* New ``Model Attributes:`` and ``Option Args:`` sections for defining the
  attributes on a model or the options in a dictionary when using JavaScript.

* Parsing improvements to allow for wrapping argument types across lines,
  which is useful when you have long module paths that won't fit on one line.

This requires the ``sphinx.ext.napoleon`` module to be loaded.


Excluding Content
~~~~~~~~~~~~~~~~~

A module can define top-level ``__autodoc_excludes__`` or ``__deprecated__``
lists. These are in the same format as ``__all__``, in that they take a list
of strings for top-level classes, functions, and variables. Anything listed
here will be excluded from any autodoc code.

``__autodoc_excludes__`` is particularly handy when documenting an
``__init__.py`` that imports contents from a submodule and re-exports it
in ``__all__``. In this case, autodoc would normally output documentation both
in ``__init__.py`` and the submodule, but that can be avoided by setting::

    __autodoc_excludes = __all__

Excludes can also be defined globally, filtered by the type of object the
docstring would belong to. See the documentation for autodoc-skip-member_ for
more information. You can configure this in ``conf.py`` by doing::

    autodoc_excludes = {
        # Applies to modules, classes, and anything else.
        '*': [
            '__dict__',
            '__doc__',
            '__module__',
            '__weakref__',
        ],
        'class': [
            # Useful for Django models.
            'DoesNotExist',
            'MultipleObjectsReturned',
            'objects',

            # Useful forms.
            'base_fields',
            'media',
        ],
    }

That's just an example, but a useful one for Django users.

To install this extension, add the following to your ``conf.py``::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.autodoc_utils',
        ...
    ]

.. _autodoc-skip-member:
   http://www.sphinx-doc.org/en/stable/ext/autodoc.html#event-autodoc-skip-member


collect_files
-------------

Collects additional files in the build directory.

This is used to copy files (indicated by glob patterns) from the source
directory into the destination build directory. Each destination file will be
in the same relative place in the tree.

This is useful when you have non-ReST/image files that you want part of your
built set of files, perhaps containing metadata or packaging that you want to
ship along with the documentation.

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.collect_files',
        ...
    ]

And then configure ``collect_file_patterns`` to be a list of
filenames/glob patterns, like::

    collect_file_patterns = ['metadata.json', '*.pdf']


django_utils
------------

Adds some improvements when working with Django-based classes in autodocs, and
when referencing Django documentation.

First, this will take localized strings using ``ugettext_lazy`` and turn them
into actual strings, which is useful for forms and models.

Second, this adds linking for setting-based documentation, allowing custom
settings (from ``django.conf.settings``) to be documented and referenced,
like so:

.. code-block:: rst

    .. setting:: MY_SETTING

    Settings go here.

    And then to reference it: :setting:`MY_SETTING`.

To install this extension, add the following to your ``conf.py``::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.django_utils',
        ...
    ]


github_linkcode
---------------

Links source code for modules, classes, etc. to the correct line on GitHub.
This prevents having to bundle the source code along with the documentation,
and better ties everything together.

To use this, simply add the following to ``conf.py``::

    from beanbag_docutils.sphinx.ext.github import github_linkcode_resolve

    extensions = [
        ...
        'sphinx.ext.linkcode',
        ...
    ]

    linkcode_resolve = github_linkcode_resolve


http_role
---------

Provides references for HTTP codes, linking to the matching docs on Wikipedia.

To create a link, simply do::

    This is :http:`404`.

If you want to use a different URL, you can add the following to
``conf.py``::

    http_status_codes_url = 'http://mydomain/http/%s'

Where ``%s`` will be replaced by the HTTP code.

To install this extension, add the following to your ``conf.py``::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.http_role',
        ...
    ]


intersphinx_utils
-----------------

Enhances Intersphinx by fixing issues with ``option`` references and by
adding a new directive for setting a priority order for Intersphinx
documentation sets to use.

To set the directives, use::

    .. default-intersphinx:: myapp1.5 python

    :ref:`some-reference`

This would ensure that references using Intersphinx without an explicit prefix
would first try ``myapp1.5`` and then ``python``. No other Intersphinx sets
would be used.

To install this extension, add the following to your ``conf.py``::

    extensions = [
        ...
        'sphinx.ext.intersphinx',
        'beanbag_docutils.sphinx.ext.intersphinx',
        ...
    ]

Note that these extensions must be listed in this order.


retina_images
-------------

Copies all Retina versions of images (any with a ``@2x`` filename) into the
build directory for the docs. This works well with scripts like retina.js_.

To install this extension, add the following to your ``conf.py``::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.retina_images',
        ...
    ]


.. _retina.js: https://imulus.github.io/retinajs/
