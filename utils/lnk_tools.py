import win32com.client
import pythoncom

def parse_lnk(path):
    shell = win32com.client.Dispatch("WScript.Shell",pythoncom.CoInitialize())
    target = self.shell.CreateShortCut(file).Targetpath.lower()
    return target