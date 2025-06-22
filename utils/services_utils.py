import platform
import subprocess

class Service:
    def __init__(self, name):
        self.name = name
        self.system = platform.system()

    def start(self):
        if self.system == "Windows":
            subprocess.run(["sc", "start", self.name], check=False)
        elif self.system == "Linux":
            subprocess.run(["systemctl", "start", self.name], check=False)

    def stop(self):
        if self.system == "Windows":
            subprocess.run(["sc", "stop", self.name], check=False)
        elif self.system == "Linux":
            subprocess.run(["systemctl", "stop", self.name], check=False)

    def restart(self):
        if self.system == "Windows":
            self.stop()
            self.start()
        elif self.system == "Linux":
            subprocess.run(["systemctl", "restart", self.name], check=False)

    def status(self):
        if self.system == "Windows":
            result = subprocess.run(["sc", "query", self.name], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                return "running"
            elif "STOPPED" in result.stdout:
                return "stopped"
            else:
                return "unknown"
        elif self.system == "Linux":
            result = subprocess.run(["systemctl", "is-active", self.name], capture_output=True, text=True)
            return result.stdout.strip()


def list_services():
    system = platform.system()
    services = []

    if system == "Windows":
        try:
            output = subprocess.check_output(['sc', 'query', 'type=', 'service', 'state=', 'all'], text=True, encoding="utf-8", errors="ignore")
        except subprocess.CalledProcessError:
            return []

        lines = output.splitlines()
        current = {}
        for line in lines:
            if "SERVICE_NAME:" in line:
                if current:
                    services.append(current)
                    current = {}
                current["name"] = line.split(":", 1)[1].strip()
            elif "STATE" in line:
                if "RUNNING" in line:
                    current["status"] = "running"
                else:
                    current["status"] = "stopped"
        if current:
            services.append(current)

    elif system == "Linux":
        try:
            output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'], text=True)
        except subprocess.CalledProcessError:
            return []

        for line in output.strip().splitlines():
            parts = line.split(None, 4)
            if len(parts) >= 4:
                name, load, active, sub = parts[:4]
                services.append({
                    "name": name,
                    "status": active
                })

    return services
