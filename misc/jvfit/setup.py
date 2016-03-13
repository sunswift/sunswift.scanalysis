#! /usr/bin/env python

from distutils.core import setup, Extension

module1 = Extension('jvfit',
                    sources = ['jvfitmodule.cpp', 'leastsquares.cpp', 'twodiodemodel.cpp', 'quadsmooth.cpp', \
                                   'decompose.cpp', 'jvfit.cpp', 'jvcalc.cpp'])

setup (name = 'jvfit',
       version = '1.0',
       description = 'JV Curve fitting software by Bonne Eggleston, Python binding by David Snowdon',
       ext_modules = [module1])
