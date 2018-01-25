PyBoof is [Python](http://www.python.org) wrapper for the computer vision library [BoofCV](http://boofcv.org). Since this is a Java library you will need to have java and javac installed.  The former is the Java compiler.  In the future the requirement for javac will be removed since a pre-compiled version of the Java code will be made available and automatically downloaded.  Installing the Java JDK is platform specific, so a quick search online should tell you how to do it.

To start using the library simply install the latest stable version using pip
```bash
sudo pip install pyboof
```

# Installing From Source
One advantage to checkout the source code and installing from source is that you also get all the example code and the example datasets.
```bash
git clone --recursive https://github.com/lessthanoptimal/PyBoof.git
```

If you forgot --recursive then you can checkout the data directory with the following command.

```bash
git submodule update --init --recursive
```

After you have the source code on your local machine you can install it and its dependencies with the following commands:

1. cd PyBoof
2. ./setup.py build
3. sudo ./setup.py install

Yes you do need to do the build first.  This will automatically build the Java jar and put it into the correct place.

# Supported Platforms

The code has been developed and tested on Ubuntu Linux 16.04.  Should work on any other Linux variant.  Might work on Mac OS and a slim chance of working on Windows.

# Examples

Examples are included with the source code.  You can obtain them by either checkout the source code, as described above, or browsing 
[github here](https://github.com/lessthanoptimal/PyBoof/tree/master/examples).  If you don't check out the source code you won't have example data and not
all of the examples will work.

To run any of the examples simply invoke python on the script

1. cd PyBoof/examples
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

input("Press any key to exit")

```

# Dependencies

PyBoof depends on the following python packages.  They should be automatically installed

* py4j
* numpy