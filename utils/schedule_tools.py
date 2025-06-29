import win32com.client
from typing import List


class ScheduledTask:
    def __init__(self, name: str, path: str, status: str, user: str, com_task=None):
        self.name = name
        self.path = path
        self.status = status
        self.user = user
        self._com_task = com_task

    def delete(self) -> bool:
        try:
            service = win32com.client.Dispatch("Schedule.Service")
            service.Connect()
            folder_path = "\\".join(self.path.strip("\\").split("\\")[:-1])
            folder = service.GetFolder(f"\\" + folder_path if folder_path else "\\")
            folder.DeleteTask(self.name, 0)
            return True
        except Exception:
            return False


class TaskSchedulerAnalyzer:
    def __init__(self):
        self.tasks: List[ScheduledTask] = []

    def analyze(self):
        self.tasks.clear()
        service = win32com.client.Dispatch("Schedule.Service")
        service.Connect()
        self._scan_folder(service.GetFolder("\\"))

    def _scan_folder(self, folder):
        for task in folder.GetTasks(0):
            name = task.Name
            path = folder.Path + "\\" + name if folder.Path != "\\" else "\\" + name
            status = self._status_to_string(task.State)
            user = task.Definition.Principal.UserId or "SYSTEM"
            self.tasks.append(ScheduledTask(name, path, status, user, task))
        for subfolder in folder.GetFolders(0):
            self._scan_folder(subfolder)

    def _status_to_string(self, state: int) -> str:
        return {
            0: "Unknown",
            1: "Disabled",
            2: "Queued",
            3: "Ready",
            4: "Running"
        }.get(state, "Unknown")

    def get_tasks(self, filter_keyword: str = "") -> List[ScheduledTask]:
        if filter_keyword:
            return [t for t in self.tasks if filter_keyword.lower() in t.name.lower()]
        return self.tasks
