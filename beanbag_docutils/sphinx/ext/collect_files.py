"""Sphinx extension to collect additional files in the build directory.

This is used to copy files (indicated by glob patterns) from the source
directory into the destination build directory. Each destination file will be
in the same relative place in the tree.

This is useful when you have non-ReST/image files that you want part of your
built set of files, perhaps containing metadata or packaging that you want to
ship along with the documentation.


Setup
=====

To use this, you just need to add the extension in :file:`conf.py`::

    extensions = [
        ...
        'beanbag_docutils.sphinx.ext.collect_files',
        ...
    ]

And then configure ``collect_file_patterns`` to be a list of
filenames/glob patterns.


Configuration
=============

``collect_file_patterns``
    List of filenames or glob patterns to include from the source directory
    into the build directory.
"""

from __future__ import annotations

import os
import shutil
from fnmatch import fnmatch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def collect_files(
    app: Sphinx,
    env: BuildEnvironment,
) -> None:
    """Collect configured files and put them into the build directory.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to register roles and configuration on.

        env (sphinx.environment.BuildEnvironment, unused):
            The build environment for the generated docs.
    """
    collect_patterns = app.config['collect_file_patterns']
    src_dir = str(app.builder.srcdir)
    out_dir = str(app.builder.outdir)

    for root, dirs, files in os.walk(src_dir):
        # Make sure we don't recurse into the build directory.
        if root == src_dir:
            try:
                dirs.remove('_build')
            except ValueError:
                pass

        for filename in files:
            for pattern in collect_patterns:
                if fnmatch(filename, pattern):
                    shutil.copy(os.path.join(root, filename),
                                os.path.join(out_dir,
                                             os.path.relpath(root, src_dir),
                                             filename))
                    break


def setup(
    app: Sphinx,
) -> dict[str, Any]:
    """Set up the Sphinx extension.

    This listens for the events needed to collect files.

    Args:
        app (sphinx.application.Sphinx):
            The Sphinx application to listen to events on.

    Returns:
        dict:
        Information about the extension.
    """
    app.add_config_value('collect_file_patterns', [], 'env')
    app.connect('env-updated', collect_files)

    return {
        'version': '1.0',
        'parallel_read_safe': True,
    }
