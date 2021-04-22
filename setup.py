#!/usr/bin/env python3

import os.path
import time
from setuptools import setup
from setuptools.command.build_py import build_py
from subprocess import call
import re


def check_for_command(command):
    try:
        call([command], stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
        return True
    except:
        return False


class MyBuild(build_py):
    def run(self):
        try:
            if os.path.exists('pyboof/PyBoof-all.jar'):
                print("*** Skipping java build since 'pyboof/PyBoof-all.jar' already exists ***")
                print("   'rm pyboof/PyBoof-all.jar' if this is not desired")
            else:
                # Create build date file.  This is used to determine if the java jar and python code are
                # compatible with each other
                f = open('pyboof/build_date.txt', 'w')
                f.write(str(int(round(time.time() * 1000))))
                f.close()
                # See if javac is available for compiling the java code
                if check_for_command("javac"):
                    if call(["bash", "gradlew", "allJar"]) != 0:
                        print("Gradle build failed.  ")
                        exit(1)
                else:
                    print("javac cannot be found. Please install it or correct your path.")
                    if os.path.isfile('pyboof/PyBoof-all.jar'):
                        print("     Found a precompiled jar.  Using that")
                    else:
                        exit(1)
        except Exception as e:
            print("Exception message:")
            print(str(e))
            print(e.message)
            print()
            if not os.path.isfile('pyboof/PyBoof-all.jar'):
                print("Gradle build failed AND there is no PyBoof-all.jar")
                print("")
                print("Did you run build as a regular user first?")
                print("    ./setup.py build")
                print("Is Gradle and Java installed?  Test by typing the following:")
                print("    gradle allJar")
                exit(1)
        build_py.run(self)


setup(name='PyBoof',
      cmdclass={'build_py': MyBuild},
      version='0.37.2',  # Change in in __init__ too
      description='Py4J Python wrapper for BoofCV',
      long_description=open('README.md', 'r').read(),
      long_description_content_type="text/markdown",
      url='https://github.com/lessthanoptimal/PyBoof',
      author="Peter Abeles",
      author_email="peter.abeles@gmail.com",
      license="Apache 2.0",
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 3.5'],
      python_requires='>=3',
      eager_resources=['java'],
      packages=['pyboof'],
      package_data={'pyboof': ['PyBoof-all.jar', 'build_date.txt']},
      install_requires=['py4j==0.10.8.1', 'numpy>=1.14.0', 'six>=1.11.0', 'transforms3d>=0.3.1'],
      )
