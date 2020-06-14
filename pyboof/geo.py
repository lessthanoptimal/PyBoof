import math
import struct
import pyboof
import numbers
import numpy as np
import py4j.java_gateway as jg
from pyboof.common import *
from pyboof import gateway


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
        if dtype == np.float:
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
    elif dtype == np.float:
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
    elif dtype == np.float:
        return pyboof.MmapType.LIST_POINT2D_F32
    elif dtype == np.double:
        return pyboof.MmapType.LIST_POINT2D_F64
    else:
        raise RuntimeError("No mmap type for dtype={}".format(dtype))


def dtype_to_mmaplistpoints3d(dtype):
    if dtype == np.float:
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