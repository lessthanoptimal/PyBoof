import cv2
import pyboof as pb
import numpy as np
import time

# Enable use of memory mapped files for MUCH faster conversion of images between java and python
pb.init_memmap(5)

# Use OpenCV to capture images
cap = cv2.VideoCapture(0)

refPt=[(0,0),(0,0)]
state = 0
quad = pb.Quadrilateral2D()
window_name = "Frame"

cv2.namedWindow(window_name)

# Call back for handling clicks inside the image window
def click_rect(event, x, y, flags, param):
    global refPt, state

    # Click and drag a rectangle
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y),(x,y)]
        state = 1
    elif event == 0:
        refPt[1] = (x,y)
    elif event == cv2.EVENT_LBUTTONUP:
        if abs(refPt[0][0]-refPt[1][0]) <= 5 or abs(refPt[0][1]-refPt[1][1]) <= 5:
            state = 0
        else:
            state = 2

# Creates a quadrilateral from the clicked points
def pts_to_quad():
    global refPt, quad
    quad.a.set((refPt[0][0],refPt[0][1]))
    quad.b.set((refPt[1][0],refPt[0][1]))
    quad.c.set((refPt[1][0],refPt[1][1]))
    quad.d.set((refPt[0][0],refPt[1][1]))

cv2.setMouseCallback(window_name, click_rect)

# Switch trackers by commenting and uncommenting a line.
tracker = pb.FactoryTrackerObjectQuad(np.uint8).tld(pb.ConfigTld(False))
# tracker = pb.FactoryTrackerObjectQuad(np.uint8).circulant()
# color_type = pb.create_ImageType(pb.Family.PLANAR,np.uint8,3)
# tracker = pb.FactoryTrackerObjectQuad(color_type).mean_shift_comaniciu()

# initialize data structures
ret, frame = cap.read()
if not ret:
    print "Failed to read frame"
    exit(-1)

image_input = tracker.get_image_type().create_boof_image(frame.shape[1], frame.shape[0])
boof_color = None

while True:
    # Capture sequence frame-by-frame
    ret, frame = cap.read()

    time0 = int(round(time.time() * 1000))
    # Convert it into a boofcv image
    boof_color = pb.ndarray_to_boof(frame, boof_color)
    time1 = int(round(time.time() * 1000))
    # Convert it into the image type required by the tracker
    pb.convert_boof_image(boof_color,image_input)
    time2 = int(round(time.time() * 1000))

    time_tracking = 0

    if state == 1:
        cv2.rectangle(frame, refPt[0], refPt[1], (100, 100, 255), 4)
    elif state == 2:
        pts_to_quad()
        if not tracker.initialize(image_input,quad):
            print "Initialization failed!"
            state = 0
        else:
            print "Success"
            state = 3
    elif state == 3:
        time3 = int(round(time.time() * 1000))
        if not tracker.process(image_input,quad):
            print "Tracking failed!"
        else:
            lines =  np.array(quad.get_tuple_tuple())
            cv2.polylines(frame,np.int32([lines]),True,(0, 0, 255),4)
        time4 = int(round(time.time() * 1000))
        time_tracking = time4-time3

    # Print how fast each part runs
    print "py to boof: {:4d} boof to boof: {:4d}  tracking: {:4d}".\
        format(time1 - time0, time2 - time1, time_tracking)

    # Display the resulting frame
    cv2.imshow(window_name, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()