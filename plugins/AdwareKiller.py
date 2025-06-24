import os
import shutil
import traceback
import winreg
import tkinter.messagebox as msg
import time
import psutil


def delete_registry_tree(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    subkey = winreg.EnumKey(key, 0)
                    delete_registry_tree(root, fr"{path}\{subkey}")
                except OSError:
                    break
        winreg.DeleteKey(root, path)
    except Exception as e:
        pass

class Main:
    name = "AdwareKiller"
    def __init__(self, API):
        globals()["API"] = API
        self.base = [
            ["Download Studio", "Adware.DStudio"],
            ["Zona", "Adware.Zona"],
            ["MediaGet", "Adware.Mediaget"]
        ]
        self.threats = {}

    def scan(self):
        installed_apps = API.installed_apps.get_installed_apps_with_paths()

        for i in installed_apps:
            for j in self.base:
                if j[0] in i["name"]:
                    API.add_threat(i["name"], j[1], self)
                    self.threats.update({i["name"]: [j[1], i]})

    def delete(self, file):
        if file in self.threats.keys():
            if API.chosen_language.language_name == "Русский":
                msg.showinfo("AdwareKiller",
                             "Будет запущена программа удаления.\nДля очистки от следов потребуются права администратора, если их нет, перезапустите с ними.")
            else:
                msg.showinfo("AdwareKiller",
                             "The removal program will be launched.\nAdministrator rights are required to clean up all traces.\nIf you don't have them, please restart with administrative privileges.")

            match self.threats[file][0]:
                case "Adware.DStudio":
                    API.process_utils.kill_processes_by_name("dstudio.exe")
                    API.process_utils.kill_processes_by_name("dstudio-gui.exe")
                    os.system(self.threats[file][1]["uninstall_path"])
                    while True:
                        found = False
                        for i in psutil.process_iter():
                            if i.name() == ["unins000.exe", "UN_DS.exe"]:
                                found = True
                        if not found:
                            break
                    # Deep Remove
                    API.logger.log("AdwareKiller", r"Removing HKLM\Software\Download Studio", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Download Studio")

                    API.logger.log("AdwareKiller", r"Removing HKLM\Software\Classes\DownloadStudio.MagnetUri.1", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\DownloadStudio.MagnetUri.1")

                    API.logger.log("AdwareKiller", r"Removing HKLM\Software\Classes\DownloadStudio.TorrentFile.1", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\DownloadStudio.TorrentFile.1")

                    API.logger.log("AdwareKiller", r"Removing HKCU\Software\Download Studio",
                                   API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"Software\Download Studio")

                    API.logger.log("AdwareKiller", r"Checking for relative: SOFTWARE\Classes\magnet",
                                   API.LOGTYPE.INFO)
                    flag = False
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\magnet\DefaultIcon", 0, winreg.KEY_READ) as key:
                        value, value_type = winreg.QueryValueEx(key, "")
                        if "dstudio-gui.exe" in value:
                            API.logger.log("AdwareKiller", r"Relative is true!: SOFTWARE\Classes\magnet",
                                           API.LOGTYPE.INFO)
                            flag = True
                    if flag:
                        API.logger.log("AdwareKiller", r"Removing HKCU\Software\Classes\magnet",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\magnet")

                    try:
                        if os.path.exists(API.paths.APPDATA_LOCAL+"\\Download Studio") and os.path.isdir(API.paths.APPDATA_LOCAL+"\\Download Studio"):
                            API.logger.log("AdwareKiller", r"Removing: $APPDATA_LOCAL/Download Studio",
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.APPDATA_LOCAL+"\\Download Studio")
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

                case "Adware.Zona":
                    API.process_utils.kill_processes_by_name("ZonaUpdater.exe")
                    API.process_utils.kill_processes_by_name("Zona.exe")
                    os.system(self.threats[file][1]["uninstall_path"])
                    # Deep Remove
                    while True:
                        found = False
                        for i in psutil.process_iter():
                            if i.name() == "uninstall.exe":
                                found = True
                        if not found:
                            break

                    API.logger.log("AdwareKiller", r"Removing HKCU\Software\Zona", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"Software\Zona")

                    API.logger.log("AdwareKiller", r"Removing HKLM\Software\magnet\Handlers\Zona", API.LOGTYPE.INFO)
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

                    API.logger.log("AdwareKiller", r"Checking for relative: HKLM\SOFTWARE\Classes\DHT", API.LOGTYPE.INFO)
                    flag = False
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\DHT\shell\open\command", 0, winreg.KEY_READ) as key:
                        value, value_type = winreg.QueryValueEx(key, "")
                        if 'Zona.exe" "%1"' in value:
                            API.logger.log("AdwareKiller", r"Relative is true!: HKLM\SOFTWARE\Classes\DHT",
                                           API.LOGTYPE.INFO)
                            flag = True
                    if flag:
                        API.logger.log("AdwareKiller", r"Removing HKLM\SOFTWARE\Classes\DHT",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\DHT")

                    API.logger.log("AdwareKiller", r"Checking for relative: HKCU: SOFTWARE\Classes\DHT\DefaultIcon",
                                   API.LOGTYPE.INFO)
                    flag = False
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\DHT\DefaultIcon", 0, winreg.KEY_READ) as key:
                        value, value_type = winreg.QueryValueEx(key, "")
                        if os.path.dirname(self.threats[file][1]["uninstall_path"])+"\\torrent.ico" in value:
                            API.logger.log("AdwareKiller", r"Relative is true!: HKCU\SOFTWARE\Classes\DHT",
                                           API.LOGTYPE.INFO)
                            flag = True
                    if flag:
                        API.logger.log("AdwareKiller", r"Removing: HKCU\SOFTWARE\Classes\DHT",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\DHT")

                    try:
                        if os.path.exists(API.paths.APPDATA_ROAMING+"\\Zona") and os.path.isdir(API.paths.APPDATA_ROAMING+"\\Zona"):
                            API.logger.log("AdwareKiller", r"Removing: $APPDATA_ROAMING/Zona",
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.APPDATA_ROAMING+"\\Zona")
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)

                    try:
                        if os.path.exists(os.path.dirname(self.threats[file][1]["uninstall_path"])) and os.path.isdir(os.path.dirname(self.threats[file][1]["uninstall_path"])):
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
                    while True:
                        found = False
                        for i in psutil.process_iter():
                            if i.name() == "mediaget-uninstaller.exe":
                                found = True
                        if not found:
                            break
                    # Deep Remove
                    API.logger.log("AdwareKiller", r"Removing HKCU\SOFTWARE\Classes\mediagetcatalogparams", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagetcatalogparams")
                    API.logger.log("AdwareKiller", r"Removing HKCU\SOFTWARE\Classes\mediagettorrentfile", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagettorrentfile")
                    API.logger.log("AdwareKiller", r"Removing HKCU\SOFTWARE\Classes\mediagetvideofile", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\mediagetvideofile")
                    API.logger.log("AdwareKiller", r"Removing HKCU\SOFTWARE\Media Get LLC", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Media Get LLC")
                    API.logger.log("AdwareKiller", r"Removing HKCU\SOFTWARE\MediaGet", API.LOGTYPE.INFO)
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\MediaGet")

                    API.logger.log("AdwareKiller", r"Checking for relative: HKLM\SOFTWARE\Classes\Magnet", API.LOGTYPE.INFO)
                    flag = False
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Magnet\DefaultIcon", 0, winreg.KEY_READ) as key:
                        value, value_type = winreg.QueryValueEx(key, "")
                        if 'mediaget.exe' in value:
                            API.logger.log("AdwareKiller", r"Relative is true!: HKLM\SOFTWARE\Classes\Magnet",
                                           API.LOGTYPE.INFO)
                            flag = True
                    if flag:
                        API.logger.log("AdwareKiller", r"Removing: HKLM\SOFTWARE\Classes\Magnet",
                                       API.LOGTYPE.INFO)
                        delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Magnet")


                    SourceType = API.autorun_utils.SourceType
                    get_autoruns = API.autorun_utils.get_autoruns

                    API.logger.log("AdwareKiller", r"Scanning autoruns...", API.LOGTYPE.INFO)
                    autoruns = get_autoruns([SourceType.HKLM_RUN])
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
                        if os.path.exists(API.paths.USERPROFILE+'\\mediaget2') and os.path.isdir(API.paths.USERPROFILE+'\\mediaget2'):
                            API.logger.log("AdwareKiller", r"Removing: "+API.paths.USERPROFILE+'\\mediaget2',
                                           API.LOGTYPE.INFO)
                            shutil.rmtree(API.paths.USERPROFILE+'\\mediaget2')
                    except:
                        API.logger.log("AdwareKiller", r"Error: "+traceback.format_exc(),
                                       API.LOGTYPE.ERROR)
            API.logger.log("AdwareKiller", f"Removed {file}", API.LOGTYPE.SUCCESS)