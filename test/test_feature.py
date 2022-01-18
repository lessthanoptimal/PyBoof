#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np


class TestMemMapFunctions(unittest.TestCase):
    def test_convert_list_tuple64(self):
        original = [[1, 2.34, 6.7], [-23.4, 934.123, 56.1]]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_TupleF64(original, java_list)

        # java to python
        found = []
        pb.mmap_list_TupleF64_to_python(java_list, found)

        self.assertEqual(len(original), len(found))

        for i in range(len(original)):
            a = original[i]
            b = found[i]
            self.assertEqual(len(a),len(b))
            for j in range(len(a)):
                self.assertEqual(a[j],b[j])

# Mostly tests to see if it can load an not crash
class TestFactoryDenseDescribe(unittest.TestCase):
    def test_createSurf_fast(self):
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)

        factory = pb.FactoryDenseDescribe(dtype=np.uint8)
        describer = factory.createSurf(pb.ConfigDenseSurfFast())
        describer.detect(j_img)
        self.assertTrue(len(describer.locations)>10)
        self.assertTrue(len(describer.descriptions)>10)

        describer = factory.createSurf(None)
        describer.detect(j_img)
        self.assertTrue(len(describer.locations) > 10)
        self.assertTrue(len(describer.descriptions) > 10)

    def test_createSurf_stable(self):
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)

        factory = pb.FactoryDenseDescribe(dtype=np.uint8)
        describer = factory.createSurf(pb.ConfigDenseSurfStable())
        describer.detect(j_img)
        self.assertTrue(len(describer.locations) > 10)
        self.assertTrue(len(describer.descriptions) > 10)

    def test_createSift(self):
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)

        factory = pb.FactoryDenseDescribe(dtype=np.uint8)
        describer = factory.createSift(None)
        describer.detect(j_img)
        self.assertTrue(len(describer.locations) > 10)
        self.assertTrue(len(describer.descriptions) > 10)

    def test_createHog(self):
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)

        factory = pb.FactoryDenseDescribe(dtype=np.uint8)
        describer = factory.createHoG(None)
        describer.detect(j_img)
        self.assertTrue(len(describer.locations) > 10)
        self.assertTrue(len(describer.descriptions) > 10)


if __name__ == '__main__':
    unittest.main()
