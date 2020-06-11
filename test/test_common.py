#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np

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


class ArrayTransfer(unittest.TestCase):

    def test_mmap_array_python_to_java_U8(self):
        pyarray = np.uint8([1, 0, 255, 100, 199])
        jarray = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_U8)

        self.assertEqual(5, len(jarray))
        for i in range(len(pyarray)):
            self.assertEqual(pyarray[i], np.uint8(jarray[i]))

    def test_mmap_array_python_to_java_S8(self):
        pyarray = [1, 0, -120, 100, -20]
        jarray = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_S8)

        self.assertEqual(5, len(jarray))
        for i in range(len(pyarray)):
            self.assertEqual(pyarray[i], np.int8(jarray[i]))

    def test_mmap_array_python_to_java_S32(self):
        pyarray = [1, 0, 1999394, -10, -99384]
        # pyarray = np.int32([1, 0, 1999394, -10, -99384])
        jarray = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_S32)

        self.assertEqual(5, len(jarray))
        for i in range(len(pyarray)):
            self.assertEqual(pyarray[i], np.int32(jarray[i]))

    def test_mmap_array_python_to_java_F32(self):
        pyarray = np.float32([1.0, 0.0, 1.059e3, -102.034, -9.3243])
        jarray = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_F32)

        self.assertEqual(5, len(jarray))
        for i in range(len(pyarray)):
            self.assertEqual(pyarray[i], np.float32(jarray[i]))

    def test_mmap_array_java_to_python_U8(self):
        pyarray = np.uint8([1, 0, 255, 100, 199])
        jarray  = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_U8)
        pyfound = pb.mmap_array_java_to_python(jarray , pb.MmapType.ARRAY_U8)

        self.assertEqual(5, len(pyfound))
        for i in range(len(pyfound)):
            self.assertEqual(pyarray[i], pyfound[i])

    def test_mmap_array_java_to_python_S8(self):
        pyarray = [1, 0, -120, 100, -20]
        jarray  = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_S8)
        pyfound = pb.mmap_array_java_to_python(jarray , pb.MmapType.ARRAY_S8)

        self.assertEqual(5, len(pyfound))
        for i in range(len(pyfound)):
            self.assertEqual(pyarray[i], pyfound[i])

    def test_mmap_array_java_to_python_S32(self):
        pyarray = [1, 0, 1999394, -10, -99384]
        jarray  = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_S32)
        pyfound = pb.mmap_array_java_to_python(jarray , pb.MmapType.ARRAY_S32)

        self.assertEqual(5, len(pyfound))
        for i in range(len(pyfound)):
            self.assertEqual(np.int32(pyarray[i]), pyfound[i])

    def test_mmap_array_java_to_python_F32(self):
        pyarray = [1.0, 0.0, 1.059e3, -102.034, -9.3243]
        jarray  = pb.mmap_array_python_to_java(pyarray, pb.MmapType.ARRAY_F32)
        pyfound = pb.mmap_array_java_to_python(jarray , pb.MmapType.ARRAY_F32)

        self.assertEqual(5, len(pyfound))
        for i in range(len(pyfound)):
            self.assertEqual(np.float32(pyarray[i]), pyfound[i])

if __name__ == '__main__':
    unittest.main()
