# NOTE: The line numbers in this file matters for tests.
from collections import namedtuple


class ClassA(object):
    pass


class ClassB(object):
    """Docstring here."""

    my_var = True

    def __init__(self):
        pass

    def do_thing(self, a, b):
        pass


def my_func():
    pass


my_var = ClassB

MyNamedTuple = namedtuple('MyNamedTuple', ('a', 'b', 'c'))
