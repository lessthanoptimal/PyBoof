import numpy as np

import pyboof as pb
from pyboof.swing import visualize_matches

# Enable use of memory mapped files for MUCH faster conversion between some python and boofcv data types
pb.init_memmap(5)

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

print "Detected {:4d} features in image 0".format(len(desc0))
print "         {:4d}             image 1".format(len(desc1))

factory_association = pb.FactoryAssociate()
factory_association.set_score(pb.AssocScoreType.DEFAULT, feature_detector.get_descriptor_type())
associator = factory_association.greedy()

associator.set_source(desc0)
associator.set_destination(desc1)
matches = associator.associate()

print "Associated {} features".format(len(matches))

# Convert matches into a format that's understood by model estimator
associated_pairs = pb.match_idx_to_point_pairs(matches, locs0, locs1)

# TODO convert to normalized image coordinates

confE = pb.ConfigEssentialMatrix(intrinsic) # TODo add this
confRansac = pb.ConfigRansac()

model_matcher = pb.FactoryMultiViewRobust.essentialRansac(confE, confRansac)

model_matcher.process(associated_pairs)

camera_motion = model_matcher.model_parameters

print "Motion"
print camera_motion