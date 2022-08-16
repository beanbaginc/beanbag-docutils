#!/usr/bin/env python

from setuptools import setup, find_packages

from beanbag_docutils import get_package_version


PACKAGE_NAME = 'beanbag-docutils'


with open('README.rst', 'r') as fp:
    readme = fp.read()


setup(
    name=PACKAGE_NAME,
    version=get_package_version(),
    license='MIT',
    description="Sphinx utility modules for Beanbag's documentation format.",
    long_description=readme,
    url='https://github.com/beanbaginc/beanbag-docutils',
    maintainer='Christian Hammond',
    maintainer_email='christian@beanbaginc.com',
    packages=find_packages(),
    install_requires=[
        'six',
        'Sphinx',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
