#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb

pb.init_memmap()


class JavaData(unittest.TestCase):
    def test_is_java_class(self):
        array_class = gateway.jvm.java.util.ArrayList().getClass()
        vector_class = gateway.jvm.java.util.Vector().getClass()

        self.assertFalse(pb.is_java_class(array_class, "java.util.Vector"))
        self.assertTrue(pb.is_java_class(vector_class, "java.util.Vector"))

    def test_ejml_matrix_d_to_f(self):
        mat_d = gateway.jvm.org.ejml.data.DMatrixRMaj(5, 4)
        mat_f = pb.ejml_matrix_d_to_f(mat_d)
        self.assertEqual(5, mat_f.getNumRows())
        self.assertEqual(4, mat_f.getNumCols())
        self.assertTrue(pb.is_java_class(mat_f.getClass(), "org.ejml.data.FMatrixRMaj"))


if __name__ == '__main__':
    unittest.main()
