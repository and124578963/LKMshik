import sys, os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QComboBox, QHBoxLayout, QApplication, QCompleter, QCheckBox, QLabel, QLineEdit



class Autocomplete(QComboBox):
    def __init__(self, parent, items):
        super(Autocomplete, self).__init__(parent)
        self.items = items
        self.init()

    def init(self):
        self.setEditable(True)
        self.setDuplicatesEnabled(False)
        self.setAutocompletion(self.items)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

    def setAutocompletion(self, items):
        word_set = set(items)
        completer = QCompleter(word_set)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(completer)


class Widget(QWidget):
    """docstring for Widget"""
    def __init__(self, items, parent=None, fixed=True, allow_duplicates=True):
        super(Widget, self).__init__()
        self.items = items
        self.checkbox = QCheckBox()
        self.labelItemCounter = QLabel()
        self.autocomplete = Autocomplete(self.items,
            parent=self
        )

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.autocomplete)
        self.layout.addWidget(self.labelItemCounter)
        self.labelItemCounter.setText(f'{self.autocomplete.count()}')
        # self.checkbox.stateChanged.connect(lambda: self.tuneAutocompletion())
        self.autocomplete.setAutocompletion(['Iron Man','Iron Man','Iron Man','Iron Man','Iron Man','Iron Man', 'hulk', 'Iron Man ', 'Captain America'])
        self.autocomplete.update()

    # def tuneAutocompletion(self):
    #     if self.checkbox.isChecked():
    #         self.autocomplete.setAutocompletion(self.items, True)
    #     else:
    #         self.autocomplete.setAutocompletion(self.items, False)

    # def currentText(self):
    #     return self.autocomplete.currentText()
    #
    # def currentIndex(self):
    #     return self.autocomplete.currentIndex()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    l = ['Captain America', 'Hulk', 'Iron Man', 'hulk', 'Iron Man ', 'Captain America']
    cb = Widget(l, parent=w)
    layout = QHBoxLayout()
    layout.addWidget(cb)
    w.setLayout(layout)
    w.show()
    sys.exit(app.exec())