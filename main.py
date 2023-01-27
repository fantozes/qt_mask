from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt,  QEasingCurve, QPropertyAnimation, QTimer, QObject, QThread,  pyqtSignal, pyqtSlot

from os import environ

import sys

import hashlib
import time

from setting_ui import setting_ui

# имя файла с настройками (Временно)
setting_file = 'setting.ini'

#######################################################################################


class ParserIniFiles():             # Класс чтения ini файла
    """ Класс чтения, записи в ini фаил
    ####################################
    return: Конфигурационный файл настроек программы
    """

    from configparser import ConfigParser

    def __init__(self, filename=setting_file):
        self.__conf = self.ConfigParser()
        self.__filename = self.__checkvalue(filename)
        self.__conf.read(self.__filename)

    def get(self, Section, Key):
        # Метод чтения значений
        return self.__conf.get(Section, Key)

    def update(self, Section, Key, Value):
        # Метод обновления значений
        self.__conf.set(Section,
                        self.__checkvalue(Key),
                        self.__checkvalue(Value)
                        )
        self.__write()

    def __write(self):
        # Метод записи файла
        with open(self.__filename, 'w') as configfile:    # save
            self.__conf.write(configfile)

    @ staticmethod
    def __checkvalue(value):
        return value if isinstance(value, str) else str(value)

#######################################################################################


class MyLoginWindow(QWidget):
    """Виджет авторизации в главном окне
    ####################################
    return: ИОФ пользователя в главное окно программы
            Уровень доступа
    """

    Letters = ('qwertyuiopasdfghjklzxcvbnm')

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./forms/authorization.ui', self)

        # Тень виджета
        shadow = QGraphicsDropShadowEffect(
            blurRadius=10, xOffset=6, yOffset=6)
        self.frame.setGraphicsEffect(shadow)

        self.info_label.setText('Введите имя пользователя и пароль')

        # Кнопка войти:
        self.btn_login.clicked.connect(self.signin)

        # Кнопка выйти:
        self.btn_logout.clicked.connect(self.logout)

        # флажек запомнить пользователя
        self.remember_me.stateChanged.connect(self.selected_checkbox)

        # Загрузка первоначальных настроек
        self.load_first_setting()

    def selected_checkbox(self):
        # Функция записи настроек чекбокса в ini файл "Запомнить меня"
        ini = ParserIniFiles()
        ini.update(Section='Setting User',
                   Key='autosignin',
                   Value=self.remember_me.isChecked()
                   )

    def keyPressEvent(self, event):
        # Горячие клавиши в окне авторизации
        print(str(event.key()))
        if event.key() == Qt.Key_Escape:  # Закрыть окно по ESC
            App.b_login()

        if str(event.key()) in ["16777221", "16777220"]:  # Qt.Key_Enter:
            self.signin()

    def load_first_setting(self):
        # Функция первоначальных настроек
        # при загрузке виджета авторизации
        ini = ParserIniFiles()
        set = ini.get(Section='Setting User',
                      Key='autosignin'
                      )

        self.remember_me.setChecked(True if set == 'True' else False)

        print(App.access_level, "access_level")
        if App.access_level == 0:
            self.stackedWidget.setCurrentIndex(0)

        else:
            self.stackedWidget.setCurrentIndex(1)
            self.info_user.setText(App.label_sign_in.text())
            self.info_access_level.setText(
                str(f"Уровень доступа: {App.access_level}"))

    def logout(self):
        # Функция деавторизации из приложения
        App.access_level = 0
        App.label_sign_in.setText("GUEST")
        self.stackedWidget.setCurrentIndex(0)
        ini = ParserIniFiles()
        ini.update(Section='Setting User',
                   Key='user_login',
                   Value=''
                   )
        ini.update(Section='Setting User',
                   Key='user_password',
                   Value=''
                   )

    def checktext(self):
        # Проверка Login на пустое значение
        if len(self.lineEdit_login.text()) == 0:
            # Автоподставление имени учетной записи
            self.lineEdit_login.setText(str(environ.get('USERNAME')))
            self.info_label.setText('Поле "Login" не может быть пустым')
            return False

        Checklettert = self.Letters + self.Letters.upper() + '-_!$@'

        if len(self.lineEdit_login.text().strip(Checklettert)) != 0:
            self.info_label.setText(
                'Поле "Login" содержит не допустимые символы')
            return False

        return True

    def signin(self):
        # Проверка вводимых символов
        if not self.checktext():
            return

        psswd = self.lineEdit_pass.text()
        psswd = hashlib.md5(psswd.encode()).hexdigest() if psswd else ''

        user = self.lineEdit_login.text()

        # Хеширование паролей перед отправкой в ДБ
        # SQL запрос на сервер

        sql_text = "SELECT first_name, father_name, last_name, access_level\n" + \
            "FROM account INNER JOIN users ON account.id_user = users.id\n" + \
            f"WHERE account.login = '{user}'" + \
            (f" AND account.pass_md5 = '{psswd}';" if (psswd) else ';')

        data = Send_to_sql.sql_requests(sql_text)

        if data:
            self.info_label.setText('Вход выполнен')
            App.access_level = data[3]
            App.label_sign_in.setText(f"{data[0]} {data[1]} {data[2]}")

            ini = ParserIniFiles()
            ini.update(Section='Setting User',
                       Key='user_login',
                       Value=user
                       )

            ini.update(Section='Setting User',
                       Key='user_password',
                       Value=psswd
                       )

            QTimer().singleShot(500, lambda: App.b_login())

        else:
            self.info_label.setText('Неверный логин или пароль')
            App.access_level = 0

#######################################################################################


class Main_UI(QtWidgets.QMainWindow):
    """Главное окно программы
    ####################################
    return: Главное окно программы
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Загрузка формы из файла ui:
        uic.loadUi('dev5.ui', self)

        # Загрузка основных настроек формы
        setting_ui(self)

        self.start_authorization()

    @property
    def access_level(self):                 # Функция чтения уровня пользователя
        return self.Application_Access

    @access_level.setter
    def access_level(self, level: int):     # Функция установки уровня пользователя
        self.Application_Access = level

    def start_authorization(self):
        # Функция автоматической авторизации при старте приложения

        ini = ParserIniFiles()
        remember_sign_in = ini.get(Section='Setting User',
                                   Key='autosignin',
                                   )

        user = ini.get(Section='Setting User',
                       Key='user_login',
                       )

        psswd = ini.get(Section='Setting User',
                        Key='user_password',
                        )

        if remember_sign_in != 'True' and user != None:
            return self

        sql_text = "SELECT first_name, father_name, last_name, access_level\n" + \
            "FROM account INNER JOIN users ON account.id_user = users.id\n" + \
            f"WHERE account.login = '{user}'" + \
            (f" AND account.pass_md5 = '{psswd}';" if (psswd) else ';')

        # data = self.sql_requests(sql_text)
        data = Send_to_sql.sql_requests(sql_text)

        if data:
            self.access_level = data[3]
            self.label_sign_in.setText(f"{data[0]} {data[1]} {data[2]}")

    def enterEvent(self, event):
        # Функция вхождения курсором в программу
        print('Enter cursor in app')

    def MoveWindow(self, event):
        # Функция перемещение окна мышкой
        # self.setWindowOpacity(0.8)
        if event.buttons() == Qt.LeftButton:
            if self.isMaximized() == False:
                self.move(self.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()

    def mousePressEvent(self, event):
        # Функция позиции курсора мышки
        if event.buttons() == Qt.LeftButton:
            self.clickPosition = event.globalPos()

    def MaxOrMinWindow(self):
        # Функция разворачивания окна
        if self.isMaximized():
            self.showNormal()
            self.btn_fscreen.setChecked(False)
        else:
            self.showMaximized()
            self.btn_fscreen.setChecked(True)

    def animation(self):

        self.animation1 = QPropertyAnimation(
            self.control, b"minimumWidth")
        self.animation1.setDuration(self.DurationAnimation)
        self.animation1.setEasingCurve(self.TypeAnimation)

        if self.MoveReverse:
            self.animation1.setStartValue(self.StartValue)
            self.animation1.setEndValue(self.EndValue)

        else:
            self.animation1.setStartValue(self.EndValue)
            self.animation1.setEndValue(self.StartValue)

        self.MoveReverse = not self.MoveReverse

    def b_show_menu(self):
        # Кнопка show menu:
        print('show_menu')
        self.control = self.left_panel_1
        self.TypeAnimation = QEasingCurve.Type.InOutCirc
        self.MoveReverse = self.left_panel_1Position
        self.StartValue = self.left_panel_1Max
        self.EndValue = self.left_panel_1Min

        self.animation()
        self.animation1.start()

        self.left_panel_1Position = self.MoveReverse
        self.btn_menu.setChecked(self.left_panel_1Position)

    # Кнопки управления из формы:

    def b_search(self):
        # Кнопка поиска по базе данных
        print(f'Поиск в базе данных: {self.line_edit_search.text()}')

    def b_setting(self):
        # Кнопка настроек главного окна программы
        self.control = self.btn_setting
        self.TypeAnimation = QEasingCurve.Type.InOutQuart
        self.MoveReverse = self.btn_settingWidth
        self.StartValue = self.btn_settingMax
        self.EndValue = self.btn_settingMin

        self.animation()
        self.animation1.start()

        self.btn_settingWidth = self.MoveReverse
        self.btn_setting.setChecked(self.MoveReverse)

        print(f'Настройки главного окна {self.btn_login.isChecked()}')

    def b_login(self):
        # Кнопка Login:
        self.control = self.btn_login
        self.TypeAnimation = QEasingCurve.Type.InOutQuart
        self.MoveReverse = self.btn_loginWidth
        self.StartValue = self.btn_loginMax
        self.EndValue = self.btn_loginMin

        self.animation()
        self.animation1.start()

        self.btn_loginWidth = self.MoveReverse
        self.btn_login.setChecked(self.MoveReverse)

        print(f'авторизация пользователя {self.btn_login.isChecked()}')

        if self.btn_loginWidth:
            self.myLoginWindow = MyLoginWindow()
            self.bodyWidget.addWidget(self.myLoginWindow)
            self.myLoginWindow.lineEdit_login.setFocus()

        else:
            self.bodyWidget.removeWidget(self.myLoginWindow)
            self.myLoginWindow.close()
            self.myLoginWindow = None

        # блокировка управляющих элементов
        self.line_edit_search.setEnabled(not self.btn_loginWidth)
        self.btn_menu.setEnabled(not self.btn_loginWidth)
        self.btn_search.setEnabled(not self.btn_loginWidth)
        self.btn_setting.setEnabled(not self.btn_loginWidth)
        self.left_panel_1.setEnabled(not self.btn_loginWidth)

#######################################################################################


class Send_to_sql:
    """ Класс для отправки запроса на сервер"""

    def sql_requests(sql_text):
        # SQL запрос на сервер
        print('отправка запроса на сервер')
        with SQL() as sql:
            return sql.fetchone(sql_text)

#######################################################################################


class SQL(ParserIniFiles):            # Класс для работы с базой данных postgresql
    """ Класс для взаимодействия с БД
    ####################################
    return: Значения,Записи в базе данных postgresql
    """

    def __init__(self):
        super().__init__()

    def __enter__(self):
        # Подключение к БД
        import psycopg2

        self.conn = psycopg2.connect(
            host=self.get('Setting Database', 'DB_HOST'),
            port=self.get('Setting Database', 'DB_PORT'),
            database=self.get('Setting Database', 'DB_NAME'),
            user=self.get('Setting Database', 'DB_USER'),
            password=self.get('Setting Database', 'DB_PASSWORD')
        )

        self.cur = self.conn.cursor()
        return self

    def __exit__(self, type, value, traceback):
        # Закрытие подключения с БД
        self.cur.close()
        self.conn.close()

    def fetchall(self, sql):
        # Прочитать все из БД
        try:
            self.cur.execute(sql)
            return self.cur.fetchall()
        except Exception as ex_:
            print(ex_)

    def fetchone(self, sql):
        # Прочитать одну строку из БД
        try:
            self.cur.execute(sql)
            return self.cur.fetchone()
        except Exception as ex_:
            print(ex_)

#######################################################################################


class MyWidget1(QWidget):        # Тестовый виджет в РАЗРАБОТКЕ
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./forms/dashboard.ui', self)

#######################################################################################


class MyWidget2(QWidget):        # Тестовый виджет в РАЗРАБОТКЕ
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./forms/progress.ui', self)


#######################################################################################

if __name__ == '__main__':       # Основное окно программы
    """ Запуск основного окна программы
    ####################################
    """
    Main_App = QtWidgets.QApplication(sys.argv)
    App = Main_UI()  # Переменная приложения
    App.show()       # Показать приложение
    sys.exit(Main_App.exec())
