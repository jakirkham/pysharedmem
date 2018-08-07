#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest


class TestImportTopLevel(unittest.TestCase):
    def runTest(self):
        try:
            import pysharedmem
        except ImportError:
            self.fail("Unable to import `pysharedmem`.")
