import numpy as np

import pyboof as pb

data_path = "../data/example/calibration/stereo/Bumblebee2_Chess/"

# Load the camera parameters
intrinsic = pb.Intrinsic()
intrinsic.load_xml(data_path+"intrinsicLeft.yaml")

# Load original image and the undistorted image
original = pb.load_single_band(data_path+"left08.jpg", np.uint8)
undistorted = original.createSameShape()

# Remove distortion and show the results
pb.remove_distortion(original, undistorted, intrinsic)
image_list = [(original, "Original"), (undistorted, "Undistorted")]
pb.swing.show_list(image_list, title="Lens Distortion")

raw_input("Press any key to exit")
