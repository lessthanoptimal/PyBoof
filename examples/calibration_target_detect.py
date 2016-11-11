import pyboof as pb
import numpy as np
import os
import cv2

# Demonstration of how to detect points in a calibration target


pb.init_memmap()

data_path = "../data/example/calibration/stereo/Bumblebee2_Chess/"

print "Configuring and creating a chessboard detector"
config = pb.ConfigFiducialChessboard(num_rows=5, num_cols=7, square_width=0.3)
detector = pb.FactoryFiducialCalibration.chessboard(config)

print "Detecting image"
image = pb.load_single_band(os.path.join(data_path, "left01.jpg"), np.float32)
detector.detect(image)

print "Detected points {}".format(len(detector.detected_points))

# Convert it into a color image for visualization purposes
ndimage = pb.boof_to_ndarray(image).astype(np.uint8)
ndimage = cv2.cvtColor(ndimage, cv2.COLOR_GRAY2RGB)

# Draw green dots with red outlines
for x in detector.detected_points:
    # x[0] is index of the control point
    # x[1] and x[2] is the (x,y) pixel coordinate, sub-pixel precision
    cv2.circle(ndimage, (int(x[1]), int(x[2])), 7, (0, 0, 255), -1)
    cv2.circle(ndimage, (int(x[1]), int(x[2])), 5, (0, 255, 0), -1)

cv2.imshow('Detected Control Points', ndimage)

print "Select Window and Press Any Key"
while cv2.getWindowProperty('Detected Control Points', 0) >= 0:
    if cv2.waitKey(50) != -1:
        break

cv2.destroyAllWindows()
