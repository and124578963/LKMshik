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
            "swap": "Переместить",
            "2k": "Показать второй компонент",
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
        }
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(img_dict[_type][0]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_on = QtGui.QIcon()
        self.icon_on.addPixmap(QtGui.QPixmap(img_dict[_type][1]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
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

class MenuButton(HoverableButton):
    def __init__(self, parent, _type, size):
        super(MenuButton, self).__init__(parent, _type, size)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        super(MenuButton, self).mouseDoubleClickEvent(a0)
        self.showMenu()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        pass


