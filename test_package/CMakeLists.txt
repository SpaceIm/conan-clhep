cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(CLHEP REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(CLHEP_SHARED)
  target_link_libraries(${PROJECT_NAME} CLHEP::CLHEP)
else()
  target_link_libraries(${PROJECT_NAME} CLHEP::CLHEPS)
endif()
