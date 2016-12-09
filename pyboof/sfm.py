import math
import struct
import pyboof
import numpy as np
import py4j.java_gateway as jg
from common import *

class ConfigEssentialMatrix(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.geo.ConfigEssential")

class ConfigRansac(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.geo.ConfigRansac")

class ModelMatcher(JavaWrapper):
    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)
        self.model_parameters = None
        self.match_set = None
        self.input_indexes = []
        self.fit_quality = 0
        self.minimum_size = -1

    def process(self, data_set):
        # TODO use type information (not available yet) to convert the dataset.
        pass


class FactoryMultiViewRobust:
    @staticmethod
    def essentialRansac(configEssential, configRansac):
        pass
