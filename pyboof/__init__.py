import atexit
import mmap
import os
import signal
import subprocess
import time
import numpy as np
import sys

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
from py4j.java_gateway import CallbackServerParameters
from py4j.protocol import Py4JError
from py4j.protocol import Py4JNetworkError

# Read the version from a file so that the build script can get the version without importing this file
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "version.txt"), "r") as myfile:
    __version__ = myfile.read()

# Read the date everything was build
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "build_date.txt"), 'r') as f:
    build_date = f.readline()

if build_date is None:
    print("Can't find build_data.txt at " + os.path.dirname(os.path.realpath(__file__)), file=sys.stderr)
    exit(1)


# Class which stores all global variables. This is done because if you import a global the reference is copied.
# As a result if it ever gets modified you're referencing the old object
class PBGlobal:
    gateway = None
    mmap_size = 0
    mmap_file = None
    java_pid = None

pbg = PBGlobal()

def init_pyboof(java_port: int = 25333, python_port: int = 25334, size_mb: int = 20):
    """
    Initializes PyBoof by connecting a Java Virtual Machine (JVM) using Py4J and if requested, will create a
    memory mapped file to enabled much faster file transfers of larger objects.

    If you wish to run multiple independent processes, then you launch each process with a unique port.
    :param size_mb: Size of the memory mapped file in megabytes. If <= 0 then memory mapped files will not be used
    """
    global pbg

    # The user is re-initializing for some reason. Let's close the gateway if already open
    if pbg.gateway is not None:
        print("Closing previously open gateway", file=sys.stderr)
        shutdown_jvm()

    pbg.gateway = JavaGateway(gateway_parameters=GatewayParameters(port=java_port, auto_field=True),
                              callback_server_parameters=CallbackServerParameters(port=python_port,
                                                                                  daemonize=True))

    # print("gateway={}".format(id(pbg.gateway)))
    signal.signal(signal.SIGINT, signal_handler)

    # kill java on a regular exit too
    atexit.register(shutdown_jvm)

    if not check_jvm(False):
        # print("Launching Java process: java_port={} python_port={}".format(java_port, python_port))
        jar_path = os.path.realpath(__file__)
        jar_path = os.path.join(os.path.dirname(jar_path), "PyBoof-all.jar")
        proc = subprocess.Popen(["java", "-jar", jar_path, str(java_port)])
        pbg.java_pid = proc.pid
        time.sleep(0.1)
        # closed loop initialization.  If it fails for 5 seconds give up
        start_time = time.time()
        success = False
        while time.time() - start_time < 5.0:
            if check_jvm(True):
                success = True
                break

        if not success:
            print("Failed to successfully launch the JVM after 5 seconds.  Aborting", file=sys.stderr)
            pass

    if size_mb > 0:
        __init_memmap(size_mb)


# Used to change the number of threads the Java code can run inside of
def set_max_threads(max_threads):
    pbg.gateway.jvm.pyboof.PyBoofEntryPoint.setMaxThreads(max_threads)


def check_jvm(set_date):
    global pbg
    try:
        pbg.gateway.jvm.pyboof.PyBoofEntryPoint.nothing()
        if set_date:
            pbg.gateway.jvm.pyboof.PyBoofEntryPoint.setBuildDate(build_date)
        else:
            java_build_date = pbg.gateway.jvm.pyboof.PyBoofEntryPoint.getBuildDate()
            if build_date != java_build_date:
                print("Python and Java build dates do not match.  Killing Java process.", file=sys.stderr)
                print("  build dates = {:s} {:s}".format(build_date, java_build_date, file=sys.stderr))
                pbg.gateway.close()
                time.sleep(1)
                return False

    except Py4JNetworkError:
        return False
    except Py4JError as e:
        print(e, file=sys.stderr)
        print("Py4J appears to have attached itself to a process that doesn't have the expected jars. "
              "Try killing py4j processes", file=sys.stderr)
        exit(1)
    return True


def shutdown_jvm():
    global pbg
    if pbg.java_pid is None:
        pass
    elif pbg.gateway is None:
        pass
    else:
        # shutdown the gateway so that it doesn't spew out a billion error messages when it can't connect
        # to the JVM
        pbg.gateway.shutdown()
        gateway = None
        os.kill(pbg.java_pid, signal.SIGTERM)
        java_pid = None


# Catch control-c and kill the java process "gracefully" first.
def signal_handler(signal, frame):
    shutdown_jvm()
    # Windows does not define this command
    try:
        sys.exit(0)
    except ImportError:
        pass


def __init_memmap(size_mb=20):
    """
    Call to enable use of memory mapped files for quick communication between Python and Java.  This
    faster communication method requires specialized code so is only used when large amounts of memory
    is being transferred.

    :param size_mb: Size of the memory mapped file in megabytes
    :type size_mb: int
    """
    global pbg
    import tempfile
    mmap_path = os.path.join(tempfile.gettempdir(), "pyboof_mmap_{}".format(pbg.java_pid))
    # print("mmap_path=", mmap_path)
    pbg.mmap_size = size_mb * 1024 * 1024
    pbg.gateway.jvm.pyboof.PyBoofEntryPoint.initializeMmap(mmap_path, size_mb)
    # Open file in read,write,binary mode
    pbg.mmap_fid = open(mmap_path, "r+b")
    if os.name == 'nt':
        pbg.mmap_file = mmap.mmap(pbg.mmap_fid.fileno(), length=0)
    else:
        pbg.mmap_file = mmap.mmap(pbg.mmap_fid.fileno(), length=0, flags=mmap.MAP_SHARED,
                              prot=mmap.PROT_READ | mmap.PROT_WRITE)


class MmapType:
    """
    Type byte for different data structures
    """
    IMAGE_U8 = 0
    IMAGE_F32 = 1
    LIST_POINT2D_U16 = 2
    LIST_POINT2D_S16 = 3
    LIST_POINT2D_S32 = 4
    LIST_POINT2D_F32 = 5
    LIST_POINT2D_F64 = 6
    LIST_POINT3D_F32 = 7
    LIST_POINT3D_F64 = 8
    LIST_TUPLE_F32 = 9
    LIST_TUPLE_F64 = 10
    LIST_ASSOCIATEDPAIR_F32 = 11
    LIST_ASSOCIATEDPAIR_F64 = 12
    ARRAY_S8 = 13
    ARRAY_U8 = 14
    ARRAY_S16 = 15
    ARRAY_U16 = 16
    ARRAY_S32 = 17
    ARRAY_F32 = 18
    ARRAY_F64 = 19


def mmap_primitive_len(mmap_type: MmapType):
    if mmap_type == MmapType.ARRAY_S8:
        return 1
    elif mmap_type == MmapType.ARRAY_U8:
        return 1
    elif mmap_type == MmapType.ARRAY_S16:
        return 2
    elif mmap_type == MmapType.ARRAY_U16:
        return 2
    elif mmap_type == MmapType.ARRAY_S32:
        return 4
    elif mmap_type == MmapType.ARRAY_F32:
        return 4
    elif mmap_type == MmapType.ARRAY_F64:
        return 8
    else:
        raise Exception("Not a primitive array type")


def mmap_primitive_format(mmap_type: MmapType):
    if mmap_type == MmapType.ARRAY_S8:
        return ">b"
    elif mmap_type == MmapType.ARRAY_U8:
        return ">B"
    elif mmap_type == MmapType.ARRAY_S16:
        return ">h"
    elif mmap_type == MmapType.ARRAY_U16:
        return ">H"
    elif mmap_type == MmapType.ARRAY_S32:
        return ">i"
    elif mmap_type == MmapType.ARRAY_F32:
        return ">f"
    elif mmap_type == MmapType.ARRAY_F64:
        return ">d"
    else:
        raise Exception("Not a primitive array type")


def mmap_force_array_type(data_array, mmap_type: MmapType):
    if mmap_type == MmapType.ARRAY_S8:
        return np.int8(data_array)
    elif mmap_type == MmapType.ARRAY_U8:
        return np.uint8(data_array)
    elif mmap_type == MmapType.ARRAY_S16:
        return np.int16(data_array)
    elif mmap_type == MmapType.ARRAY_U16:
        return np.uint16(data_array)
    elif mmap_type == MmapType.ARRAY_S32:
        return np.int32(data_array)
    elif mmap_type == MmapType.ARRAY_F32:
        return np.float32(data_array)
    elif mmap_type == MmapType.ARRAY_F64:
        return np.float64(data_array)
    else:
        raise Exception("Not a primitive array type")


init_pyboof(java_port=int(os.environ.get('PYBOOF_JAVA_PORT', 25333)),
            python_port=int(os.environ.get('PYBOOF_PYTHON_PORT', 25334)))

from pyboof.calib import *
from pyboof.common import *
from pyboof.geo import *
from pyboof.image import *
from pyboof.ip import *
from pyboof.recognition import *
from pyboof.feature import *
from pyboof.stereo import *
from pyboof.sfm import *
import pyboof.swing
