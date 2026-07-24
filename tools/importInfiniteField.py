from __future__ import annotations

from PIL import Image

import os
import struct
import sys
from typing import List, Set, Tuple


USAGE = (
    'Usage: python3 tools/importInfiniteField.py '
    '"input.png" "output.bin"'
)

THRESHOLD = 200
MAGIC = b"BWIF"
FORMAT_VERSION = 1
RECORD_SIZE = 12
REFERENCE_WIDTH = 3988
REFERENCE_HEIGHT = 3844
HEADER_STRUCT = struct.Struct("<4sHHIII")
POINT_STRUCT = struct.Struct("<ffI")

# The Infinite Field source is intentionally very large and is created locally.
# Disable Pillow's decompression-bomb limit for this trusted project asset.
Image.MAX_IMAGE_PIXELS = None


if len(sys.argv) != 3:
    print(USAGE)
    sys.exit(1)

INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


img = Image.open(INPUT).convert("RGBA")
w, h = img.size
pixels = img.load()

print("Black Wheel Infinite Field importer is alive.")
print("Image size:", img.size)



visited: Set[Tuple[int, int]] = set()
points_found: List[Tuple[float, float, int]] = []


def is_point_pixel(x: int, y: int) -> bool:
    r, g, b, a = pixels[x, y]
    return (
        a > 0
        and r > THRESHOLD
        and g > THRESHOLD
        and b > THRESHOLD
    )


def flood_fill(start_x: int, start_y: int) -> List[Tuple[int, int]]:
    stack = [(start_x, start_y)]
    component: List[Tuple[int, int]] = []

    while stack:
        x, y = stack.pop()

        if (x, y) in visited:
            continue

        if x < 0 or y < 0 or x >= w or y >= h:
            continue

        if not is_point_pixel(x, y):
            continue

        visited.add((x, y))
        component.append((x, y))

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))

    return component


for y in range(h):
    for x in range(w):
        if (
            (x, y) not in visited
            and is_point_pixel(x, y)
        ):
            component = flood_fill(x, y)

            if component:
                cx = (
                    sum(
                        point[0]
                        for point in component
                    )
                    / len(component)
                )

                cy = (
                    sum(
                        point[1]
                        for point in component
                    )
                    / len(component)
                )

                nx = (
                    cx - w / 2
                ) / (
                    REFERENCE_WIDTH / 2
                )

                ny = (
                    cy - h / 2
                ) / (
                    REFERENCE_HEIGHT / 2
                )

                points_found.append(
                    (
                        nx,
                        ny,
                        len(component)
                    )
                )

if not points_found:
    print("No points detected. Nothing was written.")
    sys.exit(1)


output_directory = os.path.dirname(OUTPUT)
if output_directory:
    os.makedirs(output_directory, exist_ok=True)


with open(OUTPUT, "wb") as file:
    file.write(
        HEADER_STRUCT.pack(
            MAGIC,
            FORMAT_VERSION,
            RECORD_SIZE,
            w,
            h,
            len(points_found),
        )
    )

    for x, y, size in points_found:
        file.write(POINT_STRUCT.pack(x, y, size))


expected_size = HEADER_STRUCT.size + len(points_found) * POINT_STRUCT.size
actual_size = os.path.getsize(OUTPUT)

if actual_size != expected_size:
    raise RuntimeError(
        f"Binary size mismatch: expected {expected_size} bytes, "
        f"wrote {actual_size} bytes."
    )

print("Points detected:", len(points_found))
print("First point:", points_found[0])
print("Last point:", points_found[-1])
print("Binary format: BWIF version 1")
print("Record layout: float32 x, float32 y, uint32 size")
print("Binary data created:")
print(OUTPUT)
print("File size:", actual_size, "bytes")
