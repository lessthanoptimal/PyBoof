from pyboof.geo import *
from pyboof.calib import *
from pyboof import gateway
from pyboof import MmapType
from py4j.java_collections import ListConverter
import tempfile


def string_to_bytearray(message: str):
    """
    Converts a string into a bytearray. This effectively does a 'static_cast' of the String into byte[]. Useful when
    a marker encodes a binary format such as a zip file
    """
    raw_data = bytearray(len(message))
    for i in range(len(raw_data)):
        raw_data[i] = ord(message[i]) % 256
        # If the unicode value is outside the 8-bit range the data is likely to be corrupted... but wont crash@
    return raw_data


class ConfigPolygonDetector(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.struct.Configuration.ConfigPolygonDetector")


class ConfigFiducialImage(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigFiducialImage")


class ConfigFiducialBinary(JavaConfig):
    def __init__(self, target_width=None):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigFiducialBinary")
        if target_width is not None:
            self.targetWidth = float(target_width)


class ConfigHammingMarker(JavaConfig):
    def __init__(self, target_width=None):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigHammingMarker")
        if target_width is not None:
            self.targetWidth = float(target_width)


class ConfigFiducialHammingDetector(JavaConfig):
    def __init__(self, config=None):
        if config:
            JavaConfig.__init__(self, config)
        else:
            JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigFiducialHammingDetector")


class HammingDictionary:
    """
    List of prebuilt hamming dictionaries
    """
    CUSTOM = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.CUSTOM
    ARUCO_ORIGINAL = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_ORIGINAL
    ARUCO_MIP_16h3 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_MIP_16h3
    ARUCO_MIP_25h7 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_MIP_25h7
    ARUCO_MIP_36h12 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_MIP_36h12
    ARUCO_OCV_4x4_1000 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_OCV_4x4_1000
    ARUCO_OCV_5x5_1000 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_OCV_5x5_1000
    ARUCO_OCV_6x6_1000 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_OCV_6x6_1000
    ARUCO_OCV_7x7_1000 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.ARUCO_OCV_7x7_1000
    APRILTAG_16h5 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.APRILTAG_16h5
    APRILTAG_25h7 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.APRILTAG_25h7
    APRILTAG_25h9 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.APRILTAG_25h9
    APRILTAG_36h10 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.APRILTAG_36h10
    APRILTAG_36h11 = gateway.jvm.boofcv.factory.fiducial.HammingDictionary.APRILTAG_36h11


class ConfigGridDimen(JavaConfig):
    def __init__(self, num_rows, num_cols, square_width):
        java_obj = gateway.jvm.boofcv.abst.fiducial.calib.ConfigGridDimen(
            int(num_rows), int(num_cols), float(square_width))
        JavaConfig.__init__(self, java_obj)


class ConfigChessboardBinary(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigChessboardBinary")


class ConfigChessboardX(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigChessboardX")


class ConfigSquareGrid(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigSquareGrid")


class ConfigSquareGridBinary(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigSquareGridBinary")


class ConfigCircleHexagonalGrid(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigCircleHexagonalGrid")


class ConfigCircleRegularGrid(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigCircleRegularGrid")


class ConfigQrCode(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigQrCode")


class ConfigMicroQrCode(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigMicroQrCode")


class ConfigAztecCode(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigAztecCode")


class ConfigUchiyaMarker(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigUchiyaMarker")


class ConfigECoCheckMarkers(JavaConfig):
    def __init__(self, java_config=None):
        if java_config:
            JavaConfig.__init__(self, java_config)
        else:
            JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigECoCheckMarkers")


class ConfigECoCheckDetector(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.fiducial.calib.ConfigECoCheckDetector")


def ecocheck_parse(description: str, square_size: float) -> ConfigECoCheckMarkers:
    """
    Parses string summary of an ECoCheck marker.
    Example 9x7n1e3c6, 9x7 grid, 1 marker, ecc=3, checksum=6bits.
    Example 9x7n2, 9x7 grid, 2 markers, default ecc and checksum.

    :param description: String summary of ECoCheck configuration
    :param square_size: How big a square in the chessboard pattern is
    """
    return ConfigECoCheckMarkers(gateway.jvm.boofcv.abst.fiducial.calib.ConfigECoCheckMarkers.
                                 parse(description, square_size))


def load_hamming_marker(dictionary):
    """
    Loads the specified prebuilt dictionary

    :param dictionary: Which dictionary
    :type dictionary: HammingDictionary
    :return: Marker configuration
    :rtype: ConfigFiducialHammingDetector
    """
    if dictionary == HammingDictionary.CUSTOM:
        raise RuntimeError("Custom dictionary")

    return ConfigFiducialHammingDetector(
        gateway.jvm.boofcv.factory.fiducial.ConfigHammingMarker.loadDictionary(dictionary))


class FiducialCalibrationDetector(JavaWrapper):
    """
    Fiducial detector for calibration targets.  Stores the list of known locations in the 2D fiducial reference
    frame on self.layout.  After detect is called self.detected_points is a list of all the detected calibration
    points seen in the image.  (index,x,y) where index refers to which point in the layout and (x,y) is the pixel
    coordinate.
    """

    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)
        self.detected_points = []
        self.layout = b2p_list_point2D(java_object.getLayout(), np.double)

    def detect(self, image):
        self.java_obj.process(image)

        self.detected_points = []
        jdetected = self.java_obj.getDetectedPoints()
        for i in range(jdetected.size()):
            jp = jdetected.get(i)
            pixel = jp.getP()
            self.detected_points.append((jp.getIndex(), pixel.getX(), pixel.getY()))


class FiducialCalibrationDetectorMulti(JavaWrapper):
    """
    Calibration fiducial detector which can handle multiple unique markers
    """

    def __init__(self, java_object):
        JavaWrapper.__init__(self, java_object)
        self.detected_markers = []
        # This is hard coded for a single target right now
        self.layout = b2p_list_point2D(java_object.getLayout(0), np.double)

    def detect(self, image):
        self.java_obj.process(image)

        self.detected_markers = []
        num_detections = self.java_obj.getDetectionCount()

        for detection_idx in range(num_detections):
            jobs = self.java_obj.getDetectedPoints(detection_idx)
            marker_id = self.java_obj.getMarkerID(detection_idx)
            landmarks = []
            jdetected = self.java_obj.getDetectedPoints(detection_idx)
            for i in range(jdetected.size()):
                jp = jdetected.get(i)
                pixel = jp.getP()
                landmarks.append((jp.getIndex(), pixel.getX(), pixel.getY()))
            self.detected_markers.append({"marker": marker_id, "landmarks": landmarks})


class FiducialDetector(JavaWrapper):
    """
    Detects fiducials and estimates their ID, 3D pose, and image location.
    Wrapper around BoofCV class of the same name
    """

    def __init__(self, java_FiducialDetector):
        JavaWrapper.__init__(self, java_FiducialDetector)

    def detect(self, image):
        self.java_obj.detect(image)

    def set_intrinsic(self, intrinsic):
        if intrinsic is None:
            self.java_obj.setLensDistortion(None, -1, -1)
        else:
            distortion = create_narrow_lens_distorter(intrinsic)
            self.java_obj.setLensDistortion(distortion.java_obj,
                                            intrinsic.width, intrinsic.height)

    def get_total(self) -> int:
        return self.java_obj.totalFound()

    def is_3d(self) -> bool:
        return self.java_obj.is3D()

    def get_fiducial_to_camera(self, which: int) -> Se3_F64:
        """
        Returns the rigid body transform from the fiducial to the camera

        :param which: Index of detected fiducial.
        :return: Rigid Body Transform
        """
        fid_to_cam = Se3_F64()
        self.java_obj.getFiducialToCamera(which, fid_to_cam.get_java_object())
        return fid_to_cam

    def get_bounds(self, which) -> Polygon2D:
        return Polygon2D(self.java_obj.getBounds(which, None))

    def get_center(self, which):
        location = gateway.jvm.georegression.struct.point.Point2D_F64()
        self.java_obj.getCenter(which, location)
        return location.getX(), location.getY()

    def get_id(self, which):
        return self.java_obj.getId(which)

    def get_width(self, which) -> int:
        return self.java_obj.getWidth(which)

    def get_input_type(self) -> ImageType:
        return ImageType(self.java_obj.get_input_type())


class FiducialImageDetector(FiducialDetector):
    def add_pattern(self, image, side_length, threshold=100.0):
        self.java_obj.addPatternImage(image, threshold, side_length)


class QrCode:
    """Description of a detected QR Code inside an image.

    """

    def __init__(self, java_object=None):
        if java_object is None:
            self.version = -1
            self.message = ""
            self.corrected = None  # raw byte data after error correction
            self.byteEncoding = ""  # Encoding used when in BYTE mode
            self.totalBitErrors = -1  # Number of errors detected in error correction
            self.bitsTransposed = False  # true if the QR code is transposed
            self.error_level = ""
            self.mask_pattern = ""
            self.mode = ""
            self.failure_cause = ""
            self.bounds = Polygon2D(4)
            self.pp_right = Polygon2D(4)
            self.pp_corner = Polygon2D(4)
            self.pp_down = Polygon2D(4)
        else:
            jobj = JavaWrapper(java_object)
            self.version = jobj.version
            self.message = jobj.message
            self.corrected = mmap_array_java_to_python(jobj.corrected, MmapType.ARRAY_U8)
            self.byteEncoding = jobj.byteEncoding
            self.totalBitErrors = jobj.totalBitErrors
            self.bitsTransposed = jobj.bitsTransposed
            self.error_level = jobj.error.toString()
            self.mask_pattern = jobj.mask.toString()
            self.mode = jobj.mode.toString()
            self.failure_cause = ""
            self.bounds = Polygon2D(jobj.bounds)
            self.pp_right = Polygon2D(jobj.ppRight)
            self.pp_corner = Polygon2D(jobj.ppCorner)
            self.pp_down = Polygon2D(jobj.ppDown)

            if jobj.failureCause is not None:
                self.failure_cause = jobj.failureCause.toString()


class QrCodeDetector(JavaWrapper):
    """Detects QR Codes inside of images

    Attributes:
        detections: List of detected QrCodes
        failures: List of objects that are highly likely to be a QR Code but were rejected.
    """

    def __init__(self, java_detector):
        JavaWrapper.__init__(self, java_detector)
        self.detections = []
        self.failures = []

    def detect(self, image):
        self.java_obj.process(image)
        self.detections = [QrCode(x) for x in self.java_obj.getDetections()]
        self.failures = [QrCode(x) for x in self.java_obj.getFailures()]

    def get_image_type(self):
        return ImageType(self.java_obj.getImageType())


class MicroQrCode:
    """Description of a detected Micro QR Code inside an image.

    """

    def __init__(self, java_object=None):
        if java_object is None:
            self.version = -1
            self.message = ""
            self.corrected = None  # raw byte data after error correction
            self.byteEncoding = ""  # Encoding used when in BYTE mode
            self.totalBitErrors = -1  # Number of errors detected in error correction
            self.bitsTransposed = False  # true if the QR code is transposed
            self.error_level = ""
            self.mask_pattern = ""
            self.mode = ""
            self.failure_cause = ""
            self.bounds = Polygon2D(4)
            self.pp = Polygon2D(4)
        else:
            jobj = JavaWrapper(java_object)
            self.version = jobj.version
            self.message = jobj.message
            self.corrected = mmap_array_java_to_python(jobj.corrected, MmapType.ARRAY_U8)
            self.byteEncoding = jobj.byteEncoding
            self.totalBitErrors = jobj.totalBitErrors
            self.bitsTransposed = jobj.bitsTransposed
            self.error_level = jobj.error.toString()
            self.mask_pattern = jobj.mask.toString()
            self.mode = jobj.mode.toString()
            self.failure_cause = ""
            self.bounds = Polygon2D(jobj.bounds)
            self.pp = Polygon2D(jobj.pp)

            if jobj.failureCause is not None:
                self.failure_cause = jobj.failureCause.toString()


class MicroQrDetector(JavaWrapper):
    """Detects Micro QR Codes inside of images

    Attributes:
        detections: List of detected MicroQrCode
        failures: List of objects that are highly likely to be a Micro QR Codes but were rejected.
    """

    def __init__(self, java_detector):
        JavaWrapper.__init__(self, java_detector)
        self.detections = []
        self.failures = []

    def detect(self, image):
        self.java_obj.process(image)
        self.detections = [MicroQrCode(x) for x in self.java_obj.getDetections()]
        self.failures = [MicroQrCode(x) for x in self.java_obj.getFailures()]

    def get_image_type(self):
        return ImageType(self.java_obj.getImageType())


class AztecCode:
    """Description of a detected Aztec Code inside an image.

    """

    def __init__(self, java_object=None):
        if java_object is None:
            self.dataLayers = 0
            self.messageWordCount = 0
            self.rawbits = None  # raw byte data
            self.corrected = None  # raw byte data after error correction
            self.message = ""
            self.structure = ""
            self.failure = ""
            self.transposed = False   # true if the marker is transposed
            self.totalBitErrors = -1  # Number of errors detected in error correction
            self.bounds = Polygon2D(4)
        else:
            jobj = JavaWrapper(java_object)
            self.dataLayers = jobj.dataLayers
            self.messageWordCount = jobj.messageWordCount
            self.rawbits = mmap_array_java_to_python(jobj.rawbits, MmapType.ARRAY_U8)
            self.corrected = mmap_array_java_to_python(jobj.corrected, MmapType.ARRAY_U8)
            self.message = jobj.message
            self.structure = jobj.structure.toString()
            self.transposed = jobj.transposed
            self.totalBitErrors = jobj.totalBitErrors
            self.bounds = Polygon2D(jobj.bounds)

            if jobj.failure is not None:
                self.failure_cause = jobj.failure.toString()


class AztecCodeDetector(JavaWrapper):
    """Detects Aztec Codes inside of images

    Attributes:
        detections: List of detected AztecCode
        failures: List of objects that are highly likely to be Aztec Codes but were rejected.
    """

    def __init__(self, java_detector):
        JavaWrapper.__init__(self, java_detector)
        self.detections = []
        self.failures = []

    def detect(self, image):
        self.java_obj.process(image)
        self.detections = [AztecCode(x) for x in self.java_obj.getDetections()]
        self.failures = [AztecCode(x) for x in self.java_obj.getFailures()]

    def get_image_type(self):
        return ImageType(self.java_obj.getImageType())


class UchiyaRandomDotDetector(FiducialDetector):
    """Detector for random dot markers
    """

    def __init__(self, java_detector):
        JavaWrapper.__init__(self, java_detector)
        self.detections = []
        self.failures = []

    def add_marker(self, marker):
        self.java_obj.addMarker(marker)


class FactoryFiducialCalibration:
    def __init__(self):
        pass

    @staticmethod
    def chessboardX(config_grid: ConfigGridDimen,
                    config_detector: ConfigChessboardX = None) -> FiducialCalibrationDetector:
        """
        Creates a chessboard detector based on x-corners. Slower but very robust.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :return: Calibration target detector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration. \
            chessboardX(cdj, config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def chessboardB(config_grid: ConfigGridDimen,
                    config_detector: ConfigChessboardBinary = None) -> FiducialCalibrationDetector:
        """
        Creates a chessboard detector based on binary images. Fast but not as robust.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :return: Calibration target detector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial. \
            FactoryFiducialCalibration.chessboardB(cdj, config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def ecocheck(config_marker: ConfigECoCheckMarkers, config_detector: ConfigECoCheckDetector = None) \
            -> FiducialCalibrationDetectorMulti:
        """
        Create an ECoCheck detector.

        :param config_marker:  Configuration for marker
        :param config_detector: Specifies how to detect the marker
        :return: Calibration target detector
        """
        jdetector = None
        if config_detector:
            jdetector = config_detector.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration. \
            ecocheck(jdetector, config_marker.java_obj)
        return FiducialCalibrationDetectorMulti(java_detector)

    @staticmethod
    def square_grid(config_grid: ConfigGridDimen,
                    config_detector: ConfigSquareGrid = None) -> FiducialCalibrationDetector:
        """
        Creates a square grid detector

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :return: Calibration target detector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration.squareGrid(cdj,
                                                                                                  config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def circle_hexagonal_grid(config_grid: ConfigGridDimen,
                              config_detector: ConfigCircleHexagonalGrid = None) -> FiducialCalibrationDetector:
        """
        Detector for hexagonal grid of circles.  All circles must be entirely inside of the image.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :return: Calibration target detector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration. \
            circleHexagonalGrid(cdj, config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def circle_regular_grid(config_grid: ConfigGridDimen,
                            config_detector: ConfigCircleRegularGrid = None) -> FiducialCalibrationDetector:
        """
        Detector for regular grid of circles.  All circles must be entirely inside of the image.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :return: Calibration target detector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration. \
            circleRegularGrid(cdj, config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)


class FactoryFiducial:
    def __init__(self, dtype):
        """
        Configures factory for the specific image type
        :param dtype: Type of single band image
        """
        self.boof_image_type = dtype_to_Class_SingleBand(dtype)

    def square_image(self, config_fiducial: ConfigFiducialImage,
                     config_threshold: ConfigThreshold) -> FiducialImageDetector:
        """
        Creates a square image fiducial detector

        :param config_fiducial: configuration for the fiducial
        :param config_threshold: Configuration for image thresholding step
        :return: The detector
        """
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            squareImage(config_fiducial.java_obj, config_threshold.java_obj, self.boof_image_type)
        return FiducialImageDetector(java_detector)

    def square_binary(self, config_fiducial: ConfigFiducialBinary, config_threshold: ThresholdType) -> FiducialDetector:
        """
        Creates a binary image fiducial detector

        :param config_fiducial: configuration for the fiducial
        :param config_threshold: Configuration for image thresholding step
        :return: The detector
        """
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            squareBinary(config_fiducial.java_obj, config_threshold.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def square_hamming(self, config_fiducial: ConfigHammingMarker,
                       config_detector: ConfigFiducialHammingDetector = None):
        """
        Creates a binary image fiducial detector

        :param config_fiducial: configuration for the fiducial
        :param config_threshold: Configuration for image thresholding step
        :return: The detector
        """
        jconfig_detector = None
        if config_detector:
            jconfig_detector = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            squareHamming(config_fiducial.java_obj, jconfig_detector, self.boof_image_type)
        return FiducialDetector(java_detector)

    def chessboardB(self, config_grid: ConfigGridDimen,
                    config_detector: ConfigChessboardBinary = None) -> FiducialDetector:
        """
        Chessboard detector binary image

        :param config_grid: Specifies the Grid's shape
        :param config_detector: Fiducial configuration
        :return: FiducialDetector
        :rtype: FiducialDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            calibChessboardB(cdj, config_grid.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def chessboardX(self, config_grid: ConfigGridDimen, config_detector: ConfigChessboardX = None) -> FiducialDetector:
        """
        Chessboard detector X-corner

        :param config_grid: Specifies the Grid's shape
        :param config_detector: Fiducial configuration
        :return: FiducialDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            calibChessboardX(cdj, config_grid.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def square_grid(self, config_grid: ConfigGridDimen,
                    config_detector: ConfigSquareGrid = None) -> FiducialDetector:
        """
        Square grid detector

        :param config_detector: Fiducial configuration
        :param config_grid: Specifies the Grid's shape
        :return: FiducialDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            calibSquareGrid(cdj, config_grid.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def qrcode(self, config: ConfigQrCode = None) -> QrCodeDetector:
        """ Creates a detector for QR Codes

        :param config: ConfigQrCode or None
        :return: QrCodeDetector
        """
        if config is None:
            jconf = None
        else:
            jconf = config.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            qrcode(jconf, self.boof_image_type)
        return QrCodeDetector(java_detector)

    def microqr(self, config: ConfigMicroQrCode = None) -> MicroQrDetector:
        """ Creates a detector for Micro QR Codes

        :param config: ConfigMicroQrCode or None
        :return: MicroQrDetector
        """
        if config is None:
            jconf = None
        else:
            jconf = config.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            microqr(jconf, self.boof_image_type)
        return MicroQrDetector(java_detector)

    def aztec(self, config: ConfigAztecCode = None) -> AztecCodeDetector:
        """ Creates a detector for QR Codes

        :param config: ConfigQrCode or None
        :return: QrCodeDetector
        """
        if config is None:
            jconf = None
        else:
            jconf = config.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            aztec(jconf, self.boof_image_type)
        return AztecCodeDetector(java_detector)

    def random_dots(self, config: ConfigUchiyaMarker) -> UchiyaRandomDotDetector:
        """ Creates a detector random dot / Uchiya markers

        :param config: ConfigUchiyaMarker or None
        :return: ConfigUchiyaMarker
        """
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            randomDots(config.java_obj, self.boof_image_type)
        return UchiyaRandomDotDetector(java_detector)


def string_to_qrcode_error(error):
    if error == "L":
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCode.ErrorLevel.L
    elif error == "M":
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCode.ErrorLevel.M
    elif error == "Q":
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCode.ErrorLevel.Q
    elif error == "H":
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCode.ErrorLevel.H
    else:
        return None


def int_to_qrcode_mask(mask):
    if mask == 0b000:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M000
    elif mask == 0b001:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M001
    elif mask == 0b010:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M010
    elif mask == 0b011:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M011
    elif mask == 0b100:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M100
    elif mask == 0b101:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M101
    elif mask == 0b110:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M110
    elif mask == 0b111:
        return gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeMaskPattern.M111
    else:
        return None


def string_to_microqr_error(error):
    if error == "L":
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCode.ErrorLevel.L
    elif error == "M":
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCode.ErrorLevel.M
    elif error == "Q":
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCode.ErrorLevel.Q
    else:
        return None


def int_to_microqr_mask(mask):
    if mask == 0b00:
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCodeMaskPattern.M000
    elif mask == 0b01:
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCodeMaskPattern.M001
    elif mask == 0b10:
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCodeMaskPattern.M010
    elif mask == 0b11:
        return gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCodeMaskPattern.M011
    else:
        return None


class QrCodeGenerator:
    """Converts a message into a QR Code that meets your specification

    """

    def __init__(self, pixels_per_module=4):
        self.java_encoder = gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeEncoder()
        self.java_generator = gateway.jvm.boofcv.alg.fiducial.qrcode.QrCodeGeneratorImage(pixels_per_module)

    def reset(self):
        self.java_encoder.reset()

    def set_version(self, version):
        self.java_encoder.setVersion(version)

    def set_error(self, level):
        """Specifies error level for encoded QR Code

        :param level: String that can be "L","M","Q","H"
        """
        self.java_encoder.setError(string_to_qrcode_error(level))

    def set_mask(self, mask):
        """Specifies the type of mask to use. If not specified then it's automatically selected.
        Probably shouldn't mess with this unless you have a very good reason.

        :param mask: 0b000, 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111
        """
        self.java_encoder.setMask(string_to_qrcode_error(mask))

    def set_message(self, message):
        self.java_encoder.addAutomatic(str(message))

    def generate(self):
        qr = self.java_encoder.fixate()
        self.java_generator.render(qr)
        return self.java_generator.getGray()


class MicroQrCodeGenerator:
    """Converts a message into a Micro QR Code that meets your specification
    """

    def __init__(self, pixels_per_module=4):
        self.pixels_per_module = int(pixels_per_module)
        self.java_encoder = gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCodeEncoder()
        self.java_generator = gateway.jvm.boofcv.alg.fiducial.microqr.MicroQrCodeGenerator()
        self.java_engine = gateway.jvm.boofcv.alg.drawing.FiducialImageEngine()
        self.java_generator.setRender(self.java_engine)

    def reset(self):
        self.java_encoder.reset()

    def set_version(self, version):
        self.java_encoder.setVersion(version)

    def set_error(self, level):
        """Specifies error level for encoded Micro QR Code

        :param level: String that can be "L","M","Q"
        """
        self.java_encoder.setError(string_to_microqr_error(level))

    def set_mask(self, mask):
        """Specifies the type of mask to use. If not specified then it's automatically selected.
        Probably shouldn't mess with this unless you have a very good reason.

        :param mask: 0b00, 0b01, 0b11, 0b10
        """
        self.java_encoder.setMask(string_to_microqr_error(mask))

    def set_message(self, message):
        self.java_encoder.addAutomatic(str(message))

    def generate(self):
        qr = self.java_encoder.fixate()
        pixel_width = qr.getNumberOfModules() * self.pixels_per_module
        self.java_engine.configure(0, pixel_width)
        self.java_generator.setMarkerWidth(float(pixel_width))
        self.java_generator.render(qr)
        return self.java_engine.getGray()


class SquareHammingGenerator:
    """
    Renders hamming type square markers
    """

    def __init__(self, config, pixels_per_square=4):
        """
        Renders hamming type markers

        :param config: Configuration for the marker
        :type config: ConfigHammingMarker
        :param pixels_per_square: Number of pixels wide each square is
        :type pixels_per_square: int
        """
        self.border_pixels = 0
        self.pixels_per_square = pixels_per_square
        self.java_generator = gateway.jvm.boofcv.alg.fiducial.square.FiducialSquareHammingGenerator(config.java_obj)
        self.java_engine = gateway.jvm.boofcv.alg.drawing.FiducialImageEngine()
        self.java_generator.setRenderer(self.java_engine)

    def generate(self, marker_idx):
        """
        Renders the specified marker into a gray scale image
        :param marker_idx: index of the marker to render. An exception is thrown if out of bounds
        :return: Rendered marker
        :rtype: BoofCV image type
        """

        marker_width = self.java_generator.getMarkerWidth()
        render.configure(whiteBorderPixels, int(marker_width))
        self.java_generator.generate(marker_idx)
        return elf.java_engine.getGray()


class ConfigCirculant(JavaConfig):
    def __init__(self, java_object=None):
        JavaConfig.__init__(self, java_object)


class ConfigTrackerTld(JavaConfig):
    def __init__(self, obj=None):
        """
        :param obj: Java object, bool, None
            If True then it will create a stable variant.  False for fast but less stable.
            None for stable
            ConfigTld for user specified configuration
        """
        if obj is None:
            config = gateway.jvm.boofcv.abst.tracker.ConfigTrackerTld()
        elif type(obj) is bool:
            config = gateway.jvm.boofcv.abst.tracker.ConfigTrackerTld(obj)
        else:
            config = obj
        JavaConfig.__init__(self, config)


class ConfigMeanShiftComaniciu(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.tracker.ConfigComaniciu2003")


class FactoryTrackerObjectQuad:
    def __init__(self, image_type):
        """
        Creates a factory for a specific image type.
        :param image_type: Specifies the type of image it processes.  Can be a dtype or ImageType
        :type image_type: int | ImageType
        """
        if isinstance(image_type, ImageType):
            self.image_type = image_type
        else:
            self.image_type = ImageType(dtype_to_ImageType(image_type))

    def circulant(self, config=None):
        """
        Creates a Circulant tracker
        :param config: Configuration for tracker or None to use default
        :type config: None | ConfigCirculant
        :return: Tracker
        :rtype: TrackerObjectQuad
        """
        boof_image_class = self.image_type.java_obj.getImageClass()
        java_tracker = gateway.jvm.boofcv.factory.tracker. \
            FactoryTrackerObjectQuad.circulant(config, boof_image_class)
        return TrackerObjectQuad(java_tracker)

    def tld(self, config=None):
        """
        Creates a TLD tracker
        :param config: Configuration for tracker or None to use default
        :type config: None | ConfigTld
        :return: Tracker
        :rtype: TrackerObjectQuad
        """
        boof_image_class = self.image_type.java_obj.getImageClass()
        if config is None:
            java_conf = None
        else:
            java_conf = config.java_obj
        java_tracker = gateway.jvm.boofcv.factory.tracker. \
            FactoryTrackerObjectQuad.tld(java_conf, boof_image_class)
        return TrackerObjectQuad(java_tracker)

    def mean_shift_comaniciu(self, config=None):
        """
        Creates a Comaniciu (histogram based) style Mean-Shift tracker
        :param config: Configuration for tracker or None to use default
        :type config: None | ConfigMeanShiftComaniciu
        :return: Tracker
        :rtype: TrackerObjectQuad
        """
        if config is None:
            java_conf = None
        else:
            java_conf = config.java_obj
        java_tracker = gateway.jvm.boofcv.factory.tracker.FactoryTrackerObjectQuad. \
            meanShiftComaniciu2003(java_conf, self.image_type.java_obj)
        return TrackerObjectQuad(java_tracker)


class TrackerObjectQuad(JavaWrapper):
    """
    High level object tracker.  Takes in a quadrilateral for the initial location of the target then proceeds to
    update it for each new image in the sequence
    """

    def __init__(self, java_TrackerObjectQuad):
        JavaWrapper.__init__(self, java_TrackerObjectQuad)

    def initialize(self, image, location):
        """
        Initialize the tracker by specifying the location of the target inside the image

        :param image: BoofCV image
        :param location: Quadrilateral2D
           Specifies the location inside the quadrilateral
        :return: bool
           True if initialization was successful or False if it failed
        """
        boof_quad = location.convert_to_boof()
        return self.java_obj.initialize(image, boof_quad)

    def process(self, image, location):
        """
        Updates the target's location using the next image in the sequence.

        :param image: BoofCV image
        :param location: Quadrilateral2D
           (output) Will contain the new location of the tracked object
        :return: bool
           True if tracking was successful or False if it failed
        """
        boof_quad = location.convert_to_boof()
        success = self.java_obj.process(image, boof_quad)
        if success:
            location.set(boof_quad)
        return success

    def get_image_type(self):
        return ImageType(self.java_obj.getImageType())


class RandomDotDefinition(JavaWrapper):
    def __init__(self, java_object=None):
        if java_object:
            JavaWrapper.__init__(self, java_object)
        else:
            JavaWrapper.__init__(self, "boofcv.io.fiducial.RandomDotDefinition")


def save_random_dot_yaml(definition: RandomDotDefinition, path: str):
    java_writer = create_java_file_writer(path)
    gateway.jvm.boofcv.io.fiducial.FiducialIO.saveRandomDotYaml(definition, java_writer)


def load_random_dot_yaml(path: str):
    java_file = gateway.jvm.java.io.File(path)
    java_obj = gateway.jvm.boofcv.io.fiducial.FiducialIO.loadRandomDotYaml(java_file)
    return RandomDotDefinition(java_obj)


class SceneRecognition(JavaWrapper):
    def __init__(self, java_object=None):
        JavaWrapper.__init__(self, java_object)

    def learn_model(self, image_files):
        """
        Learns a model from a set of images saved to disk. Does not have to be the images which you will query, but
        in some applications that's a good idea.
        """
        # Convert the python list of strings into a java list of strings
        java_list = ListConverter().convert(image_files, gateway._gateway_client)

        # Create a Java iterator that will load the images from disk
        java_imageType = self.java_obj.getImageType()
        java_iterator = gateway.jvm.boofcv.io.image.ImageFileListIterator(java_list, java_imageType)

        # Learn the model from the images
        self.java_obj.learnModel(java_iterator)

    def add_image(self, id, image):
        self.java_obj.addImage(id, image)

    def clear_database(self):
        """
        Removes all images from the database. The model is not modified
        """
        self.java_obj.clearDatabase()

    def query(self, query_image, limit):
        """
        Looks up the images which are the best match for the query image
        """
        java_class = gateway.jvm.boofcv.abst.scene.SceneRecognition.Match().getClass()
        java_matches = gateway.jvm.pyboof.PyBoofEntryPoint.createDogArray(java_class)
        self.java_obj.query(query_image, None, limit, java_matches)

        # Convert the java results into a python list of dict
        results = []
        for i in range(java_matches.size):
            java_match = java_matches.get(i)
            match = JavaWrapper(java_match)
            results.append({"id": match.id, "error": match.error})
        return results

    def get_image_ids(self):
        # py4j should auto convert this into a python list
        return self.java_obj.getImageIds(None)

    def get_image_type(self):
        return ImageType(self.java_obj.getImageType())


class ConfigFeatureToSceneRecognition(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.abst.scene.ConfigFeatureToSceneRecognition")


class FactorySceneRecognition:
    def __init__(self, image_type):
        """
        Creates a factory for a specific image type.
        :param image_type: Specifies the type of image it processes.  Can be a dtype or ImageType
        :type image_type: int | ImageType
        """
        if isinstance(image_type, ImageType):
            self.image_type = image_type
        else:
            self.image_type = ImageType(dtype_to_ImageType(image_type))

    def scene_recognition(self, config: ConfigFeatureToSceneRecognition = None) -> SceneRecognition:
        """
        Scene recognition based off of image features

        :param config: Configuration for scene detector
        :return: Calibration target detector
        """
        cdj = None
        if config:
            cdj = config.java_obj

        java_obj = gateway.jvm.boofcv.factory.scene.FactorySceneRecognition. \
            createFeatureToScene(cdj, self.image_type.java_obj)
        return SceneRecognition(java_obj)


def download_default_scene_recognition(image_type, path=None) -> SceneRecognition:
    """
    Downloads then loads the default scene recognition model provided by BoofCV. If the model has already been
    saved at the specified location it will not be downloaded again.

    :param image_type: Image format that it will use
    :param path: Path to directory where it should store the model
    :return:
    """
    if not isinstance(image_type, ImageType):
        image_type = ImageType(dtype_to_ImageType(image_type))

    if not path:
        path = tempfile.TemporaryDirectory()
    path = os.path.abspath(path)

    java_file = pyboof.create_java_file(path)
    java_recognizer = gateway.jvm.boofcv.io.recognition.RecognitionIO. \
        downloadDefaultSceneRecognition(java_file, image_type.java_obj)
    return SceneRecognition(java_recognizer)
