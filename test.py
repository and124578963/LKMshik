import sys, random

import PyQt6
from PyQt6.QtCore import QMimeData, Qt, QEvent
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QFrame, QHBoxLayout, QGridLayout, QWidget, QScrollArea, QDialog, \
    QLabel


class IndicSelectWindow(QDialog):

    def __init__(self, parent=None):
        super(IndicSelectWindow, self).__init__(parent=parent)
        self.resize(1000, 800)

        self.target = None
        self.setAcceptDrops(True)
        self.layout = QHBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.scrollArea)

        for i in range(3):
            for j in range(3):
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")

                self.Frame.setLineWidth(2)
                self.layout = QHBoxLayout(self.Frame)
                l = QLabel(parent=self.Frame)
                l.setText(str(i)+str(j))
                Box = QVBoxLayout()

                Box.addWidget(self.Frame)

                self.gridLayout.addLayout(Box, i, j)
                self.gridLayout.setColumnStretch(i % 3, 1)
                self.gridLayout.setRowStretch(j, 1)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QEvent.Type.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def get_index(self, pos):
        for i in range(self.gridLayout.count()):
            if self.gridLayout.itemAt(i).geometry().contains(pos) and i != self.target:
                return i

    def mousePressEvent(self, event:PyQt6.QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.target = self.get_index(event.position().toPoint())
        else:
            self.target = None

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.target is not None:
            drag = QDrag(self.gridLayout.itemAt(self.target))
            pix = self.gridLayout.itemAt(self.target).itemAt(0).widget().grab()
            mimedata = QMimeData()
            mimedata.setImageData(pix)
            drag.setMimeData(mimedata)
            drag.setPixmap(pix)
            # drag.setHotSpot(event.pos())
            drag.exec()

    def mouseReleaseEvent(self, event):
        self.target = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: PyQt6.QtGui.QMouseEvent):
        if not event.source().geometry().contains(event.position().toPoint()):
            source = self.get_index(event.position().toPoint())
            if source is None:
                return

            i, j = max(self.target, source), min(self.target, source)
            p1, p2 = self.gridLayout.getItemPosition(i), self.gridLayout.getItemPosition(j)

            self.gridLayout.addItem(self.gridLayout.takeAt(i), *p2)
            self.gridLayout.addItem(self.gridLayout.takeAt(j), *p1)



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    import sys
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    w = IndicSelectWindow()
    w.show()
    sys.exit(app.exec())