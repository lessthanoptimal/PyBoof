import pyboof as pb
import numpy as np
import os

data_path = "../data/example/fiducial/image/examples/"

# Load the camera parameters
intrinsic = pb.CameraPinhole()
intrinsic.load(os.path.join(data_path, "intrinsic.yaml"))

configFiducial = pb.ConfigFiducialImage()
configThreshold = pb.ConfigThreshold.create_local(pb.ThresholdType.LOCAL_SQUARE, 10)

print("Configuring detector")
detector = pb.FactoryFiducial(np.uint8).square_image(configFiducial, configThreshold)
detector.set_intrinsic(intrinsic)
detector.add_pattern(pb.load_single_band(data_path + "../patterns/pentarose.png", np.uint8), side_length=4.0)
detector.add_pattern(pb.load_single_band(data_path + "../patterns/yu.png", np.uint8), side_length=4.0)

print("Detecting image")
detector.detect(pb.load_single_band(os.path.join( data_path, "image00.jpg"), np.uint8))

print("Number Found = "+str(detector.get_total())

for i in range(detector.get_total()):
    print("=========== Found #"+str(i))
    fid_to_cam = detector.get_fiducial_to_camera(i)
    print("Pattern ID = "+str(detector.get_id(i)))
    print("Image Location " + str(detector.get_image_location(i)))
    if detector.is_3d():
        print("Rotation")
        print("  "+str(fid_to_cam.get_rotation()))
        print("Translation"
        print("  "+str(fid_to_cam.get_translation()))
