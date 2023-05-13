import copy

from PyQt6 import QtGui, QtCore, QtWidgets


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
