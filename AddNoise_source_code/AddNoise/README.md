#
Prerequisites:
1. OpenCV 3.4
2. libalglib

Build:
cd AddNoise
mkdir build
cd build
cmake ..
make

Example:
./AddNoiseToDataset PathToSequenceSource PathToSequenceDestination imagePrefix sigma_s sigma_c
