#!/usr/bin/env python3

import unittest

import pyboof as pb
import numpy as np

class SystemTests(unittest.TestCase):
    # Call init_pyboof again and see if everything is reset properly
    def test_restart_jvm(self):
        pb.FactoryFiducial(np.uint8).qrcode()
        pb.init_pyboof()
        pb.FactoryFiducial(np.uint8).qrcode()


if __name__ == '__main__':
    unittest.main()