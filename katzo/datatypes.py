import marshal
from os.path import exists,isdir


class DataWrapper:
    def __init__(self, file):
        self.data = None
        self.file = file
        if exists(file) and not isdir(file):
            self.data = marshal.load(open(self.file,'rb'))
    def set(self,val):
        self.data = val
    def get(self):
        return  self.data
    def save(self):
        marshal.dump(self.data,open(self.file,'wb'))
