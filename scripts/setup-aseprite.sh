#!/usr/bin/env bash
# Build a headless (CLI-only) Aseprite for use with aseprite-mcp.
#
# ENABLE_UI=OFF + LAF_BACKEND=none skips Skia and X11 entirely, so the build
# works in headless containers and only needs common -dev packages. The
# resulting binary supports batch mode (-b), Lua scripting, and all export
# formats — everything aseprite-mcp uses.
#
# Usage: scripts/setup-aseprite.sh [install-prefix]   (default: ~/aseprite)
set -euo pipefail

PREFIX="${1:-$HOME/aseprite}"
SRC_DIR="${ASEPRITE_SRC:-$HOME/aseprite-src}"
JOBS="$(nproc)"

if ! command -v cmake >/dev/null || ! command -v ninja >/dev/null; then
  echo "cmake and ninja are required (apt-get install cmake ninja-build g++)" >&2
  exit 1
fi

sudo_maybe() { if [ "$(id -u)" -eq 0 ]; then "$@"; else sudo "$@"; fi; }
sudo_maybe apt-get install -y -qq \
  libpixman-1-dev libfreetype6-dev libharfbuzz-dev zlib1g-dev \
  libpng-dev libjpeg-dev libcurl4-openssl-dev libgif-dev libtinyxml2-dev \
  libx11-dev libxcursor-dev libxi-dev libxrandr-dev libxrender-dev \
  libxext-dev libxfixes-dev libgl1-mesa-dev libfontconfig1-dev

if [ ! -d "$SRC_DIR/.git" ]; then
  git clone --depth 1 --recurse-submodules --shallow-submodules -j"$JOBS" \
    https://github.com/aseprite/aseprite.git "$SRC_DIR"
fi

# Link the system libjpeg instead of letting CMake download libjpeg-turbo
# sources from GitHub mid-build (blocked in sandboxed sessions).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/cmake/FindJpegTurbo.cmake" "$SRC_DIR/cmake/FindJpegTurbo.cmake"

cmake -S "$SRC_DIR" -B "$SRC_DIR/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_UI=OFF \
  -DLAF_BACKEND=none \
  -DENABLE_SCRIPTING=ON \
  -DENABLE_CCACHE=OFF
cmake --build "$SRC_DIR/build" -j"$JOBS" --target aseprite

mkdir -p "$PREFIX"
cp -a "$SRC_DIR/build/bin/." "$PREFIX/"

echo
echo "Aseprite (headless) installed at: $PREFIX/aseprite"
echo "Set: export ASEPRITE_PATH=$PREFIX/aseprite"
"$PREFIX/aseprite" --version
