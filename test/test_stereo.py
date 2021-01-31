#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np

pb.init_memmap()


class FactoryStereoDisparity(unittest.TestCase):
    def test_block_match(self):
        error_types = pb.DisparityError.values
        for input_type in [np.uint8,np.float32]:
            factory = pb.FactoryStereoDisparity(input_type)
            for error_type in error_types:
                config = pb.ConfigDisparityBM()
                config.errorType = error_type
                # See that it doesn't crash and returns a non None value
                self.assertTrue(factory.block_match(config))

    def test_block_match_best5(self):
        error_types = pb.DisparityError.values
        for input_type in [np.uint8,np.float32]:
            factory = pb.FactoryStereoDisparity(input_type)
            for error_type in error_types:
                config = pb.ConfigDisparityBMBest5()
                config.errorType = error_type
                # See that it doesn't crash and returns a non None value
                self.assertTrue(factory.block_match_best5(config))


    def test_sgm(self):
        error_hmi = pb.gateway.jvm.boofcv.factory.disparity.DisparitySgmError.MUTUAL_INFORMATION
        error_types = gateway.jvm.boofcv.factory.disparity.DisparitySgmError.values()
        # SGM only supports U8 images
        for input_type in [np.uint8]:
            factory = pb.FactoryStereoDisparity(input_type)
            for error_type in error_types:
                config = pb.ConfigDisparitySGM()
                config.errorType = error_type
                # See that it doesn't crash and returns a non None value
                self.assertTrue(factory.sgm(config))


if __name__ == '__main__':
    unittest.main()
