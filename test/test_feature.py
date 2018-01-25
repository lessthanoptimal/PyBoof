#!/usr/bin/env python

import unittest

from pyboof import gateway
import pyboof as pb

pb.init_memmap()


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


if __name__ == '__main__':
    unittest.main()
