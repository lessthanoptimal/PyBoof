import numpy as np

import pyboof as pb

original = pb.load_single_band('../data/example/fiducial/image/examples/image00.jpg',np.uint8)

binary = pb.create_single_band(original.getWidth(),original.getHeight(),np.uint8)

algorithms = []

factory = pb.FactoryThresholdBinary(np.uint8)

algorithms.append(("localGaussian",factory.localGaussian(radius=5)))
algorithms.append(("localSauvola" ,factory.localSauvola(radius=5)))
algorithms.append(("localSquare"  ,factory.localSquare(radius=5)))
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
