#!/usr/bin/env python

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np
import os

pb.init_memmap()


class ChecksCameraPinhole(unittest.TestCase):

    def test_setters(self):
        calib = pb.CameraPinhole()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.set_distortion([0.1, 0.2], 103, 104)

        self.check_expected_values(calib)

    def check_expected_values(self, calib):
        self.assertEquals(calib.width, 200)
        self.assertEquals(calib.height, 300)

        self.assertEquals(calib.fx, 100)
        self.assertEquals(calib.fy, 101)
        self.assertEquals(calib.skew, 102)
        self.assertEquals(calib.cx, 103)
        self.assertEquals(calib.cy, 104)

        self.assertEquals(calib.radial, [0.1, 0.2])
        self.assertEquals(calib.t1, 103)
        self.assertEquals(calib.t2, 104)

    def test_save_load(self):
        calib = pb.CameraPinhole()
        calib.set_image_shape(200, 300)
        calib.set_matrix(100, 101, 102, 103, 104)
        calib.set_distortion([0.1, 0.2], 103, 104)

        calib.save("junk")
        calib = pb.CameraPinhole()
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
        self.assertEquals(calib.width, 200)
        self.assertEquals(calib.height, 300)

        self.assertEquals(calib.fx, 100)
        self.assertEquals(calib.fy, 101)
        self.assertEquals(calib.skew, 102)
        self.assertEquals(calib.cx, 103)
        self.assertEquals(calib.cy, 104)

        self.assertEquals(calib.radial, [0.1, 0.2])
        self.assertEquals(calib.t1, 103)
        self.assertEquals(calib.t2, 104)

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

if __name__ == '__main__':
    unittest.main()
