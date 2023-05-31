### Version 0.43.1
- Updated to BoofCV 0.43.1

### Version 0.41.1
- Globals are handled in a way they can be updated now
- Re-initializing works. Thanks gaurav-t-sca for the bug report.
- Removed printing to stdout from __init__.py
- Faults in __init__.py now print to stderr

### Version 0.41
- Updated to BoofCV 0.41
- QR Code
  - Fixed type-o in version
- Added Aztec Code support

### Version 0.40.1

- Updated to BoofCV 0.40.1
- QR Code and Micro QR Code
  - Access to raw message bytes

### Version 0.40.0

- Updated to BoofCV 0.40
- Added Micro QR Code detector and generator
- Shuffled around functions to avoid cyclical dependencies, which Python now cares about
- Updated to Py4J 0.10.9.3

### Version 0.39.1r1

- Support for more than one instance of PyBoof has been added
- mmap is used by default now
- Fixing version strings
- Added CameraKannalaBrandt
- Added ECoCheck marker for calibration
- Added Hamming Markers (e.g. ArUco and AprilTag)
- Added stereo calibration example

### Version 0.38.0

- Updated for latest BoofCV
- Added SceneRecognition
- Added Scharr gradient
- Added Wolf and Niback binarization
- Added scene reconstruction high level API

### Version 0.37.2

- Added PointTracker
- Added Video Mosaic

### Version 0.37.1

- Fixed LinkageError by ensuring it is built to be compatible with JRE 1.8

### Version 0.37

- Updated BoofCV version

### Version 0.36.1

- Works on windows now. Thanks GokulNC for pointing out the problem and how to fix it.

### Version 0.36

- Updated for latest BoofCV
- New stereo API
- Add random dot markers
- Add point cloud viewer for stereo

### Version 0.35

- Updated for latest BoofCV

### Version 0.34

- Updated for latest BoofCV
- More informative error message when py4j copy not implemented. Thanks lijingpeng for the bug report.
- Added Hough Line detector for Gradient images

### Version 0.33.1

- Updated for latest BoofCV
- Added ability to change number of threads

### Version 0.32

- Updated for latest BoofCV

### Version 0.29

- Python 3
- Dense Image Features
- More mmap data types
- QR Code detector
- QR Code encoder
- Estimate camera motion

### Version 0.26

- mmap file py <--> java list of AssociatedPair

### Version 0.25

- First release that a change file exists
- mmap file is now a temp file