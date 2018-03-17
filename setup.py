#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import setuptools

def main():

    setuptools.setup(
        name             = "ucom_eli",
        version          = "2018.03.17.2113",
        description      = "ergonomic launcher interface",
        long_description = long_description(),
        url              = "https://github.com/wdbm/ucom-eli",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        py_modules       = [
                           "ucom-eli"
                           ],
        install_requires = [
                           "docopt",
                           "propyte",
                           "shijian"
                           ],
        scripts          = [
                           "ucom-eli.py"
                           ]
    )

def long_description(
    filename = "README.md"
    ):

    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
