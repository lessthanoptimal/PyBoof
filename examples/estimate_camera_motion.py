#!/usr/bin/env python3

import numpy as np

import pyboof as pb
from pyboof.swing import visualize_matches

# Load two images and camera calibration
image0 = pb.load_single_band("../data/example/stereo/mono_wall_01.jpg", np.uint8)
image1 = pb.load_single_band("../data/example/stereo/mono_wall_02.jpg", np.uint8)
intrinsic = pb.CameraPinhole().load("../data/example/calibration/mono/Sony_DSC-HX5V_Chess/intrinsic.yaml")

# Set up the SURF fast hessian feature detector.  Reduce the number of features it will detect by putting a limit
# on how close two features can be and the maximum number at each scale
config_fh = pb.ConfigFastHessian()
config_fh.extractRadius = 4
config_fh.maxFeaturesPerScale = 300

# Create the detector and use default for everything else
feature_detector = pb.FactoryDetectDescribe(np.uint8).createSurf(config_detect=config_fh)

# Detect features in the first image
locs0, desc0 = feature_detector.detect(image0)
locs1, desc1 = feature_detector.detect(image1)

print("Detected {:4d} features in image 0".format(len(desc0)))
print("         {:4d}             image 1".format(len(desc1)))

config_greedy = pb.ConfigAssociateGreedy()
config_greedy.forwardsBackwards = True
config_greedy.scoreRatioThreshold = 0.95
factory_association = pb.FactoryAssociate()
factory_association.set_score(pb.AssocScoreType.DEFAULT, feature_detector.get_descriptor_type())
associator = factory_association.greedy(config_greedy)

associator.set_source(desc0)
associator.set_destination(desc1)
matches = associator.associate()

print("Associated {} features".format(len(matches)))

# Convert matches into a format that's understood by model estimator
associated_pairs_pixels = pb.match_idx_to_point_pairs(matches, locs0, locs1)

# Convert from pixel to normalized image coordinates
p2n = pb.create_narrow_lens_distorter(intrinsic).undistort(pixel_in=True, pixel_out=False)
associated_pairs_norm = []
for a in associated_pairs_pixels:
    n0=p2n.apply(a[0])
    n1=p2n.apply(a[1])
    associated_pairs_norm.append((n0, n1))

# Robustly estimate the essential matrix using RANSAC
confE = pb.ConfigEssentialMatrix()
confRansac = pb.ConfigRansac()
confRansac.iterations = 200
confRansac.inlierThreshold = 0.5 # Units = pixels

model_matcher = pb.FactoryMultiViewRobust.baselineRansac(confE, confRansac)

# Same camera took both images. Specifies camera parameters for each view
model_matcher.set_intrinsic(0, intrinsic)
model_matcher.set_intrinsic(1, intrinsic)

if not model_matcher.process(associated_pairs_norm):
    print("Failed!")
    exit(1)

camera_motion = model_matcher.model_parameters

print("Inlier Size ", len(model_matcher.match_set))
print("Motion")
print( camera_motion)