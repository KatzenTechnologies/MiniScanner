import os
import platform
import katzo

class Hosts:
    def __init__(self, source="blank.com", dest="0.0.0.0", line=0, file=None):
        self.source = source
        self.dest = dest
        self.line = line
        self.file = file

    def cure(self):
        with open(self.file, 'r') as f:
            lines = [line.rstrip() for line in f]

        lines[self.line] = "# " + lines[self.line] + ' # Cured'

        with open(self.file, 'w') as f:
            f.write("\n".join(lines))


def get_default_hosts_file():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.getenv("WINDIR", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
    elif system == "Linux":
        return "/etc/hosts"

def parse_hosts(file=None, lower=True):
    if file is None:
        file = get_default_hosts_file()

    result = []

    with open(file, 'r') as f:
        lines = [line.rstrip() for line in f]

    for current_line, raw in enumerate(lines):
        line = raw
        comment_pos = line.find('#')
        if comment_pos != -1:
            line = line[:comment_pos]

        parts = katzo.clean(line.split())

        if len(parts) < 2:
            continue

        if lower:
            parts[0] = parts[0].lower()
            parts[1] = parts[1].lower()

        result.append(Hosts(
            source=parts[1],
            dest=parts[0],
            line=current_line,
            file=file
        ))

    return result
