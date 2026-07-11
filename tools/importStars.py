from PIL import Image

import os
import sys

if len(sys.argv) != 5:
    print(
        'Usage: python3 tools/importStars.py '
        '"input.png" "output.js" "exportName" "Display Name"'
    )
    sys.exit(1)

INPUT = sys.argv[1]
OUTPUT = sys.argv[2]
EXPORT_NAME = sys.argv[3]
DISPLAY_NAME = sys.argv[4]

THRESHOLD = 200

img = Image.open(INPUT).convert("RGBA")
w, h = img.size
pixels = img.load()

visited = set()
stars = []

def is_star_pixel(x, y):
    r, g, b, a = pixels[x, y]
    return a > 0 and r > THRESHOLD and g > THRESHOLD and b > THRESHOLD

def flood_fill(start_x, start_y):
    stack = [(start_x, start_y)]
    points = []

    while stack:
        x, y = stack.pop()

        if (x, y) in visited:
            continue

        if x < 0 or y < 0 or x >= w or y >= h:
            continue

        if not is_star_pixel(x, y):
            continue

        visited.add((x, y))
        points.append((x, y))

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))

    return points

for y in range(h):
    for x in range(w):
        if (x, y) not in visited and is_star_pixel(x, y):
            points = flood_fill(x, y)

            if len(points) > 0:
                cx = sum(p[0] for p in points) / len(points)
                cy = sum(p[1] for p in points) / len(points)

                stars.append((cx, cy, len(points)))

print("Black Wheel importer is alive.")
print("Image size:", img.size)
print("Stars detected:", len(stars))
print("First star:", stars[0])
print("Last star:", stars[-1])
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w") as file:
    file.write(f"export const {EXPORT_NAME} = {{\n")
    file.write(f'  name: "{DISPLAY_NAME}",\n')
    file.write(f"  width: {w},\n")
    file.write(f"  height: {h},\n")
    file.write(f"  starCount: {len(stars)},\n")
    file.write("  stars: [\n")

    for cx, cy, size in stars:
        nx = (cx - w / 2) / (w / 2)
        ny = (cy - h / 2) / (h / 2)

        file.write(
            f"    {{ x: {nx:.8f}, y: {ny:.8f}, size: {size} }},\n"
        )

    file.write("  ]\n")
    file.write("};\n")

print("JavaScript wheel data created:")
print(OUTPUT)