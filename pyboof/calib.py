from pyboof.image import *
from pyboof.ip import *
from pyboof.geo import *
from pyboof.recognition import *
from pyboof.geo import real_nparray_to_ejml32
from typing import Mapping, List


def convert_from_boof_calibration_observations(jobservations):
    # TODO For Boof 0.29 and beyond use accessors instead
    jlist = JavaWrapper(jobservations).points
    output = []
    for o in jlist:
        output.append((o.getIndex(), o.getX(), o.getY()))
    return output


def convert_into_boof_calibration_observations(observations):
    pixels = observations["pixels"]
    jobs = gateway.jvm.boofcv.alg.geo.calibration.CalibrationObservation()
    for o in pixels:
        jobs.add(int(o[0]), float(o[1]), float(o[2]))
        # TODO use this other accessor after 0.30
        # jobs.add(float(o[1]),float(o[2]),int(o[0]))

    if "target" in observations:
        jobs.target = observations["target"]

    return jobs


def calibrate_brown(width:int, height:int, observations: List, detector, num_radial=2, tangential=True, zero_skew=True):
    """
    Calibrates a Brown camera

    :param width: Image width in pixels
    :param height: Image height in pixels
    :param observations: List of {"points":(boofcv detections)}
    :param detector:
    :param num_radial:
    :param tangential:
    :param zero_skew:
    :return:
    """
    jlayout = detector.java_obj.getLayout()
    jcalib_planar = gateway.jvm.boofcv.abst.geo.calibration.CalibrateMonoPlanar()
    jcalib_planar.initialize(width, height, jlayout)
    jcalib_planar.configurePinhole(zero_skew, int(num_radial), tangential)
    for o in observations:
        jcalib_planar.addImage(convert_into_boof_calibration_observations(o))

    intrinsic = CameraBrown(jcalib_planar.process())

    errors = []
    for jerror in jcalib_planar.getErrors():
        errors.append({"mean": jerror.getMeanError(),
                       "max_error": jerror.getMaxError(),
                       "bias_x": jerror.getBiasX(), "bias_y": jerror.getBiasY()})

    return (intrinsic, errors)


def calibrate_universal(width:int, height:int, observations: List, detector, num_radial=2, tangential=True, zero_skew=True,
                        mirror_offset=None):
    """
    Calibrate a fisheye camera using Universal Omni model.

    :param width: Image width in pixels
    :param height: Image height in pixels
    :param observations: List of {"points":(boofcv detections)}
    :param detector:
    :param num_radial:
    :param tangential:
    :param zero_skew:
    :param mirror_offset: If None it will be estimated. 0.0 = pinhole camera. 1.0 = fisheye
    :return: (intrinsic, errors)
    """
    jlayout = detector.java_obj.getLayout()
    jcalib_planar = gateway.jvm.boofcv.abst.geo.calibration.CalibrateMonoPlanar()
    jcalib_planar.initialize(width, height, jlayout)
    if mirror_offset is None:
        jcalib_planar.configureUniversalOmni(zero_skew, int(num_radial), tangential)
    else:
        jcalib_planar.configureUniversalOmni(zero_skew, int(num_radial), tangential, float(mirror_offset))
    for o in observations:
        jcalib_planar.addImage(convert_into_boof_calibration_observations(o))

    intrinsic = CameraUniversalOmni(jcalib_planar.process())

    errors = []
    for jerror in jcalib_planar.getErrors():
        errors.append({"mean": jerror.getMeanError(),
                       "max_error": jerror.getMaxError(),
                       "bias_x": jerror.getBiasX(), "bias_y": jerror.getBiasY()})

    return (intrinsic, errors)


def calibrate_kannala_brandt(width:int, height:int, observations: List, detector: FiducialCalibrationDetector, num_symmetric: int = 5,
                             num_asymmetric: int = 0, zero_skew: bool = True):
    """
    Calibrate a fisheye camera using Kannala-Brandt model.

    :param width: Image width in pixels
    :param height: Image height in pixels
    :param observations: List of {"points":(boofcv detections)}
    :param detector:
    :param num_symmetric:
    :param num_asymmetric:
    :param zero_skew:
    :param mirror_offset: If None it will be estimated. 0.0 = pinhole camera. 1.0 = fisheye
    :return: (intrinsic, errors)
    """
    jlayout = detector.java_obj.getLayout()
    jcalib_planar = gateway.jvm.boofcv.abst.geo.calibration.CalibrateMonoPlanar()
    jcalib_planar.initialize(width, height, jlayout)
    jcalib_planar.configureKannalaBrandt(zero_skew, num_symmetric, num_asymmetric)

    for o in observations:
        jcalib_planar.addImage(convert_into_boof_calibration_observations(o))

    intrinsic = CameraKannalaBrandt(jcalib_planar.process())

    errors = []
    for jerror in jcalib_planar.getErrors():
        errors.append({"mean": jerror.getMeanError(),
                       "max_error": jerror.getMaxError(),
                       "bias_x": jerror.getBiasX(), "bias_y": jerror.getBiasY()})

    return (intrinsic, errors)


def calibrate_stereo(shape_left, shape_right,
                     observations_left: List, observations_right: List, detector: FiducialCalibrationDetector,
                     num_radial: int = 4, tangential: bool = False, zero_skew: bool = True) -> (StereoParameters, List):
    """
    Calibrates a stereo camera using a Brown camera model

    :param observations: List of {"points":(boofcv detections),"width":(image width),"height":(image height)}
    :param detector:
    :param num_radial:
    :param tangential:
    :param zero_skew:
    :return:
    """
    jlayout = detector.java_obj.getLayout(0) # Hard coded for a single target
    jcalib_planar = gateway.jvm.boofcv.abst.geo.calibration.CalibrateStereoPlanar(jlayout)
    jcalib_planar.configure(zero_skew, int(num_radial), tangential)
    jcalib_planar.initialize(gateway.jvm.boofcv.struct.image.ImageDimension(shape_left[0], shape_left[1]),
                             gateway.jvm.boofcv.struct.image.ImageDimension(shape_right[0], shape_right[1]))

    for idx in range(len(observations_left)):
        jobs_left = convert_into_boof_calibration_observations(observations_left[idx])
        jobs_right = convert_into_boof_calibration_observations(observations_right[idx])
        jcalib_planar.addPair(jobs_left, jobs_right)

    stereo_parameters = StereoParameters(jcalib_planar.process())

    errors = []
    for jerror in jcalib_planar.computeErrors():
        errors.append({"mean": jerror.getMeanError(),
                       "max_error": jerror.getMaxError(),
                       "bias_x": jerror.getBiasX(), "bias_y": jerror.getBiasY()})

    return (stereo_parameters, errors)
