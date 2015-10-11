from py4j import java_gateway
from pyboof import gateway


def is_java_class( java_class , string_path ):
    return gateway.jvm.pyboof.PyBoofEntryPoint.isClass(java_class,string_path)


class JavaWrapper:
    def __init__(self, java_object=None):
        self.java_obj = java_object

    def set_java_object(self, obj ):
        self.java_obj = obj

    def get_java_object(self):
        return self.java_obj

    def __str__(self):
        return self.java_obj.toString()


class Config(JavaWrapper):
    def __init__(self, java_ConfigPolygonDetector):
        self.set_java_object(java_ConfigPolygonDetector)

    def get_property(self, name):
        return java_gateway.get_field(self.java_obj,name)

    def set_property(self, name, value):
        return java_gateway.set_field(self.java_obj,name, value)

    def __dir__(self):
        return self.java_properties

class JavaConfig:
    """
    Provides a nice python wrapper around Java classes.  Public variables are automatically turned into Python
    attributes
    """
    def __init__(self, java_class_path ):
        self.java_class_path = java_class_path

        words = java_class_path.replace('$',".").split(".")

        a = gateway.jvm.__getattr__(words[0])
        for i in range(1,len(words)):
            a = a.__getattr__(words[i])

        self.java_obj = a.__call__()
        self.java_fields = [ x for x in gateway.jvm.pyboof.PyBoofEntryPoint.getPublicFields(java_class_path)]

    def get_java_object(self):
        return self.java_obj

    def __getattr__(self, item):
        if "java_fields" in self.__dict__ and item in self.__dict__["java_fields"]:
            return java_gateway.get_field(self.java_obj,item)
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if "java_fields" in self.__dict__ and key in self.__dict__["java_fields"]:
            java_gateway.set_field(self.java_obj,key, value)
        else:
            self.__dict__[key] = value

    def __dir__(self):
        return sorted(set(
                self.__dict__.keys() + self.java_fields))


