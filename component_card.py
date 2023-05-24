import webbrowser

from PIL import Image, ImageColor
from PIL.ImageQt import ImageQt
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QImage, QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QWidget, QGridLayout, QFileDialog, QColorDialog

from common.ui_elements import generate_color
from database import DB
from settings import TABLE_DICT, get_category, get_lables, get_columns, get_desc


class ComponentCard(QWidget):
    def __init__(self, parent_window, category, btn_save_name='Сохранить', global_check=False):
        super().__init__()
        self.global_check = global_check
        self.parent_window = parent_window
        self.db = DB(global_check=global_check)
        self.category = category
        self.application_flg = False  # флаг наличия вкладки Применение
        self.passport_flg = False  # флаг наличия пасспорта безопасности
        self.list_save_btn = []
        self.setObjectName("Form")
        self.resize(537, 444)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=self)

        self.tabWidget.setObjectName("tabWidget")
        self.btn_save_name = btn_save_name
        self.load_structure()
        self.setWindowTitle("Добавление компонента - " + self.category_name)

        self.init_general_tab()
        if self.category != 'Producer':
            self.init_countable_tab()
        if self.passport_flg:
            self.init_pb_tab()
        if self.application_flg:
            self.init_application_tab()
        self.init_note_tab()

        self.horizontalLayout.addWidget(self.tabWidget)

        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def load_structure(self):
        self.category_name = {y: x for x, y in TABLE_DICT.items()}[self.category]

        labels, column, descript, numeric_flg, for_count_flg, _ = zip(*get_category(self.category, gloval_check=self.global_check))
        labels, column, descript, numeric_flg, for_count_flg, = list(labels), list(column), list(descript), list(
            numeric_flg), list(for_count_flg)
        list_params = [labels, column, descript, numeric_flg, for_count_flg]

        if "Применение" in labels:
            self.application_flg = True
            index = labels.index("Применение")

            for i in list_params:
                i.pop(index)

        if self.category != "Producer":
            self.passport_flg = True
            self.hexcolor = ""

        self.general_params = []
        general_columns = []
        self.countable_params = []
        countable_columns = []

        for i, count_flg in enumerate(for_count_flg):
            if count_flg:
                self.countable_params.append([labels[i], descript[i], numeric_flg[i], ])
                countable_columns.append(column[i])

            else:
                self.general_params.append([labels[i], descript[i], ])
                general_columns.append(column[i])

        self.countable_columns = ", ".join(countable_columns)
        self.general_columns = ", ".join(general_columns)

        self.pb_params = list(zip(get_lables("Passport"), get_desc("Passport")))
        self.pb_columns = ", ".join(get_columns("Passport", global_check=self.global_check))

    def init_general_tab(self):

        self.tab_w = QtWidgets.QWidget()
        self.tab_w.setObjectName("General")

        self.gridLayout = QtWidgets.QVBoxLayout(self.tab_w)

        self.scrollArea = QtWidgets.QScrollArea(parent=self.tab_w)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea{
            background: #f9f9f9;
            border: 0px solid black;
            }
        """)

        self.tab = QtWidgets.QWidget()
        # self.scrollArea.setGeometry(QtCore.QRect(0, 0, 700, 700))
        # self.tab.setGeometry(QtCore.QRect(0, 0, 700, 700))
        self.tab.setObjectName("scrollAreaWidgetContents")
        self.tab.setStyleSheet("""
            QWidget#scrollAreaWidgetContents{
            background: #f9f9f9;
            border: 0px solid black;
            }
        """)
        self.verticalLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.verticalLayout_2.setObjectName("gridLayout")

        self.scrollArea.setWidget(self.tab)

        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)

        if self.category != 'Producer':
            self.widget_buttons = QtWidgets.QWidget(parent=self.tab_w)
            self.widget_buttons.setObjectName("buttonArea")
            self.widget_buttons.setContentsMargins(10, 10, 10, 0)
            self.widget_buttons.setStyleSheet("""
            QWidget#buttonArea{
                margin: 0;
                 background: #f9f9f9;
                border: 0px solid #999;

            }
            """)
            self.horizontalLayout_widget_buttons = QtWidgets.QGridLayout(self.widget_buttons)
            self.horizontalLayout_widget_buttons.setContentsMargins(-1, 0, -1, 0)
            self.horizontalLayout_widget_buttons.setObjectName("horizontalLayout_2")
            self.tds_btn = QtWidgets.QPushButton(parent=self.widget_buttons)
            self.tds_btn.clicked.connect(lambda: self.open_tds(self.tds_entry.text()))
            self.horizontalLayout_widget_buttons.addWidget(self.tds_btn, 0, 0, 1, 1)
            self.www_btn = QtWidgets.QPushButton(parent=self.widget_buttons)
            self.horizontalLayout_widget_buttons.addWidget(self.www_btn, 0, 1, 1, 1)
            self.email_btn = QtWidgets.QPushButton(parent=self.widget_buttons)
            self.horizontalLayout_widget_buttons.addWidget(self.email_btn, 0, 2, 1, 1)
            self.color_btn = QtWidgets.QPushButton(parent=self.widget_buttons)
            self.color_btn.clicked.connect(lambda event: self.set_color())
            self.color_btn.setIcon(QtGui.QIcon("images/black_white_background.png"))
            self.horizontalLayout_widget_buttons.addWidget(self.color_btn, 0, 3, 1, 1)
            self.gridLayout.addWidget(self.widget_buttons)
            self.tds_btn.setText("ТДС")
            self.www_btn.setText("Сайт поставщика")
            self.email_btn.setText("EMail")
            self.color_btn.setText(" Выбрать цвет")
            self.tds_btn.setDisabled(True)
            self.www_btn.setDisabled(True)
            self.email_btn.setDisabled(True)
            self.manager_label = QtWidgets.QLabel(parent=self.widget_buttons)
            self.phone_label = QtWidgets.QLabel(parent=self.widget_buttons)

        self.gridLayout.addWidget(self.scrollArea)
        self.row_widget_general = QtWidgets.QWidget(parent=self.tab)
        self.row_widget_general.setObjectName("widget_2")
        self.gridLayout_row_widget_general = QtWidgets.QGridLayout(self.row_widget_general)

        self.list_general_entry = self.draw_rows(self.row_widget_general, self.gridLayout_row_widget_general,
                                                 self.general_params)

        self.verticalLayout_2.addWidget(self.row_widget_general)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)

        self.add_save_button(self.tab_w, self.gridLayout, space=False)

        self.tabWidget.addTab(self.tab_w, "Общие")

    def init_countable_tab(self):
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_countable = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_countable.setContentsMargins(0, 9, 0, -1)
        self.verticalLayout_countable.setSpacing(0)
        self.row_widget_countable = QtWidgets.QWidget(parent=self.tab_2)
        self.gridLayout_row_widget_countable = QtWidgets.QGridLayout(self.row_widget_countable)

        self.verticalLayout_countable.addWidget(self.row_widget_countable)

        self.list_count_entry = self.draw_rows(self.row_widget_countable, self.gridLayout_row_widget_countable,
                                               self.countable_params)

        self.add_save_button(self.tab_2, self.verticalLayout_countable, space=True)

        self.tabWidget.addTab(self.tab_2, "Расчетные параметры")

    def init_pb_tab(self):
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_pb = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_pb.setContentsMargins(0, 9, 0, -1)
        self.verticalLayout_pb.setSpacing(0)
        self.row_widget_pb = QtWidgets.QWidget(parent=self.tab_3)
        self.gridLayout_row_widget_pb = QtWidgets.QGridLayout(self.row_widget_pb)

        self.verticalLayout_pb.addWidget(self.row_widget_pb)
        self.list_pb_entry = self.draw_rows(self.row_widget_pb, self.gridLayout_row_widget_pb, self.pb_params)
        self.add_save_button(self.tab_3, self.verticalLayout_pb, space=True)
        self.tabWidget.addTab(self.tab_3, "Паспорт безопасности")

    def init_application_tab(self):
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 9)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.application_text_area = QtWidgets.QTextEdit(parent=self.tab_4)
        self.verticalLayout_3.addWidget(self.application_text_area)

        self.add_save_button(self.tab_4, self.verticalLayout_3)

        self.tabWidget.addTab(self.tab_4, "Применение")

    def init_note_tab(self):
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout.setContentsMargins(0, 0, 0, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.note_text_area = QtWidgets.QTextEdit(parent=self.tab_5)
        self.verticalLayout.addWidget(self.note_text_area)

        self.add_save_button(self.tab_5, self.verticalLayout)
        self.tabWidget.addTab(self.tab_5, "Заметки")

    def draw_rows(self, parent: QWidget, gridLayout: QGridLayout, list_params: list):
        dict_objects = {}
        for i, param in enumerate(list_params):
            name = param[0]
            desc = param[1]
            countable_flg = False
            if len(param) > 2:
                is_numeric = param[2]
                countable_flg = True
                reg_ex = QRegularExpression(r"[0-9]*[\,,.]{1}[0-9]*")
                validator = QRegularExpressionValidator(reg_ex)

            label = QtWidgets.QLabel(parent=parent)
            label.setText(name)
            gridLayout.addWidget(label, i, 0, 1, 1)

            if name == "Ссылка на ТДС":
                dict_objects[name] = CustomEntry(parent)
                self.tds_entry = dict_objects[name]
                self.tds_entry.textChanged.connect(self.check_tds_param)
                gridLayout.addWidget(dict_objects[name], i, 1, 1, 1)
                btn = QtWidgets.QPushButton(parent=parent)
                btn.setText("...")
                btn.clicked.connect(lambda event, entry=dict_objects[name]: self.open_file_dialog(entry))
                gridLayout.addWidget(btn, i, 1, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                btn.setStyleSheet("""
                QPushButton{
                border: 1px;
                background: #eeedeb;
                padding: 1px 10px;
                border-radius: 5px;
                margin: 0 5px 0 0;
                }
                QPushButton:hover{

                background: #999;

                }
                """)
                btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

            elif name == "Поставщик" and self.category != 'Producer':
                dict_objects[name] = CustomCombobox(parent=parent)
                self.provider_entry = dict_objects[name]
                gridLayout.addWidget(dict_objects[name], i, 1, 1, 1)
                dict_objects[name].currentTextChanged.connect(self.check_contact_params)
                dict_objects[name].addItem("")
                dict_objects[name].setEditable(True)

                for text in self.db.load_reactives("Producer", "provider"):
                    dict_objects[name].addItem(text[0])

            elif isinstance(desc, list):
                dict_objects[name] = CustomCombobox(parent=parent)
                gridLayout.addWidget(dict_objects[name], i, 1, 1, 1)
                dict_objects[name]._type = "Валюта"
                if name != 'Валюта':
                    dict_objects[name].addItem("")
                    dict_objects[name].setEditable(True)

                for text in desc:
                    dict_objects[name].addItem(text)
            else:
                dict_objects[name] = CustomEntry(parent)
                dict_objects[name].setPlaceholderText(desc)
                if countable_flg:
                    if is_numeric:
                        dict_objects[name].setValidator(validator)
                gridLayout.addWidget(dict_objects[name], i, 1, 1, 1)

        return dict_objects

    def add_save_button(self, parent, layout, /, *coord, space=False):
        if space:
            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                               QtWidgets.QSizePolicy.Policy.Expanding)
            layout.addItem(spacerItem)

        save_btn = QtWidgets.QPushButton(parent=parent)
        save_btn.setText(self.btn_save_name)
        save_btn.clicked.connect(self.save_data)
        save_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        save_btn.setStyleSheet("""
        
        QPushButton{
          padding: 10px;

        }
  
        
        """)
        layout.addWidget(save_btn, *coord)
        self.list_save_btn.append(save_btn)

    def save_data(self):
        concat_columns = self.general_columns
        if self.category != 'Producer':
            concat_columns += ", " + self.countable_columns
        if self.passport_flg:
            concat_columns += ", " + self.pb_columns

        list_values = []
        for i in self.general_params:
            name = i[0]
            value = self.list_general_entry[name].text()
            list_values.append(value)

        for i in self.countable_params:
            name = i[0]
            value = self.list_count_entry[name].text()
            list_values.append(value)

        if self.passport_flg:
            for i in self.pb_params:
                name = i[0]
                value = self.list_pb_entry[name].text()
                list_values.append(value)

        if self.application_flg:
            concat_columns += ", application"
            list_values.append(self.application_text_area.toPlainText())

        concat_columns += ", note"
        list_values.append(self.note_text_area.toPlainText())

        if self.category != 'Producer':
            concat_columns += ", hexcolor"
            list_values.append(self.hexcolor)

        self.concat_columns = concat_columns
        self.list_values = list_values
        self.exec_db_update()

    def exec_db_update(self):

        check_unic = self.db.new_insert_data(self.category, self.concat_columns, self.list_values)

        if check_unic:
            self.parent_window.select_category(self.category)
            self.destroy()
        else:
            for btn in self.list_save_btn:
                btn.setText(f"{self.btn_save_name} - Название или шифр неуникальны")

    def open_tds(self, path):
        if len(path) > 5:
            webbrowser.open_new(rf"{path}")

    def check_contact_params(self):
        provider: str = self.provider_entry.text()
        group = "Producer"
        columns = "email, site, manager, phone"
        request = "provider = ?"
        result = self.db.search_records(columns, group, (provider,), request)

        to_disable_email = True
        to_disable_site = True
        to_disable_manager = True
        to_disable_phone = True
        if len(result) > 0:
            email: str = result[0][0]
            site: str = result[0][1]
            manager: str = result[0][2]
            phone: str = result[0][3]
            if email.count("@") > 0:
                self.email_btn.clicked.connect(lambda event, _email=email: webbrowser.open_new(rf"mailto:{_email}"))
                to_disable_email = False
            if len(site) > 5:
                self.www_btn.clicked.connect(lambda event, _site=site: webbrowser.open_new(rf"{_site}"))
                to_disable_site = False
            if len(manager) > 1:
                self.manager_label.setText(f"Менеджер: {manager}")
                self.horizontalLayout_widget_buttons.addWidget(self.manager_label, 1, 0, 1, 4,
                                                               alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
                to_disable_manager = False
            if len(phone) > 2:
                self.phone_label.setText(f"Телефон: {phone}")
                self.horizontalLayout_widget_buttons.addWidget(self.phone_label, 2, 0, 1, 4,
                                                               alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
                to_disable_phone = False
        self.horizontalLayout_widget_buttons.update()
        self.email_btn.setDisabled(to_disable_email)
        self.www_btn.setDisabled(to_disable_site)
        if to_disable_manager: self.horizontalLayout_widget_buttons.removeWidget(self.manager_label)
        if to_disable_phone: self.horizontalLayout_widget_buttons.removeWidget(self.phone_label)

    def open_file_dialog(self, goal_entry: QtWidgets.QLineEdit):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.fileMode(dialog).AnyFile)
        dialog.setViewMode(QFileDialog.viewMode(dialog).Detail)

        if dialog.exec():
            fileNames = dialog.selectedFiles()
            goal_entry.setText(fileNames[0])

    def check_tds_param(self):
        text = self.tds_entry.text()
        if len(text) > 5:
            self.tds_btn.setEnabled(True)
        else:
            self.tds_btn.setEnabled(False)

    def set_color(self, hexcolor=None):
        if hexcolor is None:
            col = QColorDialog.getColor(options=QColorDialog.ColorDialogOption.ShowAlphaChannel, title="Выбор цвета")
            if col.isValid():
                hexcolor = col.name(QColor.NameFormat.HexArgb)
            else:
                return

        # self.color_icon.setPixmap(QtGui.QPixmap(QImage(ImageQt(self.generate_color(hexcolor)))))
        self.color_btn.setIcon(QIcon(QtGui.QPixmap(generate_color(hexcolor))))
        self.hexcolor = hexcolor


class EditComponentCard(ComponentCard):
    def __init__(self, parent_window, category, name, global_check=False):
        if global_check:
            btn_save_name = "Добавить к себе"
        else:
            btn_save_name = "Редактировать"

        super(EditComponentCard, self).__init__(parent_window, category, btn_save_name=btn_save_name, global_check=global_check)
        self.name = name
        self.load_data(name)
        self.setWindowTitle(f"{self.category_name} - {name}")

    def load_data(self, name):
        request = "name = ?" if self.category != "Producer" else "provider = ?"
        global_values = self.db.search_records(self.general_columns, self.category, (name,), request)[0]
        for i, (_name, _) in enumerate(self.general_params):
            self.list_general_entry[_name].setText(global_values[i])

        if self.category != "Producer":
            countable_values = self.db.search_records(self.countable_columns, self.category, (name,), request)[0]

            for i, (_name, _, _) in enumerate(self.countable_params):
                self.list_count_entry[_name].setText(countable_values[i])

            if not self.global_check:
                hexcolor = self.db.search_records("hexcolor", self.category, (name,), "name = ?")[0][0]
                if len(hexcolor) > 6:
                    self.set_color(hexcolor=hexcolor)
                else:
                    self.hexcolor = ""
            else:
                self.hexcolor = ""

        if self.passport_flg:
            passport_values = self.db.search_records(self.pb_columns, self.category, (name,), request)[0]
            for i, (_name, _) in enumerate(self.pb_params):
                self.list_pb_entry[_name].setText(passport_values[i])

        if self.application_flg:
            application = self.db.search_records("application", self.category, (name,), request)[0][0]
            self.application_text_area.insertPlainText(application)

        note = self.db.search_records("note", self.category, (name,), request)[0][0]
        self.note_text_area.insertPlainText(note)

    def exec_db_update(self):
        if self.global_check:
            check_unic = self.db.insert_data_glob(self.category, self.concat_columns, self.name, self.list_values)
        else:
            self.concat_columns = self.concat_columns.replace(", ", " = ?, ") + " = ?"
            check_unic = self.db.new_update_record(self.category, self.concat_columns, self.name, self.list_values)

        if check_unic:
            self.parent_window.select_category(self.category)
            self.destroy()
        else:
            for btn in self.list_save_btn:
                btn.setText(f"{self.btn_save_name} - Название или шифр неуникальны")


class CustomCombobox(QtWidgets.QComboBox):
    def __init__(self, parent, _type=None):
        super(CustomCombobox, self).__init__(parent=parent)
        self._type = _type
        self.wheelEvent = lambda event: None
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""

                QComboBox {
                  border-bottom: 1px solid #aaa;
                  border-right: 1px solid #aaa;
                  border-radius: 2px;

          padding: 2px 5px;
                }
                QComboBox:focus {
                     border-bottom: 1px solid #209fa6;
                     border-right: 1px solid #209fa6;
                }
                 QComboBox:hover{

                 }
                 QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 30px;
                    cursor: pointer;
                    border-left-width: 0px;
                    border-left-color: darkgray;
                    border-left-style: solid; /* just a single line */
                    border-top-right-radius: 3px; /* same radius as the QComboBox */
                    border-bottom-right-radius: 3px;
}
QComboBox::down-arrow {
    image: url(images/arrow.png);
}

QComboBox::down-arrow:on { /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}
                """)

    def text(self):
        return self.currentText()

    def setText(self, text):
        if self.isEditable():
            self.setEditText(text)
        elif self._type == "Валюта":
            if text == "$":
                self.setCurrentIndex(1)
            elif text == "€":
                self.setCurrentIndex(2)
            else:
                self.setCurrentIndex(0)


class CustomEntry(QtWidgets.QLineEdit):
    def __init__(self, parent, padding=True):
        super(CustomEntry, self).__init__(parent=parent)
        padding = "padding-right:30px;" if padding else ""
        self.setStyleSheet("""
        
        QLineEdit {{
          border-bottom: 1px solid #aaa;
           border-right: 1px solid #aaa;
          border-radius: 2px;
          padding: 2px 5px;
           {}
                   }}
        QLineEdit:focus {{
             border-bottom: 1px solid #209fa6;
             border-right: 1px solid #209fa6;
        }}
         QLineEdit:hover{{
         
         }}
        
        """.format(padding))
