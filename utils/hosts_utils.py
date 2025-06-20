import os
import katzo

class Hosts:
    def __init__(self,
                 source="blank.com",
                 dest="0.0.0.0",
                 line=0):
        self.source = source
        self.dest = dest
        self.line = line

    def cure(self):
        with open(os.getenv("WINDIR") + "\\System32\\drivers\\etc\\hosts", 'r') as file:
            lines = [line.rstrip() for line in file]

        lines[self.line] = "# " + lines[self.line] + ' # Cured'

        with open(os.getenv("WINDIR") + "\\System32\\drivers\\etc\\hosts", 'w') as file:
            file.write("\n".join(lines))


def parse_hosts(file=(os.getenv("WINDIR") + "\\System32\\drivers\\etc\\hosts"), lower=True):

    result = []

    with open(file) as file:
        lines = [line.rstrip() for line in file]

    # Анализ строчек файла hosts

    current_line = 0

    for i in lines:
        if i.find("#") != -1:
            i = i[:i.find("#")]  # Удаление комментариев с записей файла Hosts

            this_line = i.split(" ")
            this_line = katzo.clean(this_line)  # Очистка списка от "мусорных" значений

            if len(this_line) < 1:
                current_line += 1
                continue

            if lower:
                this_line[0] = this_line[0].lower()
                this_line[1] = this_line[1].lower()

            # Создание объекта, содержащего в себе переадресацию, записанную в файле Hosts.
            datatype = Hosts(source=this_line[1],
                             dest=this_line[0],
                             line=current_line)

            result.append(datatype)

            current_line += 1
    return result
