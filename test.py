
# # User
# USERNM=test
# PASSMD5=81dc9bdb52d04dc20036dbd8313ed055
# # SQL
# DATABASE=agpz
# HOST=176.119.159.66
# USER=test_user
# PASSWORD=qwerty
# PORT=5432

# [Setting Database]
# DB_NAME=agpz
# DB_HOST=176.119.159.66
# DB_USER=test_user
# DB_PASSWORD=qwerty
# DB_PORT=5432

# [Setting User]
# AUTOSIGNIN=True
# USER_LOGIN=test
# USER_PASSWORD=81dc9bdb52d04dc20036dbd8313ed055


class ParserIniFiles():             # Класс чтения ini файла
    from configparser import ConfigParser

    def __init__(self, filename):
        self.__conf = self.ConfigParser()
        self.__filename = filename
        self.__conf.read(filename)

    def get(self, Section, Key):
        return self.__conf.get(Section, Key)

    def update(self, Section, Key, Value):
        self.__conf.set(Section, Key, self.__checkvalue(Value))
        self.__write()

    def __write(self):
        with open(self.__filename, 'w') as configfile:    # save
            self.__conf.write(configfile)

    @staticmethod
    def __checkvalue(value):
        return str(value)


a = ParserIniFiles('setting.ini')
# a.write('Setting User', 'AUTOSIGNIN', False) 'setting.ini'
print(a.get('Setting User', 'AUTOSIGNIN'))

a.update('Setting User', 'AUTOSIGNIN', 123)
