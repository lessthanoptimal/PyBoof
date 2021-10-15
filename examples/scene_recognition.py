#!/usr/bin/env python3

import glob
import numpy as np
import pyboof as pb

# Scene recognition is defined here as the problem where you wish to find multiple views of the same scene
# In this example we will load a set of images that has sets of 3 related images. We will tell it to find the 5
# most similar images so that you can see what it does when it fails to find a good match

# Get a list of all images which we wish to search
list_images = list(glob.glob("../data/example/recognition/scene/*.jpg"))
list_images.sort()

# Create an instance of SceneRecognition. This will take in images as input
recognizer = pb.FactorySceneRecognition(np.uint8).scene_recognition()

# First we need to create a model so that it knows how to describe a model. BoofCV does provide a
# pre-build model generated from vacation photos. This is fast enough that often its just easier to train it
# on the images you plan to search.
print("Learning the model. This can take a moment or two.")
recognizer.learn_model(list_images)

# Alternatively you can comment out the code above (lines 18 to 24) and load
# a pre-build model by uncommenting the line below
# recognizer = pb.download_default_scene_recognition(np.uint8, "saved_models")

# Now add all the images that we wish to look up
print("Adding images to the database")
for image_file in list_images:
    boof_gray = pb.load_single_band(image_file, np.uint8)
    recognizer.add_image(image_file, boof_gray)

# Let's look one up and see which images are related
print("Making a query: ", list_images[6])
query_image = pb.load_single_band(list_images[6], np.uint8)
found_matches = recognizer.query(query_image, 5)

# We are expecting 3 matches to be first, then other two will be incorrect/noise
print("len={}".format(len(found_matches)))
print("\nResults:")
for m in found_matches:
    print("{:s} error={:f}".format(m["id"], m["error"]))

# Display the results
image_list = [(query_image, "Query")]
for m in found_matches:
    image_list.append((pb.load_planar(m["id"], np.uint8), m["id"]))
pb.swing.show_list(image_list, title="Query Results")

input("Press any key to exit")
