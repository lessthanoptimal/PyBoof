from image import *
from ip import *


class CameraPinhole:
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
        CameraPinhole.set_from_boof(boof_intrinsic)
        self.mirror_offset = boof_intrinsic.getMirrorOffset()

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraUniversalOmni(0)
        else:
            boof_intrinsic = storage
        CameraPinhole.convert_to_boof(self, boof_intrinsic)
        boof_intrinsic.setMirrorOffset(float(self.mirror_offset))
        return boof_intrinsic


class AdjustmentType:
    NONE=0
    FULL_VIEW=1
    EXPAND=2


def adjustment_to_java( value ):
    if value == AdjustmentType.NONE:
        return gateway.jvm.boofcv.alg.distort.AdjustmentType.valueOf("NONE")
    elif value == AdjustmentType.FULL_VIEW:
        return gateway.jvm.boofcv.alg.distort.AdjustmentType.valueOf("FULL_VIEW")
    elif value == AdjustmentType.EXPAND:
        return gateway.jvm.boofcv.alg.distort.AdjustmentType.valueOf("EXPAND")
    else:
        raise RuntimeError("Unknown type")


def remove_distortion( input, output, intrinsic, adjustment=AdjustmentType.FULL_VIEW, border=Border.ZERO):
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