#compile this project with -A x64 flag on msvc
cmake_minimum_required(VERSION 3.5)

project(imspy
	LANGUAGES CXX C
	VERSION 1.0)

add_library(imspy_c SHARED
	src/ProcessPhotonStream.cpp
	)
set_property(TARGET imspy_c PROPERTY CXX_STANDARD 11)

target_include_directories(imspy_c PUBLIC
	${PROJECT_SOURCE_DIR}/include
	${PROJECT_SOURCE_DIR}/thirdparty
	)

######################################################
# export a .pyd python library
######################################################

set( SOURCES
	src/bindings.cpp
	src/ProcessPhotonStream.cpp
	)

#generate python module
add_subdirectory( thirdparty/pybind11 )
pybind11_add_module(imspy ${SOURCES})

target_include_directories(imspy PUBLIC
	thirdparty/
	include/
	)
