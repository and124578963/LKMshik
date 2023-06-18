import os
import sys

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
from sqlitedict import SqliteDict

from activation import Ui_activation_w, Ui_register_w, Ui_entry_w
from common.ui_elements import delete_chield
from projects import Projects_Ui


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.centralwidget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        # self.ui = Ui_MainWindow()
        self.set_state("activation")
        self.setWindowIcon(QtGui.QIcon('images/icon.png'))



    def set_state(self, state):
        delete_chield(self.verticalLayout)
        if state == "activation":
            self.ui = Ui_activation_w()
            self.ui.setupUi(self)
        elif state == "main":
            self.ui2 = Projects_Ui()
            self.ui2.setupUi(self)
            self.showMaximized()
        elif state == "register":
            self.ui3 = Ui_register_w()
            self.ui3.setupUi(self)
        elif state == "entry":
            self.ui4 = Ui_entry_w()
            self.ui4.setupUi(self)




def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    import sys
    sys.excepthook = except_hook
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


