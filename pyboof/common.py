from py4j import java_gateway
from pyboof import gateway
from six import string_types
import pyboof
import struct
import numpy as np


def exception_use_mmap():
    raise Exception("Need to turn on mmap. Add pb.init_memmap() to your code before any other calls to PyBoof")


def is_java_class(java_class, string_path):
    """True if the passed in object is the Class specified by the path"""
    return gateway.jvm.pyboof.PyBoofEntryPoint.isClass(java_class, string_path)


def ejml_matrix_d_to_f(D):
    F = gateway.jvm.org.ejml.data.FMatrixRMaj(D.getNumRows(), D.getNumCols())
    gateway.jvm.org.ejml.ops.ConvertMatrixData.convert(D, F)
    return F


def boof_fixed_length(length):
    return gateway.jvm.boofcv.struct.ConfigLength(float(length), float(-1))


def python_to_java_double_array(array):
    jarray = gateway.new_array(gateway.jvm.double, len(array))
    for i in range(len(array)):
        jarray[i] = array[i]
    return jarray


class JavaWrapper:
    def __init__(self, java_object=None):
        self.java_obj = java_object
        self.java_fields = [x for x in gateway.jvm.pyboof.PyBoofEntryPoint.getPublicFields(self.java_obj.getClass())]

    def __getattr__(self, item):
        if "java_fields" in self.__dict__ and item in self.__dict__["java_fields"]:
            return java_gateway.get_field(self.java_obj, item)
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if "java_fields" in self.__dict__ and key in self.__dict__["java_fields"]:
            java_gateway.set_field(self.java_obj, key, value)
        else:
            self.__dict__[key] = value

    def __dir__(self):
        return sorted(set(self.__dict__.keys() + self.java_fields))

    def set_java_object(self, obj):
        self.java_obj = obj

    def get_java_object(self):
        return self.java_obj

    def __str__(self):
        return "Wrapped Java:\n" + self.java_obj.toString()


class JavaConfig(JavaWrapper):
    """
    Provides a nice python wrapper around Java classes.  Public variables are automatically turned into Python
    attributes
    """

    # TODO variables which are java classes are a little messed up
    def __init__(self, java_class_path):
        if isinstance(java_class_path, string_types):
            self.java_class_path = java_class_path

            words = java_class_path.replace('$', ".").split(".")

            a = gateway.jvm.__getattr__(words[0])
            for i in range(1, len(words)):
                a = a.__getattr__(words[i])

            self.java_obj = a.__call__()
        else:
            self.java_obj = java_class_path
        JavaWrapper.__init__(self, self.java_obj)

    def __getattr__(self, item):
        if "java_fields" in self.__dict__ and item in self.__dict__["java_fields"]:
            a = java_gateway.get_field(self.java_obj, item)
            if gateway.jvm.pyboof.PyBoofEntryPoint.isConfigClass(a):
                return JavaConfig(a)
            else:
                return a
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if "java_fields" in self.__dict__ and key in self.__dict__["java_fields"]:
            if isinstance(value, JavaConfig):
                java_gateway.set_field(self.java_obj, key, value.java_obj)
            else:
                java_gateway.set_field(self.java_obj, key, value)
        else:
            self.__dict__[key] = value


class JavaList(JavaWrapper):
    def __init__(self, java_list, java_type):
        JavaWrapper.__init__(self, java_list)
        self.java_type = java_type

    def size(self):
        return self.java_obj.size()

    def save_to_disk(self, file_name):
        gateway.jvm.pyboof.FileIO.saveList(self.java_obj, self.java_type, file_name)


def JavaList_to_fastarray(java_list, java_class_type):
    return gateway.jvm.pyboof.PyBoofEntryPoint.listToFastArray(java_list, java_class_type)


def create_java_file_writer(path: str):
    java_file = gateway.jvm.java.io.File(path)
    return gateway.jvm.java.io.FileWriter(java_file)


def create_java_file(path: str):
    return gateway.jvm.java.io.File(path)


def mmap_array_python_to_java(pylist, mmap_type: pyboof.MmapType):
    """
    Converts a python primitive list into a java primitive array
    """

    # Ensure the data type is correct
    pylist = pyboof.mmap_force_array_type(pylist, mmap_type)

    num_elements = len(pylist)
    mm = pyboof.mmap_file

    num_element_bytes = pyboof.mmap_primitive_len(mmap_type)
    format = pyboof.mmap_primitive_format(mmap_type)

    # max number of list elements it can write at once
    max_elements = (pyboof.mmap_size - 100) / num_element_bytes

    # See if it can be writen in a single chunk
    if max_elements < num_elements:
        raise Exception("max_elements is too small")

    # Write as much of the list as it can to the mmap file
    mm.seek(0)
    mm.write(struct.pack('>HI', mmap_type, num_elements))
    for i in range(0, num_elements):
        mm.write(struct.pack(format, pylist[i]))

    # Now tell the java end to read what it just wrote
    return gateway.jvm.pyboof.PyBoofEntryPoint.mmap.read_primitive_array(mmap_type)


def mmap_array_java_to_python(java_array, mmap_type: pyboof.MmapType):
    """
    Converts a java primitive array into a python primitive list
    """
    if java_array is None:
        return None

    num_elements = len(java_array)
    mm = pyboof.mmap_file

    num_element_bytes = pyboof.mmap_primitive_len(mmap_type)
    format = pyboof.mmap_primitive_format(mmap_type)

    python_list = []

    gateway.jvm.pyboof.PyBoofEntryPoint.mmap.write_primitive_array(java_array, mmap_type, 0)
    mm.seek(0)
    data_type, num_found = struct.unpack(">HI", mm.read(2 + 4))
    if data_type != mmap_type:
        raise Exception("Unexpected data type in mmap file. {%d}" % data_type)
    if num_found != num_elements:
        raise Exception("Unexpected number of elements returned. " + str(num_found))
    for i in range(num_found):
        element = struct.unpack(format, mm.read(num_element_bytes))
        python_list.append(element)
    return pyboof.mmap_force_array_type(python_list, mmap_type)
