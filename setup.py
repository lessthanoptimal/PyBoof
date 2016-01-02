#!/usr/bin/env python

from distutils.core import setup
from setuptools.command.build_py import build_py
from subprocess import call
import os.path
import time

class MyBuild(build_py):
   def run(self):
       try:
           call(["gradle","allJar"])
           f = open('python/pyboof/build_date.txt', 'w')
           f.write(str(int(round(time.time() * 1000))))
           f.close()
       except:
           if not os.path.isfile('python/pyboof/PyBoof-all.jar'):
               print "Gradle build failed AND there is no PyBoof-all.jar"
               print ""
               print "Did you run build as a regular user first?"
               print "    ./setup.py build"
               print "Is Gradle and Java installed?  Test by typing the following:"
               print "    gradle allJar"
               exit(1)
       build_py.run(self)

setup(name='PyBoof',
      cmdclass={'build_py': MyBuild},
      version='0.21',
      description='Py4J Python wrapper for BoofCV',
      url='https://github.com/lessthanoptimal/PyBoof',
      author="Peter Abeles",
      author_email="peter.abeles@gmail.com",
      packages=['pyboof'],
      package_dir={'': 'python'},
      package_data={'pyboof': ['PyBoof-all.jar','build_date.txt']},
      )