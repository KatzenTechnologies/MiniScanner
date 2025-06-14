import os

class PATHS:
    APPDATA_ROAMING = os.getenv("appdata")
    APPDATA_LOCAL = os.getenv("userprofile") + "\\AppData\\Local"
    APPDATA_LOCALLOW = os.getenv("userprofile") + "\\AppData\\LocalLow"
    USERPROFILE = os.getenv("userprofile")
    HOMEDRIVE = os.getenv("homedrive")
    DOCUMENTS = os.getenv("userprofile") + "\\Documents"
    DESKTOP = os.getenv("userprofile") + "\\Desktop"
    TEMP = os.getenv("temp")
    PROGRAMFILES = os.getenv("PROGRAMFILES")
    PROGRAMFILES86 = os.getenv("ProgramFiles(x86)")
    WINDIR = os.getenv('SystemRoot')
    PROGRAMDATA = os.getenv("ProgramData")