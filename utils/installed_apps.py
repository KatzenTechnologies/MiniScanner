import winreg

def get_installed_apps_with_paths():
    apps = []
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for path in registry_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    sub_key_name = winreg.EnumKey(reg_key, i)
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)
                    
                    name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                    uninstall_path = winreg.QueryValueEx(sub_key, "UninstallString")[0] if "UninstallString" in [winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "N/A"
                    install_path = winreg.QueryValueEx(sub_key, "InstallLocation")[0] if "InstallLocation" in [winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "N/A"

                    apps.append({
                        "name": name,
                        "install_path": install_path,
                        "uninstall_path": uninstall_path
                    })
                except (FileNotFoundError, OSError, PermissionError, WindowsError):
                    continue
        except Exception as e:
            pass
    for path in registry_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    sub_key_name = winreg.EnumKey(reg_key, i)
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)

                    name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                    uninstall_path = winreg.QueryValueEx(sub_key, "UninstallString")[0] if "UninstallString" in [
                        winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "N/A"
                    install_path = winreg.QueryValueEx(sub_key, "InstallLocation")[0] if "InstallLocation" in [
                        winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "N/A"

                    apps.append({
                        "name": name,
                        "install_path": install_path,
                        "uninstall_path": uninstall_path
                    })
                except (FileNotFoundError, OSError, PermissionError, WindowsError):
                    continue
        except Exception as e:
            pass
    return apps