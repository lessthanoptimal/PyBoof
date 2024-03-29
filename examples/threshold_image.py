#!/usr/bin/env python3

import numpy as np

import pyboof as pb

original = pb.load_single_band('../data/example/fiducial/image/examples/image00.jpg',np.uint8)

binary = pb.create_single_band(original.getWidth(),original.getHeight(),np.uint8)

algorithms = []

factory = pb.FactoryThresholdBinary(np.uint8)

algorithms.append(("localGaussian",factory.localGaussian(region_width=11)))
algorithms.append(("localSauvola" ,factory.localSauvola(region_width=11)))
algorithms.append(("localWolf"    ,factory.localWolf(region_width=11)))
algorithms.append(("localNiblack" ,factory.localNiblack(region_width=11)))
algorithms.append(("localMean"    ,factory.localMean(region_width=11)))
algorithms.append(("localNick"    ,factory.localNick(region_width=11)))
# algorithms.append(("localOtsu"  ,factory.localOtsu(region_width=11))) # This can be slow
algorithms.append(("blockMinMax"  ,factory.blockMinMax(region_width=11)))
algorithms.append(("blockMean"    ,factory.blockMean(region_width=11)))
algorithms.append(("blockOtsu"    ,factory.blockOtsu(region_width=11)))
algorithms.append(("globalEntropy",factory.globalEntropy()))
algorithms.append(("globalOtsu"   ,factory.globalOtsu()))
algorithms.append(("globalLi"     ,factory.globalLi()))
algorithms.append(("globalHuang"  ,factory.globalHuang()))
algorithms.append(("globalFixed"  ,factory.globalFixed(threshold=100)))

image_list = [(original, "Original")]

# WARNING: There's a bug in Py4J and it's calling the wrong function when we visualize results.
#          This causes the example to crash.

for a in algorithms:
    a[1].process(original, binary)
    buffered_binary = pb.swing.render_binary(binary)
    image_list.append((buffered_binary,a[0]))

pb.swing.show_list(image_list, title="Binary Thresholding")

input("Press any key to exit")
