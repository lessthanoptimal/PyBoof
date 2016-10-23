from pyboof import gateway

from image import dtype_to_Class_SingleBand
from image import ImageType
from geo import *
from py4j.java_gateway import is_instance_of


class Border:
    SKIP=0,
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
    LOCAL_SQUARE   = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.LOCAL_SQUARE
    LOCAL_SAVOLA   = gateway.jvm.boofcv.factory.filter.binary.ThresholdType.LOCAL_SAVOLA


class InterpolationType:
    NEAREST_NEIGHBOR=0,
    BILINEAR=1,
    BICUBIC=2,
    POLYNOMIAL4=3


class ConfigThreshold(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self,"boofcv.factory.filter.binary.ConfigThreshold")

    @staticmethod
    def create_fixed( threshold ):
        java_object = gateway.jvm.boofcv.factory.filter.binary.ConfigThreshold.fixed(float(threshold))
        return JavaConfig(java_object)

    @staticmethod
    def create_global( type ):
        java_object = gateway.jvm.pyboof.PyBoofEntryPoint.createGlobalThreshold(type)
        return JavaConfig(java_object)

    @staticmethod
    def create_local( type , radius ):
        java_object = gateway.jvm.boofcv.factory.filter.binary.ConfigThreshold.local(type,int(radius))
        return JavaConfig(java_object)


def interpolation_type_to_java( type ):
    if type == InterpolationType.NEAREST_NEIGHBOR:
        return gateway.jvm.boofcv.alg.interpolate.TypeInterpolate.NEAREST_NEIGHBOR
    elif type == InterpolationType.BICUBIC:
        return gateway.jvm.boofcv.alg.interpolate.TypeInterpolate.BICUBIC
    elif type == InterpolationType.BILINEAR:
        return gateway.jvm.boofcv.alg.interpolate.TypeInterpolate.BILINEAR
    elif type == InterpolationType.POLYNOMIAL4:
        return gateway.jvm.boofcv.alg.interpolate.TypeInterpolate.POLYNOMIAL4
    else:
        raise RuntimeError("Unknown interpolation type")


def border_to_java( border ):
    """

    :param border:
    :type border: Border
    :return: java_object
    """
    if border == Border.SKIP:
        return gateway.jvm.boofcv.core.image.border.BorderType.valueOf("SKIP")
    elif border == Border.EXTENDED:
        return gateway.jvm.boofcv.core.image.border.BorderType.valueOf("EXTENDED")
    elif border == Border.NORMALIZED:
        return gateway.jvm.boofcv.core.image.border.BorderType.valueOf("NORMALIZED")
    elif border == Border.REFLECT:
        return gateway.jvm.boofcv.core.image.border.BorderType.valueOf("REFLECT")
    elif border == Border.WRAP:
        return gateway.jvm.boofcv.core.image.border.BorderType.valueOf("WRAP")
    elif border == Border.ZERO:
        return gateway.jvm.boofcv.core.image.border.BorderType.valueOf("ZERO")


def blur_gaussian(input,output,sigma=-1.0,radius=1):
    gateway.jvm.boofcv.alg.filter.blur.BlurImageOps.gaussian(input,output,sigma,radius,None)

def blur_mean(input,output,radius=1):
    gateway.jvm.boofcv.alg.filter.blur.BlurImageOps.mean(input,output,radius,None)

def blur_median(input,output,radius=1):
    gateway.jvm.boofcv.alg.filter.blur.BlurImageOps.median(input,output,radius,None)


def gradient(input, derivX , derivY, type=GradientType.SOBEL, border=Border.EXTENDED):
    java_border = border_to_java(border)
    java_DerivativeOps = gateway.jvm.boofcv.alg.filter.derivative.GImageDerivativeOps
    java_DerivativeType = gateway.jvm.boofcv.alg.filter.derivative.DerivativeType
    if type is GradientType.SOBEL:
        java_DerivativeOps.gradient(java_DerivativeType.SOBEL,input,derivX,derivY,java_border)
    elif type is GradientType.PREWITT:
        java_DerivativeOps.gradient(java_DerivativeType.PREWITT,input,derivX,derivY,java_border)
    elif type is GradientType.THREE:
        java_DerivativeOps.gradient(java_DerivativeType.THREE,input,derivX,derivY,java_border)
    elif type is GradientType.TWO0:
        java_DerivativeOps.gradient(java_DerivativeType.TWO_0,input,derivX,derivY,java_border)
    elif type is GradientType.TWO1:
        java_DerivativeOps.gradient(java_DerivativeType.TWO_1,input,derivX,derivY,java_border)
    else:
        raise RuntimeError("Unknown gradient type "+type)


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

    def apply(self, input, output=None):
        if output is None:
            output = [0.0, 0.0]
        self.java_obj.compute(float(input[0]), float(input[1]), self.point_out)
        output[0] = self.point_out.getX()
        output[1] = self.point_out.getY()
        return output


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

    def apply(self, input, output=None):
        if output is None:
            output = [0.0, 0.0, 0.0]
        self.java_obj.compute(float(input[0]), float(input[1]), self.point_out)
        output[0] = self.point_out.getX()
        output[1] = self.point_out.getY()
        output[2] = self.point_out.getZ()
        return output


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
        self.java_obj.process(input,output)


class FactoryThresholdBinary:
    def __init__(self, dtype ):
        self.boof_image_type =  dtype_to_Class_SingleBand(dtype)

    def localGaussian(self, radius, scale=0.95, down=True):
        """
        Create an instance of local gaussian threshold

        :param radius: Radius of local region
        :type radius: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            localGaussian(int(radius),float(scale),down,self.boof_image_type)
        return InputToBinary(java_object)

    def localSauvola(self, radius, k=0.3, down=True):
        """
        Create an instance of local gaussian threshold

        :param radius: Radius of local region
        :type radius: int
        :param k: User specified threshold adjustment factor.  Must be positive. Try 0.3
        :type k: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            localSauvola(int(radius),float(k),down,self.boof_image_type)
        return InputToBinary(java_object)

    def localSquare(self, radius, scale=0.95, down=True):
        """
        Create an instance of local square threshold

        :param radius: Radius of local region
        :type radius: int
        :param scale: Threshold scale adjustment
        :type scale: float
        :param down: True for thresholding down and false for up
        :type down: bool
        :return: New instance of InputToBinary
        :rtype: InputToBinary
        """
        java_object = gateway.jvm.boofcv.factory.filter.binary.FactoryThresholdBinary.\
            localSquare(int(radius),float(scale),down,self.boof_image_type)
        return InputToBinary(java_object)

    def globalEntropy(self, min_value=0, max_value=255, down=True):
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
            globalEntropy(int(min_value),int(max_value),down,self.boof_image_type)
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

    def globalOtsu(self, min_value=0, max_value=255, down=True):
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
            globalOtsu(int(min_value),int(max_value),down,self.boof_image_type)
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
