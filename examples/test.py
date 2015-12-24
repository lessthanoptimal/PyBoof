import numpy as np
from pyboof.image import *
from pyboof.feature import ConfigSurfFast,ConfigFastHessian
from pyboof.feature import FactoryDetectDescribe
from pyboof.feature import java_list_to_python
from pyboof.feature import read_list
import pyboof as pb
import time

original = pb.load_single_band('../data/example/outdoors01.jpg',np.uint8)

c = ConfigSurfFast()
d = ConfigFastHessian()
# d.extractRadius = 4
# d.maxFeaturesPerScale = 200

detector = FactoryDetectDescribe(np.uint8).createSurf(config_detect=d,config_desc=c)

before = time.time()
print "Start detect"
locations,descriptions = detector.detect(original)
print "End detect "+str(time.time()-before)

print "Total found = {} {}".format(locations.size(),descriptions.size())

before = time.time()
python_lists = java_list_to_python(locations)
after = time.time()

print "Took {} seconds to convert point list".format(after-before)

before = time.time()
descriptions.save_to_disk("raw_desc_file.data")
after = time.time()

print "Took {} seconds to save descriptions list".format(after-before)

before = time.time()
read_list("raw_desc_file.data")
after = time.time()

print "Took {} seconds to read descriptions list".format(after-before)

# before = time.time()
# python_descriptions = java_list_to_python(descriptions)
# after = time.time()
#
# print "Took {} seconds to convert descriptions list".format(after-before)