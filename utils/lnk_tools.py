import win32com.client
import pythoncom

def parse_lnk(path):
    shell = win32com.client.Dispatch("WScript.Shell",pythoncom.CoInitialize())
    target = shell.CreateShortCut(path).Targetpath.lower()
    return target