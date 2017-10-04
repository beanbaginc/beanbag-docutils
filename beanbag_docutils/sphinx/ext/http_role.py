"""Sphinx extension to add a :rst:role:`http` role for docs.

This extension makes it easy to reference HTTP status codes.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.http_role',
        ...
    ]


Roles
=====

.. rst:role:: http

   References an HTTP status code, expanding to the full status name and
   linking to documentation on the status in the process.


Configuration
=============

``http_status_codes_url``:
    The location of the docs for the status codes. This expects a string with a
    ``%s``, which will be replaced by the numeric HTTP status code.
"""

from __future__ import unicode_literals

from docutils import nodes


DEFAULT_HTTP_STATUS_CODES_URL = \
    'http://en.wikipedia.org/wiki/List_of_HTTP_status_codes#%s'

HTTP_STATUS_CODES = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    208: 'Already Reported',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: 'Switch Proxy',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    418: 'I\m a teapot',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    425: 'Unordered Collection',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    444: 'No Response',
    449: 'Retry With',
    450: 'Blocked by Windows Parental Controls',
    451: 'Unavailable For Legal Reasons',
    499: 'Client Closed Request',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage',
    508: 'Loop Detected',
    509: 'Bandwidth Limit Exceeded',
    510: 'Not Extended',
    511: 'Network Authentication Required',
    598: 'Network Read Timeout Error',
    599: 'Network Connect Timeout Error',
}


def http_role(role, rawtext, text, linenum, inliner, options={}, content=[]):
    """Implementation of the :rst:role:`http` role.

    This is responsible for converting a HTTP status code to link pointing to
    the status documentation, with the full text for the status name.

    Args:
        rawtext (unicode):
            The raw text for the entire role.

        text (unicode):
            The interpreted text content.

        linenum (int):
            The current line number.

        inliner (docutils.parsers.rst.states.Inliner):
            The inliner used for error reporting and document tree access.

        options (dict):
            Options passed for the role. This is unused.

        content (list of unicode):
            The list of strings containing content for the role directive.
            This is unused.

    Returns:
        tuple:
        The result of the role. It's a tuple containing two items:

        1) A single-item list with the resulting node.
        2) A single-item list with the error message (if any).
    """
    try:
        status_code = int(text)

        if status_code not in HTTP_STATUS_CODES:
            raise ValueError
    except ValueError:
        msg = inliner.reporter.error(
            'HTTP status code must be a valid HTTP status; '
            '"%s" is invalid.' % text,
            line=linenum)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    http_status_codes_url = \
        inliner.document.settings.env.config.http_status_codes_url

    if not http_status_codes_url or '%s' not in http_status_codes_url:
        msg = inliner.reporter.error('http_status_codes_url must be '
                                     'configured.',
                                     line=linenum)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    ref = http_status_codes_url % status_code
    status_code_text = 'HTTP %s %s' % (status_code,
                                       HTTP_STATUS_CODES[status_code])
    node = nodes.reference(rawtext, status_code_text, refuri=ref, **options)

    return [node], []


def setup(app):
    """Set up the Sphinx extension.

    This registers the :rst:role:`http` role and ``http_status_codes_url``
    configuration variable.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register roles and configuration on.
    """
    app.add_config_value(b'http_status_codes_url',
                         DEFAULT_HTTP_STATUS_CODES_URL,
                         True)
    app.add_role(b'http', http_role)
