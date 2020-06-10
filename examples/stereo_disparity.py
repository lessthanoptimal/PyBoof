#!/usr/bin/env python3

import numpy as np
import math

# pip install matplotlib

import matplotlib.pyplot as plt
import pyboof as pb

# Enable use of memory mapped files for MUCH faster conversion between some python and boofcv data types
pb.init_memmap(5)

# Load two images
image0 = pb.load_single_band("../data/example/stereo/chair01_left.jpg", np.uint8)
image1 = pb.load_single_band("../data/example/stereo/chair01_right.jpg", np.uint8)

# Load stereo rectification
stereo_param = pb.StereoParameters()
stereo_param.load("../data/example/calibration/stereo/Bumblebee2_Chess/stereo.yaml")

# Rectify and undistort the images
model_rectifier = pb.StereoRectification(stereo_param.left, stereo_param.right, stereo_param.right_to_left)
model_rectifier.all_inside_left()

distort_left = model_rectifier.create_distortion(pb.ImageType(image0.getImageType()), True)
distort_right = model_rectifier.create_distortion(pb.ImageType(image0.getImageType()), False)

rect0 = image0.createSameShape()
rect1 = image1.createSameShape()

distort_left.apply(image0, rect0)
distort_right.apply(image1, rect1)

# Configure and compute disparity
config = pb.ConfigDisparityBMBest5()
config.disparityMin = 10
config.disparityRange = 50
config.errorType = pb.DisparityError.CENSUS

factory = pb.FactoryStereoDisparity(np.uint8)

disparityAlg = factory.block_match_best5(config)

disparityAlg.process(rect0, rect1)

disparity_image = pb.boof_to_ndarray(disparityAlg.get_disparity_image())
# disparity images is in a weird format.  disparity - min disparity and a value more than range if invalid
# legacy from 8bit disparity images
disparity_image[:] += config.disparityMin
disparity_image[disparity_image > 60] = float('nan')

# plt.imshow(disparity_image)
# plt.show()

# Apply the usual equation to convert disparity into a 3D cloud
baseline = stereo_param.right_to_left.T.norm()
K = model_rectifier.rectK  # rectified camera intrinsic calibration
# TODO convert to python ndarray
fx = K.get(0, 0)
fy = K.get(1, 1)
cx = K.get(0, 2)
cy = K.get(1, 2)

cloud_xyz = []
cloud_rgb = []

# Convert the BoofCV image into a Python image to speed things up a bit since data transfer is slow
rect0 = pb.boof_to_ndarray(rect0)

for row in range(0, disparity_image.shape[0]):
    for col in range(0, disparity_image.shape[1]):
        d = disparity_image[row, col]
        if math.isnan(d) or d < 1.0:
            continue

        # Color at this pixel
        gray_value = np.uint8(rect0[row, col])
        rgb = gray_value << 24 | gray_value << 16 | gray_value

        # Compute the 3D cloud
        Z = baseline * fx / d
        X = Z * (col - cx) / fx
        Y = Z * (row - cy) / fy

        # Add to output
        cloud_xyz.append((X, Y, Z))
        cloud_rgb.append(rgb)

# TODO show the colorized point cloud

print("Done!")
