import pyboof as pb
import numpy as np
import os

data_path = "../data/example/fiducial/binary/"

# Load the camera parameters
intrinsic = pb.CameraPinhole()
intrinsic.load(os.path.join(data_path, "intrinsic.yaml"))

configFiducial = pb.ConfigFiducialBinary(target_width=0.3)
configThreshold = pb.ConfigThreshold.create_local(pb.ThresholdType.LOCAL_SQUARE, 10)

print("Configuring detector")
detector = pb.FactoryFiducial(np.uint8).square_binary(configFiducial, configThreshold)
# Without intrinsics only pattern ID and pixel location can be found
detector.set_intrinsic(intrinsic)

print("Detecting image")
detector.detect(pb.load_single_band(os.path.join(data_path, "image0000.jpg"), np.uint8))

print("Number Found = "+str(detector.get_total())

for i in range(detector.get_total()):
    print("=========== Found #{}".format(i))
    fid_to_cam = detector.get_fiducial_to_camera(i)
    print("Pattern ID = "+str(detector.get_id(i)))
    print("Image Location " + str(detector.get_image_location(i)))
    if detector.is_3d():
        print("Rotation")
        print("  "+str(fid_to_cam.get_rotation())))
        print("Translation")
        print("  "+str(fid_to_cam.get_translation()))
