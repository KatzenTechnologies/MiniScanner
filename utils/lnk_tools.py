import os
import configparser
import win32com.client
import pylnk3

def extract_url_from_linktargetidlist(path):
    try:
        with open(path, "rb") as f:
            lnk = pylnk3.parse(f)
            for item in lnk.link_target_id_list.items:
                data_str = item.data_as_string()
                return data_str
    except Exception as e:
        return None
    return None


def parse_lnk(path):
    ext = os.path.splitext(path)[1].lower()
    abspath = os.path.abspath(path)

    if ext == '.lnk':
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(abspath)

        target = shortcut.TargetPath.strip()
        arguments = shortcut.Arguments.strip()
        working_dir = shortcut.WorkingDirectory.strip()

        if target:
            if arguments:
                return f'{target} {arguments}'
            return target

        if arguments and os.path.exists(arguments):
            return arguments

        if working_dir and arguments:
            combined = os.path.join(working_dir, arguments)
            if os.path.exists(combined):
                return combined

        if arguments:
            return arguments
        if working_dir:
            return working_dir

        url = extract_url_from_linktargetidlist(abspath)
        if url:
            return url

        return None

    elif ext == '.url':
        config = configparser.ConfigParser()
        config.read(path)
        return config['InternetShortcut'].get('URL', None)

    elif ext == '.desktop':
        config = configparser.ConfigParser(strict=False)
        config.read(path)
        return config['Desktop Entry'].get('Exec', None)

    else:
        raise ValueError("Unsupported file type")
