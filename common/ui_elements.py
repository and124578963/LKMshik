import copy
import os
from decimal import Decimal
from typing import List, Tuple

import ncs
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, QRegularExpression, Qt, QSize, QRect, QModelIndex
from PyQt5.QtGui import QImage, QFont, QRegularExpressionValidator, QIcon, QColor
from PIL import Image, ImageColor
from PIL.ImageQt import ImageQt, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QCompleter, QColorDialog

import sys
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy.optimize import curve_fit
from skimage import color as color_kit

BASE_DIR = os.path.dirname(__file__).rstrip("common").replace("\\", "/")


class HoverableButton(QtWidgets.QPushButton):
    hover = QtCore.pyqtSignal(str)

    def __init__(self, parent, _type, size):
        super(HoverableButton, self).__init__(parent=parent)
        self.click_event = None
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        tooltip_dict = {
            "plus": "Добавить строку",
            "plus_2": "Добавить строку",
            "minus": "Удалить строку",
            "minus_2": "Удалить строку",
            "save": "Сохранить",
            "save_as": "Сохранить как",
            "word": "Создать Word-файл",
            "del_rec": "Удалить рецептуру",
            "swap": "Доп. действия над компонентом",
            "2k": "Показать второй компонент",
            "settings": "Настройки расчета",
            "menu": "Дополнительные действия",
            "swap_r": "",
        }
        self.setToolTip(tooltip_dict[_type])

        img_dict = {
            "plus": ["images/plus.png", "images/plus-on.png"],
            "plus_2": ["images/plus.png", "images/plus-on.png"],
            "minus": ["images/minus.png", "images/minus-on.png"],
            "minus_2": ["images/minus_2.png", "images/minus-on.png"],
            "save": ["images/save.png", "images/save-on.png"],
            "save_as": ["images/save_as.png", "images/save_as-on.png"],
            "word": ["images/word.png", "images/word-on.png"],
            "del_rec": ["images/del_rec.png", "images/del_rec-on.png"],
            "swap": ["images/swap_v.png", "images/swap_v.png"],
            "2k": ["images/2K.png", "images/2K-on.png"],
            "settings": ["images/settings_btn.png", "images/settings_btn-on.png"],
            "menu": ["images/menu.png", "images/menu-on.png"],
            "swap_r": ["images/swap_icon.png", "images/swap_icon-on.png"],
        }
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(os.path.join(BASE_DIR, img_dict[_type][0])), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_on = QtGui.QIcon()
        self.icon_on.addPixmap(QtGui.QPixmap(os.path.join(BASE_DIR, img_dict[_type][1])), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_off = self.icon
        self.setIcon(self.icon)
        x, y = size
        x = int(x * 1.5)
        y = int(y * 1.5)

        self.setIconSize(QtCore.QSize(x, y))
        additional = "padding-top: 7px;" if _type not in ["plus", "minus"] else ""
        self.setStyleSheet("""
                 QPushButton {
            border: 0px;
             color: rgb(27, 37, 36);
             """ + additional + """            
            }
            QPushButton::pressed {
            padding-bottom: 0px;
            padding-right: 0px;
            }
            QWidget{
            padding-bottom: 2px;
            padding-right: 2px;
            }
            QPushButton::menu-indicator { image: none; }
                """)

    def enterEvent(self, event):
        self.hover.emit("enterEvent")
        self.setIcon(self.icon_on)
        super(HoverableButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self.hover.emit("leaveEvent")
        self.setIcon(self.icon)
        super(HoverableButton, self).leaveEvent(event)

    def set_pressed(self):
        if self.icon_off is self.icon:
            self.icon = self.icon_on
            self.setIcon(self.icon)
        else:
            self.icon = self.icon_off
            self.setIcon(self.icon)


class DragHoverableButton(QtWidgets.QLabel):
    hover = QtCore.pyqtSignal(str)
    def __init__(self, parent, _type, size, move_area_obj):
        super(DragHoverableButton, self).__init__(parent)
        self.move_area_obj = move_area_obj

        x, y = size
        x = int(x * 1.5)
        y = int(y * 1.5)

        self.pixmap = QPixmap(os.path.join(BASE_DIR, "images/swap_icon.png")).scaled(x, y, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                                                 transformMode=Qt.TransformationMode.SmoothTransformation)
        self.pixmap_on = QPixmap(os.path.join(BASE_DIR, "images/swap_icon-on.png")).scaled(x,y,
                                                                       aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                                                                       transformMode=Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(self.pixmap)

    def enterEvent(self, event):
        self.hover.emit("enterEvent")
        self.setPixmap(self.pixmap_on)
        # self.setIcon(self.icon_on)
        self.move_area_obj.acceptMove = True
        super(DragHoverableButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self.hover.emit("leaveEvent")
        # self.setIcon(self.icon)
        self.setPixmap(self.pixmap)
        self.move_area_obj.acceptMove = False
        super(DragHoverableButton, self).leaveEvent(event)

    # def mousePressEvent(self, event: QtGui.QMouseEvent):
    #     self.move_area_obj.mousePressEvent(event)

    # def mouseMoveEvent(self, event):
    #     self.move_area_obj.mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     self.move_area_obj.mouseReleaseEvent(event)
    #
    # def dragEnterEvent(self, event):
    #     self.move_area_obj.dragEnterEvent(event)
    #
    # def dropEvent(self, event: QtGui.QMouseEvent):
    #     self.move_area_obj.dropEvent(event)


class CustomTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent, type):
        super(CustomTextEdit, self).__init__(parent=parent)
        if type == "white":
            self.setStyleSheet("""

           QTextEdit {
           background: white;
           border: 0px solid white;
                      }
           QTextEdit:focus {
                 background: white;
           }
            QLineEdit:hover{
        background: white;
            }

           """)
        elif type == "comment":
            self.setFixedHeight(49)
            self.setStyleSheet("""
                    QTextEdit {
                    border-bottom: 1px solid #aaa;
                    border-right: 1px solid #aaa;
                    border-radius: 2px;
                    }
                    QTextEdit:focus {
                    border-bottom: 1px solid #209fa6;
                    border-right: 1px solid #209fa6;
                    }
                    QLineEdit:hover{
                    }
                    """)


class ColorButton(QtWidgets.QPushButton):
    def __init__(self, parent: QtWidgets.QWidget, color: str):
        super(ColorButton, self).__init__(parent=parent)
        dict_btn_color = {
            "blue": "#3f768d",
        }
        self.setSizeIncrement(QtCore.QSize(0, 0))
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.setObjectName(color)
        self.setStyleSheet("""
                QPushButton{{
                  color: #555;
                  font-weight: 700;
                  text-decoration: none;
                  padding: .3em 1em;
                  outline: none;
                  border: 1px solid #ddd;
                  border-radius: 0px;
                  transition: 0.3s;
                  background: #eee;
                }}
                
                QPushButton:hover {{
                color: #fff;
          background: {0};
          border: 1px solid #ddd;
         }}
        QPushButton:pressed  {{
        border: 2px solid {0};
          }}
          QPushButton::menu-indicator {{ image: none; }}
                """.format(dict_btn_color.get(color, "blue")))


class CustomCombobox(QtWidgets.QComboBox):
    def __init__(self, parent, _type=None):
        super(CustomCombobox, self).__init__(parent=parent)
        self._type = _type
        self.wheelEvent = lambda event: None
        self.setMinimumSize(350, 32)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""

                QComboBox {{
                  border-bottom: 1px solid #aaa;
                  border-right: 1px solid #aaa;
                  border-radius: 2px;

          padding: 2px 5px;
                }}
                QComboBox:focus {{
                     border-bottom: 1px solid #209fa6;
                     border-right: 1px solid #209fa6;
                }}
                 QComboBox:hover{{

                 }}
                 QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 30px;
                    cursor: pointer;
                    border-left-width: 0px;
                    border-left-color: darkgray;
                    border-left-style: solid; /* just a single line */
                    border-top-right-radius: 3px; /* same radius as the QComboBox */
                    border-bottom-right-radius: 3px;
}}
QComboBox::down-arrow {{
    image: url({});
}}
QComboBox::down-arrow:on {{ /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}}
                """.format(BASE_DIR.replace("\\","/") + "/images/arrow.png"))

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
        self.setMinimumSize(250, 32)
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


class CustomMenu(QtWidgets.QMenu):
    def __init__(self, parent):
        super(CustomMenu, self).__init__(parent)
        self.setStyleSheet(
            """
            QMenu
            {
                font: 12pt;
                background-color: #f2f2f2;
            }
            QMenu::item{
            background-color: #f2f2f2;
            }
            QMenu::item:selected
            {
                background-color: #3f768d
            }
            """
        )


class MenuButton(HoverableButton):
    def __init__(self, parent, _type, size):
        super(MenuButton, self).__init__(parent, _type, size)

    # def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
    #     super(MenuButton, self).mouseDoubleClickEvent(a0)
    #     self.showMenu()
    #

    # def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
    #     # super(MenuButton, self).mousePressEvent(e)
    #     pass

    # def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
    #     super(MenuButton, self).contextMenuEvent(a0)
    #


class CustomRadioBtn(QtWidgets.QRadioButton):
    def __init__(self, color):
        super(CustomRadioBtn, self).__init__()
        color_dict = {
            "red": ["images/radioButton/rb-red.png", "images/radioButton/rb-red-true.png"],
            "green": ["images/radioButton/rb-green.png", "images/radioButton/rb-green-true.png"],
            "grey": ["images/radioButton/rb-grey.png", "images/radioButton/rb-grey-true.png"],
        }
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(
            """

QRadioButton::indicator {{
                width:20px;height:20px;
                border-radius:0px;
                }}
QRadioButton::indicator:checked {{border-image: url({1});}}
QRadioButton::indicator:unchecked {{border-image: url({0});}}
                
""".format(BASE_DIR.replace("\\","/") + "/" + color_dict[color][0],
            BASE_DIR.replace("\\","/") + "/" + color_dict[color][1])
        )


class CustomListItem(QtWidgets.QListView):
    def __init__(self, parent):
        super(CustomListItem, self).__init__(parent=parent)
        self.setAlternatingRowColors(True)
        self.setMouseTracking(True)
        self.setStyleSheet("""
        QListView {
        	background-color: white;
            border: 0px;
            margin-top: 5px;
            outline: 0;
            font: 600 10pt "Segoe UI Semibold";

        }

        QListView::item {
            border: 0px;
            padding: 6px 10px 6px 10px;

        }

        QListView::item:selected {
            padding: 6px 10px 6px 20px;
        	border:none;
        	color: black;
        	background:qlineargradient(spread:pad, x1:0.989, y1:0.494, x2:0, y2:0.506, stop:0 rgba(0, 0, 0, 0), stop:0.4375 rgba(255, 224, 58, 20), stop:0.755682 rgba(255, 224, 58, 66), stop:1 rgba(255, 224, 58, 255));
        }
        QListView::item:alternate:selected{
            padding: 6px 10px 6px 20px;
        	border:none;
        	color: black;
        	background:qlineargradient(spread:pad, x1:0.989, y1:0.494, x2:0, y2:0.506, stop:0 rgba(0, 0, 0, 0), stop:0.4375 rgba(255, 224, 58, 20), stop:0.755682 rgba(255, 224, 58, 66), stop:1 rgba(255, 224, 58, 255));
        }
        QListView::item:focus{border:none;}

        QListView::item:alternate {
        	background: #eeedeb;

        }

         /* Mouse County floats on the entry */
        QListView::item::hover {
        	background:qlineargradient(spread:pad, x1:0.989, y1:0.494, x2:0, y2:0.506, stop:0 rgba(0, 0, 0, 0), stop:0.4375 rgba(255, 224, 58, 20), stop:0.755682 rgba(255, 224, 58, 66), stop:1 rgba(255, 224, 58, 255));

        }

                """)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def set_list_elements(self, list_strings: List[str]):
        self.list_strings = list_strings
        self.listModel = QStringListModel()
        self.listModel.setStringList(self.list_strings)
        self.setModel(self.listModel)

    def change_selected(self, name):
        name = 'Тарировочные кривые' if name == "Тарировочные_кривые" else name
        self.reset()
        if name in self.list_strings:
            index = self.list_strings.index(name)
        else:
            index = -1
        self.setCurrentIndex(self.listModel.index(index))


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=5, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set(facecolor='#f9f9f9')
        self.axes = self.fig.add_subplot(111)
        self.axes.set(facecolor='white')
        self.fig.subplots_adjust(left=0.12, bottom=0.12, right=0.95, top=0.95)
        super(MplCanvas, self).__init__(self.fig)

    def curve_fit(self, *args):
        popt, _ = curve_fit(*args)
        return popt

    def exponenta(self, x, a, b, c, d, e):
        # print(x, a, b, c)
        return a * np.float_power(x, 4) + b * np.float_power(x, 3) + c * np.float_power(x, 2) \
               + d * np.float_power(x, 1) + e


class ChoiceColor(QtWidgets.QWidget):
    def __init__(self, parent, callback_color):
        super(ChoiceColor, self).__init__()
        self.parent_window = parent
        self.color = None
        self.callback_color = callback_color
        self.resize(287, 237)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.tabWidget = QtWidgets.QTabWidget(parent=self)
        set_window_icon(self)

        self.ral_tab = QtWidgets.QWidget()
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.ral_tab)
        ral_label = QtWidgets.QLabel(parent=self.ral_tab)
        ral_label.setText("Выбрать RAL:")
        self.verticalLayout_3.addWidget(ral_label)
        self.comboBox_ral = CustomCombobox(self.ral_tab)
        self.ral_list = self.get_RAL_list()
        self.comboBox_ral.addItem("")
        for ral in self.ral_list:
            self.comboBox_ral.addItem(QIcon(QtGui.QPixmap(generate_color(ral[1]))), ral[0])
        self.comboBox_ral.currentIndexChanged.connect(lambda: self.set_ral_color())
        self.verticalLayout_3.addWidget(self.comboBox_ral)
        self.verticalLayout_3.addItem(get_v_spacer())
        fix_tab_bg(self.ral_tab)
        self.tabWidget.addTab(self.ral_tab, "RAL")

        self.ncs_tab = QtWidgets.QWidget()
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.ncs_tab)
        label_ncs = QtWidgets.QLabel(parent=self.ncs_tab)
        label_ncs.setText("Выбрать NCS")
        self.verticalLayout_4.addWidget(label_ncs)
        self.comboBox_ncs = CustomEntry(self.ncs_tab)
        self.comboBox_ncs.textChanged.connect(lambda :self.set_ncs_color())
        list_all_ncs_names = [i.name for i in ncs.all()]
        self.list_all_ncs_names = set(list_all_ncs_names)
        completer = QCompleter(self.list_all_ncs_names)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.comboBox_ncs.setCompleter(completer)
        self.update()
        self.verticalLayout_4.addWidget(self.comboBox_ncs)
        self.verticalLayout_4.addItem(get_v_spacer())
        fix_tab_bg(self.ncs_tab)
        self.tabWidget.addTab(self.ncs_tab, "NCS")

        self.lab_tab = QtWidgets.QWidget()
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.lab_tab)
        lab_label = QtWidgets.QLabel(parent=self.lab_tab)
        lab_label.setText("Указать Lab:")
        self.verticalLayout_5.addWidget(lab_label)
        w, lo = create_w_lo(self.lab_tab, self.verticalLayout_5)
        label = QtWidgets.QLabel(w)
        label.setText("L (0...100):")
        lo.addWidget(label)
        self.lab_L_e = CustomEntry(w, padding=False)
        self.lab_L_e.setValidator(get_numeric_validator())
        self.lab_L_e.textChanged.connect(lambda : self.set_lab_color())
        lo.addWidget(self.lab_L_e)

        w, lo = create_w_lo(self.lab_tab, self.verticalLayout_5)
        label = QtWidgets.QLabel(w)
        label.setText("a (-128...127):")
        lo.addWidget(label)
        self.lab_a_e = CustomEntry(w, padding=False)
        self.lab_a_e.setValidator(get_numeric_validator(minus=True))
        self.lab_a_e.textChanged.connect(lambda: self.set_lab_color())
        lo.addWidget(self.lab_a_e)

        w, lo = create_w_lo(self.lab_tab, self.verticalLayout_5)
        label = QtWidgets.QLabel(w)
        label.setText("b (-128...127):")
        lo.addWidget(label)
        self.lab_b_e = CustomEntry(w, padding=False)
        self.lab_b_e.setValidator(get_numeric_validator(minus=True))
        self.lab_b_e.textChanged.connect(lambda: self.set_lab_color())
        lo.addWidget(self.lab_b_e)

        self.verticalLayout_5.addItem(get_v_spacer())
        fix_tab_bg(self.lab_tab)
        self.tabWidget.addTab(self.lab_tab, "LAB")

        self.rgb_tab = QtWidgets.QWidget()
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.rgb_tab)
        self.rgb_button = ColorButton(self.rgb_tab, color="blue")
        self.rgb_button.setText("Выбрать RGB")
        self.rgb_button.clicked.connect(lambda:self.set_rgb_color())
        self.verticalLayout_6.addWidget(self.rgb_button)
        fix_tab_bg(self.rgb_tab)
        self.tabWidget.addTab(self.rgb_tab, "RGB")

        self.verticalLayout.addWidget(self.tabWidget)

        self.common_w = QtWidgets.QWidget(parent=self)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.common_w)
        label_color = QtWidgets.QLabel(parent=self.common_w)
        label_color.setText("Выбрано:")
        label_color.setFont(generate_font(12))
        self.verticalLayout_2.addWidget(label_color)
        self.color_l = QtWidgets.QLabel(parent=self.common_w)
        image = QtGui.QPixmap(generate_color("#00000000"))
        self.color_l.setPixmap(image)
        self.color_l.setMaximumSize(QSize(99, 99))
        self.color_l.setStyleSheet("""
                QLabel{
                border: 1px solid #ddd;
                }
                """)
        self.verticalLayout_2.addWidget(self.color_l, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.button = ColorButton(self.common_w, color="blue")
        self.button.setText("Сохранить цвет")
        self.button.clicked.connect(lambda : self.save_color())
        self.verticalLayout_2.addWidget(self.button)
        self.verticalLayout.addWidget(self.common_w)

        self.tabWidget.setCurrentIndex(0)

        self.setWindowTitle("Выбрать цвет")

    def closeEvent(self, event):
        self.parent_window.choice_color_window = None

    def save_color(self):
        self.callback_color(self.color)
        self.closeEvent(None)
        self.destroy()

    @staticmethod
    def get_RAL_list():
        with open(os.path.join(BASE_DIR, 'files/RALcolor'), 'r') as ral_file:
            ral_str = ral_file.read().split("\n")
            list_ral = []
            for line in ral_str:
                line = line.strip()
                columns = line.split()
                number = columns[0]
                a = "FF"
                r = hex(int(columns[1])).split("x")[-1]
                r = r if len(r) == 2 else "0" + r
                g = hex(int(columns[2])).split("x")[-1]
                g = g if len(g) == 2 else "0" + g
                b = hex(int(columns[3])).split("x")[-1]
                b = b if len(b) == 2 else "0" + b
                argb = "#" + a + r + g + b
                # print(f"r:{r}-{columns[1]} g:{g}-{columns[2]} b:{b}-{columns[3]}  argb:{argb}")

                name = columns[4]
                list_ral.append((f"{number} - {name}", argb))

        return list_ral

    def set_ncs_color(self):
        text = self.comboBox_ncs.text()
        if text in self.list_all_ncs_names:
            ncs_hex = ncs.get(name=text).hex.replace("#", "")
            argb = "#FF" + ncs_hex
            image = QtGui.QPixmap(generate_color(argb))
            self.color_l.setPixmap(image)
            self.color = argb

    def set_lab_color(self):
        L = self.lab_L_e.text() if self.lab_L_e.text() not in ["", "-"] else "0"
        a = self.lab_a_e.text() if self.lab_a_e.text() not in ["", "-"]  else "0"
        b = self.lab_b_e.text() if self.lab_b_e.text() not in ["", "-"]  else "0"
        L = float(L.replace(",", "."))
        if L > 100:
            self.lab_L_e.setText("100")
            L = 100
        if L < 0:
            self.lab_L_e.setText("0")
            L = 0

        a = float(a.replace(",", "."))
        if a > 127:
            self.lab_a_e.setText("127")
            a = 127
        if a < -128:
            self.lab_a_e.setText("-128")
            a = -128

        b = float(b.replace(",", "."))
        if b > 127:
            self.lab_b_e.setText("127")
            a = 127
        if b < -128:
            self.lab_b_e.setText("-128")
            b = -128
        rgb = color_kit.lab2rgb(np.array([L, a, b]))
        rgb = rgb * 255
        tuple1 = (int(round(rgb[0])), int(round(rgb[1])), int(round(rgb[2])))
        hex1 = '%02x%02x%02x' % tuple1
        argb = "#FF" + hex1
        image = QtGui.QPixmap(generate_color(argb))
        self.color_l.setPixmap(image)
        self.color = argb

    def set_rgb_color(self):
        col = QColorDialog.getColor(options=QColorDialog.ColorDialogOption.ShowAlphaChannel, title="Выбор цвета")
        if col.isValid():
            argb = col.name(QColor.NameFormat.HexArgb)
            image = QtGui.QPixmap(generate_color(argb))
            self.color_l.setPixmap(image)
            self.color = argb


    def set_ral_color(self):
        selected = self.comboBox_ral.text()
        argb = None
        for i in self.ral_list:
            if i[0] == selected:
                argb = i[1]
                break
        if argb is not None:
            image = QtGui.QPixmap(generate_color(argb))
            self.color_l.setPixmap(image)
            self.color = argb


def generate_color(argb: str) -> QImage:
    if argb is None:
        argb = "#00ffffff"
    background = Image.open(os.path.join(BASE_DIR.rstrip("common").replace("\\" ,"/"), "images/black_white_background.png"))
    background = background.convert("RGBA")
    width, height = background.size
    rgba = "#" + argb[3:9] + argb[1:3]
    rgba = ImageColor.getcolor(rgba.upper(), "RGBA")
    color_loyout = Image.new("RGBA", (width, height), rgba)
    color_loyout.convert("RGBA")
    result = Image.alpha_composite(background, color_loyout)
    background.close()
    return QImage(ImageQt(result))


def generate_font(size: int, bold=False) -> QFont:
    if bold:
        font = QtGui.QFont("Roboto-Medium")
    else:
        font = QtGui.QFont("Roboto-Regular")

    font.setPointSize(size)
    return font


def delete_chield(loyout):
    while loyout.count():
        child = loyout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def create_w_lo(parent_w: QtWidgets.QWidget, parent_lo: QtWidgets.QBoxLayout) -> \
        Tuple[QtWidgets.QWidget, QtWidgets.QBoxLayout]:
    w = QtWidgets.QWidget(parent=parent_w)
    lo = QtWidgets.QHBoxLayout(w)
    lo.setSpacing(5)
    lo.setContentsMargins(0, 0, 0, 0)
    parent_lo.addWidget(w)
    return w, lo


def insert_w_lo(idex: int, parent_w: QtWidgets.QWidget, parent_lo: QtWidgets.QBoxLayout) -> \
        Tuple[QtWidgets.QWidget, QtWidgets.QBoxLayout]:
    w = QtWidgets.QWidget(parent=parent_w)
    lo = QtWidgets.QHBoxLayout(w)
    lo.setSpacing(5)
    lo.setContentsMargins(0, 0, 0, 0)
    parent_lo.insertWidget(idex, w)
    return w, lo


def normalize_number(number: Decimal) -> str:
    normalized = number.normalize()
    sign, digit, exponent = normalized.as_tuple()
    normalized = normalized if exponent <= 0 else normalized.quantize(1)
    normalized = normalized.quantize(Decimal("1.00"), "ROUND_HALF_EVEN")
    normalized = str(normalized).replace(".", ",")
    return normalized


def get_numeric_validator(minus=False):
    if minus:
        reg_ex = QRegularExpression(r"[-]?[0-9]*[\,,.]{1}[0-9]*")
    else:
        reg_ex = QRegularExpression(r"[0-9]*[\,,.]{1}[0-9]*")
    validator = QRegularExpressionValidator(reg_ex)
    return validator


def get_h_spacer():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                 QtWidgets.QSizePolicy.Policy.Minimum)


def get_v_spacer():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                 QtWidgets.QSizePolicy.Policy.Expanding)


def change_position_window(self, x: int = 0, y: int = 0):
    qr = self.frameGeometry()
    cp = self.screen().availableGeometry().center()
    qr.moveCenter(cp)
    coord = qr.topLeft()
    x = coord.x() + x
    y = coord.y() + y
    coord.setX(x)
    coord.setY(y)
    self.move(coord)


def set_window_icon(self):
    self.setWindowIcon(QtGui.QIcon(os.path.join(BASE_DIR, 'images/icon.png')))


def fix_tab_bg(tab:QtWidgets.QWidget):
    tab.setObjectName("tab")
    tab.setStyleSheet("""
    QWidget#tab{
      background: #f9f9f9;
      border: 0px solid black;
    }
    """)