#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np
import os

pb.init_memmap()


class ChecksIP(unittest.TestCase):

    def test_shrink_image(self):
        # Just test to see if it crashes
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)

        # ---------- Single axis specified
        # Shrink with integration
        found = pb.shrink_image(j_img, 60, interp_type=pb.InterpolationType.INTEGRAL)
        self.assertEqual(60*100/120, found.getWidth())
        self.assertEqual(60*120/120, found.getHeight())

        # Shrink with interpolation
        found = pb.shrink_image(j_img, 60, interp_type=pb.InterpolationType.BILINEAR)
        self.assertEqual(60 * 100 / 120, found.getWidth())
        self.assertEqual(60 * 120 / 120, found.getHeight())

        # ---------- Both axises specified
        # Shrink with integration
        found = pb.shrink_image(j_img, (50, 60), interp_type=pb.InterpolationType.INTEGRAL)
        self.assertEqual(60, found.getWidth())
        self.assertEqual(50, found.getHeight())

        # Shrink with interpolation
        found = pb.shrink_image(j_img, (50, 60), interp_type=pb.InterpolationType.BILINEAR)
        self.assertEqual(60, found.getWidth())
        self.assertEqual(50, found.getHeight())


if __name__ == '__main__':
    unittest.main()
