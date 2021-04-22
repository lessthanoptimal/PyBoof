import struct
import sys
import pyboof
from pyboof import JavaConfig
from pyboof import JavaWrapper
from pyboof import dtype_to_Class_SingleBand
from pyboof import dtype_to_ImageType
from pyboof import gateway
from pyboof.common import JavaList
from pyboof.common import JavaList_to_fastarray
from pyboof.common import is_java_class
import pyboof.image
import numpy as np


def p2b_list_descF64(pylist):
    """
    Converts a python list of feature descriptors stored in 64bit floats into a BoofCV compatible format
    :param pylist: Python list of feature descriptors
    :type pylist: list[list[float]]
    :return: List of descriptors in BoofCV format
    """
    java_list = gateway.jvm.java.util.ArrayList()

    if pyboof.mmap_file:
        mmap_list_python_to_TupleF64(pylist, java_list)
    else:
        exception_use_mmap()
    return java_list


def b2p_list_descF64(boof_list):
    """
    Converts a BoofCV list of feature descriptors stored in 64bit floats into a Python compatible format
    :param boof_list: Descriptor list in BoofCV format
    :return: List of descriptors in Python format
    :rtype: list[list[float]]
    """
    pylist = []

    if pyboof.mmap_file:
        mmap_list_TupleF64_to_python(boof_list, pylist)
    else:
        exception_use_mmap()
    return pylist


class ConfigSurfFast(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.feature.describe.ConfigSurfDescribe$Speed")


class ConfigSurfStability(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.feature.describe.ConfigSurfDescribe$Stability")


class ConfigFastHessian(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.feature.detect.interest.ConfigFastHessian")


class ConfigAverageIntegral(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.feature.orientation.ConfigAverageIntegral")


class ConfigDenseSampling(JavaConfig):
    def __init__(self, scale, periodX, periodY):
        JavaConfig.__init__(self, "boofcv.factory.feature.dense.ConfigDenseSample")
        self.scale = scale
        self.periodX = periodX
        self.periodY = periodY


class ConfigDenseSurfFast(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.dense.ConfigDenseSurfFast")


class ConfigDenseSurfStable(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.dense.ConfigDenseSurfStable")


class ConfigDenseSift(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.dense.ConfigDenseSift")


class ConfigDenseHoG(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.dense.ConfigDenseHoG")


class ConfigHoughGradient(JavaConfig):
    def __init__(self, max_lines=10):
        JavaConfig.__init__(self, "boofcv.factory.feature.detect.line.ConfigHoughGradient")
        self.maxLines = int(max_lines)


class ConfigHoughBinary(JavaConfig):
    def __init__(self, max_lines=10):
        JavaConfig.__init__(self, "boofcv.factory.feature.detect.line.ConfigHoughBinary")
        self.maxLines = int(max_lines)


class ConfigParamPolar(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.detect.line.ConfigParamPolar")


class ConfigParamFoot(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.detect.line.ConfigParamFoot")


class ConfigAssociate(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.associate.ConfigAssociate")


class ConfigAssociateGreedy(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.associate.ConfigAssociateGreedy")


class ConfigAssociateNearestNeighbor(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.feature.associate.ConfigAssociateNearestNeighbor")


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
    def __init__(self, score_type=AssocScoreType.DEFAULT, max_error=sys.float_info.max, backwards_validation=True):
        self.score_type = score_type
        self.max_error = max_error
        self.backwards_validation = backwards_validation


class AssociateDescription(JavaWrapper):
    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)

    def set_source(self, feature_list):
        """

        :param feature_list: List of feature descriptions
        :type feature_list: [[float]] | JavaList
        """
        # automatically convert from python to boof type
        if type(feature_list) is list:
            feature_list = p2b_list_descF64(feature_list)
        elif type(feature_list) is JavaList:
            feature_list = feature_list.java_obj
        else:
            raise Exception("unexpected list type " + feature_list.__class__.__name__)

        java_type = gateway.jvm.boofcv.struct.feature.TupleDesc_F64(0).getClass()

        fast_array = JavaList_to_fastarray(feature_list, java_type)
        self.java_obj.setSource(fast_array)

    def set_destination(self, feature_list):
        """

        :param feature_list: List of feature descriptions
        :type feature_list: [[float]] | JavaList
        """
        # automatically convert from python to boof type
        if type(feature_list) is list:
            feature_list = p2b_list_descF64(feature_list)
        elif type(feature_list) is JavaList:
            feature_list = feature_list.java_obj
        else:
            raise Exception("unexpected list type " + feature_list.__class__.__name__)

        java_type = gateway.jvm.boofcv.struct.feature.TupleDesc_F64(0).getClass()

        fast_queue = JavaList_to_fastarray(feature_list, java_type)
        self.java_obj.setDestination(fast_queue)

    def associate(self):
        """
        Associates the two sets of features together.  Returns a list of association indexes
        :return: List of (src index, dst index, match score)
        :rtype: [(int,int,float)]
        """
        output = []

        self.java_obj.associate()
        matches = self.java_obj.getMatches()
        for i in range(matches.getSize()):
            association = JavaWrapper(matches.get(i))
            output.append((association.src, association.dst, association.fitScore))

        return output

    def get_java_matches(self):
        return self.java_obj.getMatches()


def match_idx_to_point_pairs(matches, list_src, list_dst):
    """

    :param matches: List of (src index, dst index, ?)
    :param list_src: List of src points
    :param list_dst: List of dst points
    :return: List in point format (src point, dst point)
    """
    pairs = [None] * len(matches)
    for idx, m in enumerate(matches):
        a = list_src[m[0]]
        b = list_dst[m[1]]

        pairs[idx] = (a, b)
    return pairs


def read_list_tuple_desc_f64(f, list_length):
    output = []
    for i in range(list_length):
        desc_length = struct.unpack('>i', f.read(4))[0]
        desc = [0.0] * desc_length
        for j in range(desc_length):
            desc[j] = struct.unpack('>d', f.read(8))[0]
        output.append(desc)
    return output


def read_list(file_name):
    output = []
    with open(file_name, 'r') as f:
        data_type = f.readline()[0:-1]
        if data_type != "list":
            raise RuntimeError("Was expecting list in front of file not " + data_type)
        class_type = f.readline()
        list_length = struct.unpack('>i', f.read(4))[0]

        if "TupleDesc_F64" in class_type:
            output = read_list_tuple_desc_f64(f, list_length)
        else:
            raise RuntimeError("Unknown list data type " + class_type)

    if list_length != len(output):
        raise RuntimeError("Unexpected list size. " + str(list_length) + " " + str(len(output)))
    return output


def java_list_to_python(java_list):
    N = java_list.size()
    output = []
    if is_java_class(java_list.java_type, "boofcv.struct.feature.TupleDesc_F64"):
        for i in range(N):
            d = java_list.java_obj.get(i)
            value = d.getValue()  # some hackery to get around py4j short comings
            output.append([x for x in value])
    elif is_java_class(java_list.java_type, "georegression.struct.point.Point2D_F64"):
        for i in range(N):
            p = java_list.java_obj.get(i)
            output.append((p.x, p.y))
    else:
        raise RuntimeError("Unknown java list type")

    return output


class DetectDescribePointFeatures(JavaWrapper):
    def __init__(self, java_object):
        self.set_java_object(java_object)

    def detect(self, image):
        """
        Detects features inside the image and returns a list of feature locations and descriptions
        :param image: Image in BoofCV format
        :return: List of feature pixel locations and their descriptions. (2d pixel coordinates, list of descriptions)
        :rtype: (list[(float,float)],list[list[float]])
        """
        self.java_obj.detect(image)

        # extract a list of locations and descriptions.  Don't copy since it will immediately be convert
        # into a python format
        java_locations = gateway.jvm.pyboof.PyBoofEntryPoint.extractPoints(self.java_obj, False)
        java_descriptions = gateway.jvm.pyboof.PyBoofEntryPoint.extractFeatures(self.java_obj, False)

        # Convert into a Python format and return the two lists
        locations = pyboof.b2p_list_point2D(java_locations, np.double)
        descriptions = b2p_list_descF64(java_descriptions)

        return locations, descriptions

    def get_scales(self):
        N = self.java_obj.getNumberOfFeatures()
        output = [0] * N
        for i in range(N):
            output[i] = self.java_obj.getScale(i)
        return output

    def get_orientations(self):
        N = self.java_obj.getNumberOfFeatures()
        output = [0] * N
        for i in range(N):
            output[i] = self.java_obj.getOrientation(i)
        return output

    def has_scale(self):
        return self.java_obj.hasScale()

    def has_orientation(self):
        return self.java_obj.hasOrientation()

    def get_descriptor_type(self):
        return self.java_obj.getDescriptionType()


class DetectLine(JavaWrapper):
    def __init__(self, java_object):
        self.set_java_object(java_object)

    def detect(self, image):
        """
        Detects LineParametric2D inside the image
        """
        java_lines = self.java_obj.detect(image)
        output = []
        for l in java_lines:
            output.append(pyboof.LineParametric2D(l))
        return output


class DenseDescribePointFeatures(JavaWrapper):
    def __init__(self, java_object):
        self.set_java_object(java_object)
        self.descriptions = []
        self.locations = []

    def detect(self, image):
        self.java_obj.process(image)
        self.locations = pyboof.b2p_list_point2D(self.java_obj.getLocations(), np.int32)
        self.descriptions = b2p_list_descF64(self.java_obj.getDescriptions())


class ConfigPointTracker(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.tracker.ConfigPointTracker")


class PointTrack:
    def __init__(self):
        self.pixel = (0.0, 0.0)
        self.feature_id = -1
        self.spawn_frame_id = -1
        self.last_seen_frame_id = -1


class PointTracker(JavaWrapper):
    def __init__(self, java_object, java_image_type):
        self.set_java_object(java_object)
        self.java_image_type = java_image_type

    def process(self, image):
        """
        Updates existing tracks
        """
        self.java_obj.process(image)

    def reset(self):
        self.java_obj.reset()

    def get_frame_id(self):
        return self.java_obj.getFrameID()

    def get_total_active(self):
        return self.java_obj.getTotalActive()

    def get_total_inactive(self):
        return self.java_obj.getTotalInactive()

    def drop_all_tracks(self):
        self.java_obj.dropAllTracks()

    def get_all_tracks(self):
        return b2p_list_PointTrack(self.java_obj.getAllTracks(None))

    def get_active_tracks(self):
        return b2p_list_PointTrack(self.java_obj.getActiveTracks(None))

    def get_inactive_tracks(self):
        return b2p_list_PointTrack(self.java_obj.getInactiveTracks(None))

    def get_dropped_tracks(self):
        return b2p_list_PointTrack(self.java_obj.getDroppedTracks(None))

    def get_new_tracks(self):
        return b2p_list_PointTrack(self.java_obj.getNewTracks(None))

    def spawn_tracks(self):
        self.java_obj.spawnTracks()

    def get_image_type(self):
        return pyboof.ImageType(self.java_image_type)


def b2p_list_PointTrack(java_list):
    size = java_list.size()
    py_list = []

    for i in range(size):
        java_track = JavaWrapper(java_list.get(i))
        py_track = PointTrack()
        py_track.pixel = (float(java_track.pixel.x), float(java_track.pixel.y))
        py_track.feature_id = int(java_track.featureId)
        py_track.spawn_frame_id = int(java_track.spawnFrameID)
        py_track.last_seen_frame_id = int(java_track.lastSeenFrameID)
        py_list.append(py_track)

    return py_list


class FactoryDetectDescribe:
    def __init__(self, dtype):
        self.boof_image_class = dtype_to_Class_SingleBand(dtype)

    def createSurf(self, config_detect=None, config_desc=None, config_ori=None):
        """
        Creates a SURF detector and describer.

        :param config_detect:
        :type config_detect: ConfigFastHessian | None
        :param config_desc:
        :type config_desc: ConfigSurfFast | ConfigSurfStability | None
        :param config_ori:
        :type config_ori: ConfigAverageIntegral
        :return:
        :rtype: DetectDescribePointFeatures
        """
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
                java_config_detect, java_config_desc, java_config_ori, self.boof_image_class)
        elif config_desc.__class__.__name__ == "ConfigSurfStability":
            java_object = gateway.jvm.boofcv.factory.feature.detdesc.FactoryDetectDescribe.surfStable(
                java_config_detect, java_config_desc, java_config_ori, self.boof_image_class)
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
    def __init__(self, dtype):
        self.dtype = dtype
        self.boof_image_class = dtype_to_Class_SingleBand(dtype)
        self.py_image_type = pyboof.create_ImageType(pyboof.Family.SINGLE_BAND, self.dtype)

    def createSurf(self, config_desc=None):
        if config_desc is None:
            config_desc = ConfigDenseSurfFast()

        java_config_desc = config_desc.java_obj

        if config_desc.__class__.__name__ == "ConfigDenseSurfFast":
            java_object = gateway.jvm.boofcv.factory.feature.dense.FactoryDescribeImageDense.surfFast(
                java_config_desc, self.boof_image_class)
        elif config_desc.__class__.__name__ == "ConfigDenseSurfStable":
            java_object = gateway.jvm.boofcv.factory.feature.dense.FactoryDescribeImageDense.surfStable(
                java_config_desc, self.boof_image_class)
        else:
            raise RuntimeError("Unknown description type")

        return DenseDescribePointFeatures(java_object)

    def createSift(self, config=None):
        if config is None:
            config = ConfigDenseSift()

        java_config_desc = config.java_obj

        java_object = gateway.jvm.boofcv.factory.feature.dense.FactoryDescribeImageDense.sift(
            java_config_desc, self.boof_image_class)
        return DenseDescribePointFeatures(java_object)

    def createHoG(self, config=None):
        if config is None:
            config = ConfigDenseHoG()

        java_config_desc = config.java_obj

        # HoG supports color images also. For now we will just support gray

        java_object = gateway.jvm.boofcv.factory.feature.dense.FactoryDescribeImageDense.hog(
            java_config_desc, self.py_image_type.java_obj)
        return DenseDescribePointFeatures(java_object)


class FactoryAssociate:
    def __init__(self):
        self.score = None

    def set_score(self, score_type, descriptor_type):
        if score_type == AssocScoreType.DEFAULT:
            self.score = gateway.jvm.boofcv.factory.feature.associate. \
                FactoryAssociation.defaultScore(descriptor_type)
        elif score_type == AssocScoreType.EUCLIDEAN:
            self.score = gateway.jvm.boofcv.factory.feature.associate. \
                FactoryAssociation.scoreEuclidean(descriptor_type, False)
        elif score_type == AssocScoreType.EUCLIDEAN_SQ:
            self.score = gateway.jvm.boofcv.factory.feature.associate. \
                FactoryAssociation.scoreEuclidean(descriptor_type, True)
        elif score_type == AssocScoreType.NCC:
            self.score = gateway.jvm.boofcv.factory.feature.associate. \
                FactoryAssociation.scoreNcc()
        elif score_type == AssocScoreType.SAD:
            self.score = gateway.jvm.boofcv.factory.feature.associate. \
                FactoryAssociation.scoreSad(descriptor_type)

    def generic(self, config: ConfigAssociate, info):
        java_obj = gateway.jvm.boofcv.factory.feature.associate. \
            FactoryAssociation.generic(config.java_obj, info)
        return AssociateDescription(java_obj)

    def greedy(self, config: ConfigAssociateGreedy):
        java_obj = gateway.jvm.boofcv.factory.feature.associate. \
            FactoryAssociation.greedy(config.java_obj, self.score)
        return AssociateDescription(java_obj)

    # def nearest_neighbor(self, config: ConfigAssociateNearestNeighbor):
    #     java_obj = gateway.jvm.boofcv.factory.feature.associate.\
    #             FactoryAssociation.associateNearestNeighbor(config.java_obj, self.score)
    #     return AssociateDescription(java_obj)


class FactoryDetectLine:
    def __init__(self, dtype):
        self.boof_image_class = dtype_to_Class_SingleBand(dtype)

    def houghLinePolar(self, config_hough, config_polar=None):
        if not config_polar:
            config_polar = ConfigParamPolar()
        java_object = gateway.jvm.boofcv.factory.feature.detect.line. \
            FactoryDetectLine.houghLinePolar(config_hough.java_obj, config_polar.java_obj, self.boof_image_class)
        return DetectLine(java_object)

    def houghLineFoot(self, config_hough, config_foot=None):
        if not config_foot:
            config_foot = ConfigParamFoot()
        java_object = gateway.jvm.boofcv.factory.feature.detect.line. \
            FactoryDetectLine.houghLineFoot(config_hough.java_obj, config_foot.java_obj, self.boof_image_class)
        return DetectLine(java_object)


class FactoryPointTracker:
    def __init__(self, dtype):
        self.boof_image_class = dtype_to_Class_SingleBand(dtype)
        self.boof_image_type = dtype_to_ImageType(dtype) # TODO remove after getImageType() is added to PointTracker

    def generic(self, config_tracker:ConfigPointTracker):
        java_object = gateway.jvm.boofcv.factory.tracker. \
            FactoryPointTracker.tracker(config_tracker.java_obj, self.boof_image_class, None)
        return PointTracker(java_object, self.boof_image_type)


def mmap_list_python_to_TupleF64(pylist, java_list):
    """
    Converts a python list of float arrays into a list of TupleDesk64F in java using memmap file
    :param pylist: (Input) Python list of float arrays.  All arrays need to have the same length
    :type pylist: list[list[float]]
    :param java_list: (Output) Java list to store TupleDesc64F
    """
    num_elements = len(pylist)
    if num_elements == 0:
        dof = 0
    else:
        dof = len(pylist[0])
    mm = pyboof.mmap_file

    # max number of list elements it can write at once
    max_elements = (pyboof.mmap_size - 100) / (dof * 8)

    curr = 0
    while curr < num_elements:
        # Write as much of the list as it can to the mmap file
        num_write = min(max_elements, num_elements - curr)
        mm.seek(0)
        mm.write(struct.pack('>HII', pyboof.MmapType.LIST_TUPLE_F64, num_elements, dof))
        for i in range(curr, curr + num_write):
            mm.write(struct.pack('>%sd' % dof, *pylist[i]))

        # Now tell the java end to read what it just wrote
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.read_List_TupleF64(java_list)

        # move on to the next block
        curr = curr + num_write


def mmap_list_TupleF64_to_python(java_list, pylist):
    """
    Converts a java list of TupleDesc64F into a python list of float arrays using memmap file
    :param java_list: Input: java list
    :param pylist: output: python list
    :type pylist: list[list[float]]
    """
    num_elements = java_list.size()
    mm = pyboof.mmap_file

    num_read = 0
    while num_read < num_elements:
        gateway.jvm.pyboof.PyBoofEntryPoint.mmap.write_List_TupleF64(java_list, num_read)
        mm.seek(0)
        data_type, num_found, dof = struct.unpack(">HII", mm.read(2 + 4 + 4))
        if data_type != pyboof.MmapType.LIST_TUPLE_F64:
            raise Exception("Unexpected data type in mmap file. {%d}" % data_type)
        if num_found > num_elements - num_read:
            raise Exception("Too many elements returned. " + str(num_found))
        for i in range(num_found):
            desc = struct.unpack(">%sd" % dof, mm.read(8 * dof))
            pylist.append(desc)
        num_read += num_found
