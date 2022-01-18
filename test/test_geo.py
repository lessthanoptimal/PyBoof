#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np
import os

class ChecksCameraBrown(unittest.TestCase):
    def test_setters(self):
        calib = pb.CameraBrown()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.set_distortion([0.1, 0.2], 103, 104)

        self.check_expected_values(calib)

    def check_expected_values(self, calib):
        self.assertEqual(calib.width, 200)
        self.assertEqual(calib.height, 300)

        self.assertEqual(calib.fx, 100)
        self.assertEqual(calib.fy, 101)
        self.assertEqual(calib.skew, 102)
        self.assertEqual(calib.cx, 103)
        self.assertEqual(calib.cy, 104)

        self.assertEqual(calib.radial, [0.1, 0.2])
        self.assertEqual(calib.t1, 103)
        self.assertEqual(calib.t2, 104)

    def test_save_load(self):
        calib = pb.CameraBrown()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.set_distortion([0.1, 0.2], 103, 104)

        calib.save("junk")
        calib = pb.CameraBrown()
        calib.load("junk")
        os.remove("junk")
        self.check_expected_values(calib)


class CameraUniversalOmni(unittest.TestCase):
    def test_setters(self):
        calib = pb.CameraUniversalOmni()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.set_distortion([0.1, 0.2], 103, 104)
        calib.mirror_offset = 3.1

        self.check_expected_values(calib)

    def check_expected_values(self, calib):
        self.assertEqual(calib.width, 200)
        self.assertEqual(calib.height, 300)

        self.assertEqual(calib.fx, 100)
        self.assertEqual(calib.fy, 101)
        self.assertEqual(calib.skew, 102)
        self.assertEqual(calib.cx, 103)
        self.assertEqual(calib.cy, 104)

        self.assertEqual(calib.radial, [0.1, 0.2])
        self.assertEqual(calib.t1, 103)
        self.assertEqual(calib.t2, 104)

        self.assertEqual(calib.mirror_offset, 3.1)

    def test_save_load(self):
        calib = pb.CameraUniversalOmni()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.set_distortion([0.1, 0.2], 103, 104)
        calib.mirror_offset = 3.1

        calib.save("junk")
        calib = pb.CameraUniversalOmni()
        calib.load("junk")
        os.remove("junk")
        self.check_expected_values(calib)


class CameraKannalaBrandt(unittest.TestCase):
    def test_setters(self):
        calib = pb.CameraKannalaBrandt()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.symmetric = [0.1, 0.2, 0.3, 0.4]
        calib.radial = [0.1]
        calib.radialTrig = [0.1, 0.2, 1.0, -2.0]
        calib.tangent = [0.2]
        calib.tangentTrig = [0.3, 0.4, 1.0, -2.0]

        self.check_expected_values(calib)

    def check_expected_values(self, calib):
        self.assertEqual(calib.width, 200)
        self.assertEqual(calib.height, 300)

        self.assertEqual(calib.fx, 100)
        self.assertEqual(calib.fy, 101)
        self.assertEqual(calib.skew, 102)
        self.assertEqual(calib.cx, 103)
        self.assertEqual(calib.cy, 104)

        self.assertEqual(calib.symmetric, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(calib.radial, [0.1])
        self.assertEqual(calib.radialTrig, [0.1, 0.2, 1.0, -2.0])
        self.assertEqual(calib.tangent, [0.2])
        self.assertEqual(calib.tangentTrig, [0.3, 0.4, 1.0, -2.0])

    def test_save_load(self):
        calib = pb.CameraKannalaBrandt()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.symmetric = [0.1, 0.2, 0.3, 0.4]
        calib.radial = [0.1]
        calib.radialTrig = [0.1, 0.2, 1.0, -2.0]
        calib.tangent = [0.2]
        calib.tangentTrig = [0.3, 0.4, 1.0, -2.0]

        calib.save("junk")
        calib = pb.CameraKannalaBrandt()
        calib.load("junk")
        os.remove("junk")
        self.check_expected_values(calib)


class StereoParameters(unittest.TestCase):
    def test_save_load(self):
        calib = pb.StereoParameters()
        calib.left.set_image_shape(200, 300)
        calib.left.set_matrix(100, 101, 102, 103, 104)
        calib.left.set_distortion([0.1, 0.2], 103, 104)
        calib.right.set_image_shape(201, 301)
        calib.right.set_matrix(102, 100, 99, 98, 97)
        calib.right.set_distortion([-0.1, -0.2], 76, 77)
        calib.right_to_left.T.setTo(1.0, 2.0, 3.1)

        calib.save("junk")
        calib = pb.StereoParameters()
        calib.load("junk")
        os.remove("junk")
        self.check_expected_values(calib)

    def check_expected_values(self, calib):
        self.assertEqual(calib.left.width, 200)
        self.assertEqual(calib.left.height, 300)
        self.assertEqual(calib.right.width, 201)
        self.assertEqual(calib.right.height, 301)
        self.assertEqual(calib.right_to_left.T.x, 1.0)

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
        pb.mmap_list_python_to_Point2D(original, java_list, float)

        # java to python
        found = []
        pb.mmap_list_Point2D_to_python(java_list, found, float)

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


    def test_convert_list_Point3D_F32(self):
        original = [(1, 2.34, 9.1), (-23.4, 934.123, -0.234)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point3D(original, java_list, float)

        # java to python
        found = []
        pb.mmap_list_Point3D_to_python(java_list, found, float)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = np.float32(original[i])
            b = found[i]
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])
            self.assertEqual(a[2], b[2])


    def test_convert_list_Point3D_F64(self):
        original = [(1, 2.34, 9.1), (-23.4, 934.123, -0.234)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point3D(original, java_list, np.double)

        # java to python
        found = []
        pb.mmap_list_Point3D_to_python(java_list, found, np.double)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = np.float64(original[i])
            b = found[i]
            self.assertEqual(a[0], b[0])
            self.assertEqual(a[1], b[1])
            self.assertEqual(a[2], b[2])

if __name__ == '__main__':
    unittest.main()
