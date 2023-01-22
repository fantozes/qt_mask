from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt,  QEasingCurve, QPropertyAnimation, QTimer, QObject, QThread

from os import environ

import sys
import psycopg2

from dotenv import dotenv_values, set_key, unset_key
from setting_ui import setting_ui, load_user_setting


class MyLoginWindow(QWidget):
    # Виджет авторизации

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
        # Функция записи настроек чекбокса в env файл "Запомнить меня"
        env = Env_file()
        if self.remember_me.isChecked() == True:
            env.set_val('AUTOSIGNIN', 'TRUE')

        else:
            env.set_val('AUTOSIGNIN', 'FALSE')

    def keyPressEvent(self, event):
        # Горячие клавиши в окне авторизации
        # print(str(event.key()))
        if event.key() == Qt.Key_Escape:  # Закрыть окно по ESC
            App.b_login()

        if str(event.key()) == "16777220":  # Qt.Key_Enter:
            self.signin()

    def load_first_setting(self):
        # Функция первоначальных настроек
        # при загрузке виджета авторизации
        env = Env_file()
        if env.get_val('AUTOSIGNIN') == 'TRUE':
            self.remember_me.setChecked(True)

        else:
            self.remember_me.setChecked(False)

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
        env = Env_file()
        env.set_val('USERNM')
        env.set_val('PASSMD5')

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

    def convert_pass_to_hash(self):
        # Функция хешировани
        import hashlib
        passwd = str(self.lineEdit_pass.text())
        return hashlib.md5(passwd.encode()).hexdigest()

    def signin(self):
        # Проверка вводимых символов
        if not self.checktext():
            return

        # Хеширование паролей перед отправкой в ДБ
        if len(self.lineEdit_pass.text()) != 0:
            psswd = self.convert_pass_to_hash()
        else:
            psswd = ''

        # SQL запрос на сервер
        with SQL() as sql:
            data = sql.fetchone(
                "SELECT first_name, father_name, last_name, access_level\n" +
                "FROM account INNER JOIN users ON account.id_user = users.id\n" +
                f"WHERE account.login = '{self.lineEdit_login.text()}'" +
                (';' if (self.lineEdit_pass.text() == '') else
                 f" AND account.pass_md5 = '{psswd}';")
            )

        # print(data)

        if data:
            self.info_label.setText('Вход выполнен')
            App.access_level = data[3]
            App.label_sign_in.setText(f"{data[0]} {data[1]} {data[2]}")

            env = Env_file()
            env.set_val('USERNM', self.lineEdit_login.text())
            env.set_val('PASSMD5', psswd)

            timer = QTimer()
            timer.singleShot(500, lambda: App.b_login())

        else:
            self.info_label.setText('Неверный логин или пароль')
            App.access_level = 0


class Env_file():
    # Класс чтения и записи в env файл
    def get_val(self, Key):
        env = dotenv_values()
        return env.get(Key)

    def set_val(self, Key, Val=None):
        if Val:
            set_key(".env", key_to_set=str(Key),
                    value_to_set=str(Val))
        else:
            unset_key(".env", str(Key))


class Main_UI(QtWidgets.QMainWindow):
    # Главное окно программы
    def __init__(self, parent=None):
        super().__init__(parent)

        # Загрузка формы из файла ui:
        uic.loadUi('dev5.ui', self)

        # Загрузка основных настроек формы
        setting_ui(self)

        load_user_setting(self)

    @ property
    def access_level(self):                 # Функция чтения уровня пользователя
        return self.Application_Access

    @ access_level.setter
    def access_level(self, level: int):     # Функция установки уровня пользователя
        self.Application_Access = level

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


class SQL():            # Класс для работы с базой данных postgresql

    def __init__(self):
        # Инициализация переменных из файла env
        env = Env_file()
        self.user = env.get_val("USER")
        self.database = env.get_val("DATABASE")
        self.password = env.get_val("PASSWORD")
        self.host = env.get_val("HOST")
        self.port = env.get_val("PORT")

    def __enter__(self):
        # Подключение к БД
        self.conn = psycopg2.connect(
            database=self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port
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


class MyWidget1(QWidget):        # Тестовый виджет в РАЗРАБОТКЕ
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./forms/dashboard.ui', self)


class MyWidget2(QWidget):        # Тестовый виджет в РАЗРАБОТКЕ
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./forms/progress.ui', self)


if __name__ == '__main__':
    Main_App = QtWidgets.QApplication(sys.argv)
    App = Main_UI()  # Переменная приложения
    App.show()
    sys.exit(Main_App.exec())
