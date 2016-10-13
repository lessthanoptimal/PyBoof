import os

import pyboof
from pyboof import ClassSingleBand_to_dtype
from pyboof import JavaWrapper
from pyboof import dtype_to_Class_SingleBand
from pyboof import gateway


class StereoParameters:
    """
    Calibration parameters for a stereo camera system.
    """
    def __init__(self, java_object = None ):
        self.left = pyboof.Intrinsic()
        self.right = pyboof.Intrinsic()
        self.right_to_left = pyboof.Se3_F64()

        if java_object is not None:
            self.set_from_boof(java_object)

    def load(self, path_to_file ):
        abs_path_to_file = os.path.abspath(path_to_file)
        boof_stereo = gateway.jvm.boofcv.io.UtilIO.loadXML(abs_path_to_file)

        if boof_stereo is None:
            raise RuntimeError("Can't load stereo parameters")

        self.set_from_boof(boof_stereo)

    def set_from_boof(self, boof_stereo_param ):
        self.left.set_from_boof(boof_stereo_param.getLeft())
        self.right.set_from_boof(boof_stereo_param.getRight())
        self.right_to_left = pyboof.Se3_F64(boof_stereo_param.getRightToLeft())

    def convert_to_boof(self):
        boof = gateway.jvm.boofcv.struct.calib.StereoParameters()
        boof.getLeft().set(self.left.convert_to_boof())
        boof.getRight().set(self.right.convert_to_boof())
        boof.getRightToLeft().set(self.right_to_left.java_obj)

class DisparityAlgorithms:
    """
    Types of algorithms available for computing disparity
    """
    RECT = 0,
    FIVE_RECT = 1


class ConfigStereoDisparity:
    def __init__(self):
        # Which algorithm it should use
        self.type = DisparityAlgorithms.FIVE_RECT

        # Minimum disparity that it will check. Must be >= 0 and &lt; maxDisparity
        self.minDisparity = 0
        # Maximum disparity that it will calculate. Must be > 0
        self.maxDisparity = 40
        # Radius of the rectangular region along x-axis.
        self.regionRadiusX = 5
        # Radius of the rectangular region along y-axis.
        self.regionRadiusY = 5
        # Maximum allowed error in a region per pixel.  Set to <= 0 to disable.
        self.maxPerPixelError = 25
        # Tolerance for how difference the left to right associated values can be.
        self.validateRtoL = 1
        # Tolerance for how similar optimal region is to other region.  Closer to zero is more tolerant.
        self.texture = 0.2
        # Should a sub-pixel algorthm be used?
        self.subPixel = True


class StereoRectification:
    """
    Used to compute distortion for rectified stereo images
    """
    def __init__(self, intrinsic_left , intrinsic_right , right_to_left ):
        """
        Configures rectification

        :param intrinsic_left:  Intrinsic parameters for left camera
        :type intrinsic_left: pyboof.Intrinsic
        :param intrinsic_right: Intrinsic parameters for right camera
        :type intrinsic_right: pyboof.Intrinsic
        :param right_to_left: Extrinsic parameters for right to left camera
        :type right_to_left: pyboof.Se3_F64
        """

        boof_left = intrinsic_left.convert_to_boof()
        boof_right = intrinsic_right.convert_to_boof()

        K1 = gateway.jvm.boofcv.alg.geo.PerspectiveOps.calibrationMatrix(boof_left,None)
        K2 = gateway.jvm.boofcv.alg.geo.PerspectiveOps.calibrationMatrix(boof_right,None)
        left_to_right = right_to_left.invert()

        rectify_alg = gateway.jvm.boofcv.alg.geo.RectifyImageOps.createCalibrated()

        rectify_alg.process(K1, pyboof.Se3_F64().java_obj, K2, left_to_right.get_java_object())

        self.intrinsic_left = intrinsic_left
        self.intrinsic_right = intrinsic_right

        self.orig_rect1 = rectify_alg.getRect1()
        self.orig_rect2 = rectify_alg.getRect2()
        self.orig_rectK = rectify_alg.getCalibrationMatrix()

        self.rect1 = self.orig_rect1.copy()
        self.rect2 = self.orig_rect2.copy()
        self.rectK = self.orig_rectK.copy()

    def all_inside_left(self):
        """
        Adjusts the rectification to ensure that there are no dead regions with no pixels.
        """
        self.rect1.set(self.orig_rect1)
        self.rect2.set(self.orig_rect2)
        self.rectK.set(self.orig_rectK)

        boof_left = self.intrinsic_left.convert_to_boof()
        gateway.jvm.boofcv.alg.geo.RectifyImageOps.allInsideLeft(boof_left, self.rect1, self.rect2, self.rectK)

    def full_view_left(self):
        """
        Adjusts the rectification to ensure that the full view (every single pixel) is inside the left camera view
        """
        self.rect1.set(self.orig_rect1)
        self.rect2.set(self.orig_rect2)
        self.rectK.set(self.orig_rectK)

        boof_left = self.intrinsic_left.convert_to_boof()
        gateway.jvm.boofcv.alg.geo.RectifyImageOps.fullViewLeft(boof_left, self.rect1, self.rect2, self.rectK)

    def create_distortion(self, image_type, is_left_image):
        """
        Creates and returns a class for distorting the left image and rectifying it

        :param image_type: Type of image the distortion will process
        :type image_type: pyboof.ImageType
        :param is_left_image: If true the distortion is for the left image if false then the right image
        :type is_left_image: bool
        :return: ImageDistort class
        :rtype: pyboof.ImageDistort
        """
        boof_image_type = image_type.java_obj
        boof_border = pyboof.border_to_java( pyboof.Border.SKIP)

        if is_left_image:
            boof_distorter = gateway.jvm.boofcv.alg.geo.RectifyImageOps.\
                rectifyImage(self.intrinsic_left.convert_to_boof(), self.rect1, boof_border, boof_image_type)
        else:
            boof_distorter = gateway.jvm.boofcv.alg.geo.RectifyImageOps. \
                rectifyImage(self.intrinsic_right.convert_to_boof(), self.rect2, boof_border, boof_image_type)
        return pyboof.ImageDistort(boof_distorter)


class StereoDisparity(JavaWrapper):
    """
    Class which computes the disparity between two stereo images.  Input images are assumed to be already
    rectified.
    """
    def __init__(self, java_object ):
        JavaWrapper.__init__(self, java_object)

    def process(self, image_left, image_right):
        """
        Computes disparity from two images in BoofCV format.  To get results call
        :param image_left: BoofCV image rectified from left camera
        :param image_right: BoofCV image rectified from right camera
        """
        self.java_obj.process(image_left, image_right)

    def get_disparity_image(self):
        """
        Returns the disparity image.

        For pixel level precision a GrayU8 image is returned.  For sub-pixel a GrayF32 is returned.  Disparity
        values have a range of 0 to max-min-1 disparity.  Invalid values are any value above max-min.

        :return: BoofCV GrayU8 or GrayF32
        """
        return self.java_obj.getDisparity()

    def getBorderX(self):
        return self.java_obj.getBorderX()

    def getBorderY(self):
        return self.java_obj.getBorderY()

    def getInputType(self):
        return ClassSingleBand_to_dtype(self.java_obj.getInputType())

    def getDisparityType(self):
        return ClassSingleBand_to_dtype(self.java_obj.getDisparityType())


class FactoryStereoDisparity:
    def __init__(self, dtype ):
        self.boof_image_type =  dtype_to_Class_SingleBand(dtype)

    def region_wta(self, config):
        """
        Creates a rectangular region based winner takes all (wta) stereo disparity algorithm.
        :param config: Configuration for disparity computation
        :type config: pyboof.ConfigStereoDisparity
        :return: StereoDisparity
        :rtype: pyboof.StereoDisparity
        """
        if config is None:
            config = ConfigStereoDisparity()

        if config.type == DisparityAlgorithms.FIVE_RECT:
            alg_type = gateway.jvm.boofcv.factory.feature.disparity.DisparityAlgorithms.RECT_FIVE
        elif config.type == DisparityAlgorithms.RECT:
            alg_type = gateway.jvm.boofcv.factory.feature.disparity.DisparityAlgorithms.RECT
        else:
            raise RuntimeError("Unknown algorithm type")

        if config.subPixel:
            java_obj = gateway.jvm.boofcv.factory.feature.disparity.FactoryStereoDisparity. \
                regionSubpixelWta(alg_type, int(config.minDisparity), int(config.maxDisparity),
                                  int(config.regionRadiusX), int(config.regionRadiusY),float(config.maxPerPixelError),
                                  int(config.validateRtoL), float(config.texture), self.boof_image_type)
        else:
            java_obj = gateway.jvm.boofcv.factory.feature.disparity.FactoryStereoDisparity. \
                regionWta(alg_type, int(config.minDisparity), int(config.maxDisparity),
                          int(config.regionRadiusX), int(config.regionRadiusY), float(config.maxPerPixelError),
                          int(config.validateRtoL), float(config.texture), self.boof_image_type)

        return StereoDisparity(java_obj)

