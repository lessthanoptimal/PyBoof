PyBoof is a wrapper around BoofCV for Python.  It uses Py4j to call BoofCV Java functions.  To obtain the latest code use the following command.

```
git clone --recursive https://github.com/lessthanoptimal/PyBoof.git
```
This will check the main repository and the data repository at the same time.  If you forgot --recursive then you can
checkout the data directory with the following command.
```
git submodule update --init --recursive
```

After you have the source code on your local machine you can install it with the following commands:

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