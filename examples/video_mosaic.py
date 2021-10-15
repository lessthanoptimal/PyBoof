#!/usr/bin/env python3

import numpy as np
import time
import cv2

import pyboof as pb

# Use OpenCV to capture images
cap = cv2.VideoCapture('../data/example/mosaic/airplane01.mjpeg')
window_name = "Video Mosaic"

# Configure it to use KLT. There are a ton of options. We will stick the defaults that should work well at 640x480
config_tracker = pb.ConfigPointTracker()
config_tracker.klt.toleranceFB = 10.0
config_tracker.klt.templateRadius = 5
# TODO use SURF tracker for this example as it will be more stable

video_mosaic = pb.FactoryVideoMosaic(np.uint8).mosaic(config_tracker)

video_mosaic.configure(1000, 500, scale=0.5)

image_input = video_mosaic.get_image_type().create_boof_image(0, 0)

boof_color = None
while True:
    # Capture sequence frame-by-frame
    ret, frame = cap.read()

    # Convert it into a boofcv image
    boof_color = pb.ndarray_to_boof(frame, boof_color)
    # Convert it into the image type required by the tracker
    pb.convert_boof_image(boof_color, image_input)

    # Track the point objects
    time0 = time.time() * 1000.0
    if not video_mosaic.process(image_input):
        print("mosaic failed!")
        video_mosaic.reset()
        continue
    time1 = time.time() * 1000.0

    # Get the mosaic image and display the results
    boof_mosaic = video_mosaic.get_stitched_image()
    ndarray_mosaic = pb.boof_to_ndarray(boof_mosaic)

    cv2.imshow("Video Mosaic", ndarray_mosaic)

    print("mosaic: {:6.2f} ms".format(time1 - time0))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
