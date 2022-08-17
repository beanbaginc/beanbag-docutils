"""Unit tests for beanbag_docutils.sphinx.ext.github"""

from __future__ import unicode_literals

import kgb
import six

from beanbag_docutils.sphinx.ext.github import (clear_github_linkcode_caches,
                                                github_linkcode_resolve,
                                                _run_git)
from beanbag_docutils.sphinx.ext.tests.testcase import SphinxExtTestCase
from beanbag_docutils.sphinx.ext.tests.testdata import github_linkcode_module


class GitHubLinkCodeResolveTests(kgb.SpyAgency, SphinxExtTestCase):
    """Unit tests for github_linkcode_resolve"""

    SRC_MODULE = github_linkcode_module.__name__

    def tearDown(self):
        super(GitHubLinkCodeResolveTests, self).tearDown()

        clear_github_linkcode_caches()

    def test_with_link_to_class(self):
        """Testing github_linkcode_resolve with linking to class"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L9')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_link_to_function(self):
        """Testing github_linkcode_resolve with linking to function"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'my_func',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L21')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_link_to_class_attr(self):
        """Testing github_linkcode_resolve with linking to class attribute"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.my_var',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L12')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_link_to_variable(self):
        """Testing github_linkcode_resolve with linking to global variable"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'my_var',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L25')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_link_to_method(self):
        """Testing github_linkcode_resolve with linking to method"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L17')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_link_to_object_attr_not_in_code(self):
        """Testing github_linkcode_resolve with linking to an attribute on an
        object not defined in code
        """
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'MyNamedTuple.__match_args__',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L27')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_allowed_modules_and_found(self):
        """Testing github_linkcode_resolve with allowed_modules and module
        found
        """
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            allowed_module_names=['beanbag_docutils'])

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/beanbag_docutils/'
            'sphinx/ext/tests/testdata/github_linkcode_module.py#L17')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_allowed_modules_and_not_found(self):
        """Testing github_linkcode_resolve with allowed_modules and module
        not found
        """
        self.spy_on(_run_git, call_original=False)

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            allowed_module_names=['something_else'])

        self.assertIsNone(url)
        self.assertSpyCallCount(_run_git, 0)

    def test_with_source_prefix(self):
        """Testing github_linkcode_resolve with source_prefix"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'157ac365d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            source_prefix='foo/bar/')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/foo/bar/'
            'beanbag_docutils/sphinx/ext/tests/testdata/'
            'github_linkcode_module.py#L17')

        self.assertSpyCallCount(_run_git, 4)

    def test_with_multiple_refs(self):
        """Testing github_linkcode_resolve with multiple refs for branch"""
        self.spy_on(_run_git, op=kgb.SpyOpMatchInOrder([
            {
                'args': (['fetch', 'origin', 'mybranch', 'origin'],),
                'call_original': False,
            },
            {
                'args': (['branch', '-rv', '--contains', 'mybranch'],),
                'op': kgb.SpyOpReturn(
                    b'  origin/mybranch abcd123 Here is a commit.\n'
                    b'  origin/mybranch-dev def4567 Branched for dev.\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...abcd123'],),
                'op': kgb.SpyOpReturn(
                    b'abcd1235d792c79987966e0152d16d6d1526b24d\n'
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
            {
                'args': (['log', '--pretty=format:%H', '...def4567'],),
                'op': kgb.SpyOpReturn(
                    b'def45675d792c79987966e0152d16d6d1526b24d\n'
                ),
            },
            {
                'args': (['rev-parse', 'mybranch-dev'],),
                'op': kgb.SpyOpReturn(
                    b'55ca6286e3e4f4fba5d0448333fa99fc5a404a73\n'
                ),
            },
        ]))

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            source_prefix='foo/bar/')

        self.assertIsNotNone(url)
        self.assertIsInstance(url, six.text_type)
        self.assertEqual(
            url,
            'https://github.com/beanbaginc/beanbag_docutils/blob/'
            '55ca6286e3e4f4fba5d0448333fa99fc5a404a73/foo/bar/'
            'beanbag_docutils/sphinx/ext/tests/testdata/'
            'github_linkcode_module.py#L17')

        self.assertSpyCallCount(_run_git, 5)

    def test_with_non_py_domain(self):
        """Testing github_linkcode_resolve with non-"py" domain"""
        self.spy_on(_run_git, call_original=False)

        url = github_linkcode_resolve(
            domain='js',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            source_prefix='foo/bar/')

        self.assertIsNone(url)

    def test_with_no_module_name(self):
        """Testing github_linkcode_resolve with no module name"""
        self.spy_on(_run_git, call_original=False)

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': '',
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            source_prefix='foo/bar/')

        self.assertIsNone(url)

    def test_with_module_not_found(self):
        """Testing github_linkcode_resolve with module not found"""
        self.spy_on(_run_git, call_original=False)

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': 'beanbag_docutils.xxx',
                'fullname': 'ClassB.do_thing',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            source_prefix='foo/bar/')

        self.assertIsNone(url)

    def test_with_fullname_not_found(self):
        """Testing github_linkcode_resolve with fullname object not found"""
        self.spy_on(_run_git, call_original=False)

        url = github_linkcode_resolve(
            domain='py',
            info={
                'module': self.SRC_MODULE,
                'fullname': 'ClassB.invalid_function',
            },
            github_org_id='beanbaginc',
            github_repo_id='beanbag_docutils',
            branch='mybranch',
            source_prefix='foo/bar/')

        self.assertIsNone(url)
