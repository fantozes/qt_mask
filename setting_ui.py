from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QGraphicsOpacityEffect
import sys

# file_icon = './icons/iface/logo.png'
file_icon = './icons/source_logo.png'
file_style = './qss/theme_style.css'
name_prog = 'Alfa-C'


def setting_ui(self):

    # Загрузка css стилей из файла:
    with open(file=file_style, mode='r') as f:
        self.setStyleSheet(f.read())

    # Имя программы:
    self.setWindowTitle(name_prog)
    self.programm_name.setText(name_prog)
    shadow = QGraphicsDropShadowEffect(
        blurRadius=10, xOffset=3, yOffset=4)
    self.programm_name.setGraphicsEffect(shadow)

    # Иконка приложения:
    self.setWindowIcon(QIcon(file_icon))
    self.pixmap = QPixmap(file_icon)
    self.logo.setPixmap(self.pixmap)

    # Убрать стандартные кнопки управления окном
    # self.setWindowFlags(Qt.FramelessWindowHint)
    self.setWindowFlags(Qt.CustomizeWindowHint)

    # Прозрачность окна
    self.setAttribute(Qt.WA_TranslucentBackground, False)

    # self.opacity_effect = QGraphicsOpacityEffect()
    # self.opacity_effect.setOpacity(0.3)
    # self.bodyWidget.setGraphicsEffect(self.opacity_effect)

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
