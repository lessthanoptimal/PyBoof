import struct
import sys
from pyboof import JavaConfig
from pyboof import JavaWrapper
from pyboof import dtype_to_Class_SingleBand
from pyboof import gateway
from pyboof.common import JavaList
from pyboof.common import JavaList_to_fastqueue
from pyboof.common import is_java_class


class ConfigSurfFast(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self,"boofcv.abst.feature.describe.ConfigSurfDescribe$Speed")


class ConfigSurfStability(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self,"boofcv.abst.feature.describe.ConfigSurfDescribe$Stability")


class ConfigFastHessian(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self,"boofcv.abst.feature.detect.interest.ConfigFastHessian")


class ConfigAverageIntegral(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self,"boofcv.abst.feature.orientation.ConfigAverageIntegral")


class ConfigDenseSampling(JavaConfig):
    def __init__(self, scale,periodX ,periodY):
        JavaConfig.__init__(self,"boofcv.factory.feature.dense.ConfigDenseSample")
        self.scale = scale
        self.periodX = periodX
        self.periodY = periodY


class AssocScoreType:
    """
    Enum different types of association scoring techniques
    """
    DEFAULT = 0,
    SAD = 1
    EUCLIDEAN = 2
    EUCLIDEAN_SQ = 3
    NCC = 4


class ConfigAssociation:
    def __init__(self,score_type=AssocScoreType.DEFAULT, max_error=sys.float_info.max,backwards_validation=True):
        self.score_type = score_type
        self.max_error = max_error
        self.backwards_validation = backwards_validation


class AssociateDescription(JavaWrapper):
    def __init__(self, java_object ):
        JavaWrapper.__init__(self, java_object)

    def set_source(self, feature_list ):
        fast_queue = JavaList_to_fastqueue(feature_list.java_obj,feature_list.java_type,queue_declare=False)
        self.java_obj.setSource(fast_queue)

    def set_destination(self, feature_list ):
        fast_queue = JavaList_to_fastqueue(feature_list.java_obj,feature_list.java_type,queue_declare=False)
        self.java_obj.setDestination(fast_queue)

    def associate(self):
        output = []

        self.java_obj.associate()
        matches = self.java_obj.getMatches()
        for i in xrange(matches.getSize()):
            association = matches.get(i)
            output.append( (association.src,association.dst,association.score) )

        return output

    def get_java_matches(self):
        return self.java_obj.getMatches()

def read_list_tuple_desc_f64( f , list_length ):
    output = []
    for i in xrange(list_length):
        desc_length = struct.unpack('>i', f.read(4))[0]
        desc = [0.0]*desc_length
        for j in xrange(desc_length):
            desc[j] = struct.unpack('>d', f.read(8))[0]
        output.append(desc)
    return output

def read_list( file_name ):
    output = []
    with open(file_name, 'r') as f:
        data_type = f.readline()[0:-1]
        if data_type != "list":
            raise RuntimeError("Was expecting list in front of file not "+data_type)
        class_type = f.readline()
        list_length = struct.unpack('>i', f.read(4))[0]

        if "TupleDesc_F64" in class_type:
            output = read_list_tuple_desc_f64(f,list_length)
        else:
            raise RuntimeError("Unknown list data type "+class_type)

    if list_length != len(output):
        raise RuntimeError("Unexpected list size. "+str(list_length)+" "+str(len(output)))
    return output


def java_list_to_python( java_list ):
    N = java_list.size()
    output = []
    if is_java_class(java_list.java_type,"boofcv.struct.feature.TupleDesc_F64"):
        for i in xrange(N):
            d = java_list.java_obj.get(i)
            value = d.getValue() # some hackery to get around py4j short comings
            output.append([x for x in value])
    elif is_java_class(java_list.java_type,"georegression.struct.point.Point2D_F64"):
        for i in xrange(N):
            p = java_list.java_obj.get(i)
            output.append((p.x,p.y))
    else:
        raise RuntimeError("Unknown java list type")

    return output

class DetectDescribePointFeatures(JavaWrapper):
    def __init__(self,java_object):
        self.set_java_object(java_object)

    def detect(self, image ):
        self.java_obj.detect(image)

        java_locations = gateway.jvm.pyboof.PyBoofEntryPoint.extractPoints(self.java_obj)
        java_descriptions = gateway.jvm.pyboof.PyBoofEntryPoint.extractFeatures(self.java_obj)

        locations = JavaList(java_locations,gateway.jvm.georegression.struct.point.Point2D_F64().getClass())
        descriptions = JavaList(java_descriptions,self.java_obj.getDescriptionType())

        return locations, descriptions

    def get_scales(self):
        N = self.java_obj.getNumberOfFeatures()
        output = [0]*N
        for i in xrange(N):
            output.append(self.java_obj.getScale(i))
        return output

    def get_orientations(self ):
        N = self.java_obj.getNumberOfFeatures()
        output = [0]*N
        for i in xrange(N):
            output.append(self.java_obj.getOrientation(i))
        return output

    def has_scale(self):
        return self.java_obj.hasScale()

    def has_orientation(self):
        return self.java_obj.hasOrientation()

    def get_descriptor_type(self):
        return self.java_obj.getDescriptionType()


class DenseDescribePointFeatures(JavaWrapper):
    def __init__(self,java_object):
        self.set_java_object(java_object)

    def detect(self, image ):
        pass


class FactoryDetectDescribe:
    def __init__(self, dtype ):
        self.boof_image_type =  dtype_to_Class_SingleBand(dtype)

    def createSurf( self, config_detect=None , config_desc=None , config_ori=None ):
        if config_desc is None:
            config_desc = ConfigSurfStability()

        java_config_detect = None
        java_config_desc = config_desc.java_obj
        java_config_ori = None

        if config_detect is not None:
            java_config_detect = config_detect.java_obj
        if config_ori is not None:
            java_config_ori = config_ori.java_obj

        if config_desc.__class__.__name__ == "ConfigSurfFast":
            java_object = gateway.jvm.boofcv.factory.feature.detdesc.FactoryDetectDescribe.surfFast(
                java_config_detect,java_config_desc,java_config_ori, self.boof_image_type)
        elif config_desc.__class__.__name__ == "ConfigSurfStability":
            java_object = gateway.jvm.boofcv.factory.feature.detdesc.FactoryDetectDescribe.surfStable(
                java_config_detect,java_config_desc,java_config_ori, self.boof_image_type)
        else:
            raise RuntimeError("Unknown description type")

        return DetectDescribePointFeatures(java_object)

    def createSift(self):
        pass

    def createBrief(self):
        pass

    def createBriefSO(self):
        pass

    def createNcc(self):
        pass


class FactoryDenseDescribe:
    def __init__(self, dtype ):
        self.boof_image_type =  dtype_to_Class_SingleBand(dtype)

    def createSurf( self, config_sampling , config_desc=None ):
        if config_desc is None:
            config_desc = ConfigSurfFast()

        java_config_sampling = config_sampling.java_obj
        java_config_desc = config_desc.java_obj


class FactoryAssociate:
    def __init__(self):
        self.score = None

    def set_score(self, score_type , descriptor_type ):
        if score_type == AssocScoreType.DEFAULT:
            self.score = gateway.jvm.boofcv.factory.feature.associate.\
                FactoryAssociation.defaultScore(descriptor_type)
        elif score_type == AssocScoreType.EUCLIDEAN:
            self.score = gateway.jvm.boofcv.factory.feature.associate.\
                FactoryAssociation.scoreEuclidean(descriptor_type,False)
        elif score_type == AssocScoreType.EUCLIDEAN_SQ:
            self.score = gateway.jvm.boofcv.factory.feature.associate.\
                FactoryAssociation.scoreEuclidean(descriptor_type,True)
        elif score_type == AssocScoreType.NCC:
            self.score = gateway.jvm.boofcv.factory.feature.associate.\
                FactoryAssociation.scoreNcc()
        elif score_type == AssocScoreType.SAD:
            self.score = gateway.jvm.boofcv.factory.feature.associate.\
                FactoryAssociation.scoreSad(descriptor_type)

    def greedy(self, max_error=sys.float_info.max,backwards_validation=True):
        java_obj = gateway.jvm.boofcv.factory.feature.associate.\
                FactoryAssociation.greedy(self.score,max_error,backwards_validation)
        return AssociateDescription(java_obj)

    def kdtree(self):
        pass

    def kdRandomForest(self):
        pass
