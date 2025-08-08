import os
import katzo


class Main:
    name = "LNKCheck"
    author = "Northkatz"
    version = "2.0"
    def __init__(self, API):
        globals()["API"] = API
        API.logger.log("LNKCheck", "Loading up base..", API.LOGTYPE.INFO)
        if os.path.exists("./db/lnklist.json") and os.path.isfile("./db/lnklist.json"):
            self.base = API.get_config_object("lnklist.json", API.ConfigType.JSON, folder="db")
            for i, j in enumerate(self.base.data):
                for n in range(len(self.base.data[i]["sig"])):
                    self.base.data[i]["sig"][n] = self.base.data[i]["sig"][n].encode("utf-16le")

        else:
            API.logger.log("LNKCheck", "There's no base!")
            raise Exception("Theres no lnklist.json")
        self.threats = {}

    def scan(self):
        arrays = katzo.merge_arrays(API.indexer.index_directory(API.paths.STARTMENU[0]),
                                    API.indexer.index_directory(API.paths.STARTMENU[1]),
                                    API.indexer.index_directory(API.paths.TASKBAR),
                                    API.indexer.index_directory(API.paths.DESKTOP)
                              )

        for i in arrays:
            if os.path.splitext(i)[-1] in [".lnk", ".url"]:

                API.logger.log("LNKCheck", f"Scanning: {i}", API.LOGTYPE.INFO)
                target = API.lnk_tools.parse_lnk(i)
                for j in (self.base.data if target is not None else []):
                    for n in j["sig"]:
                        if ((n in target["LinkTargetIDList"]) if target.get("LinkTargetIDList") is not None else False) or\
                                (n in target["Arguments"] if target.get("Arguments") is not None else False):
                            API.logger.log("LNKCheck", f"Found malware!: {i}", API.LOGTYPE.INFO)
                            API.add_threat(i, j["name"], self, enable_quarantine_button=True)
                            self.threats.update({i: j["name"]})

    def delete(self, file):
        if file in self.threats.keys():
            os.remove(file)
            API.logger.log("LNKCheck", f"Removed {file}", API.LOGTYPE.SUCCESS)

    def quarantine(self, file):
        if file in self.threats:
            API.quarantine.add_path(file, self.threats[file], source=self)
            API.logger.log("LNKCheck", f"Quarantined {file}", API.LOGTYPE.SUCCESS)