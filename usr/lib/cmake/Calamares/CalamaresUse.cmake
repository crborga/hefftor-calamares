# A setup-cmake-things-for-Calamares module.
#
# This module handles looking for dependencies and including
# all of the Calamares macro modules, so that you can focus
# on just using the macros to build Calamares modules.
# Typical use looks like this:
#
# ```
# find_package( Calamares REQUIRED )
# include( "${CALAMARES_CMAKE_DIR}/CalamaresUse.cmake" )
# ```
#
# The first CMake command finds Calamares (which will contain
# this file), then adds the found location to the search path,
# and then includes this file. After that, you can use
# Calamares module and plugin macros.

if( NOT CALAMARES_CMAKE_DIR )
    message( FATAL_ERROR "Use find_package(Calamares) first." )
endif()
set( CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CALAMARES_CMAKE_DIR} )

find_package( Qt5 5.9.0 CONFIG REQUIRED Core Widgets LinguistTools )

include( CalamaresAddLibrary )
include( CalamaresAddModuleSubdirectory )
include( CalamaresAddPlugin )
include( CalamaresAddBrandingSubdirectory )

