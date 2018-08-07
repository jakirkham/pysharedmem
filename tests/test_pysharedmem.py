#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest


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
            m[i] = i.to_bytes(1, "little")

        a1 = bytearray(m)
        a2 = bytearray(b)

        self.assertIsNot(a1, a2)
        self.assertEqual(a1, a2)
