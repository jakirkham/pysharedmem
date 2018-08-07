#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import sys

import setuptools
from setuptools import setup, Extension

from distutils.sysconfig import get_config_var, get_python_inc

import versioneer

version = versioneer.get_version()

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup_requirements = [
    "Cython>=0.28.5",
]

install_requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

cmdclasses = dict()
cmdclasses.update(versioneer.get_cmdclass())

if not (({"develop", "test"} & set(sys.argv)) or
    any([v.startswith("build") for v in sys.argv]) or
    any([v.startswith("bdist") for v in sys.argv]) or
    any([v.startswith("install") for v in sys.argv])):
    setup_requirements = []
else:
    with open("src/version.pxi", "w") as f:
        f.writelines([
            "__version__ = " + "\"" + str(version) + "\""
        ])


try:
    i = sys.argv.index("test")
    sys.argv = sys.argv[:i] + ["build_ext", "--inplace"] + sys.argv[i:]
except ValueError:
    pass


include_dirs = [
    os.path.dirname(get_python_inc()),
    get_python_inc()
]
library_dirs = list(filter(
    lambda v: v is not None,
    [get_config_var("LIBDIR")]
))

headers = []
sources = glob.glob("src/*.pxd") + glob.glob("src/*.pyx")
libraries = []
define_macros = []
extra_compile_args = []
cython_directives = {}
cython_line_directives = {}


if "test" in sys.argv:
    cython_directives["binding"] = True
    cython_directives["embedsignature"] = True
    cython_directives["profile"] = True
    cython_directives["linetrace"] = True
    define_macros += [
        ("CYTHON_PROFILE", 1),
        ("CYTHON_TRACE", 1),
        ("CYTHON_TRACE_NOGIL", 1),
    ]


ext_modules = [
    Extension(
        "pysharedmem",
        sources=sources,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        language="c"
    )
]
for em in ext_modules:
    em.cython_directives = dict(cython_directives)
    em.cython_line_directives = dict(cython_line_directives)


setup(
    name="pysharedmem",
    version=version,
    description="Code for using interprocess shared memory in Python",
    long_description=readme + "\n\n" + history,
    author="John Kirkham",
    author_email="kirkhamj@janelia.hhmi.org",
    url="https://github.com/jakirkham/pysharedmem",
    cmdclass=cmdclasses,
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    setup_requires=setup_requirements,
    install_requires=install_requirements,
    headers=headers,
    ext_modules=ext_modules,
    license="BSD 3-Clause",
    zip_safe=False,
    keywords="pysharedmem",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=test_requirements
)
