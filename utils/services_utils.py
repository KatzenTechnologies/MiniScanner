import platform

if platform.system() == "Windows":
    import win32service
    import win32serviceutil
    import win32con

    class Service:
        def __init__(self, name, status=None):
            self.name = name
            self.status_cache = status

        def start(self):
            win32serviceutil.StartService(self.name)

        def stop(self):
            win32serviceutil.StopService(self.name)

        def restart(self):
            win32serviceutil.RestartService(self.name)

        def delete(self):
            win32serviceutil.RemoveService(self.name)

        def status(self):
            try:
                code = win32serviceutil.QueryServiceStatus(self.name)[1]
                return "running" if code == win32service.SERVICE_RUNNING else "stopped"
            except Exception:
                return "unknown"

    def get_services():
        hscm = win32service.OpenSCManager(None, None, win32con.GENERIC_READ)
        statuses = win32service.EnumServicesStatus(hscm)
        return [Service(name, "running" if status == win32service.SERVICE_RUNNING else "stopped")
                for name, _, status in statuses]

elif platform.system() == "Linux":
    from pydbus import SystemBus

    bus = SystemBus()
    systemd = bus.get(".systemd1")

    class Service:
        def __init__(self, name, status=None):
            self.name = name
            self.status_cache = status

        def start(self):
            systemd.StartUnit(self.name, "replace")

        def stop(self):
            systemd.StopUnit(self.name, "replace")

        def restart(self):
            systemd.RestartUnit(self.name, "replace")

        def delete(self):
            raise NotImplementedError()

        def status(self):
            try:
                unit = systemd.LoadUnit(self.name)
                return bus.get(".systemd1", unit).ActiveState
            except Exception:
                return "unknown"

    def get_services():
        units = systemd.ListUnits()
        return [Service(unit[0], unit[4]) for unit in units if unit[0].endswith(".service")]

else:
    raise NotImplementedError("Unsupported OS")
