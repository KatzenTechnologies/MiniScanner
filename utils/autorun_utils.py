import winreg
import platform

class AutorunObject:
    def __init__(self, registry_path, bad, file_path, key_type=None):
        self.reg_path = registry_path
        self.name = bad
        self.key_type = key_type
        self.file_path = file_path
    def cure(self):
        # Пока полностью не протестирована...
        raise NotImplemented
        try:
            key = winreg.OpenKey(self.key_type, self.reg_path, 0, winreg.KEY_ALL_ACCESS)

            winreg.DeleteValue(key, self.name)
            winreg.CloseKey(key)
        except FileNotFoundError:
            return float("inf")
        except OSError as e:
            return float("nan")

    def __str__(self):
        return "Key: "+self.reg_path

def get_autorun():

    autorun_programs = []
    try:
        is_64bit = platform.machine().endswith('64')
        keys = [winreg.HKEY_CURRENT_USER]
        if is_64bit:
            keys.append(winreg.HKEY_LOCAL_MACHINE)

        for key_type in keys:
            try:
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                # Большинство вирусов сидят в w32 ветке, чуть позже добавлю считывание сразу нескольких веток
                # if key_type == winreg.HKEY_LOCAL_MACHINE and is_64bit:
                #     key_path = r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run"

                key = winreg.OpenKey(key_type, key_path)
                i = 0
                while True:
                    try:
                        name, value, type = winreg.EnumValue(key, i)
                        coolobj = AutorunObject(key_path, name, value, key_type = key_type)
                        autorun_programs.append(coolobj)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except OSError as e:
                pass

    except Exception as e:
        pass

    return autorun_programs