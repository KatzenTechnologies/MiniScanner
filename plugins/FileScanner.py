import os
import traceback
import json

import psutil


class Main:
    name = "FileScanner"
    author = "Northkatz"
    version = "1.0"

    def __init__(self, API):
        self.threats = []
        self.threats2 = {}
        globals()["API"] = API
        scheme = {
            "scan_memory_extended":{
                "enabled_if": "scan_memory"
            }

        }
        self.cfg = API.get_config_object("filescanner.yml", type_of_config=API.ConfigType.YAML)
        try:
            self.loc = API.get_localization_object(json.load(open(f"db/filescanner/locales/{API.chosen_language.file}", "r", encoding='utf-8', errors='replace')), API.chosen_language.file)
        except:
            print(traceback.format_exc())
            self.loc = API.get_localization_object({})
        if self.cfg.data is None:
            # Default data
            self.cfg.data = {"scan_memory": True,
                             "scan_memory_extended": False,
                             "yara": True}

            self.cfg.save()

        API.register_config(self.cfg, self.loc, [], scheme, "FileScanner")

    def scan_file(self, file):
        try:
            match = self.yara_db.match(file)
            if match:
                rule = match[0].rule
                API.add_threat(file, rule, self, enable_quarantine_button=True)

                if file not in self.threats:
                    self.threats.append(file)
                self.threats2[file] = rule

        except Exception as e:
            API.logger.log(
                self.name,
                f"Error while scanning {file}: {e}",
                API.LOGTYPE.ERROR
            )

    def scan(self):
        yara_flag = False

        if self.cfg["yara"] and os.path.exists("db/filescanner/yara"):
            import yara
            rules = {}
            for i in os.listdir("db/filescanner/yara"):
                if i.endswith(".yar"):
                    rules.update({i: os.path.join("db","filescanner","yara",i)})
            self.yara_db = yara.compile(filepaths=rules)

            yara_flag = True

        for i in API.get_indexer_generator().scan():
            if yara_flag:
                self.scan_file(i)

        if self.cfg["scan_memory"]:
            for pid, path, memory_maps in API.memoryscanner.scan():
                self.scan_file(path)
                if self.cfg["scan_memory_extended"]:
                    for j in memory_maps:
                        if j.path in self.threats and j.path is not None:
                            self.scan_file(j.path)



    def delete(self, file):
        if file in self.threats:
            os.remove(file)
            API.logger.log(self.name, f"Removed {file}", API.LOGTYPE.SUCCESS)

    def quarantine(self, file):
        if file in self.threats:
            API.quarantine.add_path(file, self.threats2[file], self)
            API.logger.log(self.name, f"Added to quarantine {file}", API.LOGTYPE.SUCCESS)
