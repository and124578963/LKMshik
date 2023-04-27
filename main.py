import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
from projects import Projects_Ui


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # self.ui = Ui_MainWindow()
        self.ui = Projects_Ui()
        self.ui.setupUi(self)
        self.showMaximized()

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    import sys
    sys.excepthook = except_hook
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


