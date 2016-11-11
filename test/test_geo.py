#!/usr/bin/env python

import unittest

from pyboof import gateway
import pyboof as pb

pb.init_memmap()


class TestMemMapFunctions(unittest.TestCase):

    def test_convert_list_Point2DF64(self):
        original = [(1, 2.34), (-23.4, 934.123)]

        # python to java
        java_list = gateway.jvm.java.util.ArrayList()
        pb.mmap_list_python_to_Point2DF64(original, java_list)

        # java to python
        found = []
        pb.mmap_list_Point2DF64_to_python(java_list, found)

        self.assertEqual(len(original), len(found))

        for i in xrange(len(original)):
            a = original[i]
            b = found[i]
            self.assertEquals(a[0], b[0])
            self.assertEquals(a[1], b[1])


if __name__ == '__main__':
    unittest.main()
