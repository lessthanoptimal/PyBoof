import math
import struct
import pyboof
import numbers
import numpy as np
import py4j.java_gateway as jg
from pyboof.common import *
from pyboof.ip import *
from pyboof import gateway
from abc import ABCMeta, abstractmethod
import os

def real_ejml_to_nparray(ejml):
    num_rows = ejml.getNumRows()
    num_cols = ejml.getNumCols()

    M = np.zeros((num_rows, num_cols))
    for i in range(num_rows):
        for j in range(num_cols):
            M[i, j] = ejml.unsafe_get(i, j)
    return M


def real_nparray_to_ejml32(array):
    num_rows = array.shape[0]
    num_cols = array.shape[1]

    M = gateway.jvm.org.ejml.data.FMatrixRMaj(num_rows, num_cols)
    for i in range(num_rows):
        for j in range(num_cols):
            M.unsafe_set(i, j, array[i, j])
    return M


def real_nparray_to_ejml64(array):
    num_rows = array.shape[0]
    num_cols = array.shape[1]

    M = gateway.jvm.org.ejml.data.DMatrixRMaj(num_rows, num_cols)
    for i in range(num_rows):
        for j in range(num_cols):
            M.unsafe_set(i, j, array[i, j])
    return M


class Se3_F64(JavaWrapper):
    def __init__(self, java_Se3F64=None):
        if java_Se3F64 is None:
            JavaWrapper.__init__(self, gateway.jvm.georegression.struct.se.Se3_F64())
        else:
            JavaWrapper.__init__(self, java_Se3F64)

    def invert(self):
        return Se3_F64(self.java_obj.invert(None))

    def get_rotation(self):
        return real_ejml_to_nparray(self.java_obj.getR())

    def get_translation(self):
        T = self.java_obj.getT()
        return (T.getX(), T.getY(), T.getZ())


def create_java_point_2D_f32(x=0., y=0.):
    return gateway.jvm.georegression.struct.point.Point2D_F32(float(x), float(y))


def create_java_point_2D_f64(x=0., y=0.):
    return gateway.jvm.georegression.struct.point.Point2D_F64(float(x), float(y))


def create_java_point_3D_f32(x=0., y=0., z=0.):
    return gateway.jvm.georegression.struct.point.Point3D_F32(float(x), float(y), float(z))


def create_java_point_3D_f64(x=0., y=0., z=0.):
    return gateway.jvm.georegression.struct.point.Point3D_F64(float(x), float(y), float(z))


def tuple_to_Point2D_F64(ptuple, jpoint=None):
    if jpoint == None:
        return create_java_point_2D_f32(ptuple[0], ptuple[1])
    else:
        jpoint.set(float(ptuple[0]), float(ptuple[1]))
        return jpoint


def tuple_to_Point2D_F32(ptuple, jpoint=None):
    if jpoint == None:
        return create_java_point_2D_f64(ptuple[0], ptuple[1])
    else:
        jpoint.set(float(ptuple[0]), float(ptuple[1]))
        return jpoint


class Point2D:
    def __init__(self, x=0, y=0):
        """
        :param x: float
            x-coordinate
        :param y: float
            y-coordinate
        """
        if isinstance(x, numbers.Number):
            self.x = x
            self.y = y
        else:
            self.set(x)

    def convert_to_boof(self):
        return create_java_point_2D_f64(float(self.x), float(self.y))

    def set(self, o):
        if type(o) is Point2D:
            self.x = o.x
            self.y = o.y
        elif type(o) is tuple:
            self.x = o[0]
            self.y = o[1]
        elif jg.is_instance_of(gateway, o, gateway.jvm.georegression.struct.point.Point2D_F64):
            self.x = o.getX()
            self.y = o.getY()
        elif jg.is_instance_of(gateway, o, gateway.jvm.georegression.struct.point.Point2D_F32):
            self.x = o.getX()
            self.y = o.getY()
        else:
            raise Exception("Unknown object type")

    def distance(self, point):
        dx = point.x - self.x
        dy = point.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def get_tuple(self):
        """
        Returns the values of the point inside a tuple: (x,y)
        """
        return (self.x, self.y)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def copy(self):
        return Point2D(self.x, self.y)


class Polygon2D:
    def __init__(self, data=None):
        if data is not None:
            if isinstance(data, int):
                self.vertexes = [Point2D() for i in range(data)]
            else:
                self.set(data)
        else:
            self.vertexes = []

    def convert_tuple(self):
        """
        Returns the values of the point inside a tuple: (x,y)
        """
        return [(v.x, v.y) for v in self.vertexes]

    def convert_boof(self):
        jobj = gateway.jvm.georegression.struct.shapes.Polygon2D_F64(len(self.vertexes))
        for idx, v in enumerate(self.vertexes):
            jobj.set(idx, v.x, v.y)
        return jobj

    def set(self, src):
        if isinstance(src, Polygon2D):
            self.vertexes = []
            for v in src.vertexes:
                self.vertexes.append(v.copy())
        elif jg.is_instance_of(gateway, src, gateway.jvm.georegression.struct.shapes.Polygon2D_F64):
            self.vertexes = []
            for i in range(src.size()):
                self.vertexes.append(Point2D(src.get(i)))
        elif jg.is_instance_of(gateway, src, gateway.jvm.georegression.struct.shapes.Polygon2D_F32):
            self.vertexes = []
            for i in range(src.size()):
                self.vertexes.append(Point2D(src.get(i)))
        else:
            self.vertexes = []
            for v in src:
                self.vertexes.append(Point2D(v[0], v[1]))

    def side_length(self, side):
        return self.vertexes[side].distance(self.vertexes[(side + 1) % len(self.vertexes)])

    def __str__(self):
        ret = "Polygon2D( "
        for p in self.vertexes:
            ret += "({},{}) ".format(p.x, p.y)
        ret += ")"
        return ret


class Quadrilateral2D:
    """
    Four sided polygon specified by its vertexes.  The vertexes are ordered, but it's not specified if they are
    ordered in clockwise or counter clockwise direction
    """

    def __init__(self, a=Point2D(), b=Point2D(), c=Point2D(), d=Point2D()):
        """

        :param a: Point2D
            Vertex is the quadrilateral
        :param b: Point2D
            Vertex is the quadrilateral
        :param c: Point2D
            Vertex is the quadrilateral
        :param d: Point2D
            Vertex is the quadrilateral
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def convert_to_boof(self):
        a = self.a.convert_to_boof()
        b = self.b.convert_to_boof()
        c = self.c.convert_to_boof()
        d = self.d.convert_to_boof()

        return gateway.jvm.georegression.struct.shapes.Quadrilateral_F64(a, b, c, d)

    def set(self, o):
        if type(o) is Quadrilateral2D:
            self.a.set(o.a)
            self.b.set(o.b)
            self.c.set(o.c)
            self.d.set(o.d)

        elif jg.is_instance_of(gateway, o, gateway.jvm.georegression.struct.shapes.Quadrilateral_F64):
            self.a.set(o.getA())
            self.b.set(o.getB())
            self.c.set(o.getC())
            self.d.set(o.getD())
        else:
            raise Exception("Unknown object type")

    def get_vertexes(self):
        """
        Returns a tuple with all the vertexes (a,b,c,d)
        :return: tuple of all vertexes
        """
        return (self.a, self.b, self.c, self.d)

    def get_tuple_tuple(self):
        return (self.a.get_tuple(), self.b.get_tuple(), self.c.get_tuple(), self.d.get_tuple())

    def get_a(self):
        return self.a

    def get_b(self):
        return self.b

    def get_c(self):
        return self.c

    def get_d(self):
        return self.d


class LineParametric2D:
    def __init__(self, o=None):
        self.p = Point2D()
        # In java this is a vector and is distinct from a point
        self.slope = Point2D()
        if o:
            self.set(o)

    def set(self, o):
        if type(o) is LineParametric2D:
            self.p.set(o.p)
            self.slope.set(o.slope)
        elif jg.is_instance_of(gateway, o, gateway.jvm.georegression.struct.line.LineParametric2D_F32):
            self.p.set((o.getX(), o.getY()))
            self.slope.set((o.getSlopeX(), o.getSlopeY()))
        elif jg.is_instance_of(gateway, o, gateway.jvm.georegression.struct.line.LineParametric2D_F64):
            self.p.set((o.getX(), o.getY()))
            self.slope.set((o.getSlopeX(), o.getSlopeY()))
        else:
            raise Exception("Unknown object type")

    def convert_to_boof(self, dtype=np.double):
        if dtype == float:
            x = float(self.p.x)
            y = float(self.p.y)
            sx = float(self.slope.x)
            sy = float(self.slope.y)

            return gateway.jvm.georegression.struct.line.LineParametric2D_F32(x, y, sx, sy)
        elif dtype == np.double:
            x = self.p.x
            y = self.p.y
            sx = self.slope.x
            sy = self.slope.y

            return gateway.jvm.georegression.struct.line.LineParametric2D_F64(x, y, sx, sy)
        else:
            raise Exception("Unknown dtype")


class CameraModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self, file_name: str):
        pass

    @abstractmethod
    def save(self, file_name: str):
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

    def __init__(self, java_object=None):
        if java_object is None:
            # Intrinsic calibration matrix
            self.fx = 0
            self.fy = 0
            self.skew = 0
            self.cx = 0
            self.cy = 0
            # image shape
            self.width = 0
            self.height = 0
        else:
            self.set_from_boof(java_object)

    def load(self, file_name: str):
        """
        Loads BoofCV formatted intrinsic parameters with radial distortion from a yaml file

        :param file_name: Path to yaml file
        :return: this class
        """
        file_path = os.path.abspath(file_name)
        boof_intrinsic = gateway.jvm.boofcv.io.calibration.CalibrationIO.load(file_path)

        if boof_intrinsic is None:
            raise RuntimeError("Can't load intrinsic parameters")

        self.set_from_boof(boof_intrinsic)
        return self

    def save(self, file_name):
        file_path = os.path.abspath(file_name)
        java_obj = self.convert_to_boof()
        gateway.jvm.boofcv.io.calibration.CalibrationIO.save(java_obj, file_path)

    def set_matrix(self, fx: float, fy: float, skew: float, cx: float, cy: float):
        self.fx = fx
        self.fy = fy
        self.skew = skew
        self.cx = cx
        self.cy = cy

    def set_image_shape(self, width: int, height: int):
        self.width = width
        self.height = height

    def set(self, orig):
        self.fx = orig.fx
        self.fy = orig.fy
        self.skew = orig.skew
        self.cx = orig.cx
        self.cy = orig.cy
        self.width = orig.width
        self.height = orig.height

    def set_from_boof(self, boof_intrinsic):
        self.fx = boof_intrinsic.getFx()
        self.fy = boof_intrinsic.getFy()
        self.cx = boof_intrinsic.getCx()
        self.cy = boof_intrinsic.getCy()
        self.skew = boof_intrinsic.getSkew()
        self.width = boof_intrinsic.getWidth()
        self.height = boof_intrinsic.getHeight()

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraPinholeBrown()
        else:
            boof_intrinsic = storage
        boof_intrinsic.setFx(float(self.fx))
        boof_intrinsic.setFy(float(self.fy))
        boof_intrinsic.setCx(float(self.cx))
        boof_intrinsic.setCy(float(self.cy))
        boof_intrinsic.setSkew(float(self.skew))
        boof_intrinsic.setWidth(int(self.width))
        boof_intrinsic.setHeight(int(self.height))
        return boof_intrinsic

    def __str__(self):
        return "Pinhole{{ fx={:f} fy={:f} skew={:f} cx={:f} cy={:f} | width={:d} height={:d}}}".format(
            self.fx, self.fy, self.skew, self.cx, self.cy, self.width, self.height)


class CameraBrown(CameraPinhole):
    """
    BoofCV Intrinsic Camera parameters
    """

    def __init__(self, java_object=None):
        CameraPinhole.__init__(self, java_object)
        if java_object is None:
            # radial distortion
            self.radial = None
            # tangential terms
            self.t1 = 0
            self.t2 = 0
        else:
            self.set_from_boof(java_object)

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
        CameraPinhole.set_from_boof(self, boof_intrinsic)
        jarray = boof_intrinsic.getRadial()
        if jarray is None:
            self.radial = None
        else:
            self.radial = [float(x) for x in jarray]
        self.t1 = boof_intrinsic.getT1()
        self.t2 = boof_intrinsic.getT2()

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraPinholeBrown()
        else:
            boof_intrinsic = storage

        CameraPinhole.convert_to_boof(self, boof_intrinsic)
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
        out = "Brown{{ fx={:f} fy={:f} skew={:f} cx={:f} cy={:f} | width={:d} height={:d} ". \
            format(self.fx, self.fy, self.skew, self.cx, self.cy, self.width, self.height)
        if self.is_distorted():
            out += " | radial=" + str(self.radial) + " t1=" + str(self.t1) + " t1=" + str(self.t2) + " }"
        else:
            out += "}}"
        return out


class CameraUniversalOmni(CameraBrown):
    def __init__(self, java_object=None):
        CameraBrown.__init__(self, java_object)
        if java_object is None:
            self.mirror_offset = 0
        else:
            self.mirror_offset = java_object.getMirrorOffset()

    def set_from_boof(self, boof_intrinsic):
        CameraBrown.set_from_boof(self, boof_intrinsic)
        self.mirror_offset = boof_intrinsic.getMirrorOffset()

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraUniversalOmni(0)
        else:
            boof_intrinsic = storage
        CameraBrown.convert_to_boof(self, boof_intrinsic)
        boof_intrinsic.setMirrorOffset(float(self.mirror_offset))
        return boof_intrinsic

    def __str__(self):
        out = "UniversalOmni{{ fx={:f} fy={:f} skew={:f} cx={:f} cy={:f} | width={:d} height={:d} | mirror={:f}". \
            format(self.fx, self.fy, self.skew, self.cx, self.cy, self.width, self.height, self.mirror_offset)
        if self.is_distorted():
            out += " | radial=" + str(self.radial) + " t1=" + str(self.t1) + " t1=" + str(self.t2) + " }"
        else:
            out += "}}"
        return out


class CameraKannalaBrandt(CameraPinhole):
    def __init__(self, java_object=None):
        CameraPinhole.__init__(self, java_object)
        if java_object is None:
            self.symmetric = []
            self.radial = []
            self.radialTrig = []
            self.tangent = []
            self.tangentTrig = []
        else:
            self.set_from_boof(java_object)

    def set_from_boof(self, boof_intrinsic):
        CameraPinhole.set_from_boof(self, boof_intrinsic)
        jsymmetric = boof_intrinsic.getSymmetric()
        jradial = boof_intrinsic.getRadial()
        jradialTrig = boof_intrinsic.getRadialTrig()
        jtangent = boof_intrinsic.getTangent()
        jtangentTrig = boof_intrinsic.getTangentTrig()

        self.symmetric = [float(x) for x in jsymmetric]
        self.radial = [float(x) for x in jradial]
        self.radialTrig = [float(x) for x in jradialTrig]
        self.tangent = [float(x) for x in jtangent]
        self.tangentTrig = [float(x) for x in jtangentTrig]

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_intrinsic = gateway.jvm.boofcv.struct.calib.CameraKannalaBrandt(len(self.symmetric), len(self.radial))
        else:
            boof_intrinsic = storage
        CameraPinhole.convert_to_boof(self, boof_intrinsic)
        boof_intrinsic.setSymmetric(python_to_java_double_array(self.symmetric))
        boof_intrinsic.setRadial(python_to_java_double_array(self.radial))
        boof_intrinsic.setRadialTrig(python_to_java_double_array(self.radialTrig))
        boof_intrinsic.setTangent(python_to_java_double_array(self.tangent))
        boof_intrinsic.setTangentTrig(python_to_java_double_array(self.tangentTrig))
        return boof_intrinsic

    def __str__(self):
        out = "CameraKannalaBrandt{{ fx={:f} fy={:f} skew={:f} cx={:f} cy={:f} | width={:d} height={:d}". \
            format(self.fx, self.fy, self.skew, self.cx, self.cy, self.width, self.height)
        out += " | symmetric=" + str(self.symmetric) + " radial=" + str(self.radial) + " radialTrig=" + \
               str(self.radialTrig) + " tangent=" + str(self.tangent) + " tangentTrig=" + str(self.tangentTrig) + " }}"
        return out


class StereoParameters(CameraModel):
    """
    Stereo intrinsic and extrinsic parameters
    """

    def __init__(self, java_object=None):
        if java_object is None:
            self.left = CameraBrown()
            self.right = CameraBrown()
            self.right_to_left = Se3_F64()
        else:
            self.set_from_boof(java_object)

    def load(self, file_name: str):
        file_path = os.path.abspath(file_name)
        boof_parameters = gateway.jvm.boofcv.io.calibration.CalibrationIO.load(file_path)

        if boof_parameters is None:
            raise RuntimeError("Can't load stereo parameters")
        self.set_from_boof(boof_parameters)

    def save(self, file_name: str):
        file_path = os.path.abspath(file_name)
        java_obj = self.convert_to_boof()
        gateway.jvm.boofcv.io.calibration.CalibrationIO.save(java_obj, file_path)

    def set_from_boof(self, boof_parameters):
        self.left = CameraBrown(boof_parameters.left)
        self.right = CameraBrown(boof_parameters.right)
        self.right_to_left = Se3_F64(boof_parameters.right_to_left)

    def convert_to_boof(self, storage=None):
        if storage is None:
            boof_parameters = gateway.jvm.boofcv.struct.calib.StereoParameters()
            # In BoofCV 0.40 StereoParameters will not be initialized with null and this will not be needed
            boof_parameters.setLeft(CameraBrown().convert_to_boof())
            boof_parameters.setRight(CameraBrown().convert_to_boof())
            boof_parameters.setRightToLeft(Se3_F64().java_obj)
        else:
            boof_parameters = storage
        self.left.convert_to_boof(boof_parameters.left)
        self.right.convert_to_boof(boof_parameters.right)
        boof_parameters.right_to_left.setTo(self.right_to_left.java_obj)
        return boof_parameters

    def __str__(self):
        return "StereoParameters(left={} right={} right_to_left={})".format(self.left, self.right, self.right_to_left)


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

    def undistort(self, pixel_in: bool, pixel_out: bool):
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
            java_out = self.java_obj.undistort_F64(pixel_in, pixel_out)
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


def create_narrow_lens_distorter(camera_model):
    """

    :param camera_model:
    :return:
    :rtype: LensNarrowDistortionFactory
    """
    if isinstance(camera_model, CameraUniversalOmni):
        raise RuntimeError("CameraUniversalOmni is not a narrow FOV camera model")
    elif isinstance(camera_model, CameraPinhole):
        boof_model = camera_model.convert_to_boof()
        java_obj = gateway.jvm.boofcv.alg.distort.pinhole.LensDistortionPinhole(boof_model)
    elif isinstance(camera_model, CameraBrown):
        boof_model = camera_model.convert_to_boof()
        if camera_model.is_distorted():
            java_obj = gateway.jvm.boofcv.alg.distort.brown.LensDistortionBrown(boof_model)
        else:
            java_obj = gateway.jvm.boofcv.alg.distort.pinhole.LensDistortionPinhole(boof_model)
    else:
        raise RuntimeError("Unknown camera model {}".format(type(camera_model)))

    return LensNarrowDistortionFactory(java_obj)


def create_wide_lens_distorter(camera_model):
    """

    :param camera_model:
    :return:
    :rtype: LensWideDistortionFactory
    """
    if isinstance(camera_model, CameraUniversalOmni):
        boof_model = camera_model.convert_to_boof()
        java_obj = gateway.jvm.boofcv.alg.distort.universal.LensDistortionUniversalOmni(boof_model)
    elif isinstance(camera_model, CameraKannalaBrandt):
        boof_model = camera_model.convert_to_boof()
        java_obj = gateway.jvm.boofcv.alg.distort.kanbra.LensDistortionKannalaBrandt(boof_model)
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
        java_object = gateway.jvm.boofcv.alg.distort.NarrowToWidePtoP_F32(narrow_distort.java_obj,
                                                                          wide_distort.java_obj)
        JavaWrapper.__init__(self, java_object)

    def set_rotation_wide_to_narrow(self, rotation_matrix):
        """
        Used to change the principle axis of the narrow FOC camera by rotating the view

        :param rotation_matrix: 3D rotation matrix
        :return:
        """
        self.java_obj.setRotationWideToNarrow(real_nparray_to_ejml32(rotation_matrix))
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
        java_pixel_transform = gateway.jvm.boofcv.struct.distort.PointToPixelTransform_F32(self.java_obj)
        java_alg.setModel(java_pixel_transform)
        return ImageDistort(java_alg)


class AdjustmentType:
    NONE = 0
    FULL_VIEW = 1
    EXPAND = 2


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
    """
    Removes lens distortion from the input image and saves it into the output image. More specifically,
    it adjusts the camera model such that the radian and tangential distortion is zero. The modified
    camera model is returned.

    :param input: Java BoofCV Image
    :type input:
    :param output: Java BoofCV Image
    :type output:
    :param intrinsic: Camera model
    :type intrinsic: CameraPinhole
    :param adjustment: Should the camera model be adjusted to ensure the whole image can be seen?
    :type adjustment: AdjustmentType
    :param border: Border How should pixels outside the image border be handled?
    :type border: Border
    :return: The new camera model
    :rtype: CameraPinhole
    """
    image_type = ImageType(input.getImageType())
    desired = CameraPinhole()
    desired.set(intrinsic)
    desired.radial = [0, 0]
    desired.t1 = desired.t2 = 0

    distorter, intrinsic_out = create_change_camera_model(intrinsic, desired, image_type, adjustment, border)
    distorter.apply(input, output)
    return intrinsic_out


def create_change_camera_model(intrinsic_orig, intrinsic_desired, image_type,
                               adjustment=AdjustmentType.FULL_VIEW, border=Border.ZERO):
    """
    Creates an ImageDistort that converts an image from the original camera model to the desired camera model
    after adjusting the view to ensure that it meets the requested visibility requirements.

    :param intrinsic_orig: Original camera model prior to distortion
    :type intrinsic_orig: CameraPinhole
    :param intrinsic_desired: The desired new camera model
    :type intrinsic_desired: CameraPinhole
    :param image_type: Type of input image
    :type image_type: ImageType
    :param adjustment: Should the camera model be adjusted to ensure the whole image can be seen?
    :type adjustment: AdjustmentType
    :param border: Border How should pixels outside the image border be handled?
    :type border: Border
    :return: Distortion for removing the camera model and the new camera parameters
    :rtype: (ImageDistort,CameraPinhole)
    """

    java_image_type = image_type.get_java_object()
    java_adjustment = adjustment_to_java(adjustment)
    java_border = border_to_java(border)
    java_original = intrinsic_orig.convert_to_boof()
    java_desired = intrinsic_desired.convert_to_boof()
    java_intrinsic_out = gateway.jvm.boofcv.struct.calib.CameraPinholeBrown()
    id = gateway.jvm.boofcv.alg.distort.LensDistortionOps.changeCameraModel(
        java_adjustment, java_border, java_original, java_desired, java_intrinsic_out, java_image_type)
    return (ImageDistort(id), CameraPinhole(java_intrinsic_out))

def p2b_list_AssociatedPair(pylist):
    java_list = gateway.jvm.java.util.ArrayList()

    if pyboof.mmap_file:
        mmap_list_python_to_AssociatedPair(pylist, java_list)
    else:
        exception_use_mmap()
    return java_list


def b2p_list_AssociatedPair(boof_list):
    """
    Converts a BoofCV list AssociatedPair into a Python compatible format
    :param boof_list: Descriptor list in BoofCV format
    :return: List of 2d points in Python format
    :type pylist: list[(float,float)]
    """
    pylist = []

    if pyboof.mmap_file:
        mmap_list_AssociatedPair_to_python(boof_list, pylist)
    else:
        exception_use_mmap()
    return pylist


def p2b_list_point2D(pylist, dtype):
    """
    Converts a python list of feature descriptors stored in 64bit floats into a BoofCV compatible format
    :param pylist: Python list of 2d points
    :type pylist: list[(float,float)]
    :return: List of 2d points in BoofCV format
    """
    java_list = gateway.jvm.java.util.ArrayList()

    if pyboof.mmap_file:
        mmap_list_python_to_Point2D(pylist, java_list, dtype)
    else:
        exception_use_mmap()
    return java_list


def b2p_list_point2D(boof_list, dtype):
    """
    Converts a BoofCV list of 2d points into a Python compatible format
    :param boof_list: Descriptor list in BoofCV format
    :return: List of 2d points in Python format
    :type pylist: list[(float,float)]
    """
    pylist = []

    if pyboof.mmap_file:
        mmap_list_Point2D_to_python(boof_list, pylist, dtype)
    else:
        exception_use_mmap()
    return pylist


def p2b_list_LineParametric(pylist, dtype):
    """
    Converts a python list of feature descriptors stored in 64bit floats into a BoofCV compatible format
    :param pylist: Python list of 2d points
    :type pylist: list[(float,float)]
    :return: List of 2d points in BoofCV format
    """
    java_list = gateway.jvm.java.util.ArrayList()

    for o in pylist:
        java_list.add(o.convert_to_boof(dtype))

    return java_list


def mmap_list_python_to_AssociatedPair(pylist, java_list):
    """
    Converts a python list of ((x0,y0),(x1,y1)) a java list of AssociatedPair using memmap file

    :param pylist: (Input) Python list of 2D float tuples.
    :type pylist: list[((float,float),(float,float))]
    :param java_list: (Output) Java list to store AssociatedPair
    """
    num_elements = len(pylist)
    mm = pyboof.mmap_file

    # max number of list elements it can write at once
    max_elements = (pyboof.mmap_size - 100) / (4 * 8)

    curr = 0
    while curr < num_elements:
        # Write as much of the list as it can to the mmap file
        num_write = min(max_elements, num_elements - curr)
        mm.seek(0)
        mm.write(struct.pack('>HI', pyboof.MmapType.LIST_ASSOCIATEDPAIR_F64, num_elements))
        for i in range(curr, curr + num_write):
            p = pylist[i]
            mm.write(struct.pack('>4d', float(p[0][0]), float(p[0][1]), float(p[1][0]), float(p[1][1])))

        # Now tell the java end to read what it just wrote
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.read_List_AssociatedPair_F64(java_list)

        # move on to the next block
        curr = curr + num_write


def mmap_list_AssociatedPair_to_python(java_list, pylist):
    """
    Converts a java list of AssociatedPair into a python list of ((x,y),(x,y)) using memmap file
    :param java_list: Input: java list
    :param pylist: output: python list
    :type pylist: list[((float,float),(float,float))]
    """
    num_elements = java_list.size()
    mm = pyboof.mmap_file

    num_read = 0
    while num_read < num_elements:
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.write_List_AssociatedPair_F64(java_list, num_read)
        mm.seek(0)
        data_type, num_found = struct.unpack(">HI", mm.read(2 + 4))
        if data_type != pyboof.MmapType.LIST_ASSOCIATEDPAIR_F64:
            raise Exception("Unexpected data type in mmap file. %d" % data_type)
        if num_found > num_elements - num_read:
            raise Exception("Too many elements returned. " + str(num_found))
        for i in range(num_found):
            desc = struct.unpack(">4d", mm.read(8 * 4))
            pylist.append(((desc[0], desc[1]), (desc[2], desc[3])))
        num_read += num_found


def dtype_to_unpack(dtype):
    if dtype == np.uint8:
        return (1, "B")
    elif dtype == np.int8:
        return (1, "b")
    elif dtype == np.uint16:
        return (2, "H")
    elif dtype == np.int16:
        return (2, "h")
    elif dtype == np.int32:
        return (4, "i")
    elif dtype == float:
        return (4, "f")
    elif dtype == np.double:
        return (8, "d")
    else:
        raise Exception("Unknown dtype")


def dtype_to_mmaplistpoints(dtype):
    if dtype == np.int16:
        return pyboof.MmapType.LIST_POINT2D_S16
    elif dtype == np.uint16:
        return pyboof.MmapType.LIST_POINT2D_U16
    elif dtype == np.int32:
        return pyboof.MmapType.LIST_POINT2D_S32
    elif dtype == float:
        return pyboof.MmapType.LIST_POINT2D_F32
    elif dtype == np.double:
        return pyboof.MmapType.LIST_POINT2D_F64
    else:
        raise RuntimeError("No mmap type for dtype={}".format(dtype))


def dtype_to_mmaplistpoints3d(dtype):
    if dtype == float:
        return pyboof.MmapType.LIST_POINT3D_F32
    elif dtype == np.double:
        return pyboof.MmapType.LIST_POINT3D_F64
    else:
        raise RuntimeError("No mmap type for dtype={}".format(dtype))


def mmap_list_python_to_Point2D(pylist, java_list, dtype):
    """
    Converts a python list of 2d float tuples into a list of Point2D_64F in java using memmap file

    :param pylist: (Input) Python list of 2D float tuples.
    :type pylist: list[(float,float)]
    :param java_list: (Output) Java list to store Point2D_64F
    """
    num_elements = len(pylist)
    mm = pyboof.mmap_file

    num_bytes, char_type = dtype_to_unpack(dtype)
    num_bytes_per_point = num_bytes * 2
    format_string = ">2{}".format(char_type)

    mmap_type = dtype_to_mmaplistpoints(dtype)

    # max number of list elements it can write at once
    max_elements = int((pyboof.mmap_size - 100) / num_bytes_per_point)

    curr = 0
    while curr < num_elements:
        # Write as much of the list as it can to the mmap file
        num_write = min(max_elements, num_elements - curr)
        mm.seek(0)
        mm.write(struct.pack('>HI', mmap_type, num_elements))
        for i in range(curr, curr + num_write):
            mm.write(struct.pack(format_string, *pylist[i]))

        # Now tell the java end to read what it just wrote
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.read_List_Point2D(java_list, mmap_type)

        # move on to the next block
        curr = curr + num_write


def mmap_list_Point2D_to_python(java_list, pylist, dtype):
    """
    Converts a java list of Point2D_* into a python list of float 2D tuples using memmap file
    :param java_list: Input: java list
    :param pylist: output: python list
    :type pylist: list[(float,float)]
    :param dtype The numpy dtype
    """
    num_elements = java_list.size()
    mm = pyboof.mmap_file

    num_bytes, char_type = dtype_to_unpack(dtype)
    num_bytes_per_point = num_bytes * 2
    format_string = ">2{}".format(char_type)

    mmap_type = dtype_to_mmaplistpoints(dtype)

    num_read = 0
    while num_read < num_elements:
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.write_List_Point2D(java_list, mmap_type, num_read)
        mm.seek(0)
        data_type, num_found = struct.unpack(">HI", mm.read(2 + 4))
        if data_type != mmap_type:
            raise Exception("Unexpected data type in mmap file. %d" % data_type)
        if num_found > num_elements - num_read:
            raise Exception("Too many elements returned. " + str(num_found))
        for i in range(num_found):
            point = struct.unpack(format_string, mm.read(num_bytes_per_point))
            pylist.append(point)
        num_read += num_found


def mmap_list_python_to_Point3D(pylist, java_list, dtype):
    """
    Converts a python list of 3d float tuples into a list of Point3D_64F in java using memmap file
    """
    num_elements = len(pylist)
    mm = pyboof.mmap_file

    num_bytes, char_type = dtype_to_unpack(dtype)
    num_bytes_per_point = num_bytes * 3
    format_string = ">3{}".format(char_type)

    mmap_type = dtype_to_mmaplistpoints3d(dtype)

    # max number of list elements it can write at once
    max_elements = int((pyboof.mmap_size - 100) / num_bytes_per_point)

    curr = 0
    while curr < num_elements:
        # Write as much of the list as it can to the mmap file
        num_write = min(max_elements, num_elements - curr)
        mm.seek(0)
        mm.write(struct.pack('>HI', mmap_type, num_write))
        for i in range(curr, curr + num_write):
            mm.write(struct.pack(format_string, *pylist[i]))

        # Now tell the java end to read what it just wrote
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.read_List_Point3D(java_list, mmap_type)

        # move on to the next block
        curr = curr + num_write


def mmap_list_Point3D_to_python(java_list, pylist, dtype):
    """
    Converts a java list of Point3D_* into a python list of float 3D tuples using memmap file
    """
    num_elements = java_list.size()
    mm = pyboof.mmap_file

    num_bytes, char_type = dtype_to_unpack(dtype)
    num_bytes_per_point = num_bytes * 3
    format_string = ">3{}".format(char_type)

    mmap_type = dtype_to_mmaplistpoints3d(dtype)

    num_read = 0
    while num_read < num_elements:
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.write_List_Point3D(java_list, mmap_type, num_read)
        mm.seek(0)
        data_type, num_found = struct.unpack(">HI", mm.read(2 + 4))
        if data_type != mmap_type:
            raise Exception("Unexpected data type in mmap file. %d" % data_type)
        if num_found > num_elements - num_read:
            raise Exception("Too many elements returned. " + str(num_found))
        for i in range(num_found):
            point = struct.unpack(format_string, mm.read(num_bytes_per_point))
            pylist.append(point)
        num_read += num_found