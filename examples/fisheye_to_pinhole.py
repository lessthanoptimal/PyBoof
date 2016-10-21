import pyboof as pb
import numpy as np
import os
import cv2

data_path = "./"

model_pinhole = pb.CameraPinhole()
model_pinhole.set_image_shape(600, 600)
model_pinhole.set_matrix(400, 400, 0, 300, 300)

model_fisheye = pb.CameraUniversalOmni()
model_fisheye.load(os.path.join(data_path, "fisheye.yaml"))

transform = pb.NarrowToWideFovPtoP(narrow_model=model_pinhole,wide_model=model_fisheye)

image_fisheye = pb.load_planar(os.path.join(data_path, "building_side.jpg"), np.uint8)
image_pinhole = image_fisheye.createNew(model_pinhole.width, model_pinhole.height)

image_distorter = transform.create_image_distort(pb.ImageType(image_fisheye.getImageType()))

image_distorter.apply(image_fisheye, image_pinhole)

cv2.imshow("Fisheye", pb.boof_to_ndarray(image_fisheye))
cv2.imshow("Pinhole", pb.boof_to_ndarray(image_pinhole))

# Rotate the image some how
# transform.set_rotation_wide_to_narrow()

print "Press Any Key"
cv2.waitKey(0)
