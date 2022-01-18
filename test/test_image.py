#!/usr/bin/env python3

import unittest

from pyboof import gateway
import pyboof as pb
import numpy as np


class TestBImage(unittest.TestCase):

    dtypes = (np.uint8, np.float32)

    def test_array_read_gray(self):
        for dtype in self.dtypes:
            j_img = pb.create_single_band(100, 120, dtype=dtype)
            b_image = pb.BImage(j_img)

            self.assertEqual(j_img.get(3,2), b_image[2,3])

    def test_array_read_planar(self):
        for dtype in self.dtypes:
            j_img = pb.create_planar(20, 30, 3, dtype=dtype)
            b_image = pb.BImage(j_img)

            self.assertEqual(j_img.getBand(1).get(3,2), b_image[2,3,1])

    def test_array_read_interleaved(self):
        for dtype in self.dtypes:
            j_img = pb.create_interleaved(20, 30, 3, dtype=dtype)
            b_image = pb.BImage(j_img)

            self.assertEqual(j_img.getBand(3,2,1), b_image[2,3,1])

    def test_array_write_gray(self):
        for dtype in self.dtypes:
            j_img = pb.create_single_band(100, 120, dtype=dtype)
            b_image = pb.BImage(j_img)

            b_image[2,3] = 5

            self.assertEqual(5, j_img.get(3,2))

    def test_array_write_planar(self):
        for dtype in self.dtypes:
            j_img = pb.create_planar(20, 30, 3, dtype=dtype)
            b_image = pb.BImage(j_img)

            b_image[2, 3, 0] = 5

            self.assertEqual(5, j_img.getBand(0).get(3, 2))

    def test_array_write_interleaved(self):
        for dtype in self.dtypes:
            j_img = pb.create_interleaved(20, 30, 3, dtype=dtype)
            b_image = pb.BImage(j_img)

            b_image[2, 3, 0] = 5

            self.assertEqual(5, j_img.getBand(3, 2, 0))

    def test_property_reading(self):
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)
        b_image = pb.BImage(j_img)
        self.assertEqual(100, b_image.width)
        self.assertEqual(120, b_image.height)

    def test_shape_gray(self):
        j_img = pb.create_single_band(100, 120, dtype=np.uint8)
        found = pb.BImage(j_img).shape
        self.assertEqual(2, len(found))
        self.assertEqual(120, found[0])
        self.assertEqual(100, found[1])

    def test_shape_planar(self):
        j_img = pb.create_planar(100, 120, 3, dtype=np.uint8)
        found = pb.BImage(j_img).shape
        self.assertEqual(3, len(found))
        self.assertEqual(120, found[0])
        self.assertEqual(100, found[1])
        self.assertEqual(3, found[2])

    def test_shape_interleaved(self):
        j_img = pb.create_interleaved(100, 120, 3, dtype=np.uint8)
        found = pb.BImage(j_img).shape
        self.assertEqual(3, len(found))
        self.assertEqual(120, found[0])
        self.assertEqual(100, found[1])
        self.assertEqual(3, found[2])


class TestMemMapFunctions(unittest.TestCase):

    def test_mmap_numpy_to_boof_U8(self):
        np_gray = np.random.randint(0, 256, size=(100, 120), dtype=np.uint8)
        pb_gray = pb.mmap_numpy_to_boof_U8(np_gray)

        self.assertEqual( np_gray.shape[0], pb_gray.getHeight())
        self.assertEqual( np_gray.shape[1], pb_gray.getWidth())

        self.assertEqual(np_gray[0, 0], pb_gray.get(0, 0))
        self.assertEqual(np_gray[20, 10], pb_gray.get(10, 20))

    def test_mmap_numpy_to_boof_F32(self):
        np_gray = np.random.random((100, 120)).astype(np.float32)
        pb_gray = pb.mmap_numpy_to_boof_F32(np_gray)

        self.assertEqual(np_gray.shape[0], pb_gray.getHeight())
        self.assertEqual(np_gray.shape[1], pb_gray.getWidth())

        self.assertAlmostEqual(np_gray[0, 0], pb_gray.get(0, 0))
        self.assertAlmostEqual(np_gray[20, 10], pb_gray.get(10, 20))

    def test_mmap_numpy_to_boof_IU8(self):
        np_img = np.random.randint(0,256, size=(100, 120, 3), dtype=np.uint8)
        pb_img = pb.mmap_numpy_to_boof_IU8(np_img)

        self.assertEqual(np_img.shape[0], pb_img.getHeight())
        self.assertEqual(np_img.shape[1], pb_img.getWidth())
        self.assertEqual(np_img.shape[2], pb_img.getNumBands())

        self.assertEqual(np_img[0, 0, 0], pb_img.getBand(0, 0, 0))
        self.assertEqual(np_img[20, 10, 0], pb_img.getBand(10, 20, 0))
        self.assertEqual(np_img[20, 10, 1], pb_img.getBand(10, 20, 1))
        self.assertEqual(np_img[20, 10, 2], pb_img.getBand(10, 20, 2))

    def test_mmap_boof_to_numpy_U8(self):
        pb_img = pb.create_single_band(100, 120, dtype=np.uint8)
        pb.fill_uniform(pb_img, 0, 200)
        np_img = pb.mmap_boof_to_numpy_U8(pb_img)

        self.assertEqual(np_img.dtype, np.uint8)
        self.assertEqual(np_img.shape[0], pb_img.getHeight())
        self.assertEqual(np_img.shape[1], pb_img.getWidth())

        self.assertAlmostEqual(np_img[0, 0], pb_img.get(0, 0))
        self.assertAlmostEqual(np_img[20, 10], pb_img.get(10, 20))

    def test_mmap_boof_to_numpy_F32(self):
        pb_img = pb.create_single_band(100, 120, dtype=np.float32)
        pb.fill_uniform(pb_img, -2, 2)
        np_img = pb.mmap_boof_to_numpy_F32(pb_img)

        self.assertEqual(np_img.dtype, np.float32)
        self.assertEqual(np_img.shape[0], pb_img.getHeight())
        self.assertEqual(np_img.shape[1], pb_img.getWidth())

        self.assertAlmostEqual(np_img[0, 0], pb_img.get(0, 0))
        self.assertAlmostEqual(np_img[20, 10], pb_img.get(10, 20))

    def test_mmap_boof_PU8_to_numpy_IU8(self):
        pb_img = pb.create_planar(100, 120, 3,dtype=np.uint8)
        pb.fill_uniform(pb_img, -2, 2)
        np_img = pb.mmap_boof_PU8_to_numpy_IU8(pb_img)

        self.assertEqual(np_img.dtype, np.uint8)
        self.assertEqual(np_img.shape[0], pb_img.getHeight())
        self.assertEqual(np_img.shape[1], pb_img.getWidth())
        self.assertEqual(np_img.shape[2], pb_img.getNumBands())

        self.assertEqual(np_img[0, 0, 0]  , pb_img.getBand(0).get(0, 0))
        self.assertEqual(np_img[20, 10, 0], pb_img.getBand(0).get(10, 20))
        self.assertEqual(np_img[20, 10, 1], pb_img.getBand(1).get(10, 20))
        self.assertEqual(np_img[20, 10, 2], pb_img.getBand(2).get(10, 20))

if __name__ == '__main__':
    unittest.main()
