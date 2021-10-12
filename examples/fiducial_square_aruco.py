#!/usr/bin/env python3

import pyboof as pb
import numpy as np
import os

# This example shows you how to detect hamming type markers. This family of markers includes ArUco and AprilTags.
# These are all binary patterns surrounded by a black square. The matching marker is found by decoding the pattern
# then seeing which Id is the closest match by minimizing hamming distance.

data_path = "../data/example/fiducial/square_hamming/aruco_25h7"

# Load the camera parameters
intrinsic = pb.CameraPinhole()
intrinsic.load(os.path.join(data_path, "intrinsic.yaml"))

# Load a pre-built dictionary
config_marker = pb.load_hamming_marker(pb.HammingDictionary.ARUCO_MIP_25h7)

# Tweak the detector. None class be passed in for the detector
config_detector = pb.ConfigFiducialHammingDetector()
config_detector.configThreshold.type = pb.ThresholdType.LOCAL_MEAN

print("Creating the detector")
detector = pb.FactoryFiducial(np.uint8).square_hamming(config_marker, config_detector)

print("Detecting image")
detector.detect(pb.load_single_band(os.path.join(data_path, "image01.jpg"), np.uint8))

print("Number Found = " + str(detector.get_total()))

for i in range(detector.get_total()):
    print("=========== Found #" + str(i))
    fid_to_cam = detector.get_fiducial_to_camera(i)
    print("Pattern ID = " + str(detector.get_id(i)))
    print("Image Location " + str(detector.get_center(i)))
    if detector.is_3d():
        print("Rotation")
        print("  " + str(fid_to_cam.get_rotation()))
        print("Translation")
        print("  " + str(fid_to_cam.get_translation()))
