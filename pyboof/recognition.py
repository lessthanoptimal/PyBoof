from pyboof.geo import *
from pyboof.calib import *
from pyboof import gateway


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


class ConfigUchiyaMarker(JavaConfig):
    def __init__(self):
        JavaConfig.__init__(self, "boofcv.factory.fiducial.ConfigUchiyaMarker")


class FactoryFiducialCalibration:
    def __init__(self):
        pass

    @staticmethod
    def chessboardX(config_grid, config_detector=None):
        """
        Creates a chessboard detector based on x-corners. Slower but very robust.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: Calibration target detector
        :rtype: FiducialCalibrationDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration.chessboardX(cdj,
                                                                                                   config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def chessboardB(config_grid, config_detector=None):
        """
        Creates a chessboard detector based on binary images. Fast but not as robust.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: Calibration target detector
        :rtype: FiducialCalibrationDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj

        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration.chessboardB(cdj,
                                                                                                   config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def square_grid(config_grid, config_detector=None):
        """
        Creates a square grid detector

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: Calibration target detector
        :rtype: FiducialCalibrationDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration.squareGrid(cdj,
                                                                                                  config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def circle_hexagonal_grid(config_grid, config_detector=None):
        """
        Detector for hexagonal grid of circles.  All circles must be entirely inside of the image.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: Calibration target detector
        :rtype: FiducialCalibrationDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducialCalibration. \
            circleHexagonalGrid(cdj, config_grid.java_obj)
        return FiducialCalibrationDetector(java_detector)

    @staticmethod
    def circle_regular_grid(config_grid, config_detector=None):
        """
        Detector for regular grid of circles.  All circles must be entirely inside of the image.

        :param config_detector:  Configuration for the detector
        :param config_grid: Specifies the Grid's shape
        :return: Calibration target detector
        :rtype: FiducialCalibrationDetector
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

    def square_image(self, config_fiducial, config_threshold):
        """
        Creates a square image fiducial detector

        :param config_fiducial: configuration for the fiducial
        :type config_fiducial: ConfigFiducialImage
        :param config_threshold: Configuration for image thresholding step
        :type config_threshold: ConfigThreshold
        :return: The detector
        :rtype: FiducialImageDetector
        """
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            squareImage(config_fiducial.java_obj, config_threshold.java_obj, self.boof_image_type)
        return FiducialImageDetector(java_detector)

    def square_binary(self, config_fiducial, config_threshold):
        """
        Creates a binary image fiducial detector

        :param config_fiducial: configuration for the fiducial
        :type config_fiducial: ConfigFiducialBinary
        :param config_threshold: Configuration for image thresholding step
        :type config_threshold: ThresholdType
        :return: The detector
        :rtype: FiducialImageDetector
        """
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            squareBinary(config_fiducial.java_obj, config_threshold.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def chessboardB(self, config_grid, config_detector=None):
        """
        Chessboard detector binary image

        :param config_detector: Fiducial configuration
        :type config_detector: ConfigChessboardBinary
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: FiducialDetector
        :rtype: FiducialDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            calibChessboardB(cdj, config_grid.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def chessboardX(self, config_grid, config_detector=None):
        """
        Chessboard detector X-corner

        :param config_detector: Fiducial configuration
        :type config_detector: ConfigChessboardX
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: FiducialDetector
        :rtype: FiducialDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            calibChessboardX(cdj, config_grid.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def square_grid(self, config_grid, config_detector=None):
        """
        Square grid detector

        :param config_detector: Fiducial configuration
        :type config_detector: ConfigFiducialSquareGrid
        :param config_grid: Specifies the Grid's shape
        :type config_grid: ConfigGridDimen
        :return: FiducialDetector
        :rtype: FiducialDetector
        """
        cdj = None
        if config_detector:
            cdj = config_detector.java_obj
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            calibSquareGrid(cdj, config_grid.java_obj, self.boof_image_type)
        return FiducialDetector(java_detector)

    def qrcode(self, config=None):
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

    def random_dots(self, config):
        """ Creates a detector random dot / Uchiya markers

        :param config: ConfigUchiyaMarker or None
        :return: ConfigUchiyaMarker
        """
        java_detector = gateway.jvm.boofcv.factory.fiducial.FactoryFiducial. \
            randomDots(config.java_obj, self.boof_image_type)
        return UchiyaRandomDotDetector(java_detector)


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


class FiducialDetector(JavaWrapper):
    """
    Detects fiducials and estimates their ID, 3D pose, and image location.
    Wrapper around BoofCV class of the same name
    """

    def __init__(self, java_FiducialDetector):
        JavaWrapper.__init__(self, java_FiducialDetector)

    def detect(self, image):
        self.java_obj.detect(image)

    def set_intrinsic(self, intrinsic: CameraPinhole):
        if intrinsic is None:
            self.java_obj.setLensDistortion(None, -1, -1)
        else:
            distortion = create_narrow_lens_distorter(intrinsic)
            self.java_obj.setLensDistortion(distortion.java_obj,
                                            intrinsic.width, intrinsic.height)

    def get_total(self):
        return self.java_obj.totalFound()

    def is_3d(self):
        return self.java_obj.is3D()

    def get_fiducial_to_camera(self, which):
        """
        Returns the rigid body transform from the fiducial to the camera

        :param which: Index of detected fiducial.
        :type which: int
        :return: Rigid Body Transform
        :rtype: Se3_F64
        """
        fid_to_cam = Se3_F64()
        self.java_obj.getFiducialToCamera(which, fid_to_cam.get_java_object())
        return fid_to_cam

    def get_bounds(self, which):
        return Polygon2D(self.java_obj.getBounds(which, None))

    def get_center(self, which):
        location = gateway.jvm.georegression.struct.point.Point2D_F64()
        self.java_obj.getCenter(which, location)
        return location.getX(), location.getY()

    def get_id(self, which):
        return self.java_obj.getId(which)

    def get_width(self, which):
        return self.java_obj.getWidth(which)

    def get_input_type(self):
        return ImageType(self.java_obj.get_input_type())


class FiducialImageDetector(FiducialDetector):
    def add_pattern(self, image, side_length, threshold=100.0):
        self.java_obj.addPatternImage(image, threshold, side_length)


class QrCode:
    """Description of a detected QR Code inside an image.

    """

    def __init__(self, java_object=None):
        if java_object is None:
            self.verson = -1
            self.message = ""
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
            self.verson = jobj.version
            self.message = jobj.message
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


class UchiyaRandomDotDetector(FiducialDetector):
    """Detector for random dot markers
    """

    def __init__(self, java_detector):
        JavaWrapper.__init__(self, java_detector)
        self.detections = []
        self.failures = []

    def add_marker(self, marker):
        self.java_obj.addMarker(marker)


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
