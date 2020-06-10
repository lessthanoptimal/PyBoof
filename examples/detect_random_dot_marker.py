#!/usr/bin/env python3

import pyboof as pb
import numpy as np
import os

data_path = "../data/example/fiducial/random_dots/"

# Enable use of memory mapped files for MUCH faster conversion between some python and boofcv data types
pb.init_memmap()

# Load marker descriptions
defs = pb.load_random_dot_yaml(os.path.join(data_path, "descriptions.yaml"))

# Create the detector
config = pb.ConfigUchiyaMarker()
config.markerLength = defs.markerWidth
detector = pb.FactoryFiducial(np.uint8).random_dots(config)

# Load / learn all the markers. This can take a few seconds if there are a lot of markers
for marker in defs.markers:
    detector.add_marker(marker)

# Load the image and process it
gray_image = pb.load_single_band(os.path.join(data_path, "image02.jpg"), np.uint8)
detector.detect(gray_image)

# Print out the location of found markers
for i in range(detector.get_total()):
    print("=========== Found #{}".format(i))
    fid_to_cam = detector.get_fiducial_to_camera(i)
    print("Pattern ID = "+str(detector.get_id(i)))
    print("Image Location " + str(detector.get_center(i)))
    if detector.is_3d():
        print("Rotation")
        print("  "+str(fid_to_cam.get_rotation()))
        print("Translation")
        print("  "+str(fid_to_cam.get_translation()))

print("Done!")
