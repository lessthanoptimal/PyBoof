PyBoof is a wrapper around BoofCV for Python.  It uses Py4j to call BoofCV Java functions.

# Installation

1) sudo ./setup.py install
2) gradle PyBoofJar
  
Then when you are ready to run PyBoof launch the jar which step two created:

  java -jar PyBoof.jar

Now you are ready to run the Python code

1) cd examples
2) python example_blur_image.py

