import numpy as np

import pyboof as pb

original = pb.load_single_band('../data/example/fiducial/image/examples/image00.jpg',np.uint8)

binary = pb.create_single_band(original.getWidth(),original.getHeight(),np.uint8)

algorithms = []

factory = pb.FactoryThresholdBinary(np.uint8)

algorithms.append(("localGaussian",factory.localGaussian(region_width=11)))
algorithms.append(("localSauvola" ,factory.localSauvola(region_width=11)))
algorithms.append(("localSquare"  ,factory.localMean(region_width=11)))
# algorithms.append(("localOtsu"  ,factory.localOtsu(region_width=11))) # This can be slow
algorithms.append(("blockMinMax"  ,factory.blockMinMax(region_width=11)))
algorithms.append(("blockMean"    ,factory.blockMean(region_width=11)))
algorithms.append(("blockOtsu"    ,factory.blockOtsu(region_width=11)))
algorithms.append(("globalEntropy",factory.globalEntropy()))
algorithms.append(("globalOtsu"   ,factory.globalOtsu()))
algorithms.append(("globalFixed"  ,factory.globalFixed(threshold=100)))

image_list = [(original, "Original")]

for a in algorithms:
    a[1].process(original, binary)
    buffered_binary = pb.swing.render_binary(binary)
    image_list.append((buffered_binary,a[0]))

pb.swing.show_list(image_list, title="Binary Thresholding")

input("Press any key to exit")
