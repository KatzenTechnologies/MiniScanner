import winreg

class FirewallRule:
    def __init__(self, name, raw_data):
        self.name = name
        self.raw_data = raw_data
        self.parsed = self.parse_data(raw_data)
        self.description = self.parsed.get("Desc")
        self.application = self.parsed.get("App")
        self.service = self.parsed.get("Svc")
        self.protocol = self.parsed.get("Prot")
        self.local_ports = self.parsed.get("LPort")
        self.remote_ports = self.parsed.get("RPort")
        self.local_addresses = self.parsed.get("LA4") or self.parsed.get("LA6")
        self.remote_addresses = self.parsed.get("RA4") or self.parsed.get("RA6")
        self.direction = self.parsed.get("Dir")
        self.action = self.parsed.get("Action")
        self.edge_traversal = self.parsed.get("Edge")
        self.interfacetype = self.parsed.get("IFType")
        self.profile = self.parsed.get("Profile")
        self.enabled = self.parsed.get("Active") == "TRUE"

    def parse_data(self, data):
        result = {}
        for item in data.split("|"):
            if "=" in item:
                key, val = item.split("=", 1)
                result[key] = val
        return result

    def delete(self):
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules",
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, self.name)

def get_firewall_rules():
    rules = []
    path = r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                name, data, _ = winreg.EnumValue(key, i)
                rules.append(FirewallRule(name, data))
                i += 1
            except OSError:
                break
    return rules
