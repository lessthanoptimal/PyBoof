#!/usr/bin/env python3

import pyboof as pb
import numpy as np
import os
import glob

# Demonstration of how to calibrate a stereo camera
pb.init_memmap()

data_path = "../data/example/calibration/stereo/Zed_ecocheck/"

print("Configuring and creating a chessboard detector")
config_ecocheck = pb.ecocheck_parse("9x7n1", square_size=0.3)
detector = pb.FactoryFiducialCalibration.ecocheck(config_ecocheck)

print("Detecting calibration targets")
files_left = sorted(glob.glob(os.path.join(data_path, "left*.jpg")))
files_right = sorted(glob.glob(os.path.join(data_path, "right*.jpg")))

observations_left = []
observations_right = []
for file_left, file_right in zip(files_left, files_right):
    # left image
    image = pb.load_single_band(file_left, np.float32)
    detector.detect(image)
    o = {"width": image.getWidth(),
         "height": image.getHeight()}
    if detector.detected_markers:
        print("success " + file_left)
        o["pixels"] = detector.detected_markers[0]["landmarks"]
    else:
        o["pixels"] = []
    observations_left.append(o)

    # right image
    image = pb.load_single_band(file_right, np.float32)
    detector.detect(image)
    o = {"width": image.getWidth(),
         "height": image.getHeight()}
    if detector.detected_markers:
        print("success " + file_right)
        o["pixels"] = detector.detected_markers[0]["landmarks"]
    else:
        o["pixels"] = []
    observations_right.append(o)

print("Solving for stereo parameters")

stereo_parameters, errors = pb.calibrate_stereo(
    observations_left, observations_right, detector, num_radial=4, tangential=False)

print()
print("Average Error {:.3f} pixels".format(sum([x["mean"] for x in errors]) / len(errors)))
print(str(stereo_parameters))
