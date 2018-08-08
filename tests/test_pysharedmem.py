#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pickle
import sys
import unittest


try:
    unichr
except NameError:
    unichr = chr


class TestPySharedMem(unittest.TestCase):
    def test_import(self):
        try:
            import pysharedmem
        except ImportError:
            self.fail("Unable to import `pysharedmem`.")


    def test_create_empty_mem(self):
        import pysharedmem
        with self.assertRaises(ValueError):
            pysharedmem.cbuffer(0)


    def test_create_negative_mem(self):
        import pysharedmem
        with self.assertRaises(ValueError):
            pysharedmem.cbuffer(-1)


    def test_create_singleton_mem(self):
        import pysharedmem
        pysharedmem.cbuffer(1)


    def test_memoryview(self):
        import pysharedmem

        l = 3
        b = pysharedmem.cbuffer(l)

        m = memoryview(b)

        self.assertEqual(m.readonly, False)

        self.assertEqual(m.format, 'c')
        self.assertEqual(m.itemsize, 1)

        self.assertEqual(m.ndim, 1)
        self.assertEqual(m.shape, (l,))
        self.assertEqual(m.strides, (1,))

        if sys.version_info[0] >= 3:
            self.assertEqual(m.suboffsets, ())
        else:
            self.assertEqual(m.suboffsets, None)


    @unittest.skipIf(sys.version_info[0] < 3,
                     "This test requires Python 3.")
    def test_memoryview_py3(self):
        import pysharedmem

        l = 3
        b = pysharedmem.cbuffer(l)

        m = memoryview(b)

        self.assertIs(m.obj, b)

        self.assertTrue(m.c_contiguous)
        self.assertTrue(m.contiguous)
        self.assertTrue(m.f_contiguous)

        self.assertEqual(m.readonly, False)

        self.assertEqual(m.format, 'c')
        self.assertEqual(m.itemsize, 1)

        self.assertEqual(m.ndim, 1)
        self.assertEqual(m.nbytes, l)
        self.assertEqual(m.shape, (l,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.suboffsets, ())


    def test_assignment(self):
        import pysharedmem

        l = 3
        b = pysharedmem.cbuffer(l)

        m = memoryview(b)
        for i in range(len(m)):
            m[i] = unichr(i).encode("utf-8")

        a1 = bytearray(m)
        a2 = bytearray(b)

        self.assertIsNot(a1, a2)
        self.assertEqual(a1, a2)


    def test_pickle(self):
        import pysharedmem

        l = 3
        b1 = pysharedmem.cbuffer(l)

        m = memoryview(b1)
        for i in range(len(m)):
            m[i] = unichr(i).encode("utf-8")

        b2 = pickle.loads(pickle.dumps(b1))

        a1 = bytes(memoryview(b1))
        a2 = bytes(memoryview(b2))

        self.assertIsNot(b1, b2)
        self.assertIsNot(a1, a2)
        self.assertEqual(a1, a2)
