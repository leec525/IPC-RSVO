cmake_minimum_required(VERSION 3.0)
project(AddNoise)

set(CMAKE_CXX_STANDARD 14)

find_package(OpenCV 3.4 REQUIRED)

include_directories( ${OpenCV_INCLUDE_DIRS} )
set( THIRD_PARTY_LIBS    ${OpenCV_LIBS} )

include_directories(
        ${PROJECT_NAME}
        /usr/include/libalglib/
)

add_executable(AddNoiseToDataset AddNoiseToDataset.cpp)

target_link_libraries(AddNoiseToDataset ${THIRD_PARTY_LIBS}  /usr/lib/x86_64-linux-gnu/libalglib.so)


