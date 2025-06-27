import os
import shutil
import traceback
import winreg
import tkinter.messagebox as msg
import time
import psutil



def delete_registry_tree(root, path, not_recursive=True):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    subkey = winreg.EnumKey(key, 0)
                    delete_registry_tree(root, fr"{path}\{subkey}", not_recursive=False)
                except OSError:
                    break
        winreg.DeleteKey(root, path)
        if not_recursive:
            API.logger.log("AdwareKiller", f"Removed {"HKLM" if root == winreg.HKEY_LOCAL_MACHINE else ""}{"HKCU" if root == winreg.HKEY_CURRENT_USER else ""}\\{path}", API.LOGTYPE.INFO)
    except Exception as e:
        pass

def check_registry_key_exists(hive, key):
    try:
        winreg.OpenKey(hive, key)
        return True
    except FileNotFoundError:
        return False

def check_firewall(rules):
    firewall_rules = API.firewall_tools.get_firewall_rules()
    for i in firewall_rules:
        if i.name in rules:
            return True
    return False

def get_relative(hive, key):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_READ) as key:
            value, value_type = winreg.QueryValueEx(key, "")
            return value
    except FileNotFoundError:
        return ""

def wait_for_exit(list_of_processes):
    while any(p.name() in list_of_processes for p in psutil.process_iter()):
        time.sleep(0.5)

def dir_exists(direc):
    return os.path.exists(direc) and os.path.isdir(direc)

def file_exists(file):
    return os.path.exists(file) and os.path.isfile(file)

def check_autoruns(lst):
    SourceType = API.autorun_utils.SourceType
    get_autoruns = API.autorun_utils.get_autoruns

    autoruns = get_autoruns([SourceType.HKLM_RUN, SourceType.HKCU_RUN])
    for i in autoruns:
        for j in lst:
            if j in i.command:
                return True
    return False


class Main:
    name = "AdwareKiller"
    def __init__(self, API):
        globals()["API"] = API
        self.base = [
            ["Download Studio", "PUP.DStudio"],
            ["Zona", "Adware.Zona"],
            ["MediaGet", "Adware.Mediaget"],
            ["Telamon Cleaner", "PUP.Telamon"]
        ]
        self.threats_families = []
        self.threats = {}

    def scan(self):
        installed_apps = API.installed_apps.get_installed_apps_with_paths()

        for i in installed_apps:
            for j in self.base:
                if j[0] in i["name"]:
                    API.add_threat(i["name"], j[1], self)
                    self.threats.update({i["name"]: [j[1], i]})
                    self.threats_families.append(j[1])

        download_studio_flag = any([check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"Software\Download Studio"),
                                    check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\DownloadStudio.MagnetUri.1"),
                                    check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\DownloadStudio.TorrentFile.1"),
                                    check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"Software\Download Studio"),
                                    check_firewall(["Download Studio", "Download Studio Daemon", "Download Studio WebEngine"]),
                                    "dstudio-gui.exe" in get_relative(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\magnet\DefaultIcon"),
                                    dir_exists(API.paths.APPDATA_LOCAL+"\\Download Studio")])

        if not "Adware.DStudio" in self.threats_families and download_studio_flag:
            API.add_threat("Download Studio (remnants)", "PUP.DStudio", self)
            self.threats.update({"Download Studio (remnants)": ["PUP.DStudio", {"uninstall_path":""}]})

        zona_flag = any([check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"Software\Zona"),
                                    check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"Software\magnet\Handlers\Zona"),
                                    check_firewall(["Zona.exe"]),
                                    'Zona.exe" "%1"' in get_relative(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\DHT\shell\open\command"),
                                    dir_exists(API.paths.APPDATA_ROAMING+"\\Zona"),
                                    file_exists(API.paths.WINDIR+"\\ZonaUpdater.log")])

        if not "Adware.Zona" in self.threats_families and zona_flag:
            API.add_threat("Zona (remnants)", "Adware.Zona", self)
            self.threats.update({"Zona (remnants)": ["Adware.Zona", {"uninstall_path":""}]})

        mediaget_flag = any([check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagetcatalogparams"),
                            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagettorrentfile"),
                            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagetvideofile"),
                            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Media Get LLC"),
                            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\MediaGet"),
                            'mediaget.exe' in get_relative(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Magnet\DefaultIcon"),
                             check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\Directory\shell\PlayWithMediaGet"),
                             dir_exists(API.paths.USERPROFILE+'\\mediaget2'),
                             check_firewall(["MediaGet"]),
                             dir_exists(API.paths.APPDATA_LOCAL+'\\Media Get LLC'),
                             check_autoruns(['mediaget.exe', "proxy-sdk.exe"])])

        if not "Adware.Mediaget" in self.threats_families and mediaget_flag:
            API.add_threat("Mediaget (remnants)", "Adware.Mediaget", self)
            self.threats.update({"Mediaget (remnants)": ["Adware.Mediaget", {"uninstall_path":""}]})

        telamon_cleaner_flag = dir_exists(API.paths.APPDATA_LOCAL+'\\TelamonCleaner')

        if not "PUP.Telamon" in self.threats_families and telamon_cleaner_flag:
            API.add_threat("Telamon Cleaner (remnants)", "PUP.Telamon", self)
            self.threats.update({"Telamon Cleaner (remnants)": ["PUP.Telamon", {"uninstall_path":""}]})
    def delete(self, file):

        if file in self.threats.keys():
            if API.chosen_language.language_name == "Русский":
                msg.showinfo("AdwareKiller",
                             "Будет запущена программа удаления.\nДля очистки от следов потребуются права администратора, если их нет, перезапустите с ними.")
            else:
                msg.showinfo("AdwareKiller",
                             "The removal program will be launched.\nAdministrator rights are required to clean up all traces.\nIf you don't have them, please restart with administrative privileges.")

            match self.threats[file][0]:
                case "PUP.DStudio":
                    API.process_utils.kill_processes_by_name("dstudio.exe")
                    API.process_utils.kill_processes_by_name("dstudio-gui.exe")
                    os.system(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["unins000.exe", "UN_DS.exe"])
                    # Deep Remove
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Download Studio")
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\DownloadStudio.MagnetUri.1")
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\DownloadStudio.TorrentFile.1")
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"Software\Download Studio")

                    API.logger.log("AdwareKiller", r"Checking for relative: SOFTWARE\Classes\magnet",
                                   API.LOGTYPE.INFO)

                    if "dstudio-gui.exe" in get_relative(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\magnet\DefaultIcon"):
                        API.logger.log("AdwareKiller", r"Relative is true!: SOFTWARE\Classes\magnet",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\magnet")

                    try:
                        if dir_exists(API.paths.APPDATA_LOCAL+"\\Download Studio"):
                            API.logger.log("AdwareKiller", f"Removing: {API.paths.APPDATA_LOCAL}/Download Studio",
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.APPDATA_LOCAL+"\\Download Studio")
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

                    API.logger.log("AdwareKiller", r"Scanning firewall rules...", API.LOGTYPE.INFO)
                    firewall_rules = API.firewall_tools.get_firewall_rules()
                    for i in firewall_rules:
                        if i.name in ["Download Studio", "Download Studio Daemon", "Download Studio WebEngine"]:
                            API.logger.log("AdwareKiller", r"Found DStudio rule, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)
                case "Adware.Zona":
                    API.process_utils.kill_processes_by_name("ZonaUpdater.exe")
                    API.process_utils.kill_processes_by_name("Zona.exe")
                    os.system(self.threats[file][1]["uninstall_path"])
                    # Deep Remove
                    wait_for_exit(["uninstall.exe"])

                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"Software\Zona")
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\magnet\Handlers\Zona")

                    API.logger.log("AdwareKiller", r"Scanning firewall rules...", API.LOGTYPE.INFO)
                    firewall_rules = API.firewall_tools.get_firewall_rules()
                    for i in firewall_rules:
                        if i.name == "Zona.exe":
                            API.logger.log("AdwareKiller", r"Found Zona's rule, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)

                    API.logger.log("AdwareKiller", r"Checking for relative: HKCU\SOFTWARE\Classes\DHT", API.LOGTYPE.INFO)
                    if 'Zona.exe" "%1"' in get_relative(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\DHT\shell\open\command"):
                        API.logger.log("AdwareKiller", r"Relative is true!: HKCU\SOFTWARE\Classes\DHT",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\DHT")

                    API.logger.log("AdwareKiller", r"Checking for relative: HKCU\SOFTWARE\Classes\DHT\DefaultIcon",
                                   API.LOGTYPE.INFO)

                    try:
                        if dir_exists(API.paths.APPDATA_ROAMING+"\\Zona"):
                            API.logger.log("AdwareKiller", f"Removing: {API.paths.APPDATA_ROAMING}/Zona",
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.APPDATA_ROAMING+"\\Zona")
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

                    try:
                        if file_exists(API.paths.WINDIR+"\\ZonaUpdater.log"):
                            API.logger.log("AdwareKiller", f"Removing: {API.paths.WINDIR}/ZonaUpdater.log",
                                           API.LOGTYPE.INFO)
                            os.remove(API.paths.WINDIR+"\\ZonaUpdater.log")
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

                    try:
                        if dir_exists(os.path.dirname(self.threats[file][1]["uninstall_path"])):
                            API.logger.log("AdwareKiller", r"Removing: "+os.path.dirname(self.threats[file][1]["uninstall_path"]),
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(os.path.dirname(self.threats[file][1]["uninstall_path"]))
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)
                case "Adware.Mediaget":
                    API.process_utils.kill_processes_by_name("mediaget.exe")
                    API.process_utils.kill_processes_by_name("proxy-sdk.exe")
                    os.system(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["mediaget-uninstaller.exe"])
                    # Deep Remove
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagetcatalogparams")
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagettorrentfile")
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagetvideofile")
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Media Get LLC")
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\MediaGet")
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\Directory\shell\PlayWithMediaGet")


                    API.logger.log("AdwareKiller", r"Checking for relative: HKCU\SOFTWARE\Classes\Magnet", API.LOGTYPE.INFO)
                    if 'mediaget.exe' in get_relative(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Magnet\DefaultIcon"):
                        API.logger.log("AdwareKiller", r"Relative is true!: HKCU\SOFTWARE\Classes\Magnet",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Magnet")


                    SourceType = API.autorun_utils.SourceType
                    get_autoruns = API.autorun_utils.get_autoruns

                    API.logger.log("AdwareKiller", r"Scanning autoruns...", API.LOGTYPE.INFO)
                    autoruns = get_autoruns([SourceType.HKLM_RUN, SourceType.HKCU_RUN])
                    for i in autoruns:
                        if 'mediaget.exe' in i.command:
                            API.logger.log("AdwareKiller", r"Found Mediaget, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)
                        if "proxy-sdk.exe" in i.command:
                            API.logger.log("AdwareKiller", r"Found ProxySDK, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)

                    API.logger.log("AdwareKiller", r"Scanning firewall rules...", API.LOGTYPE.INFO)
                    firewall_rules = API.firewall_tools.get_firewall_rules()
                    for i in firewall_rules:
                        if i.name == "MediaGet":
                            API.logger.log("AdwareKiller", r"Found Mediaget rule, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)

                    try:
                        if dir_exists(API.paths.USERPROFILE+'\\mediaget2'):
                            API.logger.log("AdwareKiller", r"Removing: "+API.paths.USERPROFILE+'\\mediaget2',
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.USERPROFILE+'\\mediaget2')
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

                    try:
                        if dir_exists(API.paths.APPDATA_LOCAL+'\\Media Get LLC'):
                            API.logger.log("AdwareKiller", r"Removing: "+API.paths.APPDATA_LOCAL+'\\Media Get LLC',
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.APPDATA_LOCAL+'\\Media Get LLC')
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)
                case "PUP.Telamon":
                    API.process_utils.kill_processes_by_name("TelamonCleaner.exe")
                    os.system(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["TelamonCleaner.exe"])
                    # Deep Remove
                    try:
                        if dir_exists(os.path.dirname(self.threats[file][1]["uninstall_path"])):
                            API.logger.log("AdwareKiller",
                                           r"Removing: " + os.path.dirname(self.threats[file][1]["uninstall_path"]),
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(os.path.dirname(self.threats[file][1]["uninstall_path"]))
                    except:
                        API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                       API.LOGTYPE.ERROR)
                    try:
                        if dir_exists(API.paths.APPDATA_LOCAL+"\\TelamonCleaner"):
                            API.logger.log("AdwareKiller", f"Removing: {API.paths.APPDATA_LOCAL}/TelamonCleaner",
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.APPDATA_LOCAL+"\\TelamonCleaner")
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

            API.logger.log("AdwareKiller", f"Removed {file}", API.LOGTYPE.SUCCESS)