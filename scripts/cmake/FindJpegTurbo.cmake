# Replacement for Aseprite's cmake/FindJpegTurbo.cmake that links the system
# libjpeg(-turbo) instead of downloading sources from GitHub at build time.
# Used by scripts/setup-aseprite.sh for sandboxed/offline builds where the
# original ExternalProject download is blocked by an egress proxy.

if(LAF_BACKEND STREQUAL "skia")

  find_library(LIBJPEG_TURBO_LIBRARY NAMES libjpeg jpeg
    HINTS "${SKIA_LIBRARY_DIR}" NO_DEFAULT_PATH)
  set(LIBJPEG_TURBO_INCLUDE_DIRS "${SKIA_DIR}/third_party/externals/libjpeg-turbo")

  add_library(libjpeg-turbo STATIC IMPORTED)
  set_target_properties(libjpeg-turbo PROPERTIES
    IMPORTED_LOCATION "${LIBJPEG_TURBO_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES ${LIBJPEG_TURBO_INCLUDE_DIRS})

else()

  find_library(LIBJPEG_TURBO_LIBRARY NAMES jpeg REQUIRED)
  find_path(LIBJPEG_TURBO_INCLUDE_DIRS NAMES jpeglib.h REQUIRED)

  add_library(libjpeg-turbo UNKNOWN IMPORTED)
  set_target_properties(libjpeg-turbo PROPERTIES
    IMPORTED_LOCATION "${LIBJPEG_TURBO_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${LIBJPEG_TURBO_INCLUDE_DIRS}")

endif()
