import os
import shutil
import traceback
import katzo
import hashlib
import re
import psutil
import time

def wait_for_exit(list_of_processes):
    while any(p.name() in list_of_processes for p in psutil.process_iter()):
        time.sleep(0.5)
def run_uninstaller(uninstall_path: str):
    uninstall_path = uninstall_path.strip()

    match = re.match(r'^(.*?\.exe)\s*(.*)$', uninstall_path, re.IGNORECASE)
    if not match:
        return

    exe_path = match.group(1)
    args_str = match.group(2)

    args = args_str.split() if args_str else []

    try:
        os.system(
            f'{exe_path if exe_path.startswith('"') and exe_path.endswith('"') else '"' + exe_path + '"'} {" ".join(args)}')
    except:
        pass

def get_name_by_console(uninstall_path):
    uninstall_path = uninstall_path.strip()

    match = re.match(r'^(.*?\.exe)\s*(.*)$', uninstall_path, re.IGNORECASE)
    if not match:
        return

    exe_path = match.group(1)
    return (exe_path if exe_path.startswith('"') and exe_path.endswith('"') else '"' + exe_path + '"')[1:-1]


def sha512_file(filepath):
    sha512 = hashlib.sha512()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha512.update(chunk)
        return sha512.hexdigest()
    except:
        return "Can't read hash!!!"
class Main:
    name = "GarbageAway"
    version = "1.1"
    author = "Northkatz & KdR"

    # About this module:
    #  A lot of adware gets on computer with fake software
    #  Like fake steam, word, etc.
    #  And them installing programs, commonly with random hex titles (as we seen)
    #  And that programs shouldn't be on user's computer because
    #  Them takes memory and unusable usually
    # (written by KdR)

    def __init__(self, API):
        globals()["API"] = API
        API.logger.log(self.name, f"Loading {self.name} v{self.version} by {self.author}", API.LOGTYPE.INFO)
        API.logger.log(self.name, "Loading up base..", API.LOGTYPE.INFO)
        if os.path.exists("./db/garbageaway.txt") and os.path.isfile("./db/garbageaway.txt"):
            preparse = katzo.clean(open("./db/garbageaway.txt", 'r').read().split("\n"))
            self.base_exists = []
            self.base_hashes = []
            self.base_rootfiles = []
            for i in preparse:
                if i.startswith("exists:"):
                    self.base_exists.append(i[7:])
                elif i.startswith("hash:"):
                    self.base_hashes.append(i[5:])
                elif i.startswith("inroot:"):
                    self.base_rootfiles.append(i[5:])
                # no else cuz its just ignored ;)
        else:
            API.logger.log(self.name, "There's no base!")
            raise Exception("Theres no garbageaway.txt")
        self.threats = []
        self.threats_dict = {}
        self.threats2 = []

    def scan(self):
        API.logger.log(self.name, f"Scanning appdata local...", API.LOGTYPE.INFO)
        for i in os.listdir(API.paths.APPDATA_LOCAL):
            if i in self.base_rootfiles:
                API.logger.log(self.name, f"Found garbage!: {os.path.join(API.paths.APPDATA_LOCAL, i)}", API.LOGTYPE.INFO)
                API.add_threat(os.path.join(API.paths.APPDATA_LOCAL, i), "PUP.AdwareRemnants", self)
                self.threats.append(os.path.join(API.paths.APPDATA_LOCAL, i))
        API.logger.log(self.name, f"Scanning apps...", API.LOGTYPE.INFO)
        installed_apps = API.installed_apps.get_installed_apps_with_paths()

        for i in installed_apps:
            if (not i["install_path"] == "N/A" and not i["install_path"] == "" and
                    not API.indexer.is_child(API.paths.PROGRAMFILES86, i["install_path"]) and
                    not API.indexer.is_child(API.paths.PROGRAMFILES, i["install_path"])):
                API.logger.log(self.name, f"Scanning: {i['name']}",
                               API.LOGTYPE.INFO)
                files = API.indexer.index_directory(i["install_path"])
                flag = False
                for j in files:
                    if os.path.basename(j) in self.base_exists or sha512_file(j) in self.base_hashes:
                        flag = True
                        break
                if flag:
                    API.logger.log(self.name, f"Found garbage!: {os.path.join(API.paths.APPDATA_LOCAL, i["name"])}",
                                   API.LOGTYPE.INFO)
                    API.add_threat(i["name"], "PUP.Trashware", self)
                    self.threats_dict.update({i["name"]: i})
                    self.threats2.append(i["name"])

    def delete(self, file):
        if file in self.threats:
            os.remove(file)
            API.logger.log(self.name, f"Removed {file}", API.LOGTYPE.SUCCESS)
        if file in self.threats2:
            API.logger.log(self.name, f"Uninstalling: {file}",
                           API.LOGTYPE.INFO)
            run_uninstaller(self.threats_dict[file]["uninstall_path"])
            wait_for_exit(get_name_by_console(self.threats_dict[file]["uninstall_path"]))
            API.logger.log(self.name, f"Removing: {self.threats_dict[file]["install_path"]}", API.LOGTYPE.INFO)
            try:
                shutil.rmtree(self.threats_dict[file]["install_path"])
            except:
                API.logger.log(self.name, f"Error: {traceback.format_exc()}", API.LOGTYPE.INFO)