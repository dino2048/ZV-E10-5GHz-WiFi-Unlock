#!/bin/sh
# Rebuild into an ignored directory; never replace the pinned runtime helpers.
set -eu
cd "$(dirname "$0")"
CLANG_BIN=${CLANG:-clang}
ARM_LINKER=${ARM_LD:-arm-none-eabi-ld}
BUILD_PYTHON=${PYTHON:-python3}
for tool in "$CLANG_BIN" "$ARM_LINKER" "$BUILD_PYTHON"; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Required build tool not found: $tool" >&2; exit 1; }
done
mkdir -p build
for name in patch restore; do
  "$CLANG_BIN" --target=arm-linux-gnueabi -c "$name.s" -o "build/$name.o"
  "$ARM_LINKER" -Ttext=0x10000 -e _start -o "build/$name.arm" "build/$name.o"
  rm "build/$name.o"
done
"$BUILD_PYTHON" -B check_offline.py --rebuilt-dir build
