from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
import sys


def setting_ui(self):

    # Загрузка css стилей из файла:
    with open(file='./css/theme_style.css', mode='r') as f:
        self.setStyleSheet(f.read())

    # Имя программы:
    self.setWindowTitle('Alfa-C')
    self.programm_name.setText(
        "<strong> <font color=yellow><i>Alfa-C<i></font></strong>")
    shadow = QtWidgets.QGraphicsDropShadowEffect(
        blurRadius=10, xOffset=3, yOffset=4)
    self.programm_name.setGraphicsEffect(shadow)

    # Иконка приложения:
    self.setWindowIcon(QIcon(
        './icons/iface/icons8-mind-map-100.png'))

    # Убрать стандартные кнопки управления окном
    self.setWindowFlags(Qt.FramelessWindowHint)

    # Прозрачность окна
    self.setAttribute(Qt.WA_TranslucentBackground, False)

    # Таймер для автоматического скрытия меню
    self.timer = QTimer()

    # Кнопка закрыть приложение:
    self.btn_close.clicked.connect(sys.exit)
    # Кнопка свернуть приложение:
    self.btn_hide.clicked.connect(self.showMinimized)
    # Кнопка развернуть приложение на весь экран:
    self.btn_fscreen.clicked.connect(self.MaxOrMinWindow)

    # Перемещение окна мышкой
    self.fr_top.mouseMoveEvent = self.MoveWindow

    # Отслеживание курсора на центральном Widget
    self.centralwidget.setMouseTracking(True)

    # Установка виджета по умолчанию
    self.bodyWidget.setCurrentIndex(0)

    # Кнопка скрыть/показать боковое меню
    self.btn_menu.clicked.connect(self.b_show_menu)

    # Кнопка Setting (Скрыть показать текст)
    self.btn_setting.clicked.connect(self.b_setting)

    # Авторизация пользователя в приложении
    self.btn_login.clicked.connect(self.b_login)

    # Поиск в базе данных
    self.btn_search.clicked.connect(self.b_search)

    # Переменная для уровня доступа (0-100, 0 -> guest, 100 -> root)
    self.Application_Access = 0

    # Скорость анимации
    self.DurationAnimation = 400

    # Анимация левого меню #1
    self.left_panel_1Position = False
    self.left_panel_1Min = self.left_panel_1.minimumWidth()
    self.left_panel_1Max = self.left_panel_1.maximumWidth()
    self.left_panel_1.setMaximumWidth(self.left_panel_1Min)

    # Анимация кнопки Setting
    self.btn_settingWidth = False
    self.btn_settingMin = self.btn_setting.minimumWidth()
    self.btn_settingMax = self.btn_setting.maximumWidth()
    self.btn_setting.setMaximumWidth(self.btn_settingMin)

    # Анимация button Sign In
    self.btn_loginWidth = False
    self.btn_loginMin = self.btn_login.minimumWidth()
    self.btn_loginMax = self.btn_login.maximumWidth()
    self.btn_login.setMaximumWidth(self.btn_loginMin)


def load_user_setting(self):
    # Функция автоматической авторизации в приложении
    from main import SQL, Env_file

    env = Env_file()
    remember_sign_in = env.get_val('AUTOSIGNIN')
    user = env.get_val('USERNM')

    if remember_sign_in == 'TRUE' and user:

        psswd = env.get_val('PASSMD5')

        # SQL запрос на сервер
        with SQL() as sql:
            data = sql.fetchone(
                "SELECT first_name, father_name, last_name, access_level\n" +
                "FROM account INNER JOIN users ON account.id_user = users.id\n" +
                f"WHERE account.login = '{user}'" +
                (f" AND account.pass_md5 = '{psswd}';" if (psswd) else ';')
            )

        if data:
            self.access_level = data[3]
            self.label_sign_in.setText(f"{data[0]} {data[1]} {data[2]}")