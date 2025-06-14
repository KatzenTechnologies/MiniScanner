import random



def random_string(length):
    r = ""
    for i in range(length):
        r += random.choice("QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890")
    return r