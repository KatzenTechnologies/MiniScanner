from PySide6.QtWidgets import QApplication, QDialog
from datetime import datetime
import katzo.color as color
import katzo.tui as tui
import importlib
import colorama
import logging
import shutil
import winreg
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

class Logger:
    def __init__(self):
        now = datetime.now()
        logging.basicConfig(filename=f'./logs/log-{now.strftime("%Y-%m-%d-%H-%M-%S")}.txt',
                    level=logging.INFO,
                    format='%(message)s')
    def log(self, name, message, log_type):
        print(tui.colorize_onecolor(f"[{name}/{log_type[1]}] {message}", log_type[0]))
        logging.info(f"[{name}/{log_type[1]}] {message}")

globals()["logger"] = Logger()

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
                    logger.log("MiniScanner", f"В плагине {filename} отсутствует класс Main!", LogType.ERROR)
            except Exception as e:
                logger.log("MiniScanner", f"Не удалось импортировать {filename}! Ошибка: {e}", LogType.ERROR)
                
    return modules
# GUI
from ui.plugins_select import PluginSelectorDialog
from ui.load import *
from ui.threats_table import *
def get_plugins(app):
    dlg = PluginSelectorDialog()
    
    logger.log("MiniScanner", "Начинаю поиск плагинов", LogType.INFO)
    for i in os.listdir("./plugins"):
        if i.split(".")[-1] == "py":
            suspicious = False
            logger.log("MiniScanner", f"Найден плагин {i}, запускаю проверку...", LogType.INFO)
            dlg.add_plugin(i, suspicious=suspicious)
        elif i.split(".")[-1] == ".pyc":
            logger.log("MiniScanner", f"Найден плагин {i}, плагины с расширением .pyc не поддерживаются ввиду невозможности их проверки, пропускаю!", LogType.WARN)
        else:
            logger.log("MiniScanner", f"Найден файл {i}, не Python-файл, пропускаю!", LogType.WARN)
        
            

    if dlg.exec() == QDialog.Accepted:
        return dlg.get_result()
    return []
    
app = QApplication.instance() or QApplication(sys.argv)

modules = loader("./plugins", get_plugins(app))

# API Toolkit
import utils.installed_apps as installed_apps
import utils.lnk_tools as lnk_tools


class API:
    version = "1.0"
    LOGTYPE = LogType()
    APIs = {}
    logger = logger

    # Libraries
    installed_apps = installed_apps
    lnk_tools = lnk_tools

    # CAPIs System
    def get_api(self, name):
        return self.APIs.get(name)
    
    def register_api(self, name, object):
        if self.APIs.get(name) is None:
            self.APIs.update({name: object})
        else:
            logger.log("API System", "Имя кастомного API уже зарегистрировано, перезапись не разрешается", LogType.WARN)

api = API()

dlg = PluginLoaderDialog(modules, api)
if dlg.exec() == QDialog.Accepted:
    loaded_plugins = dlg.get_result()

threat_gui = VirusScanWindow(loaded_plugins, api)
api.add_threat = threat_gui.add_threat


threat_gui.exec()