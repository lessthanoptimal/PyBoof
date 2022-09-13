#!/usr/bin/env python3

import pyboof as pb
import numpy as np
import os
import glob

data_path = "../data/example/calibration/fisheye/chessboard/"

print("Configuring and creating a chessboard detector")
config_grid = pb.ConfigGridDimen(num_rows=5, num_cols=7, square_width=0.3)
detector = pb.FactoryFiducialCalibration.chessboardX(config_grid)

print("Detecting calibration targets")
observations = []

for file in glob.glob(os.path.join(data_path, "*.jpg")):
    image = pb.load_single_band(file, np.float32)
    detector.detect(image)

    if detector.detected_points:
        print("success " + file)
        o = {"pixels": detector.detected_points}
        observations.append(o)
    else:
        print("failed " + file)

print("Solving for intrinsic parameters")

width = image.getWidth()
height = image.getHeight()

# Switch camera model by commenting / uncommenting the two lines below
intrinsic, errors = pb.calibrate_kannala_brandt(width, height, observations, detector, num_symmetric=5, num_asymmetric=2)
# intrinsic,errors = pb.calibrate_universal(width, height, observations, detector, num_radial=2, tangential=True)

print()
print("Average Error {:.3f} pixels".format(sum([x["mean"] for x in errors]) / len(errors)))
print(str(intrinsic))
