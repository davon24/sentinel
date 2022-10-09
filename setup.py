
# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from setuptools import setup

setup(
    name = "sentinel-server",
    packages = ["sentinel_server"],
    entry_points = {
        "console_scripts": ['sentinel = sentinel_server.sentinel:main']
        },
    version = '1.8.3',
    description = "sentinel command and daemon",
    long_description = "Python command line tool for administration of sentinel.",
    author = "Karl Rink",
    author_email = "karl@rink.us",
    url = "https://gitlab.com/krink/sentinel",
    install_requires = [],
    include_package_data=True,
    package_data={'': ['db/manuf',
        'modules/ps/ps.py',
        'modules/hv/kvm.py',
        'modules/gitegridy/gitegridy.py',
        'modules/ipwhois/ipwhois.py',
        ]},
    )


