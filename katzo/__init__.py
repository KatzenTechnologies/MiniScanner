import os

def inverse(
        dictionary: dict
        ):
    '''
    inverses dictionary
    inverse({3:4}) -> {4:3}
    '''
    result = {}
    for i in list(dictionary):
        if result.get(dictionary[i]) == None:
            result |= {dictionary[i]:i}
    return result

def clean(arraylist: list | tuple) -> list:
    '''
    cleans list by removing empty variables
    '''
    result = []
    for i in arraylist:
        if i != '' and i != b'':
            result.append(i)
    return result

def split_by_blocks(data,
                    block_size: int):
    '''
    Split data by blocks:
    split_by_blocks("data", 2) -> ["da","ta"]
    '''
    return list(data[0+i:block_size+i] for i in range(0, len(data), block_size))

def merge_arrays(*args):
    result = []
    seen = set()
    for lst in args:
        for x in lst:
            if x not in seen:
                seen.add(x)
                result.append(x)
    return result

def wide(data):
    return b''.join(bytes([b, 0x00]) for b in data)

def dir_exists(direc):
    return os.path.exists(direc) and os.path.isdir(direc)

def file_exists(file):
    return os.path.exists(file) and os.path.isfile(file)