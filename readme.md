PyBoof is a wrapper around BoofCV for Python.  It uses Py4j to call BoofCV Java functions.  To obtain the latest code use the following command.

```
git clone --recursive https://github.com/lessthanoptimal/PyBoof.git
```
This will check the main repository and the data repository at the same time.  If you forgot --recursive then you can
checkout the data directory with the following command.
```
git submodule update --init --recursive
```

After you have the source code on your local machine you can install it and its dependencies with the following commands:

1. ./setup.py build
2. sudo ./setup.py install
3. sudo pip install py4j==0.10.3

Yes you do need to do the build first.  This will automatically build the Java jar and put it into the correct place.
The end result is that you don't need to personally launch the JVM it will do it for you!

# Supported Platforms

The code has been developed and tested on Ubuntu Linux 16.04.  Should work on any other Linux variant.  Might work on Mac OS and a slim chance of working on Windows.

# Examples

Lots of usage examples are included and can be found in the 'examples' directory.  To run any of the examples simply invoke python on the script

1. cd examples
2. python example_blur_image.py

Code for applying a Gaussian and mean spatial filter to an image and displays the results.
```Python
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

raw_input("Press any key to exit")

```
