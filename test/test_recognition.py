#!/usr/bin/env python3

import unittest

import pyboof as pb
import numpy as np


class ChecksRecognitionFunctions(unittest.TestCase):
    def test_string_to_bytearray(self):
        integers = [0, 1, 2, 3, 4, 100, 120, 180, 200, 201, 225, 255]
        str = bytearray(integers).decode('latin-1')
        found = pb.string_to_bytearray(str)
        for i in range(len(found)):
            self.assertEqual(integers[i], found[i])


class ChecksFactoryFiducialCalibration(unittest.TestCase):
    """
    Test factory function calls to see if they crash.
    """

    def test_chessboardX(self):
        config_detector = pb.ConfigChessboardX()
        config_target = pb.ConfigGridDimen(5, 6, 0.30)

        pb.FactoryFiducialCalibration.chessboardX(config_target, config_detector)
        pb.FactoryFiducialCalibration.chessboardX(config_target)

    def test_chessboardB(self):
        config_detector = pb.ConfigChessboardBinary()
        config_target = pb.ConfigGridDimen(5, 6, 0.30)

        pb.FactoryFiducialCalibration.chessboardB(config_target, config_detector)
        pb.FactoryFiducialCalibration.chessboardB(config_target)

    def test_ecocheck(self):
        config_detector = pb.ConfigECoCheckDetector()
        config_target = pb.ecocheck_parse("5x4n2", 2.0)

        pb.FactoryFiducialCalibration.ecocheck(config_target, config_detector)
        pb.FactoryFiducialCalibration.ecocheck(config_target)

    def test_square_grid(self):
        config_detector = pb.ConfigSquareGrid()
        config_target = pb.ConfigGridDimen(5, 6, 0.30)

        pb.FactoryFiducialCalibration.square_grid(config_target, config_detector)

    def test_circle_hexagonal_grid(self):
        config_detector = pb.ConfigCircleHexagonalGrid()
        config_target = pb.ConfigGridDimen(5, 6, 0.30)

        pb.FactoryFiducialCalibration.circle_hexagonal_grid(config_target, config_detector)

    def test_circle_regular_grid(self):
        config_detector = pb.ConfigCircleRegularGrid()
        config_target = pb.ConfigGridDimen(5, 6, 0.30)

        pb.FactoryFiducialCalibration.circle_regular_grid(config_target, config_detector)


class ChecksFactoryFiducial(unittest.TestCase):
    """
    Test factory function calls to see if they crash.
    """

    def test_square_image(self):
        config_detector = pb.ConfigFiducialImage()
        config_threshold = pb.ConfigThreshold.create_fixed(50.0)
        pb.FactoryFiducial(np.uint8).square_image(config_detector, config_threshold)

    def test_square_binary(self):
        config_detector = pb.ConfigFiducialBinary()
        config_threshold = pb.ConfigThreshold.create_fixed(50.0)
        pb.FactoryFiducial(np.uint8).square_binary(config_detector, config_threshold)

    def test_square_hamming(self):
        config_marker = pb.load_hamming_marker(pb.HammingDictionary.ARUCO_ORIGINAL)
        pb.FactoryFiducial(np.uint8).square_hamming(config_marker)

    def test_chessboardB(self):
        config_target = pb.ConfigGridDimen(5, 6, 0.30)
        config_detector = pb.ConfigChessboardBinary()
        pb.FactoryFiducial(np.uint8).chessboardB(config_target, config_detector)

    def test_chessboardX(self):
        config_target = pb.ConfigGridDimen(5, 6, 0.30)
        config_detector = pb.ConfigChessboardX()
        pb.FactoryFiducial(np.uint8).chessboardX(config_target, config_detector)

    def test_square_grid(self):
        config_target = pb.ConfigGridDimen(5, 6, 0.30)
        config_detector = pb.ConfigSquareGrid()
        pb.FactoryFiducial(np.uint8).square_grid(config_target, config_detector)

    def test_qrcode(self):
        config_detector = pb.ConfigQrCode()
        pb.FactoryFiducial(np.uint8).qrcode(config_detector)

    def test_microqrcode(self):
        config_detector = pb.ConfigMicroQrCode()
        pb.FactoryFiducial(np.uint8).microqr(config_detector)

    def test_random_dots(self):
        config_detector = pb.ConfigUchiyaMarker()
        config_detector.markerWidth = 5.0
        config_detector.markerHeight = 5.0
        pb.FactoryFiducial(np.uint8).random_dots(config_detector)


class ChecksFactorySceneRecognition(unittest.TestCase):
    """
    Test factory function calls to see if they crash.
    """

    def test_scene_recognition(self):
        config = pb.ConfigFeatureToSceneRecognition()
        pb.FactorySceneRecognition(np.uint8).scene_recognition(config)


if __name__ == '__main__':
    unittest.main()
