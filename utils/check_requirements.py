import importlib.metadata
from packaging import version, requirements
import pip._internal
import sys
import katzo

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

class RequirementTool:
    def __init__(self):
        self.requirements = {}

    def add(self, requirement, plugin):
        if self.requirements.get(plugin) is None:
            self.requirements.update({plugin: [requirements.Requirement(requirement)]})
        else:
            self.requirements[plugin] += [requirements.Requirement(requirement)]

    def not_installed(self):
        missing = {}
        for i in self.requirements.keys():
            for req in self.requirements[i]:
                if req.marker and not req.marker.evaluate({"sys_platform": sys.platform}):
                    continue
                try:
                    installed_version = importlib.metadata.version(req.name)
                except importlib.metadata.PackageNotFoundError:
                    if missing.get(i) is None:
                        missing.update({i: [req]})
                    else:
                        missing[i] += [req]
                    continue
                if req.specifier and not req.specifier.contains(installed_version, prereleases=True):
                    if missing.get(i) is None:
                        missing.update({i: [req]})
                    else:
                        missing[i] += [req]
        self.missing = missing
        return self.missing == {}

    def install(self):
        if self.enabled:
            reqs = list(set(katzo.merge_arrays(self.missing.values())))
            if reqs:
                pip._internal.main(["install", *reqs])