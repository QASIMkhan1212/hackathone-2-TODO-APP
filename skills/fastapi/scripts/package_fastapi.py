#!/usr/bin/env python3
"""Simple packaging script for FastAPI skill"""

import zipfile
from pathlib import Path

skill_path = Path(".claude/skills/fastapi")
output_path = Path("fastapi.skill")

print("Packaging FastAPI skill...")

with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_path in skill_path.rglob('*'):
        if file_path.is_file():
            arcname = file_path.relative_to(skill_path.parent)
            zipf.write(file_path, arcname)
            print(f"  Added: {arcname}")

print(f"\nSuccess! Created: {output_path.absolute()}")
