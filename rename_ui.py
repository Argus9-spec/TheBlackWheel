python3 <<'PY'
from pathlib import Path
import shutil
import sys

file_path = Path("src/index.html")
backup_path = Path("src/index.before-ui-language-update.html")

if not file_path.exists():
    sys.exit(f"ERROR: Could not find {file_path.resolve()}")

# Preserve the exact pre-change version.
shutil.copy2(file_path, backup_path)

text = file_path.read_text(encoding="utf-8")

replacements = [
    # Field names
    ("Sky I", "Field I"),
    ("Sky II", "Field II"),
    ("Sky III", "Field III"),

    # Control labels
    ("Dot Size", "Point Size"),
    ("Star Size", "Point Size"),
    ("Dot Density", "Point Density"),
    ("Star Density", "Point Density"),
    ("Magnitude Randomizer", "Magnitude Variation"),
    ("Center Star", "Center"),

    # Primary buttons
    ("Phantom Axis Mode", "Phantom Axis Illusion"),
    ("Phantom Axis", "Phantom Axis Illusion"),
    ("Observation Instructions", "Observation Guide"),
]

total = 0

for old, new in replacements:
    count = text.count(old)

    if count:
        text = text.replace(old, new)
        total += count
        print(f"✓ {old!r} → {new!r}  ({count})")
    else:
        print(f"– {old!r} not found")

file_path.write_text(text, encoding="utf-8")

print()
print(f"Updated: {file_path}")
print(f"Backup:  {backup_path}")
print(f"Total replacements: {total}")
PY

