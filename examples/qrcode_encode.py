#!/usr/bin/env python3

import pyboof as pb

pb.init_memmap()

generator = pb.QrCodeGenerator(pixels_per_module=5)

generator.set_message("This is my message. I'll let all other settings be "
                      "automatically selected")

boof_gray_image = generator.generate()

# Note: 0.30 will add a white border automatically.
#       A white border needs to be added for this to be a compliant QR Code
#       You can add one yourself by creating a larger image and pasting this inside of it

pb.swing.show(boof_gray_image,"QR Code")
input("Press any key to exit")