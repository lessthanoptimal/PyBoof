#!/usr/bin/env python3

import numpy as np

import cv2
import pyboof as pb

image_path = '../data/example/outdoors01.jpg'

# Can load an image using OpenCV then convert it into BoofCV
ndarray_img = cv2.imread(image_path, 0)

boof_cv = pb.ndarray_to_boof(ndarray_img)

# Can also use BoofCV to load the image directly
boof_gray = pb.load_single_band(image_path, np.uint8)
boof_color = pb.load_planar(image_path, np.uint8)

# Let's display all 3 of them in Java
# display the results in a single window as a list
image_list = [(boof_cv, "OpenCV"),
              (boof_gray, "Gray Scale"),
              (boof_color, "Color")]

pb.swing.show_list(image_list, title="Images")

input("Press any key to exit")
