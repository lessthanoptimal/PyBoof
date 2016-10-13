import atexit
import mmap
import os
import signal
import subprocess
import time

from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JError
from py4j.protocol import Py4JNetworkError

gateway = JavaGateway()

mmap_size = 0
mmap_file = None

build_date = None

java_pid = None

# Read the date everything was build
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"build_date.txt"), 'r') as f:
    build_date = f.readline()

if build_date is None:
    print "Can't find build_data.txt at "+os.path.dirname(os.path.realpath(__file__))
    exit(1)

def check_jvm( set_date ):
    global gateway
    try:
        gateway.jvm.pyboof.PyBoofEntryPoint.nothing()
        if set_date:
            gateway.jvm.pyboof.PyBoofEntryPoint.setBuildDate(build_date)
        else:
            java_build_date = gateway.jvm.pyboof.PyBoofEntryPoint.getBuildDate()
            if build_date != java_build_date:
                print "Python and Java build dates do not match.  Killing Java process."
                print "  build dates = {:s} {:s}".format(build_date,java_build_date)
                gateway.close()
                time.sleep(1)
                return False

    except Py4JNetworkError:
        return False
    except Py4JError as e:
        print e
        print "Py4J appears to have attached itself to a process that doesn't have the expected jars.  " \
              "Try killing py4j processes"
        exit(1)
    return True


def shutdown_jvm():
    global java_pid, gateway
    if java_pid is None:
        pass
    else:
        # shutdown the gateway so that it doesn't spew out a billion error messages when it can't connect
        # to the JVM
        gateway.shutdown()
        gateway = None
        os.kill(java_pid, signal.SIGTERM)
        java_pid = None

# Catch control-c and kill the java process "gracefully" first.
def signal_handler(signal, frame):
    shutdown_jvm()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# kill java on a regular exit too
atexit.register(shutdown_jvm)

if not check_jvm(False):
    print "Launching Java process"
    jar_path = os.path.realpath(__file__)
    jar_path = os.path.join(os.path.dirname(jar_path),"PyBoof-all.jar")
    proc = subprocess.Popen(["java","-jar",jar_path])
    java_pid = proc.pid
    time.sleep(0.1)
    # closed loop initialization.  If it fails for 5 seconds give up
    start_time = time.time()
    success = False
    while time.time() - start_time < 5.0:
        if check_jvm(True):
            success = True
            break

    if not success:
        print "Failed to successfully launch the JVM after 5 seconds.  Aborting"
        pass

class MmapType:
    """
    Type byte for different data structures
    """
    IMAGE_U8 = 0
    IMAGE_F32 = 1
    LIST_POINT2D_F64 = 2
    LIST_TUPLE_F64 = 3


def init_memmap( size_MB=2):
    """
    Call to enable use of memory mapped files for quick communication between Python and Java.  This
    faster communication method requires specialized code so is only used when large amounts of memory
    is being transferred.

    :param size_MB: Size of the memory mapped file in megabytes
    :type size_MB: int
    """
    global mmap_size, mmap_file
    mmap_name = "mmap_python_java.mmap"
    mmap_size = size_MB*1024*1024
    mmap_name_path = os.path.join(os.getcwd(), mmap_name)
    gateway.jvm.pyboof.PyBoofEntryPoint.initializeMmap(mmap_name_path, size_MB)
    # Open file in read,write,binary mode
    mmap_fid = open(mmap_name, "r+b")
    mmap_file = mmap.mmap(mmap_fid.fileno(), length=0, flags=mmap.MAP_SHARED,
                          prot=mmap.PROT_READ | mmap.PROT_WRITE)

from calib import *
from common import *
from geo import *
from image import *
from ip import *
from recognition import *
from feature import *
from stereo import *
import swing
