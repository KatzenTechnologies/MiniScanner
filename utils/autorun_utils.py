import os
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum, auto

class SourceType(Enum):
    HKCU_RUN = auto()
    HKLM_RUN = auto()
    HKCU_RUNONCE = auto()
    HKLM_RUNONCE = auto()
    HKCU_SHELL = auto()
    HKLM_SHELL = auto()
    STARTUP_FOLDER = auto()

@dataclass
class AutorunEntry:
    source: SourceType
    platform: str
    location: str
    name: str
    command: str

    def delete(self):
        try:
            if self.platform == "Windows":
                import winreg

                if self.source in {
                    SourceType.HKCU_RUN,
                    SourceType.HKLM_RUN,
                    SourceType.HKCU_RUNONCE,
                    SourceType.HKLM_RUNONCE,
                    SourceType.HKCU_SHELL,
                    SourceType.HKLM_SHELL,
                }:
                    hive = winreg.HKEY_CURRENT_USER if "HKCU" in self.location else winreg.HKEY_LOCAL_MACHINE
                    subkey = self.location.split("\\", 1)[1]
                    with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, self.name)
                        return True

                elif self.source == SourceType.STARTUP_FOLDER:
                    os.remove(os.path.join(self.location, self.name))
                    return True

        except Exception:
            return False

        return False

def get_autoruns(sources: list[SourceType]) -> list[AutorunEntry]:
    entries = []
    system = platform.system()

    if system == "Windows":
        import winreg
        registry_paths = {
            SourceType.HKCU_RUN: ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", winreg.HKEY_CURRENT_USER),
            SourceType.HKLM_RUN: ("HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", winreg.HKEY_LOCAL_MACHINE),
            SourceType.HKCU_RUNONCE: ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce", winreg.HKEY_CURRENT_USER),
            SourceType.HKLM_RUNONCE: ("HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce", winreg.HKEY_LOCAL_MACHINE),
            SourceType.HKCU_SHELL: ("HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", winreg.HKEY_CURRENT_USER),
            SourceType.HKLM_SHELL: ("HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", winreg.HKEY_LOCAL_MACHINE),
        }

        for source in sources:
            if source in registry_paths:
                path, hive = registry_paths[source]
                subkey = path.split("\\", 1)[1]
                try:
                    with winreg.OpenKey(hive, subkey) as key:
                        i = 0
                        while True:
                            try:
                                value_name, value_data, _ = winreg.EnumValue(key, i)
                                if source.name.endswith("SHELL") and value_name.lower() != "shell":
                                    i += 1
                                    continue
                                entries.append(AutorunEntry(source, "Windows", path, value_name, value_data))
                                i += 1
                            except OSError:
                                break
                except FileNotFoundError:
                    continue

            elif source == SourceType.STARTUP_FOLDER:
                paths = [
                    os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),
                    os.path.expandvars(r"%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),
                ]
                for folder in paths:
                    if os.path.isdir(folder):
                        for f in os.listdir(folder):
                            full = os.path.join(folder, f)
                            entries.append(AutorunEntry(source, "Windows", folder, f, full))

    return entries
