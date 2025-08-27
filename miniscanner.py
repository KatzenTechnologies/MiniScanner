import utils.check_requirements as check_requirements

need = check_requirements.check_requirements(check_requirements.parse_requirements_file())

if need:
    import tkinter.messagebox as msg
    choice = msg.askyesno("MiniScanner", "Some requirements is not installed, do you want install them?\nНекоторые зависимости не установлены, желаете установить их?")
    if choice:
        check_requirements.install_requirements(need)
        msg.showinfo("MiniScanner","You need to restart Miniscanner to apply changes\nЧтобы применить изменения перезапустите Miniscanner")
    exit()

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
import ui.choose_language as choose_language
from utils.localization import Localization
import utils.configuration as config_tools
import ui.scantype as scantype
from datetime import datetime
import ui.license as license
import katzo.color as color
import katzo.tui as tui
import importlib
import platform
import logging
import json
import sys
import os

full_version = "3.1"
api_version  = "3.1.0"
base_version = "3.1.0"
revision = "beta3"

class LogType:
    INFO = [color.BLUE, "INFO"]
    WARN = [color.YELLOW, "WARN"]
    ERROR = [color.RED, "ERROR"]
    CRITICAL = [color.darker(color.RED, -50), "CRITICAL"]
    SUCCESS = [color.GREEN, "SUCCESS"]

print("Tyyrve! Te prougram tehdenoe bue Ingebeplandae Litte fyy Kehidajajes da KatzenTech.")
print(f"MiniScanner v{full_version} ({revision})")
if not os.path.exists("./logs") or os.path.isfile("./logs"):
    os.mkdir("./logs")

if not os.path.exists("./config") or os.path.isfile("./config"):
    os.mkdir("./config")

class Logger:
    def __init__(self):
        now = datetime.now()
        logging.basicConfig(filename=f'./logs/log-{now.strftime("%Y-%m-%d-%H-%M-%S")}.txt',
                    level=logging.INFO,
                    format='%(message)s')
    def log(self, name, message, log_type):
        print(tui.colorize_onecolor(f"[{name}/{log_type[1]}] {message}", log_type[0]))
        logging.info(f"[{name}/{log_type[1]}] {message}")

myconfig = config_tools.Configuration("./config/MiniScanner.json")

globals()["logger"] = Logger()

logger.log("MiniScanner", f"Running v{base_version} API:{api_version} Base:{base_version} Rev:{revision}", LogType.INFO)

if myconfig.data == None:
    myconfig.data = {"agreed_with_disclaimer": False, "last_language": "", "skip_lang": False, "scan_plugins": True}

if myconfig["skip_lang"]:
    chosen_language = Localization(json.load(open(f"./translations/{myconfig["last_language"]}", "r", encoding='utf-8', errors='replace')))
else:
    localizations_map = {}
    localization_data_for_ui = []

    for i in os.listdir("./translations"):
        obj = Localization(json.load(open(f"./translations/{i}", "r", encoding='utf-8', errors='replace')))
        localizations_map.update({i: obj})
        localization_data_for_ui.append([i, obj.language_name])

    language, skip = choose_language.select_language(localization_data_for_ui, default_key=myconfig["last_language"])

    myconfig["last_language"] = language
    myconfig["skip_lang"] = skip

    myconfig.save()

    chosen_language = localizations_map[language]



if not myconfig["agreed_with_disclaimer"]:
    agreed = license.show_agreement_dialog(chosen_language)
    if not agreed:
        logger.log("MiniScanner", chosen_language.translate("disclaimer_not_accepted"), LogType.CRITICAL)
        exit()
    myconfig["agreed_with_disclaimer"] = agreed
    myconfig.save()



def loader(path, paths):
    sys.path.insert(0, path)
    modules = []

    for filename in paths:
        if filename.endswith('.py'):
            module_name = filename[:-3]
            file_path = os.path.join(path, filename)

            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'Main'):
                    modules.append(module)
                else:
                    logger.log("MiniScanner", chosen_language.translate("plugin_class_main_not_found", plugin_name=filename), LogType.ERROR)
            except Exception as e:
                logger.log("MiniScanner", chosen_language.translate("plugin_loading_error", plugin_name=filename, error=e), LogType.ERROR)

    return modules
# GUI
from ui.plugins_select import PluginSelectorDialog
from ui.load import *
from ui.threats_table import *

#
import utils.check_plugin as check_plugin
def get_plugins(app):
    dlg = PluginSelectorDialog(chosen_language)
    
    logger.log("MiniScanner", chosen_language.translate("start_searching_of_plugins"), LogType.INFO)
    for i in os.listdir("./plugins"):
        if os.path.isdir("./plugins/" + i): continue
        if i.split(".")[-1] == "py":
            suspicious = check_plugin.is_obfuscated(open("./plugins/" + i, "r").read()) if myconfig["scan_plugins"] else False

            logger.log("MiniScanner", chosen_language.translate("found_plugin_starting_check", plugin_name=i), LogType.INFO)
            dlg.add_plugin(i, suspicious=suspicious)
        elif i.split(".")[-1] == ".pyc":
            logger.log("MiniScanner", chosen_language.translate("pyc_skip", plugin_name=i), LogType.WARN)
        else:
            logger.log("MiniScanner", chosen_language.translate("found_not_python_plugin", plugin_name=i), LogType.WARN)
        
            

    if dlg.exec() == QDialog.Accepted:
        return dlg.get_result()
    return []
    
app = QApplication.instance() or QApplication(sys.argv)

modules = loader("./plugins", get_plugins(app))

# API Toolkit
import utils.lnk_tools as lnk_tools
import utils.paths as paths
import utils.indexer as indexer
import utils.hosts_utils as hosts_utils
import utils.process_utils as process_utils
import utils.quarantine as quarantine

if platform.system() == "Windows":
    import utils.firewall_tools as firewall_tools
    import utils.schedule_tools as schedule_tools
    import utils.services_utils as services_toolkit
    import utils.installed_apps as installed_apps
    import utils.autorun_utils as autorun_utils

class API:
    api_version  = api_version
    base_version = base_version
    full_version = full_version
    revision     = revision

    LOGTYPE = LogType()
    APIs = {}
    logger = logger
    ConfigType = config_tools.ConfigurationTypes
    chosen_language = chosen_language # Нужно потому что в уи передается апи
    loaded = []
    _preruns = []
    _pl_configs = {}
    _custom_tabs = []

    # Libraries

    requirements = check_requirements.RequirementTool()
    lnk_tools = lnk_tools
    paths = paths.PATHS()
    indexer = indexer
    hosts_utils = hosts_utils
    process_utils = process_utils
    if platform.system() == "Windows":
        autorun_utils = autorun_utils
        firewall_tools = firewall_tools
        schedule_tools = schedule_tools
        services_toolkit = services_toolkit
        installed_apps = installed_apps
    quarantine = quarantine.QuarantineSystem()

    def register_config(self, config, localization, hidden_variables, name):
        self._pl_configs.update({name if isinstance(name, str) else name.name: [config, localization, hidden_variables]})

    def add_custom_tab(self, tab, name):
        self._custom_tabs.append([tab, name])

    def is_loaded(self, name):
        return name in self.loaded

    def get_config_object(self, name_of_file, type_of_config=ConfigType.JSON, folder="config"):
        return config_tools.Configuration(f"./{folder}/{name_of_file}", type_of_config=type_of_config)

    def get_localization_object(self, data):
        return Localization(data)

    def get_indexer_generator(self):
        return indexer.FileIndexer(include_dirs=self.scancore.include_dirs,
                                   include_files=self.scancore.include_files,
                                   exclude_dirs=self.scancore.exclude_dirs,
                                   exclude_files=self.scancore.exclude_files,
                                   )

    # CAPIs System
    def get_api(self, name):
        return self.APIs.get(name)
    
    def register_api(self, name, object):
        if self.APIs.get(name) is None:
            self.APIs.update({name: object})
        else:
            logger.log("API System", chosen_language.translate("custom_api_already_registrated"), LogType.WARN)

    # For hooks, patching, etc...
    def register_prerun(self, function):
        self._preruns.append(function)

    def prerun(self):
        for i in self._preruns:
            i()

if modules == []:
    logger.log("MiniScanner", chosen_language.translate("havent_get_any_plugins"), LogType.CRITICAL)
    exit()

def get_excludes():
    config_path = os.path.join("config", "indexer_excludes.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    data = config_tools.Configuration(config_path, api.ConfigType.JSON)
    if data.data is None:
        data.data = {"paths": []}
    elif "paths" not in data.data:
        data.data["paths"] = []
    return data

api = API()

dlg = PluginLoaderDialog(modules, api)
if dlg.exec() == QDialog.Accepted:
    loaded_plugins = dlg.get_result()

if loaded_plugins == []:
    logger.log("MiniScanner", chosen_language.translate("havent_loaded_any_plugins"), LogType.CRITICAL)
    exit()

reqs_flag = False
if not api.requirements.not_installed():
    reply = QMessageBox.question(
        None, "MiniScanner", chosen_language.translate("requirements_not_satisfied"),
        QMessageBox.Yes | QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        # more code for security reasons
        api.requirements.enabled = True
        api.requirements.install()
        delattr(api.requirements, "enabled")
        delattr(api.requirements, "install")
    else:
        logger.log("MiniScanner", chosen_language.translate("requirements_removing_plugins"), LogType.INFO)

        reqs_flag = True
        # remove plugins, which have missing reqs
        for i in api.requirements.missing.keys():
            loaded_plugins.remove(i)

if loaded_plugins == [] and reqs_flag:
    logger.log("MiniScanner", chosen_language.translate("requirements_plugins_not_loaded"), LogType.CRITICAL)
    exit()

api.register_config(myconfig, chosen_language, ["agreed_with_disclaimer", "last_language"], "MiniScanner")

scannertype = scantype.ScannerGUI(api, get_excludes)
scannertype.show()
app.exec()

if scannertype.scan_type == None:
    logger.log("MiniScanner", chosen_language.translate("type_not_chosen"), LogType.CRITICAL)
    exit()

memoryscanner = process_utils.MemoryScanner()

if scannertype.scan_tab.scan_memory_checkbox.checkState() == Qt.Checked:
    memoryscanner.enabled = True

api.memoryscanner = memoryscanner

class ScanCore:
    version = "1.0.0"
    def __init__(self):
        self.exclude_files = []
        self.exclude_paths = []
        self.include_paths = []
        self.include_files = []
        self.scan_type = None

scancore_obj = ScanCore()
scancore_obj.scan_type = scannertype.scan_type
if scannertype.scan_type != "custom":
    scancore_db = json.load(open("./db/scancore.json", 'r'))
    scancore_db = scancore_db[platform.system()]
    scancore_obj.exclude_files = scancore_db[scannertype.scan_type]["exclude_files"]
    for i, j in enumerate(scancore_obj.exclude_files):
        scancore_obj.exclude_files[i] = indexer.replace_env_vars(j)
    scancore_obj.include_dirs = scancore_db[scannertype.scan_type]["include_dirs"]
    for i, j in enumerate(scancore_obj.include_dirs):
        scancore_obj.include_dirs[i] = indexer.replace_env_vars(j)
    scancore_obj.include_files = scancore_db[scannertype.scan_type]["include_files"]
    for i, j in enumerate(scancore_obj.include_files):
        scancore_obj.include_files[i] = indexer.replace_env_vars(j)
    scancore_obj.exclude_dirs = scancore_db[scannertype.scan_type]["exclude_dirs"]
    for i, j in enumerate(scancore_obj.exclude_dirs):
        scancore_obj.exclude_dirs[i] = indexer.replace_env_vars(j)
    dirs_e = []
    files_e = []
    for i in scannertype.scan_tab.exclusions_config.data["paths"]:
        if os.path.exists(i):
            if os.path.isfile(i):
                files_e.append(i)
            else:
                dirs_e.append(i)
    scancore_obj.exclude_files += files_e
    scancore_obj.exclude_dirs += dirs_e
else:
    dirs = []
    files = []
    for i in scannertype.scan_paths:
        if os.path.exists(i):
            if os.path.isfile(i):
                files.append(i)
            else:
                dirs.append(i)
    dirs_e = []
    files_e = []
    for i in scannertype.scan_tab.exclusions_config.data["paths"]:
        if os.path.exists(i):
            if os.path.isfile(i):
                files_e.append(i)
            else:
                dirs_e.append(i)

    scancore_obj.exclude_files = files_e
    scancore_obj.include_dirs = dirs
    scancore_obj.include_files = files
    scancore_obj.exclude_dirs = dirs_e
api.scancore = scancore_obj

threat_gui = VirusScanWindow(loaded_plugins, api)
# api.add_threat = threat_gui.add_threat



threat_gui.exec()