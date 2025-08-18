import importlib.metadata
from packaging import version, requirements
import pip._internal
import sys

def parse_requirements_file(path="requirements.txt"):
    reqs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            reqs.append(requirements.Requirement(line))
    return reqs

def check_requirements(reqs):
    missing = []
    for req in reqs:
        if req.marker and not req.marker.evaluate({"sys_platform": sys.platform}):
            continue
        try:
            installed_version = importlib.metadata.version(req.name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(str(req))
            continue
        if req.specifier and not req.specifier.contains(installed_version, prereleases=True):
            missing.append(str(req))
    return missing

def install_requirements(reqs):
    if reqs:
        pip._internal.main(["install", *reqs])

