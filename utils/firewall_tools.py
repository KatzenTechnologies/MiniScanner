import winreg
import re

class FirewallRule:
    def __init__(self, reg_name, raw_data):
        self.reg_name = reg_name
        self.raw_data = raw_data
        self.fields = self.parse(raw_data)

        self.name = self.fields.get("Name") or self.guess_name()
        self.app = self.fields.get("App")
        self.action = self.fields.get("Action")
        self.direction = self.fields.get("Dir")
        self.protocol = self.fields.get("Protocol")
        self.description = self.fields.get("Desc")
        self.active = self.fields.get("Active") == "TRUE"

    def parse(self, raw: str) -> dict:
        result = {}
        parts = raw.strip().split("|")
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                result[k] = v
        return result

    def guess_name(self) -> str:
        if "EmbedCtxt" in self.fields:
            return self.clean_resource_name(self.fields["EmbedCtxt"])
        if "AppPkgId" in self.fields:
            return self.fields["AppPkgId"]
        if "App" in self.fields:
            return self.fields["App"].split("\\")[-1]
        if "Desc" in self.fields and self.fields["Desc"]:
            return self.fields["Desc"]
        return "[NoName]"

    def clean_resource_name(self, ctxt: str) -> str:
        ctxt = re.sub(r"^@?\{?", "", ctxt)
        ctxt = re.sub(r"\?.*$", "", ctxt)
        ctxt = ctxt.split("\\")[-1]
        return ctxt.strip(" {}")

    def delete(self):
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules",
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, self.reg_name)

def get_firewall_rules():
    rules = []
    path = r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                name, data, _ = winreg.EnumValue(key, i)
                rule = FirewallRule(name, data)
                rules.append(rule)
                i += 1
            except OSError:
                break
    return rules
