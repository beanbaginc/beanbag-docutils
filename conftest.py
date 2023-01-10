"""Configures pytest for beanbag-docutils.

Version Added:
    2.1
"""

import django
import sphinx


def pytest_report_header(config):
    """Return information for the report header.

    This will log the version of Sphinx.

    Args:
        config (object):
            The pytest configuration object.

    Returns:
        list of str:
        The report header entries to log.
    """
    return [
        'Sphinx: %s' % sphinx.__version__,
        'Django: %s' % django.get_version(),
    ]
