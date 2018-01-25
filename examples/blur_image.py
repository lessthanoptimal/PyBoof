import numpy as np
import pyboof as pb

original = pb.load_single_band('../data/example/outdoors01.jpg', np.uint8)

gaussian = original.createSameShape() # useful function which creates a new image of the
mean = original.createSameShape()     # same type and shape as the original

# Apply different types of blur to the image
pb.blur_gaussian(original, gaussian,radius=3)
pb.blur_mean(original, mean, radius=3)

# display the results in a single window as a list
image_list = [(original, "original"), (gaussian, "gaussian"), (mean, "mean")]
pb.swing.show_list(image_list, title="Outputs")

input("Press any key to exit")
