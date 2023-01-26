
# # User
# USERNM=test
# PASSMD5=81dc9bdb52d04dc20036dbd8313ed055
# # SQL
# DATABASE=agpz
# HOST=176.119.159.66
# USER=test_user
# PASSWORD=qwerty
# PORT=5432

import hashlib


print(hashlib.md5(None.encode()).hexdigest())


class TelephoneDirectory:
    def __init__(self):
        self.teldict = {}

    def add_entry(self, name, number):
        self.teldict[name] = number

    def del_entry(self, name):
        self.teldict.pop(name)

    def upd_entry(self, name, number):
        self.teldict[name] = number

    def lookup_number(self, name):
        return self.teldict[name]

    def __str__(self):
        ret_dct = ""
        for key, value in self.teldict.item():
            куе_все += f'{key} : {value}\n'
        return ret_dct
