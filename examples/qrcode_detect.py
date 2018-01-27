import numpy as np

import pyboof as pb

# Demonstration of how to calibrate a camera using a pinhole model
pb.init_memmap()

data_path = "../data/example/fiducial/qrcode/image03.jpg"

detector = pb.FactoryFiducial(np.uint8).qrcode()

image = pb.load_single_band(data_path, np.uint8)

detector.detect(image)

print("Detected a total of {} QR Codes".format(len(detector.detections)))

for qr in detector.detections:
    print("Message: "+qr.message)
    print("     at: "+str(qr.bounds))
