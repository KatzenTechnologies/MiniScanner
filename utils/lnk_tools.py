import os
import struct
import configparser

def extract_string(data, offset):
    if offset >= len(data):
        return None, offset
    string_len = struct.unpack_from("<H", data, offset)[0]
    offset += 2
    string_bytes = data[offset:offset+string_len*2]
    offset += string_len*2
    return string_bytes, offset

def parse_lnk(path):
    with open(path, 'rb') as f:
        data = f.read()

    if data[0:4] != b'\x4C\x00\x00\x00':
        return None

    header_size = struct.unpack_from("<I", data, 0)[0]
    link_flags = struct.unpack_from("<I", data, 0x14)[0]

    result = {}

    has_link_target_id_list = link_flags & 0x00000001
    offset = header_size
    if has_link_target_id_list:
        id_list_size = struct.unpack_from("<H", data, offset)[0]
        id_list_data = data[offset+2 : offset+2+id_list_size]
        offset += 2 + id_list_size
        result['LinkTargetIDList'] = id_list_data

    has_link_info = link_flags & 0x00000002
    if has_link_info:
        link_info_size = struct.unpack_from("<I", data, offset)[0]
        link_info_data = data[offset:offset+link_info_size]
        result['LinkInfo'] = link_info_data
        offset += link_info_size

    if link_flags & 0x00000004:
        description, offset = extract_string(data, offset)
        result['Description'] = description

    if link_flags & 0x00000008:
        relative_path, offset = extract_string(data, offset)
        result['RelativePath'] = relative_path

    if link_flags & 0x00000010:
        working_dir, offset = extract_string(data, offset)
        result['WorkingDirectory'] = working_dir

    if link_flags & 0x00000020:
        arguments, offset = extract_string(data, offset)
        result['Arguments'] = arguments

    if link_flags & 0x00000040:
        icon_location, offset = extract_string(data, offset)
        result['IconLocation'] = icon_location

    return result

def parse_url(path):
    config = configparser.ConfigParser()
    config.read(path)
    try:
        url = config['InternetShortcut'].get('URL', None)
        return url.encode('utf-8') if url else None
    except:
        return None

def parse_desktop(path):
    config = configparser.ConfigParser(strict=False)
    config.read(path)
    try:
        exec_cmd = config['Desktop Entry'].get('Exec', None)
        return exec_cmd.encode('utf-8') if exec_cmd else None
    except:
        return None

def parse_link(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == '.lnk':
        return parse_lnk(path)
    elif ext == '.url':
        return parse_url(path)
    elif ext == '.desktop':
        return parse_desktop(path)
    else:
        raise ValueError("Unsupported file type")
