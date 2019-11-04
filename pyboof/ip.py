from pyboof import gateway

from pyboof.image import dtype_to_Class_SingleBand
from pyboof.image import ImageType
from pyboof.geo import *
from py4j.java_gateway import is_instance_of


class Border:
    SKIP=0
    EXTENDED=1
    NORMALIZED=2
    REFLECT=3
    WRAP=4
    ZERO=5


class GradientType:
    SOBEL="sobel"
    PREWITT="prewitt"
    THREE="three"
    TWO0="two0"
    TWO1="two1"


class ThresholdType:
    FIXED          = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.FIXED
    GLOBAL_ENTROPY = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.GLOBAL_ENTROPY
    GLOBAL_OTSU    = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.GLOBAL_OTSU
    LOCAL_GAUSSIAN = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.LOCAL_GAUSSIAN
    LOCAL_MEAN     = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.LOCAL_MEAN
    LOCAL_OTSU     = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.LOCAL_OTSU
    LOCAL_SAVOLA   = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.LOCAL_SAVOLA
    BLOCK_MIN_MAX  = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.BLOCK_MIN_MAX
    BLOCK_MEAN     = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.BLOCK_MEAN
    BLOCK_OTSU     = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.BLOCK_OTSU


class InterpolationType:
    NEAREST_NEIGHBOR = 0
    BILINEAR = 1
    BICUBIC = 2
    POLYNOMIAL4 = 3
    INTEGRAL = 4


class ConfigThreshold(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self,"boofcv.factory.filter.binary.ConfigThreshold")

    @staticmethod
    def create_fixed(threshold):
        java_object = gateway.jvm.boofcv.factory.filter.binary.ConfigThreshold.fixed(float(threshold))
        return JavaConfig(java_object)

    @staticmethod
    def create_global(threshold_type):
        java_object = gateway.jvm.pyboof.PyBoofEntryPoint.createGlobalThreshold(threshold_type)
        return JavaConfig(java_object)

    @staticmethod
    def create_local(threshold_type, radius):
        java_object = gateway.jvm.boofcv.factory.filter.binary.ConfigThreshold.local(threshold_type, int(radius))
        return JavaConfig(java_object)


def interpolation_type_to_java(interp_type):
    """
    Converts PyBoof interpolation type into BoofCV java object
    :param interp_type: Which interpolation method to use
    :type interp_type: int
    :return: BoofCV interpolation type
    """
    if interp_type == InterpolationType.NEAREST_NEIGHBOR:
        return gateway.jvm.boofcv.alg.interpolate.InterpolationType.NEAREST_NEIGHBOR
    elif interp_type == InterpolationType.BICUBIC:
        return gateway.jvm.boofcv.alg.interpolate.InterpolationType.BICUBIC
    elif interp_type == InterpolationType.BILINEAR:
        return gateway.jvm.boofcv.alg.interpolate.InterpolationType.BILINEAR
    elif interp_type == InterpolationType.POLYNOMIAL4:
        return gateway.jvm.boofcv.alg.interpolate.InterpolationType.POLYNOMIAL4
    elif interp_type == InterpolationType.INTEGRAL:
        raise RuntimeError("Integral is a special case and can't be handled the same way")
    else:
        raise RuntimeError("Unknown interpolation type")


def border_to_java(border):
    """

    :param border:
    :type border: Border
    :return: java_object
    """
    if border == Border.SKIP:
        return gateway.jvm.boofcv.struct.border.BorderType.valueOf("SKIP")
    elif border == Border.EXTENDED:
        return gateway.jvm.boofcv.struct.border.BorderType.valueOf("EXTENDED")
    elif border == Border.NORMALIZED:
        return gateway.jvm.boofcv.struct.border.BorderType.valueOf("NORMALIZED")
    elif border == Border.REFLECT:
        return gateway.jvm.boofcv.struct.border.BorderType.valueOf("REFLECT")
    elif border == Border.WRAP:
        return gateway.jvm.boofcv.struct.border.BorderType.valueOf("WRAP")
    elif border == Border.ZERO:
        return gateway.jvm.boofcv.struct.border.BorderType.valueOf("ZERO")


def blur_gaussian(image, output, sigma=-1.0,radius=1):
    gateway.jvm.boofcv.alg.filter.blur.BlurImageOps.gaussian(image, output, sigma, radius, None)


def blur_mean(image, output, radius=1):
    gateway.jvm.boofcv.alg.filter.blur.BlurImageOps.mean(image, output, radius, None, None)


def blur_median(image, output, radius=1):
    gateway.jvm.boofcv.alg.filter.blur.BlurImageOps.median(image, output, radius, None)


def shrink_image(image, output_size, interp_type=InterpolationType.INTEGRAL, output=None):
    """
    Shrinks the image using the specified interpolation method.  If the change in scale is larger than a factor
    of two then integral should be used.  Otherwise bilinear should be sufficient.
    :param image: Input image.
    :param output_size: Size of output image.  If a single value then this is the size of the largest axis
    :type output_size: int or (int,int)
    :param interp_type: Interpolation type
    :type interp_type: InterpolationType
    :param output: Optional storage for output image.  Will be resized
    :return: The shrunk image
    """

    if isinstance(output_size, (int, int)):
        scale = float(output_size) / max(image.getWidth(), image.getHeight())
        output_shape = (int(image.getHeight()*scale), int(image.getWidth()*scale))
    else:
        output_shape = output_size

    if image.getWidth() < output_shape[1] or image.getHeight() < output_shape[0]:
        raise RuntimeError("Either width or height is larger in output than input")

    if output is None:
        output = image.createNew(output_shape[1], output_shape[0])
    else:
        output.reshape(output_shape[1], output_shape[0])

    if interp_type == InterpolationType.INTEGRAL:
        gateway.jvm.boofcv.alg.filter.misc.AverageDownSampleOps.down(image, output)
    else:
        scale_x = output_shape[1] / float(image.getWidth())
        scale_y = output_shape[0] / float(image.getHeight())

        fdist = gateway.jvm.boofcv.abst.distort.FDistort(image, output)
        fdist.interp(interpolation_type_to_java(interp_type))
        fdist.affine(scale_x, 0.0, 0.0, scale_y, 0.0, 0.0)
        fdist.apply()

    return output


def gradient(input, derivX, derivY, gradient_type=GradientType.SOBEL, border_type=Border.EXTENDED):
    java_border = border_to_java(border_type)
    java_DerivativeOps = gateway.jvm.boofcv.alg.filter.derivative.GImageDerivativeOps
    java_DerivativeType = gateway.jvm.boofcv.alg.filter.derivative.DerivativeType
    if gradient_type is GradientType.SOBEL:
        java_DerivativeOps.gradient(java_DerivativeType.SOBEL,input,derivX,derivY,java_border)
    elif gradient_type is GradientType.PREWITT:
        java_DerivativeOps.gradient(java_DerivativeType.PREWITT,input,derivX,derivY,java_border)
    elif gradient_type is GradientType.THREE:
        java_DerivativeOps.gradient(java_DerivativeType.THREE,input,derivX,derivY,java_border)
    elif gradient_type is GradientType.TWO0:
        java_DerivativeOps.gradient(java_DerivativeType.TWO_0,input,derivX,derivY,java_border)
    elif gradient_type is GradientType.TWO1:
        java_DerivativeOps.gradient(java_DerivativeType.TWO_1,input,derivX,derivY,java_border)
    else:
        raise RuntimeError("Unknown gradient type " + gradient_type)


class Transform2to2(JavaWrapper):
    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)
        if is_instance_of(gateway, java_object, gateway.jvm.boofcv.struct.distort.Point2Transform2_F32):
            self.is32 = True
            self.point_out = create_java_point_2D_f32()
        elif is_instance_of(gateway, java_object, gateway.jvm.boofcv.struct.distort.Point2Transform2_F64):
            self.is32 = False
            self.point_out = create_java_point_2D_f64()
        else:
            raise RuntimeError("Unexpected java object. "+java_object.getClass().getSimpleName())

    def apply(self, input):
        self.java_obj.compute(float(input[0]), float(input[1]), self.point_out)
        return self.point_out.getX(), self.point_out.getY()


class Transform2to3(JavaWrapper):
    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)
        if is_instance_of(gateway, java_object, gateway.jvm.boofcv.struct.distort.Point2Transform3_F32):
            self.is32 = True
            self.point_out = create_java_point_3D_f32()
        elif is_instance_of(gateway, java_object, gateway.jvm.boofcv.struct.distort.Point2Transform3_F64):
            self.is32 = False
            self.point_out = create_java_point_3D_f64()
        else:
            raise RuntimeError("Unexpected java object. "+java_object.getClass().getSimpleName())

    def apply(self, input):
        self.java_obj.compute(float(input[0]), float(input[1]), self.point_out)
        return self.point_out.getX(), self.point_out.getY(), self.point_out.getZ()


class Transform3to2(JavaWrapper):
    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)
        if is_instance_of(gateway, java_object, gateway.jvm.boofcv.struct.distort.Point3Transform2_F32):
            self.is32 = True
            self.point_out = create_java_point_2D_f32()
        elif is_instance_of(gateway, java_object, gateway.jvm.boofcv.struct.distort.Point3Transform2_F64):
            self.is32 = False
            self.point_out = create_java_point_2D_f64()
        else:
            raise RuntimeError("Unexpected java object. "+java_object.getClass().getSimpleName())

    def apply(self, input, output=None):
        if output is None:
            output = [0.0, 0.0]
        self.java_obj.compute(float(input[0]), float(input[1]), float(input[2]), self.point_out)
        output[0] = self.point_out.getX()
        output[1] = self.point_out.getY()
        return output


class ImageDistort(JavaWrapper):
    """
    Applies a distortion to a BoofCV image.
    Wrapper around BoofCV ImageDistort class
    """

    def __init__(self, boof_ImageDistort):
        JavaWrapper.__init__(self, boof_ImageDistort)

    def apply(self, imageA , imageB ):
        self.java_obj.apply(imageA,imageB)


class InputToBinary(JavaWrapper):

    def __init__(self, java_object):
        self.set_java_object(java_object)

    def process(self, input , output):
        self.java_obj.process(input, output)


class FactoryThresholdBinary:
    def __init__(self, dtype ):
        self.boof_image_type = dtype_to_Class_SingleBand(dtype)

    def localGaussian(self, region_width, scale=0.95, down=True):
        """
        Create an instance of local gaussian threshold

        :param region_width: Width of local region
        :type region_width: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            localGaussian(region_width,float(scale),down,self.boof_image_type)
        return InputToBinary(java_object)

    def localSauvola(self, region_width, k=0.3, down=True):
        """
        Create an instance of local gaussian threshold

        :param region_width: Width of local region
        :type region_width: int
        :param k: User specified threshold adjustment factor.  Must be positive. Try 0.3
        :type k: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            localSauvola(region_width,down,float(k),self.boof_image_type)
        return InputToBinary(java_object)

    def localMean(self, region_width, scale=0.95, down=True):
        """
        Create an instance of local square threshold

        :param region_width: Width of local region
        :type region_width: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            localMean(region_width,float(scale),down,self.boof_image_type)
        return InputToBinary(java_object)

    def localNick(self, region_width, down=True, k=-0.1):
        """
        Create an instance of local square threshold

        :param region_width: Width of local region
        :type region_width: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            localNick(region_width,down,float(k),self.boof_image_type)
        return InputToBinary(java_object)

    def localOtsu(self, region_width, scale=0.95, down=True, otsu2 = False, tuning=0):
        """
        Create an instance of local otsu threshold

        :param region_width: Width of local region
        :type radius: int
        :param region_width: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :param otsu2: True to use the otsu2 variant
        :type otsu2: bool
        :param tuning: Tuning parameter. 0 = standard Otsu. Greater than 0 will penalize zero texture.
        :type tuning: int
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            localOtsu(otsu2,region_width,float(tuning),float(scale),down,self.boof_image_type)
        return InputToBinary(java_object)

    def blockMinMax(self, region_width, scale=0.95, down=True, minimumSpread=-1.0,thresholdFromLocalBlocks=True):
        """
        Applies a very fast non-overlapping block thresholding algorithm which uses min/max statistics

        :param region_width: Width of local region
        :type region_width: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :param minimumSpread: If the difference between min max is less than or equal to this  value then it is
        considered textureless.  Set to <= -1 to disable.
        :type minimumSpread: float
        :param thresholdFromLocalBlocks: Should it use the local 3x3 block region
        :type thresholdFromLocalBlocks: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            blockMinMax(region_width, float(scale), down, thresholdFromLocalBlocks, float(minimumSpread), self.boof_image_type)
        return InputToBinary(java_object)

    def blockMean(self, region_width, scale=0.95, down=True,thresholdFromLocalBlocks=True):
        """
        Create an instance of block square threshold

        :param region_width: Width of local region
        :type region_width: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :param thresholdFromLocalBlocks: Should it use the local 3x3 block region
        :type thresholdFromLocalBlocks: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            blockMean(region_width,float(scale),down,thresholdFromLocalBlocks,self.boof_image_type)
        return InputToBinary(java_object)

    def blockOtsu(self, region_width, scale=0.95, down=True, otsu2 = False, tuning=0,thresholdFromLocalBlocks=True):
        """
        Create an instance of block otsu threshold

        :param region_width: Width of local region
        :type radius: int
        :param region_width: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :param otsu2: True to use the otsu2 variant
        :type otsu2: bool
        :param tuning: Tuning parameter. 0 = standard Otsu. Greater than 0 will penalize zero texture.
        :type tuning: int
        :param thresholdFromLocalBlocks: Should it use the local 3x3 block region
        :type thresholdFromLocalBlocks: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        region_width = boof_fixed_length(region_width)

        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            blockOtsu(region_width,float(scale),down,thresholdFromLocalBlocks,otsu2,float(tuning),self.boof_image_type)
        return InputToBinary(java_object)

    def globalEntropy(self, min_value=0, max_value=255, scale=0.95, down=True):
        """
        Applies a global entropy based threshold to the entire image.

        :param min_value: Minimum pixel value.
        :type min_value: int
        :param max_value: Maximum pixel value
        :type min_value: int
        :param down: True for thresholding down and false for up
        :type down: bool:
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            globalEntropy(int(min_value), int(max_value), float(scale), down, self.boof_image_type)
        return InputToBinary(java_object)

    def globalLi(self, min_value=0, max_value=255, scale=0.95, down=True):
        """
        Implements Li's Minimum Cross Entropy thresholding method

        :param min_value: Minimum pixel value.
        :type min_value: int
        :param max_value: Maximum pixel value
        :type min_value: int
        :param down: True for thresholding down and false for up
        :type down: bool:
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            globalLi(float(min_value), float(max_value), float(scale), down, self.boof_image_type)
        return InputToBinary(java_object)

    def globalHuang(self, min_value=0, max_value=255, scale=0.95, down=True):
        """
        Implements Huang's fuzzy thresholding method

        :param min_value: Minimum pixel value.
        :type min_value: int
        :param max_value: Maximum pixel value
        :type min_value: int
        :param down: True for thresholding down and false for up
        :type down: bool:
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary. \
            globalHuang(float(min_value), float(max_value), float(scale), down, self.boof_image_type)
        return InputToBinary(java_object)

    def globalFixed(self, threshold, down=True):
        """
        Applies a fixed threshold to the entire image.

        :param min_value: Minimum pixel value.
        :type min_value: int
        :param max_value: Maximum pixel value
        :type min_value: int
        :param down: True for thresholding down and false for up
        :type down: bool:
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            globalFixed(float(threshold),down,self.boof_image_type)
        return InputToBinary(java_object)

    def globalOtsu(self, min_value=0, max_value=255, scale=0.95, down=True):
        """
        Computes the Otsu threshold and applies it to the entire image.

        :param min_value: Minimum pixel value.
        :type min_value: int
        :param max_value: Maximum pixel value
        :type min_value: int
        :param down: True for thresholding down and false for up
        :type down: bool:
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            globalOtsu(float(min_value), float(max_value), float(scale), down, self.boof_image_type)
        return InputToBinary(java_object)
    
    def threshold(self, config ):
        """
        Creates an instance of InputToBinary from a configuration class for a specific method
        :param config: Config class for a
        :type config: ConfigThreshold
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            threshold(config.java_obj,self.boof_image_type)
        return InputToBinary(java_object)


class FactoryInterpolation:
    def __init__(self, image_type ):
        """

        :param image_type:
        :type image_type: ImageType
        """
        self.image_type = image_type

    def bilinear(self, min_pixel=0, max_pixel=255, border_type=Border.ZERO):
        """
        :param min_pixel:
        :type min_pixel: float
        :param max_pixel:
        :type max_pixel: float
        :param border_type:
        :type border_type: Border
        :return: java_object
        """
        java_border = border_to_java(border_type)
        java_interp = interpolation_type_to_java(InterpolationType.BILINEAR)

        return gateway.jvm.boofcv.factory.interpolate.FactoryInterpolation.\
            createPixel(float(min_pixel), float(max_pixel), java_interp, java_border, self.image_type.java_obj)
