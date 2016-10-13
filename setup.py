#!/usr/bin/env python

import os.path
import time
from distutils.core import setup
from setuptools.command.build_py import build_py
from setuptools import find_packages
from subprocess import call


def check_for_command( command ):
  try:
    call([command], stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
    return True
  except:
    return False


class MyBuild(build_py):
    def run(self):
        try:
            # Create build date file.  This is used to determine if the java jar and python code are
            # compatible with each other
            f = open('pyboof/build_date.txt', 'w')
            f.write(str(int(round(time.time() * 1000))))
            f.close()
            # See if javac is available for compiling the java code
            if check_for_command("javac"):
                if call(["bash", "gradlew", "allJar"]) != 0:
                    print "Gradle build failed."
                    exit(1)
            else:
                print "javac isn't installed on your systems.  exiting now"
                # TODO Should download instead if possible?
                exit(1)
        except Exception as e:
            print "Exception message:"
            print str(e)
            print e.message
            print
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
      version='0.24.1r6',
      description='Py4J Python wrapper for BoofCV',
      long_description=open('README.md', 'r').read(),
      url='https://github.com/lessthanoptimal/PyBoof',
      author="Peter Abeles",
      author_email="peter.abeles@gmail.com",
      eager_resources=['java'],
      packages=['pyboof'],
      package_data={'pyboof': ['PyBoof-all.jar','build_date.txt']},
      )
