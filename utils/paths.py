import platform
from os import getenv
from pathlib import Path

class PATHS:
    if platform.system() == "Windows":
        APPDATA_ROAMING = getenv("appdata")
        APPDATA_LOCAL = getenv("userprofile") + "\\AppData\\Local"
        APPDATA_LOCALLOW = getenv("userprofile") + "\\AppData\\LocalLow"
        USERPROFILE = getenv("userprofile")
        HOMEDRIVE = getenv("homedrive")
        DOCUMENTS = getenv("userprofile") + "\\Documents"
        DESKTOP = getenv("userprofile") + "\\Desktop"
        TEMP = getenv("temp")
        PROGRAMFILES = getenv("PROGRAMFILES")
        PROGRAMFILES86 = getenv("ProgramFiles(x86)")
        WINDIR = getenv('SystemRoot')
        PROGRAMDATA = getenv("ProgramData")

        # ICONS
        TASKBAR = getenv("appdata") + "\\Microsoft\\Internet Explorer\\Quick Launch\\User Pinned\\TaskBar"
        STARTMENU = [
            getenv("ProgramData") + "\\Microsoft\\Windows\\Start Menu\\Programs",
            getenv("appdata") + "\\Microsoft\\Windows\\Start Menu\\Programs",
        ]
    elif platform.system() == "Linux":
        HOME = getenv("HOME") or str(Path.home())
        USER = getenv("USER")
        TEMP = getenv("TMPDIR") or "/tmp"
        DESKTOP = f"{HOME}/Desktop"
        DOCUMENTS = f"{HOME}/Documents"
        DOWNLOADS = f"{HOME}/Downloads"
        CONFIG = f"{HOME}/.config"
        LOCAL_SHARE = f"{HOME}/.local/share"
        CACHE = f"{HOME}/.cache"
        BIN = f"{HOME}/.local/bin"
        ETC = "/etc"
        VAR = "/var"
        USR = "/usr"
        USR_BIN = "/usr/bin"
        USR_LOCAL_BIN = "/usr/local/bin"
        AUTOSTART = f"{CONFIG}/autostart"
        APPLICATIONS = [
            "/usr/share/applications",
            f"{LOCAL_SHARE}/applications",
        ]