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


class ModelMatcherMultiview(ModelMatcher):
    def __init__(self, java_object):
        ModelMatcher.__init__(self, java_object)

    def set_intrinsic(self, view:int , intrinsic:CameraPinhole ):
        """
        Specifies intrinsic parameters for each view

        :param view: Index of the view
        :param intrinsic: Intrinsic camera parameters
        """
        self.java_obj.setIntrinsic(view,intrinsic.convert_to_boof())

    def get_number_of_views(self):
        """
        The number of views which need to have camera parameters specified
        """
        return self.java_obj.getNumberOfViews()

        return True


class FactoryMultiViewRobust:
    def __init__(self):
        pass

    @staticmethod
    def baselineRansac(configEssential, configRansac):
        """
        Estimates the stereo baseline (SE3) between two images.

        :param configEssential:
        :type configEssential: ConfigEssentialMatrix
        :param configRansac:
        :type configRansac: ConfigRansac
        :return:
        :rtype: ModelMatcherMultiview
        """
        mm = gateway.jvm.boofcv.factory.geo.FactoryMultiViewRobust. \
            baselineRansac(configEssential.java_obj, configRansac.java_obj)
        return ModelMatcherMultiview(mm)
