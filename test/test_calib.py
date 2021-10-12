#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np
import os

pb.init_memmap()


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

if __name__ == '__main__':
    unittest.main()
