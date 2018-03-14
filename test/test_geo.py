#!/usr/bin/env python

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np

pb.init_memmap()


class TestMemMapFunctions(unittest.TestCase):

    def test_convert_list_AssociatedPair(self):
        original = [((1, 2.34),(4,4.5)), ((-23.4, 934.123),(5.1,3.2))]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_AssociatedPair(original, java_list)

        # java to python
        found = []
        pb.mmap_list_AssociatedPair_to_python(java_list, found)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = original[i]
            b = found[i]
            self.assertEqual(a[0][0], b[0][0])
            self.assertEqual(a[0][1], b[0][1])
            self.assertEqual(a[1][0], b[1][0])
            self.assertEqual(a[1][1], b[1][1])


    def test_convert_list_Point2D_F64(self):
        original = [(1, 2.34), (-23.4, 934.123)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point2D(original, java_list, np.double)

        # java to python
        found = []
        pb.mmap_list_Point2D_to_python(java_list, found, np.double)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = original[i]
            b = found[i]
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])


    def test_convert_list_Point2D_F32(self):
        original = [(1, 2.34), (-23.4, 934.123)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point2D(original, java_list, np.float)

        # java to python
        found = []
        pb.mmap_list_Point2D_to_python(java_list, found, np.float)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = np.float32(original[i])
            b = found[i]
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])


    def test_convert_list_Point2D_I32(self):
        original = [(1, 2), (-23, 934)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point2D(original, java_list, np.int32)

        # java to python
        found = []
        pb.mmap_list_Point2D_to_python(java_list, found, np.int32)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = original[i]
            b = found[i]
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])


    def test_convert_list_Point2D_I16(self):
        original = [(1, 2), (-23, 934)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point2D(original, java_list, np.int16)

        # java to python
        found = []
        pb.mmap_list_Point2D_to_python(java_list, found, np.int16)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = original[i]
            b = found[i]
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])

if __name__ == '__main__':
    unittest.main()
