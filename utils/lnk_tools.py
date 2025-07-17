import os
import configparser
import struct

def extract_linktargetidlist(path):
    with open(path, 'rb') as f:
        data = f.read()

    if data[0:4] != b'\x4C\x00\x00\x00':
        return None

    header_size = struct.unpack_from("<I", data, 0)[0]
    link_flags = struct.unpack_from("<I", data, 0x14)[0]

    has_link_target_id_list = link_flags & 0x00000001
    if not has_link_target_id_list:
        return None

    id_list_size = struct.unpack_from("<H", data, header_size)[0]
    id_list_data = data[header_size+2 : header_size+2+id_list_size]

    return id_list_data


def parse_lnk(path):
    ext = os.path.splitext(path)[1].lower()
    abspath = os.path.abspath(path)

    if ext == '.lnk':
        url = extract_linktargetidlist(abspath)
        if url:
            return url

        return None

    elif ext == '.url':
        config = configparser.ConfigParser()
        config.read(path)
        try:
            return config['InternetShortcut'].get('URL', None).encode()
        except:
            return None

    elif ext == '.desktop':
        config = configparser.ConfigParser(strict=False)
        config.read(path)
        return config['Desktop Entry'].get('Exec', None).encode()

    else:
        raise ValueError("Unsupported file type")
