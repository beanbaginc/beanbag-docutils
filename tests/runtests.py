#!/usr/bin/env python
from __future__ import unicode_literals

import os
import sys

import nose


def run_tests():
    nose_argv = [
        'runtests.py',
        '-v',
    ]

    if len(sys.argv) > 2:
        nose_argv += sys.argv[2:]

    if not nose.run(argv=nose_argv):
        sys.exit(1)


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, os.getcwd())
    run_tests()
