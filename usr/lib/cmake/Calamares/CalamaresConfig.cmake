# Config file for the Calamares package
#
# It defines the following variables
#  CALAMARES_INCLUDE_DIRS - include directories for Calamares
#  CALAMARES_LIBRARIES    - libraries to link against
#  CALAMARES_USE_FILE     - name of a convenience include
#  CALAMARES_APPLICATION_NAME - human-readable application name
#
# Typical use is:
#
#    find_package(Calamares REQUIRED)
#    include("${CALAMARES_USE_FILE}")
#

# Compute paths
get_filename_component(CALAMARES_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
if(EXISTS "${CALAMARES_CMAKE_DIR}/CMakeCache.txt")
   # In build tree
   include("${CALAMARES_CMAKE_DIR}/CalamaresBuildTreeSettings.cmake")
else()
   set(CALAMARES_INCLUDE_DIRS "${CALAMARES_CMAKE_DIR}/../../../include/libcalamares")
endif()

# Our library dependencies (contains definitions for IMPORTED targets)
include("${CALAMARES_CMAKE_DIR}/CalamaresLibraryDepends.cmake")

# These are IMPORTED targets created by CalamaresLibraryDepends.cmake
set(CALAMARES_LIBRARIES calamares)

# Convenience variables
set(CALAMARES_USE_FILE "${CALAMARES_CMAKE_DIR}/CalamaresUse.cmake")
set(CALAMARES_APPLICATION_NAME  "Calamares")
