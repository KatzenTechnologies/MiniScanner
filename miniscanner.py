from PySide6.QtWidgets import QApplication, QDialog
import ui.choose_language as choose_language
from utils.localization import Localization
import utils.configuration as config_tools
from datetime import datetime
import ui.license as license
import katzo.color as color
import katzo.tui as tui
import importlib
import logging
import json
import sys
import os

class LogType:
    INFO = [color.BLUE, "INFO"]
    WARN = [color.YELLOW, "WARN"]
    ERROR = [color.RED, "ERROR"]
    CRITICAL = [color.darker(color.RED, -50), "CRITICAL"]
    SUCCESS = [color.GREEN, "SUCCESS"]
    
print("Tyyrve! Te prougram tehdenoe bue Ingebeplandae Litte fyy Kehidajajes da KatzenTech.")
print("MiniScanner v1.0")

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

if myconfig.data == None:
    myconfig.data = {"agreed_with_disclaimer": False, "last_language": "", "skip_lang": False}

if myconfig["skip_lang"]:
    chosen_language = Localization(json.load(open(f"./translations/{myconfig["last_language"]}", "r")))
else:
    localizations_map = {}
    localization_data_for_ui = []

    for i in os.listdir("./translations"):
        obj = Localization(json.load(open(f"./translations/{i}", "r")))
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
def get_plugins(app):
    dlg = PluginSelectorDialog(chosen_language)
    
    logger.log("MiniScanner", chosen_language.translate("start_searching_of_plugins"), LogType.INFO)
    for i in os.listdir("./plugins"):
        if os.path.isdir("./plugins/" + i): continue
        if i.split(".")[-1] == "py":
            suspicious = False
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
import utils.installed_apps as installed_apps
import utils.lnk_tools as lnk_tools
import utils.paths as paths
import utils.autorun_utils as autorun_utils

class API:
    version = "1.0"
    LOGTYPE = LogType()
    APIs = {}
    logger = logger
    ConfigType = config_tools.ConfigurationTypes
    chosen_language = chosen_language # Нужно потому что в уи передается апи

    # Libraries
    installed_apps = installed_apps
    lnk_tools = lnk_tools
    paths = paths
    autorun_utils = autorun_utils

    def get_config_object(self, plugin_object, name_of_file, type_of_config=ConfigType.JSON):
        if not os.path.exists(f"./config/{plugin_object.name}") or os.path.isfile(f"./config/{plugin_object.name}"):
            os.mkdir(f"./config/{plugin_object.name}")

        return config_tools.Configuration(f"./config/{plugin_object.name}/{name_of_file}", type_of_config=type_of_config)

    # CAPIs System
    def get_api(self, name):
        return self.APIs.get(name)
    
    def register_api(self, name, object):
        if self.APIs.get(name) is None:
            self.APIs.update({name: object})
        else:
            logger.log("API System", chosen_language.translate("custom_api_already_registrated"), LogType.WARN)

if modules == []:
    logger.log("MiniScanner", chosen_language.translate("havent_get_any_plugins"), LogType.CRITICAL)
    exit()

api = API()

dlg = PluginLoaderDialog(modules, api)
if dlg.exec() == QDialog.Accepted:
    loaded_plugins = dlg.get_result()

if loaded_plugins == []:
    logger.log("MiniScanner", chosen_language.translate("havent_loaded_any_plugins"), LogType.CRITICAL)
    exit()

threat_gui = VirusScanWindow(loaded_plugins, api)
api.add_threat = threat_gui.add_threat


threat_gui.exec()