import math
import struct
import pyboof
import numpy as np
import py4j.java_gateway as jg
from pyboof.common import *
from pyboof.calib import *


class ConfigEssentialMatrix(JavaConfig):
    def __init__(self, java_object=None):
        if java_object is None:
            JavaConfig.__init__(self, "boofcv.factory.geo.ConfigEssential")
        else:
            if type(java_object) is CameraPinhole:
                java_object = pyboof.gateway.jvm.boofcv.factory.geo.\
                    ConfigEssential(java_object.convert_to_boof())

            JavaWrapper.__init__(self, java_object)



class ConfigRansac(JavaConfig):
    def __init__(self, java_object=None):
        if java_object is None:
            JavaConfig.__init__(self, "boofcv.factory.geo.ConfigRansac")
        else:
            JavaWrapper.__init__(self, java_object)


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
        if not self.java_obj.process( java_list ):
            return False

        # TODO convert model based on model type info
        self.model_parameters = pyboof.Se3_F64(self.java_obj.getModelParameters())
        self.match_set = pyboof.b2p_list_AssociatedPair(self.java_obj.getMatchSet())
        self.input_indexes = [0]*len(self.match_set)
        for i in range(len(self.input_indexes)):
            self.input_indexes[i] = self.java_obj.getInputIndex(i)
        self.fit_quality = self.java_obj.getFitQuality()

        return True


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
