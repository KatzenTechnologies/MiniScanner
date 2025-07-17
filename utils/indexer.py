import os
from pathlib import Path

def index_directory(path):
    file_paths = []
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if os.access(os.path.join(root, d), os.R_OK)]
        for name in files:
            file_path = os.path.join(root, name)
            if os.access(file_path, os.R_OK):
                file_paths.append(file_path)
    return file_paths

def is_child(path_parent, path_child):
    parent = Path(path_parent)
    child = Path(path_child)
    return child.resolve().is_relative_to(parent.resolve())