from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError
import subprocess
import time

gateway = JavaGateway()

from pyboof.calib import *
from pyboof.common import *
from pyboof.geo import *
from pyboof.image import *
from pyboof.ip import *
from pyboof.recognition import *
import pyboof.swing

try_again = False

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