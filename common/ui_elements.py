import copy
from decimal import Decimal
from typing import List, Tuple

import numpy as np
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtCore import QStringListModel, QRegularExpression
from PyQt6.QtGui import QImage, QFont, QRegularExpressionValidator
from PIL import Image, ImageColor
from PIL.ImageQt import ImageQt
from PyQt6.QtWidgets import QAbstractItemView

import sys
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy.optimize import curve_fit


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
            "swap":  ["images/swap_v.png", "images/swap_v.png"],
            "2k": ["images/2K.png", "images/2K-on.png"],
            "settings": ["images/settings_btn.png", "images/settings_btn-on.png"],
            "menu": ["images/menu.png", "images/menu-on.png"],
        }
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(img_dict[_type][0]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_on = QtGui.QIcon()
        self.icon_on.addPixmap(QtGui.QPixmap(img_dict[_type][1]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_off = self.icon
        self.setIcon(self.icon)
        self.setIconSize(QtCore.QSize(*size))
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

    def leaveEvent(self, event):
        self.hover.emit("leaveEvent")
        self.setIcon(self.icon)

    def set_pressed(self):
        if self.icon_off is self.icon:
            self.icon = self.icon_on
            self.setIcon(self.icon)
        else:
            self.icon = self.icon_off
            self.setIcon(self.icon)


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
                
""".format(color_dict[color][0], color_dict[color][1])
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
        listModel = QStringListModel()
        listModel.setStringList(list_strings)
        self.setModel(listModel)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set(facecolor='#f0f0f0')
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
               + d * np.float_power(x,1) + e


def generate_color(argb: str) -> QImage:
    background = Image.open("images/black_white_background.png")
    background = background.convert("RGBA")
    width, height = background.size
    rgba = "#" + argb[3:9] + argb[1:3]
    rgba = ImageColor.getcolor(rgba, "RGBA")
    color_loyout = Image.new("RGBA", (width, height), rgba)
    color_loyout.convert("RGBA")
    result = Image.alpha_composite(background, color_loyout)
    background.close()
    return QImage(ImageQt(result))

def generate_font(size: int, bold=False) -> QFont:
    font = QtGui.QFont()
    font.setPointSize(size)
    font.setBold(bold)
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
    lo.setContentsMargins(0,0,0,0)
    parent_lo.addWidget(w)
    return w, lo

def insert_w_lo(idex: int, parent_w: QtWidgets.QWidget, parent_lo: QtWidgets.QBoxLayout) -> \
        Tuple[QtWidgets.QWidget, QtWidgets.QBoxLayout]:
    w = QtWidgets.QWidget(parent=parent_w)
    lo = QtWidgets.QHBoxLayout(w)
    lo.setSpacing(5)
    lo.setContentsMargins(0,0,0,0)
    parent_lo.insertWidget(idex, w)
    return w, lo

def normalize_number(number: Decimal) -> str:
    normalized = number.normalize()
    sign, digit, exponent = normalized.as_tuple()
    normalized = normalized if exponent <= 0 else normalized.quantize(1)
    normalized = normalized.quantize(Decimal("1.00"), "ROUND_HALF_EVEN")
    normalized = str(normalized).replace(".", ",")
    return normalized

def get_numeric_validator():
    reg_ex = QRegularExpression(r"[0-9]*[\,,.]{1}[0-9]*")
    validator = QRegularExpressionValidator(reg_ex)
    return validator

def get_h_spacer():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                       QtWidgets.QSizePolicy.Policy.Minimum)

def get_v_spacer():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                       QtWidgets.QSizePolicy.Policy.Expanding)
