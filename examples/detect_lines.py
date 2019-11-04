#!/usr/bin/env python3

import numpy as np

import pyboof as pb
from pyboof.swing import visualize_lines

# Enable use of memory mapped files for MUCH faster conversion between some python and boofcv data types
pb.init_memmap()

# Load an image with strong lines in it
image = pb.load_single_band("../data/example/simple_objects.jpg", np.uint8)
blurred = image.createSameShape()

# Appying a little bit of blur tends to improve the results
pb.blur_gaussian(image, blurred,radius=5)

# There are a few variants of Hough in BoofCV. The variant we will use here uses the image gradient directly
# This is useful you want to find the edges of objects. If you have an image with thin black lines and you want
# to find the lines and not their edges then the binary variant is what you want to use
config_gradient = pb.ConfigHoughGradient(10)

# Detect the lines using several different variants of Hough line detector
results = []

detector = pb.FactoryDetectLine(np.uint8).houghLinePolar(config_hough=config_gradient)
results.append(("Gradient Polar", detector.detect(blurred)))
detector = pb.FactoryDetectLine(np.uint8).houghLineFoot(config_hough=config_gradient)
results.append(("Gradient Foot", detector.detect(blurred)))

# Use swing to visualize the results
visualize_lines(image, results)

input("Press any key to exit")