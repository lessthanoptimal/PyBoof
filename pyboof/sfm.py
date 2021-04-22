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
        if not self.java_obj.process(java_list):
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


class StitchingFromMotion2D(JavaWrapper):
    def __init__(self, java_object, image_type): # Remove when getImageType() is added
        JavaWrapper.__init__(self, java_object)
        self.image_type = image_type

    def configure(self, mosaic_width:int, mosaic_height:int, scale:float = 1.0 ):

        # Hard code it to scale the iamge down and start in the center
        homography = JavaWrapper(gateway.jvm.georegression.struct.homography.Homography2D_F64())
        homography.a11 = scale
        homography.a22 = scale
        homography.a13 = mosaic_width/2 - (scale*mosaic_width/2)
        homography.a23 = mosaic_height/2 - (scale*mosaic_height/2)
        homography = JavaWrapper(homography.java_obj.invert(None))
        self.java_obj.configure(mosaic_width, mosaic_height, homography.java_obj)

    def process(self, image):
        return self.java_obj.process(image)

    def reset(self):
        self.java_obj.reset()

    def set_origin_to_current(self):
        self.java_obj.setOriginToCurrent()

    def get_stitched_image(self):
        return self.java_obj.getStitchedImage()

    def get_image_type(self):
        return self.image_type


class FactoryMultiViewRobust:
    def __init__(self):
        pass

    @staticmethod
    def baseline_ransac(config_essential, config_ransac):
        """
        Estimates the stereo baseline (SE3) between two images.

        :param config_essential:
        :type config_essential: ConfigEssentialMatrix
        :param config_ransac:
        :type config_ransac: ConfigRansac
        :return:
        :rtype: ModelMatcherMultiview
        """
        mm = gateway.jvm.boofcv.factory.geo.FactoryMultiViewRobust. \
            baselineRansac(config_essential.java_obj, config_ransac.java_obj)
        return ModelMatcherMultiview(mm)


class FactoryVideoMosaic:
    def __init__(self, dtype):
        self.boof_image_class = dtype_to_Class_SingleBand(dtype)
        # TODO remove when getImageType() is added
        self.image_type = create_ImageType(Family.PLANAR, dtype, 3)

    def mosaic(self, config_tracker:pyboof.ConfigPointTracker):
        java_object = gateway.jvm.pyboof.FactoryPyBoofTemp. \
            basicVideoMosaic(config_tracker.java_obj, self.boof_image_class)
        return StitchingFromMotion2D(java_object, self.image_type)