from os import getenv

class PATHS:
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