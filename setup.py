#! /usr/bin/env python3

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name = "wytch",
    version = "0.1",
    packages = ["wytch"],
    description = "Python TUI library",
    author = "Josef Gajdusek",
    author_email = "atx@atx.name",
    url = "https://github.com/atalax/wytch",
    license = "MIT",
    setup_requires = ["pytest-runner"],
    tests_require = ["pytest"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        ]
    )
