import datetime
import os
import shutil

import logging
import win32com
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow

from activation import Ui_activation_w, Ui_register_w, Ui_entry_w
from common.ui_elements import delete_chield
from projects import Projects_Ui

BASE_DIR = os.path.dirname(__file__)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.centralwidget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        # self.ui = Ui_MainWindow()
        self.set_state("activation")
        self.setWindowIcon(QtGui.QIcon(os.path.join(BASE_DIR, 'images/icon.png')))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        now = str(datetime.datetime.now())[0:10]
        try:
            shutil.copy2('reactives.db', f'backup/reactives_{now}.db')
            shutil.copytree('saves/', f'backup/saves_{now}/')

        except Exception as e:
            logging.error("Ошибка при создании бэкапа", e, exc_info=True)

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

    try:
        shutil.rmtree(win32com.__gen_path__ + '\\00020905-0000-0000-C000-000000000046x0x8x5')
    except Exception as e:
        pass

    logging.basicConfig(filename='./errors.log', filemode='w', level=logging.INFO,
                        format="%(asctime)s;%(levelname)s;%(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


