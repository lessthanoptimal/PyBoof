import mmap
import os
import subprocess
import time
from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError
from py4j.protocol import Py4JError

gateway = JavaGateway()

mmap_size = 0
mmap_file = None

build_date = None

# Read the date everything was build
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"build_date.txt"), 'r') as f:
    build_date = f.readline()

if build_date is None:
    print "Can't find build_data.txt!"
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

if not check_jvm(False):
    print "Launching Java process"
    jar_path = os.path.realpath(__file__)
    jar_path = os.path.join(os.path.dirname(jar_path),"PyBoof-all.jar")
    subprocess.Popen(["java","-jar",jar_path])
    time.sleep(1)
    if not check_jvm(True):
        print "Failed to start p4j to jvm connection"
        exit(1)


class MmapType:
    """
    Type byte for different data structures
    """
    IMAGE_U8 = 0
    LIST_POINT2D_F64 = 1
    LIST_TUPLE_F64 = 2


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
import swing
