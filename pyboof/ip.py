from pyboof import gateway

from common import JavaConfig
from common import JavaWrapper
from image import dtype_to_Class_SingleBand


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

def border_to_java( border ):
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

class ImageDistort(JavaWrapper):
    """
    Applies a distortion to a BoofCV image.
    Wrapper around BoofCV ImageDistort class
    """

    def __init__(self, boof_ImageDistort):
        self.set_java_object(boof_ImageDistort)

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