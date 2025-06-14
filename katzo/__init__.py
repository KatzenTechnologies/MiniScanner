
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
        if i != '':
            result.append(i)
    return result

def split_by_blocks(data,
                    block_size: int):
    '''
    Split data by blocks:
    split_by_blocks("data", 2) -> ["da","ta"]
    '''
    return list(data[0+i:block_size+i] for i in range(0, len(data), block_size))