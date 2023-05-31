#!/usr/bin/env python3

import numpy as np
import cv2

import pyboof as pb

# Use OpenCV to capture images
cap = cv2.VideoCapture(0)
window_name = "Point Tracker"

# Configure it to use KLT. There are a ton of options. We will stick the defaults that should work well at 640x480
config_tracker = pb.ConfigPointTracker()

point_tracker = pb.FactoryPointTracker(np.uint8).generic(config_tracker)

image_input = point_tracker.get_image_type().create_boof_image(0, 0)

boof_color = None
while True:
    # Capture sequence frame-by-frame
    ret, frame = cap.read()
    if not frame.any():
        break

    # Convert it into a boofcv image
    boof_color = pb.ndarray_to_boof(frame, boof_color)
    # Convert it into the image type required by the tracker
    pb.convert_boof_image(boof_color, image_input)

    # Track the point objects
    point_tracker.process(image_input)

    # Spawn new tracks. This will avoid spawning tracks where there are existing tracks
    point_tracker.spawn_tracks()

    # TODO Copying tracks from java to Python is painfully slow. Implement a mmap method
    # Let's visualize the tracks
    active_tracks = point_tracker.get_active_tracks()
    for track in active_tracks:
        x = int(track.pixel[0])
        y = int(track.pixel[1])
        cv2.rectangle(frame, (x - 2, y - 2), (x + 2, y + 2), (100, 100, 255), 4)

    cv2.imshow(window_name, frame)

    print("total tracks {}. WARNING: Very slow now but this can be fixed".format(len(active_tracks)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
