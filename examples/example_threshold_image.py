import pyboof as pb
import numpy as np

original = pb.load_single_band('../data/example/fiducial/image/examples/image00.jpg',np.uint8)

binary = pb.create_single_band(original.getWidth(),original.getHeight(),np.uint8)

algorithms = []

algorithms.append(("localGaussian",pb.FactoryThresholdBinary(np.uint8).localGaussian(radius=10)))
algorithms.append(("localSauvola" ,pb.FactoryThresholdBinary(np.uint8).localSauvola(radius=10)))
algorithms.append(("localSquare"  ,pb.FactoryThresholdBinary(np.uint8).localSquare(radius=10)))
algorithms.append(("globalEntropy",pb.FactoryThresholdBinary(np.uint8).globalEntropy()))
algorithms.append(("globalOtsu"   ,pb.FactoryThresholdBinary(np.uint8).globalOtsu()))
algorithms.append(("globalFixed"  ,pb.FactoryThresholdBinary(np.uint8).globalFixed(threshold=100)))

image_list = [(original,"Original")]

for a in algorithms:
    a[1].process(original,binary)
    buffered_binary = pb.swing.render_binary(binary)
    image_list.append((buffered_binary,a[0]))

pb.swing.show_list(image_list,title="Binary Thresholding")