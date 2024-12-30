# CMakeList.txt : CMake project for exampleCppFfmpeg, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("exampleCppFfmpeg")

find_package(OpenCV CONFIG REQUIRED)

include_directories(exampleCppFfmpeg PRIVATE 
	${OpenCV_INCLUDE_DIRS}
)

# Add source to this project's executable.
add_executable (exampleCppFfmpeg "exampleCppFfmpeg.cpp" "exampleCppFfmpeg.h")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET exampleCppFfmpeg PROPERTY CXX_STANDARD 20)
endif()


add_custom_command(
        TARGET exampleCppFfmpeg POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
                ${CMAKE_SOURCE_DIR}/haarcascade_frontalface_default.xml
                ${CMAKE_CURRENT_BINARY_DIR}/haarcascade_frontalface_default.xml)

target_link_libraries(exampleCppFfmpeg PRIVATE 
	${OpenCV_LIBS}
)