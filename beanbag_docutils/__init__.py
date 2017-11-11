from __future__ import unicode_literals


#: The version of beanbag_docutils.
#:
#: This is in the format of:
#:
#:   (Major, Minor, Micro, alpha/beta/rc/final, Release Number, Released)
#:
VERSION = (1, 5, 0, 'final', 0, True)


def get_version_string():
    """Return the version as a human-readable string.

    Returns:
        unicode:
        The version number as a human-readable string.
    """
    version = '%s.%s' % (VERSION[0], VERSION[1])

    if VERSION[2]:
        version += ".%s" % VERSION[2]

    if VERSION[3] != 'final':
        if VERSION[3] == 'rc':
            version += ' RC%s' % VERSION[4]
        else:
            version += ' %s %s' % (VERSION[3], VERSION[4])

    if not is_release():
        version += " (dev)"

    return version


def get_package_version():
    """Return the version as a Python package version string.

    Returns:
        unicode:
        The version number as used in a Python package.
    """
    version = '%s.%s' % (VERSION[0], VERSION[1])

    if VERSION[2]:
        version += ".%s" % VERSION[2]

    if VERSION[3] != 'final':
        version += '%s%s' % (VERSION[3], VERSION[4])

    return version


def is_release():
    """Return whether this is a released version.

    Returns:
        bool:
        ``True`` if this is a released version of the package.
    """
    return VERSION[5]


#: An alias for the the version information from :py:data:`VERSION`.
#:
#: This does not include the last entry in the tuple (the released state).
__version_info__ = VERSION[:-1]

#: An alias for the version used for the Python package.
__version__ = get_package_version()
