import os
import katzo

class Main:
    name = "LNKCheck"
    def __init__(self, API):
        globals()["API"] = API
        API.logger.log("LNKCheck", "Loading up base..", API.LOGTYPE.INFO)
        if os.path.exists("./db/lnk_list.txt") and os.path.isfile("./db/lnk_list.txt"):
            self.base = katzo.clean(open("./db/lnk_list.txt", 'r').read().split("\n"))
            for i, j in enumerate(self.base):
                self.base[i] = j.encode().replace(b"\r", b"") # cleanup

        else:
            API.logger.log("LNKCheck", "There's no base!")
            raise Exception("Theres no lnk_list.txt")
        self.threats = []

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
                for j in self.base if target is not None else []:
                    if j in target or katzo.wide(j) in target:
                        API.logger.log("LNKCheck", f"Found malware!: {i}", API.LOGTYPE.INFO)
                        API.add_threat(i, "Adware.Shortcut.Generic", self)
                        self.threats.append(i)

    def delete(self, file):
        API.logger.log("LNKCheck", f"Removed {file}", API.LOGTYPE.SUCCESS)
        if file in self.threats:
            os.remove(file)