"""Base definitions and version info for beanbag_docutils."""

from __future__ import annotations

#: The version of beanbag_docutils.
#:
#: This is in the format of:
#:
#:   (Major, Minor, Micro, alpha/beta/rc/final, Release Number, Released)
#:
VERSION: tuple[int, int, int, str, int, bool] = \
    (3, 0, 0, 'alpha', 0, False)


def get_version_string() -> str:
    """Return the version as a human-readable string.

    Returns:
        str:
        The version number as a human-readable string.
    """
    major, minor, micro, release_type, release_num, _released = VERSION

    version = f'{major}.{minor}'

    if micro:
        version += f'.{micro}'

    if release_type != 'final':
        if release_type == 'rc':
            version += f' RC{release_num}'
        else:
            version += f' {release_type} {release_num}'

    if not is_release():
        version += ' (dev)'

    return version


def get_package_version() -> str:
    """Return the version as a Python package version string.

    Returns:
        str:
        The version number as used in a Python package.
    """
    major, minor, micro, release_type, release_num, _released = VERSION

    version = f'{major}.{minor}'

    if micro:
        version += f'.{micro}'

    if release_type != 'final':
        version += f'{release_type}{release_num}'

    return version


def is_release() -> bool:
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
