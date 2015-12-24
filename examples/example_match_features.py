import pyboof as pb
import numpy as np

# Load two images
image0 = pb.load_single_band("../data/example/stitch/cave_01.jpg",np.uint8)
image1 = pb.load_single_band("../data/example/stitch/cave_02.jpg",np.uint8)

# Set up the SURF fast hessian feature detector.  Reduce the number of features it will detect by putting a limit
# on how close two features can be and the maximum number at each scale
config_fh = pb.ConfigFastHessian()
config_fh.extractRadius = 4
config_fh.maxFeaturesPerScale = 300

# Create the detector and use default for everything else
feature_detector = pb.FactoryDetectDescribe(np.uint8).createSurf( config_detect=config_fh)

# Detect features in the first image
locs0,desc0 = feature_detector.detect(image0)
locs1,desc1 = feature_detector.detect(image1)

# IMPORTANT: descriptions and locations above are returned as the PyBoof type JavaList.  This is a hack around py4j
# being insanely slow at converting Java into Python data structures.  It's actually 120x faster to save them to disk
# and load them.  That's exactly what we do in the example showing you how to use PyBoof features with OpenCV.

print "Detected {} features in image 0".format(desc0.size())
print "                        image 1".format(desc1.size())


factory_association = pb.FactoryAssociate()
factory_association.set_score(pb.AssocScoreType.DEFAULT,feature_detector.get_descriptor_type())
associator = factory_association.greedy()

associator.set_source(desc0)
associator.set_destination(desc1)
matches = associator.associate()

print "Associated {} features".format(len(matches))