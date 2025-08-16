import os
from pathlib import Path

import os
import re


def replace_env_vars(path):
    if not path:
        return path

    pattern = r'\${([^}]+)}'
    matches = re.findall(pattern, path)

    for match in matches:
        env_var = match
        env_value = os.environ.get(env_var, '')

        if env_var == 'ProgramFiles(x86)':
            env_value = os.environ.get('ProgramFiles(x86)', '')

        if not env_value and '(' in env_var:
            base_var = env_var.split('(')[0]
            env_value = os.environ.get(base_var, '')

        path = path.replace('${' + env_var + '}', env_value)

    pattern = r'%([^%]+)%'
    matches = re.findall(pattern, path)

    for match in matches:
        env_var = match
        env_value = os.environ.get(env_var, '')

        if env_var == 'ProgramFiles(x86)':
            env_value = os.environ.get('ProgramFiles(x86)', '')

        path = path.replace('%' + env_var + '%', env_value)

    return path

import os

class FileIndexer:
    def __init__(self, include_dirs=None, include_files=None, exclude_dirs=None, exclude_files=None):
        self.include_dirs = [os.path.abspath(d) for d in (include_dirs or [])]
        self.include_files = set(os.path.abspath(f) for f in (include_files or []))
        self.exclude_dirs = set(os.path.abspath(d) for d in (exclude_dirs or []))
        self.exclude_files = set(os.path.abspath(f) for f in (exclude_files or []))

    def scan(self):
        for file_path in self.include_files:
            try:
                if os.path.isfile(file_path) and file_path not in self.exclude_files:
                    yield file_path
            except OSError:
                continue

        for root_dir in self.include_dirs:
            try:
                for root, dirs, files in os.walk(root_dir, topdown=True, onerror=lambda e: None):
                    root = os.path.abspath(root)
                    if root in self.exclude_dirs:
                        dirs[:] = []
                        continue
                    dirs[:] = [
                        d for d in dirs
                        if os.path.abspath(os.path.join(root, d)) not in self.exclude_dirs
                    ]
                    for filename in files:
                        filepath = os.path.abspath(os.path.join(root, filename))
                        if filepath not in self.exclude_files:
                            try:
                                yield filepath
                            except OSError:
                                continue
            except PermissionError:
                continue



# Indexer
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