"""Sphinx extension to add useful Django-related functionality.

This adds some improvements when working with Django-based classes in autodocs,
and when referencing Django documentation.

Localized strings using ``ugettext_lazy`` will be turned into actual strings
for the documentation, which is usedul for forms and models.

Roles are also added for common cross-references.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.django_utils',
        ...
    ]


Roles
=====

.. rst:role:: setting

   Creates and links to references for Django settings (those that live in
   ``django.conf.settings``).

   For example:

   .. code-block:: rst

       .. setting:: MY_SETTING

       Settings go here.

       And then to reference it: :setting:`MY_SETTING`.
"""

from __future__ import unicode_literals

from django.utils import six
from django.utils.functional import Promise


def _repr_promise(promise):
    """Return a sane representation of a lazy localized string.

    If the promise is a result of ugettext_lazy(), it will be converted into
    a Unicode string before generating a representation.
    """
    if hasattr(promise, '_proxy____text_cast'):
        return '_(%s)' % repr(six.text_type(promise))

    return super(promise.__class__, promise).__repr__(promise)


def setup(app):
    """Set up the Sphinx extension.

    This registers cross-references and fixes up the lazily-localizeed strings
    for display.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to listen to events on.
    """
    Promise.__repr__ = _repr_promise

    app.add_crossref_type(directivename=b'setting',
                          rolename=b'setting',
                          indextemplate=b'pair: %s; setting')
