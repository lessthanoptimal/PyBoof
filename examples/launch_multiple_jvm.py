#!/usr/bin/env python3

# This example demonstrates how to lunch multiple instances of PyBoof at the same time. Because PyBoof connects
# to a JVM process, even there are multiple Python processes it will crash because each JVM can only have one
# connection at a time to avoid conflicts.

# Each process must have its own set of TCP ports that are unique. This will cause a unique JVM to spawn for
# each process
import os

os.environ['PYBOOF_JAVA_PORT'] = "24000"
os.environ['PYBOOF_PYTHON_PORT'] = "24001"

# Now proceed as usual
import numpy as np
import pyboof as pb
import time

# Open an image so that you can see we are doing something with PyBoof
original = pb.load_single_band('../data/example/outdoors01.jpg', np.uint8)

# Block for 5 seconds
time.sleep(20)
print("Done! port={}".format(os.environ['PYBOOF_PYTHON_PORT']))

# To test the code launch the script, modify the ports, then launch it again from another terminal