import logging
import os
import webbrowser
import datetime
from urllib.request import urlopen

import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from sqlitedict import SqliteDict

from common.secrets import Secrets
from common.settings import update_config_param, get_config_param
from common.ui_elements import generate_font, create_w_lo, CustomEntry, get_v_spacer
from newReactives import DarkBtn_Ui


class Ui_activation_w(object):
    def setupUi(self, MainWindow):
        self.main_window = MainWindow
        MainWindow.resize(400, 200)
        if not self.check_activated():
            self.centralwidget = MainWindow.centralwidget
            self.verticalLayout = MainWindow.verticalLayout

            self.activ_l = QtWidgets.QLabel(parent=self.centralwidget)
            self.activ_l.setFont(generate_font(16))
            self.activ_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.activ_l.setText("Введите код активации")
            self.verticalLayout.addWidget(self.activ_l, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            label = QtWidgets.QLabel(parent=self.centralwidget)
            label.setFont(generate_font(10))
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label.setText("Подробнее на https://лкмщик.рф")
            label.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            label.mousePressEvent = lambda event: webbrowser.open_new(r"https://лкмщик.рф/")
            self.verticalLayout.addWidget(label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


            self.verticalLayout.addItem(get_v_spacer())
            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText("Код активации:")
            lo.addWidget(code_l)
            self.code_e = CustomEntry(w, padding=False)
            self.code_e.setFixedWidth(300)
            lo.addWidget(self.code_e)
            #
            self.verticalLayout.addItem(get_v_spacer())
            activate_btn = DarkBtn_Ui(self.centralwidget, name="edit_proj")
            activate_btn.setText("   Активировать")
            activate_btn.clicked.connect(lambda: self.activate())
            self.verticalLayout.addWidget(activate_btn)

            MainWindow.setWindowTitle("ЛКМщик - Активация")

        else:
            self.main_window.set_state("register")

    def activate(self):
        try:
            data_dict = {"f": "license", "l_key": self.code_e.text()}
            result = requests.get("http://лкмщик.рф/api_path", params=data_dict)
            response_date = result.text.replace("\"", "")
            datetime.datetime.strptime(response_date, "%Y-%m-%d").date()
            update_config_param("end_date", response_date)
            if self.check_activated():
                self.main_window.set_state("register")
            else:
                self.activ_l.setText("Не получилось активировать")

        except:
            self.activ_l.setText("Не получилось активировать")


    def check_activated(self) -> bool:
        date = get_config_param("end_date")
        if date is None:
            return False

        end_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        try:
            res = urlopen('http://just-the-time.appspot.com/')
            result = res.read().strip()
            result_str = result.decode('utf-8')
            date_now = datetime.datetime.strptime(result_str, "%Y-%m-%d %H:%M:%S").date()
        except Exception:
            date_now = datetime.datetime.now().date()
            logging.info(f"Текущая дата {date_now}")
        # print(end_date)
        # print(date_now)
        if end_date > date_now:
            return True
        else:
            return False


class Ui_register_w(object):
    def setupUi(self, MainWindow):
        self.main_window = MainWindow
        if not self.check_created():
            MainWindow.resize(400, 200)
            # if not self.check_activated():
            self.centralwidget = MainWindow.centralwidget
            self.verticalLayout = MainWindow.verticalLayout

            self.activ_l = QtWidgets.QLabel(parent=self.centralwidget)
            self.activ_l.setFont(generate_font(14))
            self.activ_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.activ_l.setText("Информация о пользователе:")
            self.activ_l.setStyleSheet("""
            margin:15 0 3 0;
            """)
            self.verticalLayout.addWidget(self.activ_l, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

            describe = QtWidgets.QLabel(parent=self.centralwidget)
            describe.setFont(generate_font(10))
            describe.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            describe.setText("Для статистики на сервер передаются только имя, email и компания.\n"
                             "Любая другая информация, добавленная в данное приложение,\n"
                             "храниться только на вашем компьютере.")

            describe.setStyleSheet("""
                        margin:0 0 7 0;
                        """)
            self.verticalLayout.addWidget(describe, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText("Ваше имя:")
            code_l.setToolTip("Для разделения пользователей \nпри многопользовательском режиме")
            lo.addWidget(code_l)
            self.name_e = CustomEntry(w, padding=False)
            self.name_e.setFixedWidth(400)
            lo.addWidget(self.name_e, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText("E-mail:")
            code_l.setToolTip("Для уведомлений о крупных обновлениях")
            lo.addWidget(code_l)
            self.email_e = CustomEntry(w, padding=False)
            self.email_e.setFixedWidth(400)
            lo.addWidget(self.email_e, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText("Название компании:")
            code_l.setToolTip("Для статистики")
            lo.addWidget(code_l)
            self.company_e = CustomEntry(w, padding=False)
            self.company_e.setFixedWidth(400)
            lo.addWidget(self.company_e, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            self.passw_l = QtWidgets.QLabel(parent=self.centralwidget)
            self.passw_l.setFont(generate_font(10))
            self.passw_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.passw_l.setText("Придумайте пароль для входа в приложение:")
            self.passw_l.setStyleSheet("""
            margin:15 0 7 0;
            """)
            self.verticalLayout.addWidget(self.passw_l, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText("Пароль:")
            code_l.setToolTip("Может быть пустым")
            lo.addWidget(code_l)
            self.passw_e = CustomEntry(w, padding=False)
            self.passw_e.setFixedWidth(400)
            self.passw_e.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            lo.addWidget(self.passw_e, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText("Повторите пароль:")
            code_l.setToolTip("Может быть пустым")
            lo.addWidget(code_l)
            self.passw_2_e = CustomEntry(w, padding=False)
            self.passw_2_e.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.passw_2_e.setFixedWidth(400)
            lo.addWidget(self.passw_2_e, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            w, lo = create_w_lo(self.centralwidget, self.verticalLayout)
            code_l = QtWidgets.QLabel(parent=w)
            code_l.setText(" ")
            lo.addWidget(code_l)

            self.verticalLayout.addItem(get_v_spacer())
            activate_btn = DarkBtn_Ui(self.centralwidget, name="edit_proj")
            activate_btn.setText("   Создать пользователя")
            activate_btn.clicked.connect(lambda: self.save())
            self.verticalLayout.addWidget(activate_btn)

            MainWindow.setWindowTitle("ЛКМщик - Создание пользователя")

        else:
            self.main_window.set_state("entry")

    def save(self):
        update_config_param("name", self.name_e.text())
        update_config_param("email", self.email_e.text())
        update_config_param("company", self.company_e.text())

        passw1 = self.passw_e.text()
        passw2 = self.passw_2_e.text()
        if passw1 == passw2:
            update_config_param("password", "Hello, Интерлакокраска!", password=passw1)
            self.main_window.set_state("entry")
        else:
            self.passw_l.setText("Пароли не совпадают!")

    @staticmethod
    def check_created():
        with SqliteDict('configuration_') as mydict:
            return mydict.get("password", False)


class Ui_entry_w(object):
    def setupUi(self, MainWindow):
        self.main_window = MainWindow


        self.centralwidget = MainWindow.centralwidget
        self.verticalLayout: QtWidgets.QVBoxLayout = MainWindow.verticalLayout
        self.verticalLayout.setSpacing(15)

        name = get_config_param("name")

        if name.strip() != "":
            MainWindow.resize(250, 150)
            self.activ_l = QtWidgets.QLabel(parent=self.centralwidget)
            self.activ_l.setFont(generate_font(16))
            self.activ_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.activ_l.setStyleSheet("""
                        margin:5 0 5 0;
                        """)

            self.activ_l.setText(f"Добрый день, {name}")
            self.verticalLayout.addWidget(self.activ_l, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        else:
            MainWindow.resize(250, 125)

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setFont(generate_font(10))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setText("Для входа в приложение введите ваш пароль:")
        self.verticalLayout.addWidget(self.label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


        self.verticalLayout.addItem(get_v_spacer())
        w, lo = create_w_lo(self.centralwidget, self.verticalLayout)

        self.passw_e = CustomEntry(w, padding=False)
        self.passw_e.setMinimumSize(250, 32)
        self.passw_e.setMaximumWidth(250)
        self.passw_e.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        lo.addWidget(self.passw_e)
        #
        self.verticalLayout.addItem(get_v_spacer())
        activate_btn = DarkBtn_Ui(self.centralwidget, name="edit_proj")
        activate_btn.setText("   Войти")
        activate_btn.clicked.connect(lambda: self.enter())
        activate_btn.setShortcut("Return")
        self.verticalLayout.addWidget(activate_btn)
        MainWindow.setWindowTitle("ЛКМщик - Вход в приложение")

    def enter(self):
        name = get_config_param("name")
        company = get_config_param("company")
        email = get_config_param("email")

        try:
            from uuid import getnode as get_mac
            mac = get_mac()
        except:
            mac = "Не удалось определить"

        try:
            windows_name = os.getlogin()
        except:
            windows_name = "Не удалось определить"

        try:
            get_config_param("password", password=self.passw_e.text())
            # try:
            #     # f=logging&name=1&company=яыфв&email=фцу@sad.wq&mac=123123&windows_name=qweqw.qweqwфцв_
            #
            #     data_dict = {"f": "logging",
            #                  "name": name,
            #                  "company": company,
            #                  "email": email,
            #                  "mac": mac,
            #                  "windows_name": windows_name
            #                  }
            #     requests.get("http://лкмщик.рф/api_path", params=data_dict)
            #
            # except:
            #     logging.error("Не удалось подключиться к API")

            self.main_window.set_state("main")
            Secrets.password = self.passw_e.text()

        except Exception as e:
            self.label.setText("Введен неверный пароль")
            logging.info("Неверный пароль")

