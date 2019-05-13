#!/usr/bin/env python3

import numpy as np
import pyboof as pb
import time

# This example shows how you can adjust the number of threads that BoofCV will use in the JVM

original = pb.load_single_band('../data/example/outdoors01.jpg', np.uint8)

gaussian = original.createSameShape()

# Let's warm up the JVM.
for i in range(5):
    time0 = time.time()
    pb.blur_gaussian(original, gaussian,radius=12)
    time1 = time.time()
    print("Warm up iteration {:.1f} ms".format(1000*(time1-time0)))

print()
print()

N = 30

time0 = time.time()
for i in range(N):
    pb.blur_gaussian(original, gaussian,radius=12)
time1 = time.time()

print("Time with default threads {:.1f} ms".format(1000*(time1-time0)))

pb.set_max_threads(1)
time0 = time.time()
for i in range(N):
    pb.blur_gaussian(original, gaussian,radius=12)
time1 = time.time()

print("Time with one threads {:.1f} ms".format(1000*(time1-time0)))

pb.set_max_threads(2)
time0 = time.time()
for i in range(N):
    pb.blur_gaussian(original, gaussian,radius=12)
time1 = time.time()

print("Time with 2 threads {:.1f} ms".format(1000*(time1-time0)))
