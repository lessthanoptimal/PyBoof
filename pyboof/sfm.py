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
        self.minimum_size = java_object.getMinimumSize()

    def process(self, data_set):
        # TODO use type information (not available yet) to convert the dataset.
        java_list = pyboof.p2b_list_AssociatedPair(data_set)
        self.java_obj.process( java_list )

        # TODO convert model based on model type info
        self.model_parameters = pyboof.Se3_F64(self.java_obj.getModelParameters())
        self.match_set = pyboof.b2p_list_AssociatedPair(self.getMatchSet())
        self.input_indexes = [0]*len(self.match_set)
        for i in range(len(self.input_indexes)):
            self.input_indexes[i] = self.java_obj.getInputIndex(i)
        self.fit_quality = self.java_obj.getFitQuality()


class FactoryMultiViewRobust:
    def __init__(self):
        pass

    @staticmethod
    def essentialRansac(configEssential, configRansac):
        """

        :param configEssential:
        :type configEssential: ConfigEssentialMatrix
        :param configRansac:
        :type configRansac: ConfigRansac
        :return:
        :rtype: ModelMatcher
        """
        mm = gateway.jvm.boofcv.factory.geo.FactoryMultiViewRobust. \
            essentialRansac(configEssential.java_obj, configRansac.java_obj)
        return ModelMatcher(mm)
