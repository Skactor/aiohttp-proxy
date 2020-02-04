#!/usr/bin/env python
import codecs
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = None

with codecs.open(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "aiohttp_proxy", "__init__.py"
    ),
    "r",
    "latin1",
) as fp:
    try:
        version = re.findall(r'^__version__ = "(\S+?)"$', fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")

if sys.version_info < (3, 5, 3):
    raise RuntimeError("aiohttp_proxy requires Python 3.5.3+")

with open("README.md") as f:
    long_description = f.read()

setup(
    name="aiohttp_proxy",
    author="Skactor",
    author_email="sk4ct0r@gmail.com",
    version=version,
    license="Apache 2",
    url="https://github.com/Skactor/aiohttp-proxy",
    description="Full-featured proxy connector for aiohttp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["aiohttp_proxy"],
    keywords="asyncio aiohttp socks socks5 socks4 http https proxy",
    install_requires=["aiohttp>=2.3.2", "yarl"],
)
