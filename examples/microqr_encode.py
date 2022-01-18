#!/usr/bin/env python3

import pyboof as pb

generator = pb.MicroQrCodeGenerator(pixels_per_module=5)

generator.set_message("BOOFCV")

boof_gray_image = generator.generate()

pb.swing.show(boof_gray_image, "Micro QR Code")
input("Press any key to exit")
