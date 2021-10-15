#!/usr/bin/env python3

import numpy as np
import pyboof as pb

# Detects all the QR Codes in the image and prints their message and location
data_path = "../data/example/fiducial/qrcode/image03.jpg"

detector = pb.FactoryFiducial(np.uint8).qrcode()

image = pb.load_single_band(data_path, np.uint8)

detector.detect(image)

print("Detected a total of {} QR Codes".format(len(detector.detections)))

for qr in detector.detections:
    print("Message: "+qr.message)
    print("     at: "+str(qr.bounds))
