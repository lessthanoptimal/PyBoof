import mmap
import os
import subprocess
import time
from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError

gateway = JavaGateway()

try_again = False

mmap_size = 0
mmap_file = None

try:
    gateway.jvm.pyboof.PyBoofEntryPoint.nothing()
except Py4JNetworkError:
    try_again = True
    print "Launching Java process"
    jar_path = os.path.realpath(__file__)
    jar_path = os.path.join(os.path.dirname(jar_path),"PyBoof-all.jar")
    subprocess.Popen(["java","-jar",jar_path])
    time.sleep(1)

if try_again:
    try:
        gateway.jvm.pyboof.PyBoofEntryPoint.nothing()
    except Py4JNetworkError:
        print "Doesn't look like the java process started."
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
    gateway.jvm.pyboof.PyBoofEntryPoint.initializeMmap(mmap_name, size_MB)
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
