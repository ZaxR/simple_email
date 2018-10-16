#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc


with open("README.md") as readme_file:
    readme = readme_file.read()

# list of strings specifying what other distributions need to be present in order for the setup script to run
setup_requires = ["pytest-runner"]

# Put package requirements here
install_requires = []

tests_require = ["pytest"]

cmdclass = {'build_sphinx': BuildDoc}

name = "simple_email"
copyright = "2018, Test"
version = '0.1'
release = '0.1.0'
setup(
    name=name,
    version=release,
    description="Easy e-mailing with pure python; wraps the standard library's smtp and email modules.",
    long_description=readme,
    url="https://github.com/zaxr/simple_email",
    author="Zax Rosenberg",
    author_email="zaxr@protonmail.com",
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Natural Language :: English",
                 "Programming Language :: Python :: 3.6"],
    packages=find_packages(exclude=["docs", "tests"]),
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="tests",
    cmdclass=cmdclass,
    # these are optional and override conf.py settings
    command_options={'build_sphinx': {"project": ("setup.py", name),
                                      "copyright": ("setup.py", copyright),
                                      "version": ("setup.py", version),
                                      "release": ("setup.py", release),
                                      "source_dir": ("setup.py", "docs")}}
)
