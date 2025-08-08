import os
import shutil
import traceback
import winreg
import tkinter.messagebox as msg
import time
import psutil
from pathlib import Path
import subprocess
import os
import re

def run_uninstaller(uninstall_path: str):
    uninstall_path = uninstall_path.strip()

    match = re.match(r'^(.*?\.exe)\s*(.*)$', uninstall_path, re.IGNORECASE)
    if not match:
        return

    exe_path = match.group(1)
    args_str = match.group(2)

    args = args_str.split() if args_str else []

    try:
        os.system(f'{exe_path if exe_path.startswith('"') and exe_path.endswith('"') else '"' + exe_path + '"'} {" ".join(args)}')
    except subprocess.CalledProcessError as e:
        pass

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

def remove(file):
    try:
        if dir_exists(file):
            API.logger.log("AdwareKiller", f"Removing: {file}",
                           API.LOGTYPE.INFO)
            shutil.rmtree(file)
        elif file_exists(file):
            API.logger.log("AdwareKiller", f"Removing: {file}",
                           API.LOGTYPE.INFO)
            os.remove(file)

    except:
        API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                       API.LOGTYPE.ERROR)

def get_services(name):
    data = []
    for i in API.services_toolkit.get_services():
        if name in i.name:
            data.append(i)
    return data

def kill_luminati():
    my_try = API.process_utils.find_process_paths_by_name("net_updater32.exe")

    luminati_path = os.path.dirname(my_try[0]) if len(my_try) == 1 else "C:/a/plug.txt"
    API.process_utils.kill_processes_by_name("brightdata.exe")
    API.process_utils.kill_processes_by_name("net_updater32.exe")
    API.process_utils.kill_processes_by_name("luminati-m-controller.exe")
    if list(Path(luminati_path).parts)[-1] == "Luminati-m":
        remove(luminati_path)
    remove(API.paths.PROGRAMDATA + "\\BrightData")
    for i in get_services("luminati_net_updater_"):
        API.logger.log("AdwareKiller", f"Killing service: {i.name}", API.LOGTYPE.INFO)
        i.delete()

def kill_proxysdk():
    API.process_utils.kill_processes_by_name("proxy-sdk_crashpad_handler.exe")
    API.process_utils.kill_processes_by_name("proxy-sdk.exe")
    SourceType = API.autorun_utils.SourceType
    get_autoruns = API.autorun_utils.get_autoruns

    API.logger.log("AdwareKiller", r"Scanning autoruns...", API.LOGTYPE.INFO)
    autoruns = get_autoruns([SourceType.HKLM_RUN, SourceType.HKCU_RUN])
    for i in autoruns:
        if "proxy-sdk.exe" in i.command:
            API.logger.log("AdwareKiller", r"Found ProxySDK, removing...", API.LOGTYPE.INFO)
            try:
                i.delete()
            except:
                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                               API.LOGTYPE.ERROR)
    remove(API.paths.APPDATA_LOCAL + '\\proxy-sdk')




class Main:
    name = "AdwareKiller"
    author = "Northkatz"
    version = '4.1'

    def __init__(self, API):
        globals()["API"] = API
        self.base = [
            ["Download Studio", "PUP.DStudio"],
            ["Zona", "Adware.Zona"],
            ["MediaGet", "Adware.Mediaget"],
            ["Telamon Cleaner", "PUP.Telamon"],
            ["KLauncher","PUP.KLauncher"],
            ["PixelSee", "Adware.Pixelsee"],
            ["uFiler", "PUP.uBar.A"],
            ["UDL Client", "Adware.Udelka"],
            ["AppWizard", "Adware.Multibundler.A"]
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

        if not "PUP.DStudio" in self.threats_families and download_studio_flag:
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
                             check_autoruns(['mediaget.exe'])])

        if not "Adware.Mediaget" in self.threats_families and mediaget_flag:
            API.add_threat("Mediaget (remnants)", "Adware.Mediaget", self)
            self.threats.update({"Mediaget (remnants)": ["Adware.Mediaget", {"uninstall_path":""}]})

        if not "PUP.Telamon" in self.threats_families and dir_exists(API.paths.APPDATA_LOCAL+'\\TelamonCleaner'):
            API.add_threat("Telamon Cleaner (remnants)", "PUP.Telamon", self)
            self.threats.update({"Telamon Cleaner (remnants)": ["PUP.Telamon", {"uninstall_path":""}]})

        klauncher_flag = any([
            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"Software\KLauncher"),
            dir_exists(API.paths.APPDATA_ROAMING + '\\.minecraft\\gameicons'),
            file_exists(API.paths.APPDATA_ROAMING + '\\.minecraft\\tbp.exe'),
            dir_exists(API.paths.APPDATA_ROAMING + '\\.minecraft\\logs\\klauncher')

        ])

        if not "PUP.KLauncher" in self.threats_families and klauncher_flag:
            API.add_threat("KLauncher (remnants)", "PUP.KLauncher", self)
            self.threats.update({"KLauncher (remnants)": ["PUP.KLauncher", {"uninstall_path":""}]})

        pixelsee_flag = any([
            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\PixelSee"),
            check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\PixelSee LLC"),
            dir_exists(API.paths.APPDATA_LOCAL + "\\PixelSee LLC")
        ])

        if not "Adware.Pixelsee" in self.threats_families and pixelsee_flag:
            API.add_threat("PixelSee (remnants)", "Adware.Pixelsee", self)
            self.threats.update({"PixelSee (remnants)": ["Adware.Pixelsee", {"uninstall_path":""}]})


        luminati_flag = any([
            API.process_utils.get_pids_by_name("net_updater32.exe") != [],
            API.process_utils.get_pids_by_name("brightdata.exe") != [],
            dir_exists(API.paths.PROGRAMDATA+"\\BrightData"),
            get_services("luminati_net_updater_") != []

        ])
        if not "Adware.Pixelsee" in self.threats_families and \
            not "Proxy.Luminati" in self.threats_families\
            and luminati_flag:
            API.add_threat("Luminati", "Proxy.Luminati", self)
            self.threats.update({"Luminati": ["Proxy.Luminati", {"uninstall_path":""}]})

        proxysdk_flag = any([
            API.process_utils.get_pids_by_name("proxy-sdk.exe") != [],
            dir_exists(API.paths.APPDATA_LOCAL + '\\proxy-sdk'),
            check_autoruns(["proxy-sdk.exe"])

        ])
        if not "Adware.Mediaget" in self.threats_families and \
            not "Proxy.ProxySDK" in self.threats_families\
            and proxysdk_flag:
            API.add_threat("ProxySDK", "Proxy.ProxySDK", self)
            self.threats.update({"ProxySDK": ["Proxy.ProxySDK", {"uninstall_path":""}]})

        #PUP.uBar.A
        ufiler_flag = any([
            check_firewall(["uFiler"]),
            check_autoruns(["uFiler.exe"]),
            check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\.ufile"),
            check_registry_key_exists(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\uFiler"),
            dir_exists(API.paths.PROGRAMDATA+'\\uFiler'),
            dir_exists(API.paths.PROGRAMFILES86 + '\\uFiler'),
        ])
        if not "PUP.uBar.A" in self.threats_families and ufiler_flag:
            API.add_threat("uFiler (remnants)", "PUP.uBar.A", self)
            self.threats.update({"uFiler (remnants)": ["PUP.uBar.A", {"uninstall_path":""}]})

        #Adware.Multibundler.A
        appwizard_flag = check_registry_key_exists(winreg.HKEY_CURRENT_USER, r"SOFTWARE\AppWizard")

        if not "Adware.Multibundler.A" in self.threats_families and appwizard_flag:
            API.add_threat("AppWizard (remnants)", "Adware.Multibundler.A", self)
            self.threats.update({"AppWizard (remnants)": ["Adware.Multibundler.A", {"uninstall_path":""}]})
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
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
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

                    remove(API.paths.APPDATA_LOCAL+"\\Download Studio")

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
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
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

                    remove(API.paths.APPDATA_ROAMING+"\\Zona")
                    remove(API.paths.WINDIR+"\\ZonaUpdater.log")
                    remove(os.path.dirname(self.threats[file][1]["uninstall_path"]))
                case "Adware.Mediaget":
                    API.process_utils.kill_processes_by_name("mediaget.exe")
                    API.process_utils.kill_processes_by_name("proxy-sdk.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
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

                    remove(API.paths.USERPROFILE+'\\mediaget2')
                    remove(API.paths.APPDATA_LOCAL+'\\Media Get LLC')
                case "PUP.Telamon":
                    API.process_utils.kill_processes_by_name("TelamonCleaner.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["TelamonCleaner.exe"])
                    # Deep Remove
                    remove(os.path.dirname(self.threats[file][1]["uninstall_path"]))
                    remove(API.paths.APPDATA_LOCAL+"\\TelamonCleaner")
                case "PUP.KLauncher":
                    API.process_utils.kill_processes_by_name("javaw.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["uninstall.exe"])
                    # Deep Remove
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"Software\KLauncher")
                    remove(API.paths.APPDATA_ROAMING + '\\.minecraft\\gameicons')
                    remove(API.paths.APPDATA_ROAMING + '\\.minecraft\\tbp.exe')
                    remove(API.paths.APPDATA_ROAMING + '\\.minecraft\\logs\\klauncher')
                case "Adware.Pixelsee":
                    API.process_utils.kill_processes_by_name("pixelsee_crashpad_handler.exe")
                    API.process_utils.kill_processes_by_name("pixelsee.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["pixelsee-uninstaller.exe"])
                    # Deep Remove
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\PixelSee")
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\PixelSee LLC")
                    remove(API.paths.APPDATA_LOCAL+"\\PixelSee LLC")
                case "Proxy.Luminati":
                    kill_luminati()
                case "Proxy.ProxySDK":
                    kill_proxysdk()
                case "PUP.uBar.A":
                    API.process_utils.kill_processes_by_name("uFiler.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["uFiler.exe", "UFilerUninstaller.exe"])
                    # Deep Remove
                    SourceType = API.autorun_utils.SourceType
                    get_autoruns = API.autorun_utils.get_autoruns

                    API.logger.log("AdwareKiller", r"Scanning autoruns...", API.LOGTYPE.INFO)
                    autoruns = get_autoruns([SourceType.HKLM_RUN, SourceType.HKCU_RUN])
                    for i in autoruns:
                        if 'uFiler.exe' in i.command:
                            API.logger.log("AdwareKiller", r"Found UFiler, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\.ufile")
                    delete_registry_tree(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\uFiler")

                    API.logger.log("AdwareKiller", r"Scanning firewall rules...", API.LOGTYPE.INFO)
                    firewall_rules = API.firewall_tools.get_firewall_rules()
                    for i in firewall_rules:
                        if "uFiler" in i.name:
                            API.logger.log("AdwareKiller", r"Found UFiler's rule, removing...", API.LOGTYPE.INFO)
                            try:
                                i.delete()
                            except:
                                API.logger.log("AdwareKiller", r"Error: " + traceback.format_exc(),
                                               API.LOGTYPE.ERROR)
                    remove(API.paths.PROGRAMDATA+'\\uFiler')
                    # if exists cuz ufiler sometimes dont add itself to installed apps
                    remove(API.paths.PROGRAMFILES86 + '\\uFiler')
                    remove(os.path.dirname(self.threats[file][1]["uninstall_path"]))
                case "Adware.Udelka":
                    API.process_utils.kill_processes_by_name("ClientLauncher.exe")
                    API.process_utils.kill_processes_by_name("udl-client.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["unins000.exe"])
                case "Adware.Multibundler.A":
                    API.process_utils.kill_processes_by_name("AppWizard.exe")
                    run_uninstaller(self.threats[file][1]["uninstall_path"])
                    wait_for_exit(["unins000.exe"])
                    # Deep Remove
                    delete_registry_tree(winreg.HKEY_CURRENT_USER, r"SOFTWARE\AppWizard")


            API.logger.log("AdwareKiller", f"Removed {file}", API.LOGTYPE.SUCCESS)