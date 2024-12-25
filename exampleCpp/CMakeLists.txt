# CMakeList.txt : CMake project for exampleCpp, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("exampleCpp")

find_package(OpenCV CONFIG REQUIRED)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0)
pkg_check_modules(GSTREAMER_BASE REQUIRED gstreamer-base-1.0)
pkg_check_modules(GSTREAMER_APP REQUIRED gstreamer-app-1.0)


include_directories(exampleCpp PRIVATE 
	${OpenCV_INCLUDE_DIRS}
	${GSTREAMER_INCLUDE_DIRS}
	${GSTREAMER_BASE_INCLUDE_DIRS}
	${GSTREAMER_APP_INCLUDE_DIRS}
)

link_directories(${GSTREAMER_LIBRARY_DIRS} ${GSTREAMER_BASE_LIBRARY_DIRS})
add_definitions(${GSTREAMER_CFLAGS_OTHER})

# Add source to this project's executable.
add_executable (exampleCpp "exampleCpp.cpp" "exampleCpp.h")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET exampleCpp PROPERTY CXX_STANDARD 20)
endif()

add_custom_command(
        TARGET exampleCpp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
                ${CMAKE_SOURCE_DIR}/haarcascade_frontalface_default.xml
                ${CMAKE_CURRENT_BINARY_DIR}/haarcascade_frontalface_default.xml)

# TODO: Add tests and install targets if needed.
target_link_libraries(exampleCpp PRIVATE 
	${OpenCV_LIBS}
	${GSTREAMER_LIBRARIES}
	${GSTREAMER_BASE_LIBRARIES}
	${GSTREAMER_APP_LIBRARIES}
)