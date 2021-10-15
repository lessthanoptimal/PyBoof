#!/usr/bin/env python3

import pyboof as pb

generator = pb.QrCodeGenerator(pixels_per_module=5)

generator.set_message("This is my message. I'll let all other settings be "
                      "automatically selected")

boof_gray_image = generator.generate()

pb.swing.show(boof_gray_image, "QR Code")
input("Press any key to exit")
