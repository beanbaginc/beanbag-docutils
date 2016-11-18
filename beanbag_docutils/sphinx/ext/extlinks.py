"""Sphinx extension to define external links that support anchors.

Sphinx comes bundled with a :py:mod:`sphinx.ext.extlinks` extension, which
allows a :file:`conf.py` to define roles for external linkes. These don't
support anchors, however, making it impossible to link to properly link in some
cases.

This is a wrapper around that module that looks for anchors and appends them to
the resulting URL.


Setup
=====

This extension works identically to :py:mod:`sphinx.ext.extlinks` and contains
the same configuration. To use it, configure external links the way you would
for that extension, but add ours instead to :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.extlinks',
        ...
    ]
"""

from __future__ import unicode_literals

import six
from sphinx.ext.extlinks import make_link_role


class ExternalLink(object):
    """Wraps a URL and formats references to allow for using anchors.

    This will work like a string, from the point of view of
    :py:mod:`sphinx.ext.extlinks`. It takes the URL for the external link and
    intercepts any string formatting, pulling out the anchor and appending it
    to the final result.
    """

    def __init__(self, base_url):
        """Initialize the class.

        Args:
            base_url (unicode):
                The URL to wrap. This must contain a ``%s``.
        """
        self.base_url = base_url

    def __mod__(self, ref):
        """Return a URL based on the stored string format and the reference.

        Args:
            ref (unicode):
                The reference to place into the URL. This may contain an
                anchor starting with ``#``.

        Returns:
            unicode:
            The formatted URL.
        """
        parts = ref.split('#', 1)
        url = self.base_url % parts[0]

        if len(parts) == 2:
            url = '%s#%s' % (url, parts[1])

        return url

    def __add__(self, s):
        """Return the concatenated string for the base URL and another string.

        Args:
            s (unicode):
                A string to concatenate onto this base URL.

        Returns:
            unicode:
            The concatenated string.
        """
        return self.base_url + s


def setup_link_roles(app):
    """Register roles for each external link that's been defined.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application.
    """
    for name, (base_url, prefix) in six.iteritems(app.config.extlinks):
        app.add_role(name, make_link_role(ExternalLink(base_url), prefix))


def setup(app):
    """Set up the Sphinx extension.

    This registers the configuration for external links and adds the roles
    for each when the builder initializes.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application.

    Returns:
        dict:
        Information about the extension. This is in the same format as what
        :py:func:`sphinx.ext.extlinks.setup` returns.
    """
    app.add_config_value(b'extlinks', {}, b'env')
    app.connect(b'builder-inited', setup_link_roles)

    return {
        'version': '1.0',
        'parallel_read_safe': True,
    }
