PyBoof is a wrapper around BoofCV for Python.  It uses Py4j to call BoofCV Java functions.

# Getting Example Data

Data is stored in a git submodule.  The first time you check out the code you need to initialize it

```
git submodule init
```

Then to download the latest update it

```
git submodule update
```

# Installation

1. ./setup.py build
2. sudo ./setup.py install

Yes you do need to do the build first.  This will automatically build the Java jar and put it into the correct place.
The end result is that you don't need to personally launch the JVM it will do it for you!

# Examples
  
1. cd examples
2. python example_blur_image.py

Ignore the following text, it appears to be a Py4J issue.
'''
Exception TypeError: "'NoneType' object is not callable" in <function <lambda> at 0x7f9e78d49c08> ignored
'''