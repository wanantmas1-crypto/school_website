import os
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent / 'media'
TARGET_DIRS = ['site_pages', 'announcements', 'videos', 'documents', 'principals']
removed = []
errors = []
print('Media root:', root)
for d in TARGET_DIRS:
    dirpath = root / d
    if dirpath.exists() and dirpath.is_dir():
        for child in list(dirpath.iterdir()):
            try:
                if child.is_file():
                    child.unlink()
                    removed.append(str(child.relative_to(root)))
                elif child.is_dir():
                    shutil.rmtree(child)
                    removed.append(str(child.relative_to(root)))
            except Exception as e:
                errors.append((str(child), str(e)))

print('Removed:', len(removed))
for r in removed:
    print('-', r)
if errors:
    print('Errors:')
    for e in errors:
        print(e)
