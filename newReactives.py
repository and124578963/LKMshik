import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, Qt, QAbstractTableModel, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QHeaderView, QVBoxLayout, QLabel, QWidget, QDialog, QFileDialog

from component_card import ComponentCard, EditComponentCard, generate_color
from settings import TABLE_DICT, get_category, PASSPORT, update_config_param
from database import DB
import pandas as pd


class MyComponentsUi(QWidget):
    _instance = False  # Keep instance reference


    def __init__(self):
        super(MyComponentsUi, self).__init__()
        self.db = DB()
        self.selected_category = None
        self.dialogs = []
        self.global_component_f = False
        self.setupUi()
        MyComponentsUi._instance = True

    def closeEvent(self, event):
        MyComponentsUi._instance = None

    def setupUi(self):
        self.main_window = self
        self.setObjectName("MainWindow")
        # self.resize(1188, 505)
        # self.setDocumentMode(False)
        # self.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = self
        self.setStyleSheet("QWidget#MainWindow{background:rgb(238, 237, 235)}")
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0,0,0,0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_side = QtWidgets.QWidget(parent=self.centralwidget)
        self.left_side.setMaximumSize(QtCore.QSize(300, 16777215))
        self.left_side.setStyleSheet("background:rgb(238, 237, 235)")
        self.left_side.setObjectName("left_side")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.left_side)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_3 = QtWidgets.QWidget(parent=self.left_side)

        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 100))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(parent=self.widget_3)
        self.label_2.setMaximumSize(QtCore.QSize(300, 350))
        self.label_2.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label_2.setPixmap(QtGui.QPixmap("images/Логотип.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.widget_3)

        self.category_btn_dict = {}
        for category_label, category in TABLE_DICT.items():
            self.category_btn_dict[category] = CategoryButton(self.left_side, category_label)
            self.category_btn_dict[category].clicked.connect(lambda event, cat=category: self.select_category(cat))
            self.verticalLayout.addWidget(self.category_btn_dict[category])

        self.global_switch_btn = SwitchGlobalButton(self.left_side)
        self.global_switch_btn.clicked.connect(lambda event: self.global_switch())

        self.verticalLayout.addWidget(self.global_switch_btn)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.left_side)
        self.right_side = QtWidgets.QWidget(parent=self.centralwidget)
        self.right_side.setObjectName("right_side")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.right_side)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toolbar = QtWidgets.QFrame(parent=self.right_side)
        self.toolbar.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.toolbar.setStyleSheet("background:rgb(238, 237, 235)")
        self.toolbar.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.toolbar.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.toolbar.setLineWidth(1)
        self.toolbar.setObjectName("toolbar")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.toolbar)
        self.horizontalLayout_2.setContentsMargins(0, 3, 0, 3)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.add_btn = ToolbarBtn(self.toolbar, "add")
        self.horizontalLayout_2.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.open_component_card)

        self.del_btn = ToolbarBtn(self.toolbar, "del")
        self.del_btn.clicked.connect(self.delete_selected)
        self.horizontalLayout_2.addWidget(self.del_btn)

        self.setting_btn = ToolbarBtn(self.toolbar, "setting")
        self.setting_btn.clicked.connect(lambda event: self.open_settings())
        self.horizontalLayout_2.addWidget(self.setting_btn)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)

        # self.search_comboBox = CastomCombobox(self.toolbar)
        # self.horizontalLayout_2.addWidget(self.search_comboBox)
        # self.search_comboBox.addItem("Название")
        # self.search_comboBox.addItem("Тип")
        # self.search_comboBox.setItemText(0,  "Название")
        # self.search_comboBox.setItemText(1, "Тип")

        self.search_lineEdit = CastomInput(self.toolbar)
        self.search_lineEdit.textChanged.connect(lambda event: self.search_result(event))
        self.horizontalLayout_2.addWidget(self.search_lineEdit)

        self.label = QtWidgets.QLabel(parent=self.toolbar)
        self.label.setMaximumSize(QtCore.QSize(32, 32))
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label.setPixmap(QtGui.QPixmap("images/search.png"))
        self.label.setScaledContents(True)
        self.horizontalLayout_2.addWidget(self.label)

        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_2.addWidget(self.toolbar)

        self.table = CustomTable(self.right_side)
        self.table.setSortingEnabled(True)

        self.table.doubleClicked.connect(self.edit_component_card)
        self.verticalLayout_2.addWidget(self.table)

        self.select_category("Solvents")

        self.table.show()
        self.horizontalLayout.addWidget(self.right_side)
        # self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def delete_selected(self):
        indexes = {i.row() for i in self.table.selectedIndexes()}
        text = "Вы уверены, что хотите удалить \n"
        if len(indexes) == 0:
            return

        elif len(indexes) == 1:
            row = list(indexes)[0]
            text += self.data[row][1] + "?"

        elif len(indexes) > 1:
            text += str(len(indexes)) + " шт. элементов?"

        if InfoWindow(text).exec():
            for i in indexes:
                self.db.delete_records(self.selected_category, self.data[i][1])
            new_data = []
            for i, row in enumerate(self.data):
                if i not in indexes:
                    new_data.append(row)

            self.data = new_data
            column_lables = [i[0] for i in get_category(self.selected_category, gloval_check=False)]
            self.model = TableModel(self.data, column_lables, self.selected_category)
            self.table.setModel(self.model)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ЛКМщик - Моя лаборатория"))

        self.del_btn.setShortcut(_translate("MainWindow", "Del"))

    def select_category(self, category: str):
        self.selected_category = category

        for cat, button in self.category_btn_dict.items():
            button.setSelected() if cat == category else button.setNotSelected()

        column_lables = [i[0] for i in get_category(category, gloval_check=self.global_component_f, table_view=True)]
        columns = [i[1] for i in get_category(category, gloval_check=self.global_component_f, table_view=True)]
        columns = ", ".join(columns)
        if category != "Producer" and not self.global_component_f:
            columns = columns + ", hexcolor"
            column_lables += ["hexcolor", ]
        try:
            self.data = self.db.load_reactives(category, columns)
        except Exception:
            text = "Неверное хранилище. \nВыберите в настройках другое хранилище компонентов." \
                   "\nПо умолчанию: reactives.db в папке с программой."
            if InfoWindow(text).exec():
                dialog = QFileDialog()
                dialog.setNameFilter("Хранилище компонентов (*.db)")
                dialog.setFileMode(QFileDialog.fileMode(dialog).AnyFile)
                dialog.setViewMode(QFileDialog.viewMode(dialog).Detail)

                if dialog.exec():
                    fileNames = dialog.selectedFiles()[0]
                    update_config_param("database_path", fileNames)
            return

        if category != 'Producer':
            self.index_name = column_lables.index("Название")
        else:
            self.index_name = column_lables.index("Поставщик")

        self.model = TableModel(self.data, column_lables, self.selected_category)
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.table.setModel(self.proxyModel)
        self.table.resizeColumnsToContents()

    def search_result(self, text: str):
        text = text.lower()
        column_lables = [i[0] for i in get_category(self.selected_category, gloval_check=self.global_component_f)]
        columns = [i[1] for i in get_category(self.selected_category, gloval_check=self.global_component_f)]
        columns_row = ", ".join(columns)
        request = "lower(" + ") like ? or lower(".join(columns) + ") like ?"
        goal = [f"%{text}%" for _ in columns]

        self.data = self.db.search_records(columns_row, self.selected_category, goal, request)

        self.model = TableModel(self.data, column_lables, self.selected_category)
        self.table.setModel(self.model)

    def open_component_card(self):
        dialog = ComponentCard(self, self.selected_category)
        self.dialogs.append(dialog)
        dialog.show()

    def edit_component_card(self):
        row = self.table.currentIndex().row()
        name = self.data[row][self.index_name]
        dialog = EditComponentCard(self, self.selected_category, name, global_check=self.global_component_f)
        self.dialogs.append(dialog)
        dialog.show()

    def open_settings(self):
        dialog = SettingsWindow()
        self.dialogs.append(dialog)
        dialog.show()

    def global_switch(self):
        self.global_component_f = not self.global_component_f
        if self.global_component_f:
            self.db = DB(global_check=self.global_component_f)
            self.db.update_reactives_base()
            self.add_btn.hide()
            self.del_btn.hide()
            self.setting_btn.hide()
            self.global_switch_btn.setSelected()
            self.main_window.setWindowTitle("ЛКМщик - Глобальная база")
            self.select_category("Solvents")

        else:
            self.db = DB(global_check=self.global_component_f)
            self.add_btn.show()
            self.del_btn.show()
            self.setting_btn.show()
            self.global_switch_btn.setNotSelected()
            self.main_window.setWindowTitle("ЛКМщик - Моя лаборатория")
            self.select_category("Solvents")


class CastomInput(QtWidgets.QLineEdit):
    def __init__(self, parent):
        super(CastomInput, self).__init__(parent=parent)
        self.setMaximumSize(QtCore.QSize(200, 16777215))
        self.setStyleSheet("""
        QLineEdit{
        background:white;
         border : 2px solid #ccc;
        border-radius: 3px;
        padding: 6px 6px 4px 6px;
        }
        QLineEdit:focus{
          border: 2px solid #3f768d;
          }
        
        
        """)
        self.setDragEnabled(False)
        self.setObjectName("search_lineEdit")


class ToolbarBtn(QtWidgets.QPushButton):
    def __init__(self, parent, name):
        super(ToolbarBtn, self).__init__(parent=parent)
        dict_btn_img = {
            "add": ["images/add.png", "  Добавить"],
            "del": ["images/del.png", "  Удалить"],
            "setting": ["images/setting.png", ""],
            "add_proj": ["images/add.png", "  Добавить проект"],
            "warehouse": ["images/warehouse.png", "  Мои компоненты"],
            "edit_proj": ["images/edit_proj.png", "  Изменить проект"],
        }
        self.setSizeIncrement(QtCore.QSize(0, 0))
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setTabletTracking(False)
        self.setAcceptDrops(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(dict_btn_img[name][0]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setIcon(icon)
        self.setText(dict_btn_img[name][1])
        self.setIconSize(QtCore.QSize(16, 16))
        self.setObjectName(name)
        self.setStyleSheet("""
        
        QPushButton{
 
          color: #eeedeb;
          font-weight: 700;
          text-decoration: none;
         
          padding: .3em 1em;
          outline: none;
          border: 2px solid #1c2524;
          border-radius: 1px;
          transition: 0.3s;
          background:#1c2524;
          image-position:left;
      
        }
        QPushButton:hover {
  background: #333e39;
  border: 2px solid #333e39;
}
QPushButton:pressed  {
border: 1px solid #eeedeb;
  }
        
        """)


class TableModel(QAbstractTableModel):

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            # return f"Column {section + 1}"
            return self.columns[section]
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return f"{section + 1}"

    def __init__(self, _data: list, columns: list, category: str):
        self.columns = columns
        if category != 'Producer':
            self.index_name = self.columns.index("Название")
        else:
            self.index_name = self.columns.index("Поставщик")

        self.category = category
        self.hexcolor_f = False
        super(TableModel, self).__init__()

        if "hexcolor" in self.columns:
            index = self.columns.index("hexcolor")
            self.columns.pop(index)
            self.hexcolor_f = True
            self.list_hex_color = []
            for i in _data:
                self.list_hex_color.append(i.pop(index))

        if len(_data) == 0:
            _data = ['' for _ in columns]
            _data = [_data, ]
            if self.hexcolor_f: self.list_hex_color = ["", ]
        self._data = _data


    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:

            value = self._data[index.row()][index.column()]
            # if isinstance(value, datetime):
            #     return value.strftime("%Y-%m-%d")
            if isinstance(value, float):
                return f"{value:.2f}"
            return value
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == self.index_name:
                return Qt.AlignmentFlag.AlignLeft + Qt.AlignmentFlag.AlignVCenter
            else:
                return Qt.AlignmentFlag.AlignHCenter + Qt.AlignmentFlag.AlignVCenter

        # if role == Qt.ItemDataRole.BackgroundRole:
        #     return QColor("#adcdff") if index.row() % 2 == 0 else QColor("#d8ffc2")

        if role == Qt.ItemDataRole.DecorationRole:

            value = self._data[index.row()][index.column()]

            if value is None:
                return None
            #     return self.naIcon
            # # if isinstance(value, datetime):
            # #     return self.calendarIcon
            if index.column() == 1 and self.hexcolor_f:
                value = self.list_hex_color[index.row()]
                if len(value)>5:
                    return QIcon(QtGui.QPixmap(generate_color(value)))

            # if index.column() == 1:
            #     return self.dollarIcon

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    # def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
    #     print(self._data)
    #     if order == Qt.SortOrder.DescendingOrder:
    #         order = True
    #     else:
    #         order = False
    #     self._data.sort(key=lambda x: x[1], reverse=order)
    #     self.beginResetModel()


class CustomTable(QtWidgets.QTableView):
    def __init__(self, parent):
        super(CustomTable, self).__init__(parent=parent)
        self.setAutoScroll(True)
        self.setObjectName("table")
        self.verticalHeader().hide()
        self.setStyleSheet("""

                           QTableView{
                           background:white;
                           border: 0px;

                           }
                           QTableView::item:selected:active{
                           selection-color: #fff;
                           background: #3c748b
                           }
                   
                           QHeaderView::section{
                           border : 1px solid #3c758c;
                           border-radius:1px;
                           background: white;

                           }

               """)
        # self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # self.setWordWrap(True)
        # self.horizontalHeader().setStretchLastSection(True)


class CategoryButton(QtWidgets.QPushButton):
    def __init__(self, parent, text):
        super(CategoryButton, self).__init__(parent=parent)
        self.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(16)
        self.setFont(font)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        # self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        # self.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        # self.setAutoFillBackground(False)
        self.setAutoRepeat(False)
        self.setDefault(False)
        self.setText(text)
        self.setNotSelected()

    def setSelected(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/selected.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setIcon(icon)
        self.setIconSize(QSize(26, 26))
        self.setObjectName("selected")
        self.setStyleSheet(
            """
                QPushButton{
                    text-align: left; 
                    border: 0px;
                    padding: 15px 0 0 15px;
                    color: rgb(62, 118, 141);
                }
                QPushButton:hover{
                  color: rgb(61, 117, 138);
                }
            """)


    def setNotSelected(self):
        icon = QtGui.QIcon()
        self.setIcon(icon)
        self.setObjectName("notSelected")
        self.setStyleSheet(
            """
                QPushButton{
                    text-align: left; 
                    border: 0px;
                    padding: 15px 0 0 15px;
                     color: rgb(27, 37, 36);
                }
                QPushButton:hover{
                  color: rgb(61, 117, 138);
                }
            """
        )


class SwitchGlobalButton(QtWidgets.QPushButton):
    def __init__(self, parent):
        super(SwitchGlobalButton, self).__init__(parent=parent)
        self.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(18)
        self.setFont(font)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        # self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        # self.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        # self.setAutoFillBackground(False)
        self.setAutoRepeat(False)
        self.setDefault(False)

        self.setNotSelected()

    def setSelected(self):
        self.setObjectName("selected")
        self.setText("Моя лаборатория")
        self.setStyleSheet(
            """
               QPushButton {
            background-image: url(images/arrow-left.png);
            background-origin: content;
            background-position: left bottom;

            background-repeat: no-repeat;
            text-align: right; 
            border: 0px;
            padding: 15px 35px 15px 30px;
             color: rgb(27, 37, 36);
        }
     QPushButton:hover{
              color: rgb(61, 117, 138);
              background-image: url(images/arrow-left-on.png);
            }
            """)


    def setNotSelected(self):
        self.setText("Глобальная база")
        self.setStyleSheet("""        
        QPushButton {
            background-image: url(images/arrow-right.png);
            background-origin: content;
            background-position: right bottom;

            background-repeat: no-repeat;
            text-align: left; 
            border: 0px;
            padding: 15px 70px 15px 15px;
             color: rgb(27, 37, 36);
        }
     QPushButton:hover{
              color: rgb(61, 117, 138);
              background-image: url(images/arrow-right-on.png);
            }

    """
                               )


class CastomCombobox(QtWidgets.QComboBox):
    def __init__(self, parent):
        super(CastomCombobox, self).__init__(parent=parent)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""
        QComboBox{
          width:60px;
          height:27px;
          color:black;
          font-weight: 700;
        border : 2px solid #ccc;
        border-radius: 3px;
        padding: 0px 6px 1px 6px;
          background: white;

          }
          QComboBox:hover{
          border: 2px solid #3f768d;
          }
  
  QListView::item{
    padding-left:5px;
    border-bottom: 1px solid #ccc;
    color: #1c2524;
    background: white;
    font-weight:lighter;
    padding: 5px 0 5px 0px;

    }
QListView::item:hover{ 
border-bottom: 2px solid #3c758c;

}

QComboBox::drop-down{
    border:                 none;
     subcontrol-origin: margin;
    }
QComboBox QAbstractItemView {
    outline: none;
    font-weight: lighter;
}
       
        
        """)
        self.setObjectName("search_comboBox")


class InfoWindow(QDialog):

    def __init__(self, text):
        super().__init__()
        self.setObjectName("background")
        self.resize(497, 183)
        self.setStyleSheet("QWidget#background{\n"
                                 "background-color: #d0b394;\n"
                                 "}")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(17, 17, 17, 17)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.setWindowOpacity(0.9)
        self.widget = QtWidgets.QWidget(parent=self)
        self.widget.setStyleSheet("")
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(parent=self.widget)
        self.label_2.setMaximumSize(QtCore.QSize(150, 125))
        self.label_2.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("images/INFO.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(parent=self.widget)
        self.label.setStyleSheet("QLabel{\n"
                                 "    font: 12pt \"Segoe UI Variable Display\";\n"
                                 "}")
        self.label.setScaledContents(False)
        self.label.setText(text)
        self.label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=self)
        self.buttonBox.setAcceptDrops(False)
        self.buttonBox.setAutoFillBackground(False)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.setWindowTitle("Предупреждение")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.setObjectName("Form")
        self.resize(426, 112)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(parent=self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tab.setStyleSheet("""
                   QWidget#scrollAreaWidgetContents{
                   background: #f9f9f9;
                   border: 0px solid black;
                   }
               """)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(parent=self.tab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setStyleSheet("""
            QScrollArea{
            background: #f9f9f9;
            border: 0px solid black;
            }
        """)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()

        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 418, 81))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        self.import_btn = QtWidgets.QPushButton(parent=self.scrollAreaWidgetContents)
        self.import_btn.setObjectName("pushButton")
        self.import_btn.setText("Импорт компонентов")
        self.import_btn.clicked.connect(lambda e: self.import_f())
        self.verticalLayout.addWidget(self.import_btn)
        self.select_db_btn = QtWidgets.QPushButton(parent=self.scrollAreaWidgetContents)
        self.select_db_btn.clicked.connect(lambda e: self.select_db())
        self.select_db_btn.setObjectName("pushButton_2")
        self.select_db_btn.setText("Выбрать хранилище")
        
        self.verticalLayout.addWidget(self.select_db_btn)


        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.tab, "")
        self.verticalLayout_2.addWidget(self.tabWidget)


        self.setWindowTitle("Настройки хранилища")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "Общие")
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def import_f(self):
        self.params_f()
        text = "Для загрузки вашей базы добавьте данные в файл import.xlsx" \
               "\nЗначения в выделенных столбцах должны быть конкретными числовыми значениями" \
               "\n(не диапазоны). Названия и шифры (при использовании) не должны повторяться."
        
        if InfoWindow(text).exec():
            xl = pd.ExcelFile('import.xlsx')

            list_groups = ['Solvents', 'Pigments', 'PigmPast', 'Fillers', 'Films', 'Additives', 'Hardener', 'Producer']
            list_params = [self.params_solvent, self.params_pigments, self.params_pigmpasts, self.params_fillers,
                           self.params_films, self.params_additives, self.params_hardener, self.params_provider]
            list_errors = 'Не удалось добавить следующие компоненты:'
            for sheet, group, params in zip(xl.sheet_names, list_groups, list_params):
                ncols = len(list(xl.parse(sheet)))
                df1 = xl.parse(sheet, converters={i: str for i in range(ncols)})
                df1 = df1.fillna(' ')

                params += ' , note'
                if group != 'Producer':
                    params = params + self.pb_params_str
                for i in range(len(df1)):
                    if group != 'Producer':
                        values = list(map(self.map_replace_point, list(df1.iloc[i])))

                    else:
                        values = list(df1.iloc[i])

                    result = self.db.new_insert_data(group, params, values)
                    if not result:
                        if group != 'Producer':
                            list_errors += f'\n{sheet}:{df1.iloc[i][1]}'
                        else:
                            list_errors += f'\n{sheet}:{df1.iloc[i][0]}'
            if list_errors == 'Не удалось добавить следующие компоненты:':
                self.destroy()
            else:
                InfoWindow(list_errors).exec()

    # TODO: Переписать функцию
    def params_f(self):
        self.solvent_zip = get_category('Solvents', gloval_check=False)
        self.labels_list_solvent, params, self.example_tags_solvent, self.calc_tags_solvent, self.counting_solvent, _ = zip(
            *self.solvent_zip)
        self.params_solvent = ', '.join(params)

        self.pigm_zip = get_category('Pigments', gloval_check=False)
        self.labels_list_pigment, params, self.example_tags_pigment, self.calc_tags_pigment, self.counting_pigm, _ = zip(
            *self.pigm_zip)
        self.params_pigments = ', '.join(params)

        self.zip_pigmpast = get_category('PigmPast', gloval_check=False)
        self.lables_list_pigm_pasts, params, self.example_tags_pigmpast, self.calc_tags_pigmpast, self.counting_pigmpast, _ = zip(
            *self.zip_pigmpast)
        self.params_pigmpasts = ', '.join(params)

        self.zip_fillers = get_category('Fillers', gloval_check=False)
        self.labels_list_filler, params, self.example_tags_fillers, self.calc_tags_fillers, self.counting_fillers, _ = zip(
            *self.zip_fillers)
        self.params_fillers = ', '.join(params)

        self.zip_films = get_category('Films', gloval_check=False)
        self.labels_list_film, params, self.example_tags_films, self.calc_tags_films, self.counting_films, _ = zip(
            *self.zip_films)
        self.params_films = ', '.join(params)

        self.zip_additives = get_category('Additives', gloval_check=False)
        self.labels_list_additive, params, self.example_tags_additives, self.calc_tags_additive, self.counting_additive, _ = zip(
            *self.zip_additives)
        self.params_additives = ', '.join(params)

        self.zip_hardener = get_category('Hardener', gloval_check=False)
        self.labels_list_hardener, params, self.example_tags_hardener, self.calc_tags_hardener, self.counting_hardener, _ = zip(
            *self.zip_hardener)
        self.params_hardener = ', '.join(params)

        self.zip_pb = PASSPORT
        self.pb_label_str, params, self.example_tags_pb = zip(*self.zip_pb)
        self.pb_params_str = ', ' + ', '.join(params)

        self.params_provider = 'provider, manager, phone, email, site'
        self.labels_list_provider = get_category('Producer', gloval_check=False)

        self.PARAMS_DICT = {
            'Solvents': self.solvent_zip,
            'Pigments': self.pigm_zip,
            'PigmPast': self.zip_pigmpast,
            'Fillers': self.zip_fillers,
            'Films': self.zip_films,
            'Additives': self.zip_additives,
            'Hardener': self.zip_hardener,
            'Producer': self.labels_list_provider,
        }

        self.money_dict = {
            u"Руб": 0,
            u"$": 1,
            u"€": 2,
        }

    def select_db(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter("Хранилище компонентов (*.db)")
        dialog.setFileMode(QFileDialog.fileMode(dialog).AnyFile)
        dialog.setViewMode(QFileDialog.viewMode(dialog).Detail)

        if dialog.exec():
            fileNames = dialog.selectedFiles()[0]
            update_config_param("database_path", fileNames)
            self.destroy()


    def map_replace_point(self, string):
        try:
            if int(float(string)) == float(string):
                string = int(string)
                string = str(string)
            else:
                string = str(string).replace('.', ',')
            return string
        except:
            return string

