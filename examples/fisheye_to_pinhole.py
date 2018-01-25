import pyboof as pb
import numpy as np
import os
import cv2
import transforms3d.euler # pip install transforms3d

pb.init_memmap(5)

data_path = "../data/example/fisheye/theta/"

model_pinhole = pb.CameraPinhole()
model_pinhole.set_image_shape(450, 450)
model_pinhole.set_matrix(250, 250, 0, 300, 300)

model_fisheye = pb.CameraUniversalOmni()
model_fisheye.load(os.path.join(data_path, "front.yaml"))

transform = pb.NarrowToWideFovPtoP(narrow_model=model_pinhole,wide_model=model_fisheye)

image_fisheye = pb.load_planar(os.path.join(data_path, "front_hike.jpg"), np.uint8)
image_pinhole = image_fisheye.createNew(model_pinhole.width, model_pinhole.height)

image_distorter = transform.create_image_distort(pb.ImageType(image_fisheye.getImageType()))

image_distorter.apply(image_fisheye, image_pinhole)

# Make the fisheye image smaller so that it's easier to manage
small_fisheye = cv2.resize(pb.boof_to_ndarray(image_fisheye),None,fx=0.5, fy=0.5, interpolation = cv2.INTER_LINEAR)

cv2.imshow("Fisheye", small_fisheye[...,[2,1,0]])
cv2.imshow("Pinhole", pb.boof_to_ndarray(image_pinhole)[...,[2,1,0]])

# Rotate the camera so that it's focused on the path behind and rotated to appear "up"
transform.set_rotation_wide_to_narrow(transforms3d.euler.euler2mat(-0.1,-0.4,-1.7,axes='sxyz'))
image_distorter.apply(image_fisheye, image_pinhole)
cv2.imshow("Pinhole Rotated", pb.boof_to_ndarray(image_pinhole)[...,[2,1,0]])

print("Close Windows to Exit")
cv2.waitKey(0)
