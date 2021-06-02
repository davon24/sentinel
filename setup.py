
# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


from setuptools import setup


setup(
    name = "sentinel",
    packages = ["sentinel"],
    entry_points = {
        "console_scripts": ['sentinel = sentinel.sentinel:main']
        },
    version = '1.6.28-1',
    description = "sentinel command and daemon",
    long_description = "Python command line tool for administration of sentinel.",
    author = "Karl Rink",
    author_email = "karl@rink.us",
    url = "https://gitlab.com/krink/sentinel",
    install_requires = [ ]
    )


