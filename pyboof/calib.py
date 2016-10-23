from image import *
from ip import *
from geo import real_nparray_to_ejml
from abc import ABCMeta, abstractmethod


class CameraModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, file_name):
        pass

    @abstractmethod
    def save(self, file_name):
        pass

    @abstractmethod
    def set_from_boof(self, boof_intrinsic):
        pass

    @abstractmethod
    def convert_to_boof(self, storage=None):
        pass


# TODO Turn this into JavaConfig instead?
class CameraPinhole(CameraModel):
    """
    BoofCV Intrinsic Camera parameters
    """
    def __init__(self):
        # Intrinsic calibration matrix
        self.fx = 0
        self.fy = 0
        self.skew = 0
        self.cx = 0
        self.cy = 0
        # image shape
        self.width = 0
        self.height = 0
        # radial distortion
        self.radial = None
        # tangential terms
        self.t1 = 0
        self.t2 = 0

    def load(self, file_name):
        file_path = os.path.abspath(file_name)
        boof_intrinsic = gateway.jvm.boofcv.io.calibration.CalibrationIO.load(file_path)

        if boof_intrinsic is None:
            raise RuntimeError("Can't load intrinsic parameters")

        self.set_from_boof(boof_intrinsic)

    def save(self, file_name):
        file_path = os.path.abspath(file_name)
        java_obj = self.convert_to_boof()
        gateway.jvm.boofcv.io.calibration.CalibrationIO.save(java_obj, file_path)

    def set_matrix(self, fx, fy, skew, cx, cy):
        self.fx = fx
        self.fy = fy
        self.skew = skew
        self.cx = cx
        self.cy = cy

    def set_image_shape(self, width, height):
        self.width = width
        self.height = height

    def set_distortion(self, radial=None, t1=0, t2=0):
        """
        Sets distortion values

        :param radial: Radial distortion
        :type radial: [float] or None
        :param t1: Tangential distortion
        :type t1: float
        :param t2:  Tangential distortion
        :type t2: float
        """
        self.radial = radial
        self.t1 = t1
        self.t2 = t2

    def set(self, orig):
        self.fx = orig.fx
        self.fy = orig.fy
        self.skew = orig.skew
        self.cx = orig.cx
        self.cy = orig.cy
        self.width = orig.width
        self.height = orig.height
        self.radial = orig.radial
        self.t1 = orig.t1
        self.t2 = orig.t2

    def set_from_boof(self, boof_intrinsic):
        self.fx = boof_intrinsic.getFx()
        self.fy = boof_intrinsic.getFy()
        self.cx = boof_intrinsic.getCx()
        self.cy = boof_intrinsic.getCy()
        self.skew = boof_intrinsic.getSkew()
        self.width = boof_intrinsic.getWidth()
        self.height = boof_intrinsic.getHeight()
        jarray = boof_intrinsic.getRadial()
        if jarray is None:
            self.radial = None
        else:
            self.radial = [float(x) for x in jarray]
        self.t1 = boof_intrinsic.getT1()
        self.t2 = boof_intrinsic.getT2()

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraPinholeRadial()
        else:
            boof_intrinsic = storage
        boof_intrinsic.setFx(float(self.fx))
        boof_intrinsic.setFy(float(self.fy))
        boof_intrinsic.setCx(float(self.cx))
        boof_intrinsic.setCy(float(self.cy))
        boof_intrinsic.setSkew(float(self.skew))
        boof_intrinsic.setWidth(int(self.width))
        boof_intrinsic.setHeight(int(self.height))
        if self.radial is not None:
            jarray = gateway.new_array(gateway.jvm.double, len(self.radial))
            for i in range(len(self.radial)):
                jarray[i] = self.radial[i]
            boof_intrinsic.setRadial(jarray)
        boof_intrinsic.setT1(float(self.t1))
        boof_intrinsic.setT2(float(self.t2))
        return boof_intrinsic

    def is_distorted(self):
        return (self.radial is not None) or self.t1 != 0 or self.t2 != 0

    def __str__(self):
        out = "Intrinsic{{ fx={:f} fy={:f} skew={:f} cx={:f} cy={:f} | width={:d} height={:d} ".\
            format(self.fx,self.fy,self.skew,self.cx,self.cy,self.width,self.height)
        if self.is_distorted():
            out += " | radial="+str(self.radial)+" t1="+str(self.t1)+" t1="+str(self.t2)+" }"
        else:
            out += "}}"
        return out


class CameraUniversalOmni(CameraPinhole):
    def __init__(self):
        CameraPinhole.__init__(self)
        self.mirror_offset = 0

    def set_from_boof(self, boof_intrinsic):
        CameraPinhole.set_from_boof(self, boof_intrinsic)
        self.mirror_offset = boof_intrinsic.getMirrorOffset()

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraUniversalOmni(0)
        else:
            boof_intrinsic = storage
        CameraPinhole.convert_to_boof(self, boof_intrinsic)
        boof_intrinsic.setMirrorOffset(float(self.mirror_offset))
        return boof_intrinsic


class LensNarrowDistortionFactory(JavaWrapper):
    def __init__(self, java_object, use_32=True):
        JavaWrapper.__init__(self, java_object)
        self.use_32 = use_32

    def distort(self, pixel_in, pixel_out):
        """

        :param pixel_in:
        :type pixel_in: bool
        :param pixel_out:
        :type pixel_in: bool
        :return: Point2Transform2_F32 or Point2Transform2_F64
        """
        if self.use_32:
            java_out = self.java_obj.distort_F32(pixel_in, pixel_out)
        else:
            java_out = self.java_obj.distort_F64(pixel_in, pixel_out)
        return Transform2to2(java_out)

    def undistort(self, pixel_in, pixel_out):
        """

        :param pixel_in:
        :type pixel_in: bool
        :param pixel_out:
        :type pixel_in: bool
        :return: Point2Transform2_F32 or Point2Transform2_F64
        """
        if self.use_32:
            java_out = self.java_obj.undistort_F32(pixel_in, pixel_out)
        else:
            java_out = self.java_obj.undistort_F32(pixel_in, pixel_out)
        return Transform2to2(java_out)

class LensWideDistortionFactory(JavaWrapper):
    def __init__(self, java_object, use_32=True):
        JavaWrapper.__init__(self, java_object)
        self.use_32 = use_32

    def distort_s_to_p(self):
        """
        Transform from unit sphere coordinates to pixel coordinates
        :return: transform
        :rtype: Transform3to2
        """
        if self.use_32:
            java_out = self.java_obj.distortStoP_F32()
        else:
            java_out = self.java_obj.distortStoP_F64()
        return Transform3to2(java_out)

    def undistort_p_to_s(self):
        """
        Transform from pixels to unit sphere coordinates
        :return: transform
        :rtype: Transform2to3
        """
        if self.use_32:
            java_out = self.java_obj.undistortPtoS_F32()
        else:
            java_out = self.java_obj.undistortPtoS_F64()
        return Transform2to3(java_out)


def create_narrow_lens_distorter( camera_model ):
    """

    :param camera_model:
    :return:
    :rtype: LensNarrowDistortionFactory
    """
    if isinstance(camera_model, CameraUniversalOmni):
        raise RuntimeError("CameraUniversalOmni is not a narrow FOV camera model")
    elif isinstance(camera_model, CameraPinhole):
        boof_model = camera_model.convert_to_boof()
        if camera_model.is_distorted():
            java_obj = gateway.jvm.boofcv.alg.distort.radtan.LensDistortionRadialTangential(boof_model)
        else:
            java_obj = gateway.jvm.boofcv.alg.distort.pinhole.LensDistortionPinhole(boof_model)
    else:
        raise RuntimeError("Unknown camera model {}".format(type(camera_model)))

    return LensNarrowDistortionFactory(java_obj)

def create_wide_lens_distorter( camera_model ):
    """

    :param camera_model:
    :return:
    :rtype: LensWideDistortionFactory
    """
    if isinstance(camera_model, CameraUniversalOmni):
        boof_model = camera_model.convert_to_boof()
        java_obj = gateway.jvm.boofcv.alg.distort.universal.LensDistortionUniversalOmni(boof_model)
    else:
        raise RuntimeError("Unknown camera model {}".format(type(camera_model)))

    return LensWideDistortionFactory(java_obj)


class NarrowToWideFovPtoP(JavaWrapper):
    """
    Distortion for converting an image from a wide FOV camera (e.g. fisheye) into a narrow FOV camera (e.g. pinhole)
    Mathematically it performs a conversion from pixels in the narrow camera to the wide camera.  The center of
    focus for the narrow camera can be changed by rotating the view by invoking set_rotation_wide_to_narrow().

    """
    def __init__(self, narrow_model, wide_model):
        """
        Constructor where camera models are specified

        :param narrow_model: Camera model for narrow FOV camera
        :type narrow_model: CameraModel
        :param wide_model: Camera model for wide FOV camera
        :type wide_model: CameraModel
        """
        narrow_distort = create_narrow_lens_distorter(narrow_model)
        wide_distort = create_wide_lens_distorter(wide_model)
        java_object = gateway.jvm.boofcv.alg.distort.NarrowToWidePtoP_F32(narrow_distort.java_obj, wide_distort.java_obj)
        JavaWrapper.__init__(self, java_object)

    def set_rotation_wide_to_narrow(self, rotation_matrix):
        """
        Used to change the principle axis of the narrow FOC camera by rotating the view

        :param rotation_matrix: 3D rotation matrix
        :return:
        """
        self.java_obj.setRotationWideToNarrow( real_nparray_to_ejml(rotation_matrix) )
        pass

    def create_image_distort(self, image_type, border_type=Border.ZERO):
        """

        :param image_type:
        :type image_type: ImageType
        :param border_type:
        :type border_type: Border
        :return: The image distort based on this transformation
        :rtype: ImageDistort
        """
        java_image_type = image_type.java_obj
        java_interp = FactoryInterpolation(image_type).bilinear(border_type=border_type)

        java_alg = gateway.jvm.boofcv.factory.distort.FactoryDistort.distort(False, java_interp, java_image_type)
        java_pixel_transform = gateway.jvm.boofcv.alg.distort.PointToPixelTransform_F32(self.java_obj)
        java_alg.setModel(java_pixel_transform)
        return ImageDistort(java_alg)


class AdjustmentType:
    NONE=0
    FULL_VIEW=1
    EXPAND=2


def adjustment_to_java(value):
    if value == AdjustmentType.NONE:
        return gateway.jvm.boofcv.alg.distort.AdjustmentType.valueOf("NONE")
    elif value == AdjustmentType.FULL_VIEW:
        return gateway.jvm.boofcv.alg.distort.AdjustmentType.valueOf("FULL_VIEW")
    elif value == AdjustmentType.EXPAND:
        return gateway.jvm.boofcv.alg.distort.AdjustmentType.valueOf("EXPAND")
    else:
        raise RuntimeError("Unknown type")


def remove_distortion(input, output, intrinsic, adjustment=AdjustmentType.FULL_VIEW, border=Border.ZERO):
    image_type = ImageType(input.getImageType())
    distorter, java_intrinsic_out = create_remove_lens_distortion(intrinsic,image_type,adjustment,border)
    distorter.apply(input,output)
    intrinsic_out = CameraPinhole()
    intrinsic_out.set_from_boof(java_intrinsic_out)
    return intrinsic_out


def create_remove_lens_distortion( intrinsic, image_type, adjustment=AdjustmentType.FULL_VIEW, border=Border.ZERO):
    java_image_type = image_type.get_java_object()
    java_adjustment = adjustment_to_java(adjustment)
    java_border = border_to_java(border)
    java_intrinsic = intrinsic.convert_to_boof()
    java_intrinsic_out = gateway.jvm.boofcv.struct.calib.CameraPinholeRadial()
    id =  gateway.jvm.boofcv.alg.distort.LensDistortionOps.imageRemoveDistortion(java_adjustment,java_border,java_intrinsic,java_intrinsic_out,java_image_type)
    return [ImageDistort(id),java_intrinsic_out]