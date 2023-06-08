import os
import shutil

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QStringListModel, Qt, QSize
from PyQt6.QtWidgets import QAbstractItemView, QInputDialog, QLineEdit
from sqlitedict import SqliteDict

from common.secrets import Secrets
from common.ui_elements import HoverableButton, CustomListItem, generate_font, ColorButton, generate_color, ChoiceColor, \
    get_v_spacer
from component_card import CustomEntry
from newReactives import DarkBtn_Ui, InfoWindow, MyComponentsUi
from recepture import ReceptureWindow


class Projects_Ui(object):
    instance = None
    def __init__(self):
        self.list_projects = []
        self.selected_project = ""
        self.dialogs = []
        Projects_Ui.instance = self

    def setupUi(self, MainWindow):
        self.parent = MainWindow
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setStyleSheet("""
            QWidget#centralwidget{
            background:#eeedeb;
            }
        """)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.left_side = QtWidgets.QWidget(parent=self.centralwidget)
        self.left_side.setMaximumSize(QtCore.QSize(300, 16777215))
        self.left_side.setObjectName("left_side")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.left_side)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logo = QtWidgets.QLabel(parent=self.left_side)
        self.logo.setMinimumSize(QtCore.QSize(0, 0))
        self.logo.setMaximumSize(QtCore.QSize(300, 100))
        self.logo.setPixmap(QtGui.QPixmap("images/Логотип.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.verticalLayout.addWidget(self.logo)

        self.add_project_btn = DarkBtn_Ui(self.left_side, "add_proj")
        self.add_project_btn.setObjectName("addProject")
        self.add_project_btn.clicked.connect(self.add_project)
        self.verticalLayout.addWidget(self.add_project_btn)

        self.listView = CustomListItem(self.left_side)
        self.listView.setMaximumSize(QtCore.QSize(300, 16777215))
        self.listView.setObjectName("listView")
        self.listView.clicked.connect(lambda x: self.select_project(self.list_projects[x.row()]))
        self.load_list_projects()
        self.verticalLayout.addWidget(self.listView)

        self.horizontalLayout.addWidget(self.left_side)

        self.right_side = QtWidgets.QWidget(parent=self.centralwidget)
        self.right_side.setObjectName("right_side")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.right_side)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.toolbar = QtWidgets.QWidget(parent=self.right_side)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setStyleSheet("""
        QWidget#toolbar{
        background:#eeedeb;
        }
        """)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.toolbar)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")


        self.label_name_project = QtWidgets.QLabel(parent=self.toolbar)
        self.label_name_project.setContentsMargins(10, 0, 10, 3)
        self.label_name_project.setFont(generate_font(20))
        self.label_name_project.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_name_project)

        self.edit_btn = ProjectToolButton(self.toolbar, "edit")
        self.edit_btn.clicked.connect(lambda x: self.edit_project())
        self.horizontalLayout_2.addWidget(self.edit_btn)

        self.del_proj_btn = ProjectToolButton(self.toolbar, "del")
        self.del_proj_btn.clicked.connect(self.del_project)
        self.horizontalLayout_2.addWidget(self.del_proj_btn)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.components = DarkBtn_Ui(self.toolbar, "warehouse")
        self.components.clicked.connect(self.open_my_components)
        self.horizontalLayout_2.addWidget(self.components)
        self.verticalLayout_3.addWidget(self.toolbar)

        self.scrollArea = QtWidgets.QScrollArea(parent=self.right_side)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setStyleSheet("""
         QWidget#scrollAreaWidgetContents{
                   background: white;
                   border: 0px solid black;
                   }
         QScrollArea{
            background: white;
            border: 1px solid #bbb;
            }          
                   """)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 796, 544))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # self.main_grid = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.main_grid = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.main_grid.setContentsMargins(10, 10, 10, 10)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.horizontalLayout.addWidget(self.right_side)
        MainWindow.setCentralWidget(self.centralwidget)

        MainWindow.setWindowTitle("ЛКМщик - Мои проекты")
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.scrollArea.setWidgetResizable(True)

    def load_list_projects(self):
        self.list_projects = os.listdir('saves/')
        list_projects = list(map(lambda x: 'Тарировочные кривые' if x == "Тарировочные_кривые" else x,
                                 self.list_projects))
        self.listView.set_list_elements(list_projects)

    def select_project(self, name):
        name_label = 'Тарировочные кривые' if name == "Тарировочные_кривые" else name
        self.selected_project = name
        self.listView.change_selected(self.selected_project)
        self.label_name_project.setText(name_label)
        self.edit_btn.show()
        self.del_proj_btn.show()
        self.load_data_project()

    # Загрузка параметров проекта
    def load_data_project(self):
        self.delete_chield(self.main_grid)

        password = ""
        dec_data_params = []
        dec_data_params_value = []
        with SqliteDict('saves/' + self.selected_project + '/params') as mydict:
            enc_data_params = mydict['params']
            enc_data_params_value = mydict['params_value']
            if self.selected_project not in ['Тарировочные_кривые', 'Примеры']:
                for params, params_value in zip(enc_data_params, enc_data_params_value):
                    dec_data_params.append(Secrets().symmetric_decrypt(params, password).decode())
                    dec_data_params_value.append(Secrets().symmetric_decrypt(params_value, password).decode())
            else:
                dec_data_params = enc_data_params
                dec_data_params_value = enc_data_params_value

        self.goal_name_params_of_project = dec_data_params
        self.goal_value_params_of_project = dec_data_params_value
        self.list_iteration_names = os.listdir('saves/' + self.selected_project + '/')
        self.list_iteration_names.remove('params')
        self.list_iteration_names = self.list_iteration_names or []

        self.list_iter_obj = []

        for name in self.list_iteration_names:
            _iter = Iteration(self.scrollAreaWidgetContents, self.selected_project, name)
            self.main_grid.addWidget(_iter)
            self.list_iter_obj.append(_iter)

        add_iter = AddButtonIteration(self.scrollAreaWidgetContents, "iter")
        add_iter.set_click_event(self.add_iter)

        self.main_grid.addWidget(add_iter)

        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.main_grid.addItem(spacerItem3)

    def del_project(self):
        name = self.selected_project
        if name != 'Тарировочные_кривые':
            if InfoWindow(f"Вы уверены, что хотите удалить проект:\n{name}?").exec():
                shutil.rmtree('saves\\' + name, ignore_errors=True)
                self.load_list_projects()
                self.label_name_project.setText("")
                self.edit_btn.hide()
                self.del_proj_btn.hide()
                self.delete_chield(self.main_grid)

    def open_my_components(self):
        if not MyComponentsUi._instance:
            dialog = MyComponentsUi()
            self.dialogs.append(dialog)
            dialog.show()

    def delete_chield(self, loyout):
        while loyout.count():
            child = loyout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_iter(self):
        name, ok = QInputDialog().getText(self.parent, "Добавить итерацию",
                                          "Название:", QLineEdit.EchoMode.Normal,
                                          "")
        if ok and name:
            name = name.strip()
            iters = os.listdir('saves/' + self.selected_project)
            iters.remove('params')
            iters = iters or []

            if name not in iters and name != '':
                with SqliteDict('saves/' + self.selected_project + '/' + name) as mydict:
                    mydict.commit()

                Projects_Ui.instance.load_data_project()

    def add_project(self):
        if not AddProjectWindow.instance:
            dialog = AddProjectWindow()
            self.dialogs.append(dialog)
            dialog.show()

    def edit_project(self):
        if self.selected_project not in ['Тарировочные_кривые', 'Тарировочные кривые']:
            if not AddProjectWindow.instance:
                dialog = EditProjectWindow(self.selected_project)
                self.dialogs.append(dialog)
                dialog.show()



class ProjectToolButton(QtWidgets.QPushButton):
    hover = QtCore.pyqtSignal(str)

    def __init__(self, parent, _type):
        super(ProjectToolButton, self).__init__(parent=parent)
        dict_type = {'edit': ['images/edit.png', 'images/edit-on.png'],
                     "del": ["images/del_project.png", "images/del_project-on.png"],
                     "graph": ["images/graph.png", "images/graph-on.png"]
                     }

        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.hide()
        self.setContentsMargins(0, 0, 3, 0)


        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(dict_type[_type][0]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_on = QtGui.QIcon()
        self.icon_on.addPixmap(QtGui.QPixmap(dict_type[_type][1]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setIcon(self.icon)
        self.setIconSize(QtCore.QSize(20, 20))

        self.setStyleSheet(
            """
               QPushButton {
            border: 0px;
             color: rgb(27, 37, 36);
            }
            """)
        # self.hover.connect(lambda : print("a"))

    def enterEvent(self, event):
        self.hover.emit("enterEvent")
        self.setIcon(self.icon_on)

    def leaveEvent(self, event):
        self.hover.emit("leaveEvent")
        self.setIcon(self.icon)


class Iteration(QtWidgets.QWidget):

    def __init__(self, parent, project, name):
        super(Iteration, self).__init__(parent=parent)
        self.project = project
        self.name = name
        self.dialogs = []

        self.vertical_loyout = QtWidgets.QVBoxLayout(self)
        self.iteration_toolbar = QtWidgets.QWidget(self)
        self.iteration_toolbar.setContentsMargins(0,15,0,5 )
        self.iteration_toolbar.setObjectName("iterNameArea")
        self.iteration_toolbar.setStyleSheet("""
        QWidget#iterNameArea{
        border-bottom: 2px solid #ddd;
        }
        """)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.iteration_toolbar)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.iter_name = QtWidgets.QLabel(parent=self.iteration_toolbar)
        self.iter_name.setText(name)
        self.iter_name.setFont(generate_font(16))
        self.horizontalLayout_3.addWidget(self.iter_name)

        self.graph_iter_btn = ProjectToolButton(self.iteration_toolbar, "graph")
        self.graph_iter_btn.show()
        self.horizontalLayout_3.addWidget(self.graph_iter_btn)
        self.del_iter_btn = ProjectToolButton(self.iteration_toolbar, "del")
        self.del_iter_btn.show()
        self.del_iter_btn.clicked.connect(self.del_iter)
        self.horizontalLayout_3.addWidget(self.del_iter_btn)



        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.vertical_loyout.addWidget(self.iteration_toolbar)

        self.iter = QtWidgets.QWidget(self)
        self.loyout = QtWidgets.QHBoxLayout(self.iter)
        self.loyout.setSpacing(10)
        self.vertical_loyout.addWidget(self.iter)

        self.list_recepture_names = self.get_list_recepture_names()
        self.list_recepture_obj = []

        list_size = []
        for r_name in self.list_recepture_names:
            recepture = Recepture(self.iter, self.project, self.name, r_name, self.iter_data[r_name])
            self.list_recepture_obj.append(recepture)
            self.loyout.addWidget(recepture)
            list_size.append(recepture.get_size())

        if len(list_size):
            max_size = max(list_size)

            for recepture in self.list_recepture_obj:
                while recepture.get_size() < max_size:
                    recepture.add_component("", "")

        add_recepture = AddButtonIteration(self.iter, "recepture")
        add_recepture.set_click_event(lambda: self.add_recepture())
        self.loyout.addWidget(add_recepture)

        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.loyout.addItem(spacerItem2)



    def get_list_recepture_names(self):
        with SqliteDict('saves/' + self.project + '/' + self.name) as mydict:
            self.iter_data = dict(mydict)
        sorted_list_key = list(self.iter_data.keys())
        sorted_list_key.sort()
        return sorted_list_key

    def del_iter(self):
        if InfoWindow(f"Вы хотете удалить итерацию: \n{self.name}?").exec():
            os.remove('saves/' + self.project + '/' + self.name)

        Projects_Ui.instance.load_data_project()

    def add_recepture(self):
        name_recepture, ok = QInputDialog().getText(self, "Добавить рецептуру",
                                          "Название:", QLineEdit.EchoMode.Normal,
                                          "")
        if ok and name_recepture:
            dialog = ReceptureWindow(self.project, self.name, name_recepture, project_window=Projects_Ui.instance)
            self.dialogs.append(dialog)
            dialog.show()


class Recepture(QtWidgets.QFrame):

    def __init__(self, parent, project, iter, name, data):
        super(Recepture, self).__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus | Qt.FocusPolicy.NoFocus)
        self.data = data
        self.name = name
        self.project = project
        self.iter = iter
        self.row = 0
        self.row_p = 0
        self.dialogs = []

        self.g_loyout = QtWidgets.QVBoxLayout(self)
        self.g_loyout.setContentsMargins(10,10,10,10)

        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setObjectName("recepture")
        self.setStyleSheet("""
        QFrame#recepture{
        border: 2px solid #eeedeb;
        border-radius: 5px;
        background: #fafafa;
        }
        QFrame#recepture::focus{
        border: 2px solid #ffe03a;
        }
        """)

        self.nameArea = QtWidgets.QWidget(parent=self)
        self.nameArea.setMaximumSize(QtCore.QSize(300, 16777215))
        self.nameArea.setMinimumSize(QtCore.QSize(200, 0))
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.nameArea)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0,0,0,0)
        self.label_name = QtWidgets.QLabel(parent=self.nameArea)
        self.label_name.setText(name)
        self.label_name.setFont(generate_font(12))
        self.horizontalLayout_5.addWidget(self.label_name)

        # self.empty = QtWidgets.QLabel(parent=self)
        # self.empty.setText("")

        self.pushButton_7 = QtWidgets.QPushButton(parent=self.nameArea)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setText("...")
        self.pushButton_7.setStyleSheet("""QPushButton{border:0px solid black;}""")
        self.horizontalLayout_5.addWidget(self.pushButton_7, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.g_loyout.addWidget(self.nameArea)
        # self.g_loyout.addWidget()

        self.consist = QtWidgets.QFrame(parent=self)
        self.consist.setMaximumSize(QtCore.QSize(300, 16777215))
        self.vertical_comp_loyout = QtWidgets.QVBoxLayout(self.consist)
        self.vertical_comp_loyout.setObjectName("gridLayout")
        self.vertical_comp_loyout.setContentsMargins(0,0,0,5)
        self.vertical_comp_loyout.setSpacing(1)
        for name, amount in zip(self.data[0], self.data[1]):
            if name.strip() != '':
                self.add_component(name, amount)
        self.g_loyout.addWidget(self.consist)

        self.ecsperiment = QtWidgets.QFrame(parent=self)
        self.ecsperiment.setObjectName("experimentArea")
        self.ecsperiment.setStyleSheet("""
            QFrame#experimentArea{
            border-top: 2px solid #aaa;
            }
        """)
        self.ecsperiment.setMaximumSize(QtCore.QSize(300, 16777215))
        self.vertical_exp_loyout = QtWidgets.QVBoxLayout(self.ecsperiment)
        self.vertical_exp_loyout.setContentsMargins(0,7,0,0)
        self.vertical_exp_loyout.setSpacing(1)
        for param, value in zip(self.data[2], self.data[3]):
            if param.strip() != '':
                self.add_experiment(param, value)
        self.g_loyout.addWidget(self.ecsperiment)

    def add_component(self, name, value):
        if len(name) > 30:
            name = name[0:29] + "..."

        row_w = QtWidgets.QFrame(self.consist)
        if name != "":
            row_w.setObjectName("row_c")
        row_w.setStyleSheet("""
            QFrame#row_c{
            border-bottom: 1px solid #eee;
            border-radius: 2px;
            background: #fafafa;;
            }
        """)
        self.vertical_comp_loyout.addWidget(row_w)
        row_l = QtWidgets.QHBoxLayout(row_w)
        row_l.setContentsMargins(0,0,0,0)
        row_l.setSpacing(5)
        lable_n = QtWidgets.QLabel(parent=row_w)
        lable_n.setText(name)
        row_l.addWidget(lable_n)
        lable_a = QtWidgets.QLabel(parent=row_w)
        lable_a.setText(value)
        row_l.addWidget(lable_a, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.row += 1

    def add_experiment(self, name, value):
        if len(name) > 30:
            name = name[0:29] + "..."

        row_w = QtWidgets.QFrame(self.ecsperiment)
        if name != "":
            row_w.setObjectName("row_c")
        row_w.setStyleSheet("""
                    QFrame#row_c{
                    border-bottom: 1px solid #eee;
                    border-radius: 2px;
                    background: #fafafa;;
                    }
                """)


        self.vertical_exp_loyout.addWidget(row_w)
        row_l = QtWidgets.QHBoxLayout(row_w)
        row_l.setContentsMargins(0,0,0,0)
        row_l.setSpacing(5)
        lable_p = QtWidgets.QLabel(parent=row_w)
        lable_p.setText(name)
        row_l.addWidget(lable_p)
        lable_v = QtWidgets.QLabel(parent=row_w)
        lable_v.setText(value)
        row_l.addWidget(lable_v, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.row_p += 1

    def get_size(self):
        return self.row

    def get_size_experiment(self):
        return self.row_p

    def mouseDoubleClickEvent(self, event):
        super(Recepture, self).mouseDoubleClickEvent(event)
        self.open_recepture(self.name)

    def open_recepture(self, name_r):
        dialog = ReceptureWindow(self.project, self.iter, name_r, project_window=Projects_Ui.instance)
        self.dialogs.append(dialog)
        dialog.show()


class AddButtonIteration(QtWidgets.QFrame):
    hover = QtCore.pyqtSignal(str)

    def __init__(self, parent, _type):
        super(AddButtonIteration, self).__init__(parent=parent)
        self.setObjectName("border")
        self.click_event = None
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setMinimumSize(100, 100)
        self.button = QtWidgets.QPushButton(self)
        self.loyout = QtWidgets.QVBoxLayout(self)
        self.loyout.addWidget(self.button)
        self.loyout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)

        tooltip_dict = {
            "iter": "Добавить итерацию",
            "recepture": "Добавить рецептуру в итерацию"
        }
        self.setToolTip(tooltip_dict[_type])

        img_dict = {
            "iter": ["images/add_iter.png", "images/add_iter-on.png"],
            "recepture": ["images/add_iter.png", "images/add_iter-on.png"],
        }

        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(img_dict[_type][0]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.icon_on = QtGui.QIcon()
        self.icon_on.addPixmap(QtGui.QPixmap(img_dict[_type][1]), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.button.setIcon(self.icon)
        self.button.setIconSize(QtCore.QSize(48, 48))

        self.setStyleSheet("""
                QFrame#border{
                border: 2px solid #f5f5f5;
                border-radius: 5px;
               
                }
                QFrame#border::hover{
                border: 2px solid #232b2c;
                }
                 QPushButton {
            border: 0px;
             color: rgb(27, 37, 36);
            }
                """)

    def enterEvent(self, event):
        self.hover.emit("enterEvent")
        self.button.setIcon(self.icon_on)

    def leaveEvent(self, event):
        self.hover.emit("leaveEvent")
        self.button.setIcon(self.icon)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        click_event = self.get_click_event()
        if click_event:
            click_event()

    def set_click_event(self, func):
        self.click_event = func
        self.button.clicked.connect(func)

    def get_click_event(self):
        return self.click_event


class AddProjectWindow(QtWidgets.QWidget):
    instance = None

    def __init__(self, btn_type="add_proj"):
        super().__init__()
        AddProjectWindow.instance = self
        self.setObjectName("Form")
        self.row = 0
        self.project_color = "#00FFFFFF"
        self.choice_color_window = None
        self.setMinimumSize(500, 400)
        self.setMaximumSize(600, 999999)
        self.list_entry_name_obj = []
        self.list_entry_value_obj = []
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=self)
        self.tabWidget.setObjectName("tabWidget")
        self.general_tab = QtWidgets.QWidget()
        self.general_tab.setObjectName("general_tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.general_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.widget_name = QtWidgets.QWidget(parent=self.general_tab)
        self.widget_name.setObjectName("widget_name")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_name)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.name_label = QtWidgets.QLabel(parent=self.widget_name)
        self.name_label.setText("Название проекта:")
        self.name_label.setObjectName("name_label")
        self.horizontalLayout.addWidget(self.name_label)
        self.name_lineEdit = CustomEntry(self.widget_name)
        self.name_lineEdit.setObjectName("name_lineEdit")
        self.horizontalLayout.addWidget(self.name_lineEdit)
        self.verticalLayout_3.addWidget(self.widget_name)

        self.labels_w = QtWidgets.QWidget(self.general_tab)
        h_loyout = QtWidgets.QHBoxLayout(self.labels_w)
        h_loyout.setContentsMargins(0,15,0,0)
        tech_lable = QtWidgets.QLabel(parent=self.labels_w)
        tech_lable.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        tech_lable.setText("Требуемые характеристики:")
        h_loyout.addWidget(tech_lable)
        val_lable = QtWidgets.QLabel(parent=self.labels_w)
        val_lable.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        val_lable.setText("Требуемые значения:   \t\t\t\t\t\t\t\t")
        h_loyout.addWidget(val_lable)
        self.verticalLayout_3.addWidget(self.labels_w)

        self.scrollArea = QtWidgets.QScrollArea(parent=self.general_tab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setStyleSheet("""
                QWidget#scrollAreaWidgetContents{
                          background: #f9f9f9;
                          border: 0px solid black;
                          }
                QScrollArea#scrollArea{
                   background: #f9f9f9;
                   border: 0px solid #bbb;
                   }          
                          """)
        self.params_widget = QtWidgets.QWidget()
        self.params_widget.setGeometry(QtCore.QRect(0, 0, 796, 800))
        self.params_widget.setObjectName("scrollAreaWidgetContents")

        self.scrollArea.setWidget(self.params_widget)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.params_widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea.setWidgetResizable(True)

        self.button_w = QtWidgets.QWidget(parent=self.general_tab)
        self.button_w.setObjectName("button_w")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.button_w)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.plus = HoverableButton(self.button_w, "plus", [24, 24])
        self.plus.clicked.connect(lambda: self.add_row())
        self.horizontalLayout_4.addWidget(self.plus, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.button_w)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)

        self.save_btn = DarkBtn_Ui(self.general_tab, btn_type)
        self.save_btn.clicked.connect(lambda x: self.save_data())
        self.verticalLayout_3.addWidget(self.save_btn)

        self.color_tab = QtWidgets.QWidget()
        self.verticalLayout_color = QtWidgets.QVBoxLayout(self.color_tab)
        self.lable_color = QtWidgets.QLabel(parent=self.color_tab)
        self.lable_color.setText("Требуемый цвет:")
        self.lable_color.setFont(generate_font(12))
        self.verticalLayout_color.addWidget(self.lable_color)

        self.color_img = QtWidgets.QLabel(parent=self.color_tab)
        image = QtGui.QPixmap(generate_color(self.project_color))
        self.color_img.setPixmap(image)
        self.color_img.setMaximumSize(QSize(82, 80))
        self.color_img.setStyleSheet("""
                QLabel{
                border: 1px solid #ddd;
                }
                """)
        self.verticalLayout_color.addWidget(self.color_img, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        select_color_btn = ColorButton(self.color_tab, "blue")
        select_color_btn.setText("Выбрать цвет")
        select_color_btn.clicked.connect(lambda: self.open_choice_color())
        self.verticalLayout_color.addWidget(select_color_btn)
        self.verticalLayout_color.addItem(get_v_spacer())
        self.save_btn = DarkBtn_Ui(self.color_tab, btn_type)
        self.save_btn.setContentsMargins(9, 9, 9, 9)
        self.save_btn.clicked.connect(lambda x: self.save_data())
        self.verticalLayout_color.addWidget(self.save_btn)

        self.descript_tab = QtWidgets.QWidget()
        self.descript_tab.setObjectName("descript_tab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.descript_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.textEdit = QtWidgets.QTextEdit(parent=self.descript_tab)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.addWidget(self.textEdit)
        self.save_btn = DarkBtn_Ui(self.descript_tab, btn_type)
        self.save_btn.setContentsMargins(9, 9, 9, 9)
        self.save_btn.clicked.connect(lambda x: self.save_data())
        self.verticalLayout_4.addWidget(self.save_btn)
        self.add_default_rows()
        self.tabWidget.addTab(self.general_tab, "Основные")
        self.tabWidget.addTab(self.color_tab, "Цвет")
        self.tabWidget.addTab(self.descript_tab, "Описание")
        self.verticalLayout.addWidget(self.tabWidget)

        self.setWindowTitle("Добавить проект")
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def add_default_rows(self):
        default = [
            "Стоимость, руб/кг",
            "Цвет",
            "Блеск, у.е.",
            "Адгезия, балл",
            "Массовая доля нелетучих веществ, %",
            "Условная вязкость В3-4, сек",
            "Время высыхания до ст. 3, ч",
            "Время высыхания до ст. 5, ч",
            "Стойкость к NaCl 3%, ч",
            "Водостойкость, ч",
            "Прочность при ударе, см",
            "Прочность при изгибе, мм",
            "Тиксотропность, мм",
            "Термостойкость 100°С, ч",
        ]

        for i in default:
            self.add_row(text=i)

    def add_row(self, text="", value_text=""):
        row_param = QtWidgets.QWidget(parent=self.params_widget)
        horizontalLayout = QtWidgets.QHBoxLayout(row_param)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)
        name = CustomEntry(row_param)
        self.list_entry_name_obj.append(name)
        name.setText(text)
        horizontalLayout.addWidget(name)

        value = CustomEntry(parent=row_param)
        value.setText(value_text)
        value.setMaximumSize(QtCore.QSize(125, 16777215))
        self.list_entry_value_obj.append(value)
        horizontalLayout.addWidget(value)
        minus = HoverableButton(row_param, "minus", [16, 16])
        minus.clicked.connect(lambda _index=self.row, frame=row_param: self.del_row(_index, frame))
        minus.setObjectName("minus")
        horizontalLayout.addWidget(minus, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        self.verticalLayout_2.addWidget(row_param)
        self.row += 1

    def del_row(self, _index: int, row_w: QtWidgets.QWidget):
        self.list_entry_value_obj[_index] = None
        self.list_entry_name_obj[_index] = None
        row_w.deleteLater()

    def collect_data(self):
        data_params = []
        data_params_value = []
        for name, value in zip(self.list_entry_name_obj, self.list_entry_value_obj):
            name: QtWidgets.QLineEdit
            value: QtWidgets.QLineEdit
            if name is not None and value is not None:
                data_params.append(name.text())
                data_params_value.append(value.text())

        name_project = self.name_lineEdit.text().strip()
        description = self.textEdit.toPlainText()

        return (name_project, data_params, data_params_value, description)

    def save_data(self):
        password = ""
        name_project, data_params, data_params_value, description = self.collect_data()

        projects = os.listdir('saves/')
        if name_project not in projects and name_project != "":
            os.mkdir('saves/' + name_project)
            enc_data_params = []
            enc_data_params_value = []
            if name_project not in ['Тарировочные_кривые', 'Тарировочные кривые', 'Примеры']:
                for params, params_value in zip(data_params, data_params_value):
                    enc_data_params.append(Secrets().symmetric_encrypt(params.encode(), password))
                    enc_data_params_value.append(Secrets().symmetric_encrypt(params_value.encode(), password))
                description = Secrets().symmetric_encrypt(description.encode(), password)
            else:
                enc_data_params = data_params
                enc_data_params_value = data_params_value

            with SqliteDict('saves/' + name_project + '/params') as mydict:
                mydict['params'] = enc_data_params
                mydict['params_value'] = enc_data_params_value
                mydict['description'] = description
                mydict['project_color'] = self.project_color
                mydict.commit()
            Projects_Ui.instance.load_list_projects()
            self.closeEvent(None)
            self.destroy()

    def closeEvent(self, event):
        AddProjectWindow.instance = None

    def open_choice_color(self):
        if self.choice_color_window is None:
            self.choice_color_window = ChoiceColor(self, self.set_selected_color)
            self.choice_color_window.show()

    def set_selected_color(self, argb):
            image = QtGui.QPixmap(generate_color(argb))
            self.color_img.setPixmap(image)
            self.project_color = argb

class EditProjectWindow(AddProjectWindow):

    instance = None
    def __init__(self, project_name):
        self.project_name = project_name
        AddProjectWindow.instance = self
        super(EditProjectWindow, self).__init__(btn_type="edit_proj")
        self.setWindowTitle(f"Редактирование проекта - {self.project_name}")

    def add_default_rows(self):
        password = ""

        self.name_lineEdit.setText(self.project_name)
        dec_data_params = []
        dec_data_params_value = []
        with SqliteDict('saves/' + self.project_name + '/params') as mydict:
            enc_data_params = mydict['params']
            enc_data_params_value = mydict['params_value']
            description = mydict.get('description', None)
            self.project_color = mydict.get('project_color', "#00FFFFFF")
            self.set_selected_color(self.project_color)
            if self.project_name not in ['Тарировочные_кривые', 'Тарировочные кривые', 'Примеры']:
                for params, params_value in zip(enc_data_params, enc_data_params_value):
                    dec_data_params.append(Secrets().symmetric_decrypt(params, password).decode())
                    dec_data_params_value.append(Secrets().symmetric_decrypt(params_value, password).decode())
                if description:
                    description = Secrets().symmetric_decrypt(description, password).decode()
            else:
                dec_data_params = enc_data_params
                dec_data_params_value = enc_data_params_value


        self.textEdit.setText(description)
        for name, value in zip(dec_data_params, dec_data_params_value):
            self.add_row(text=name, value_text=value)

    def save_data(self):
        password = ""

        name_project = self.project_name
        edited_name_project, data_params, data_params_value, description = self.collect_data()

        projects = os.listdir('saves/')
        if name_project != edited_name_project:
            if edited_name_project not in projects:
                os.rename('saves/' + name_project, 'saves/' + edited_name_project)
                enc_data_params = []
                enc_data_params_value = []
                if edited_name_project not in ['Тарировочные_кривые', 'Примеры']:
                    for params, params_value in zip(data_params, data_params_value):
                        enc_data_params.append(Secrets().symmetric_encrypt(params.encode(), password))
                        enc_data_params_value.append(Secrets().symmetric_encrypt(params_value.encode(), password))
                    description = Secrets().symmetric_encrypt(description.encode(), password)
                else:
                    enc_data_params = data_params
                    enc_data_params_value = data_params_value

                with SqliteDict('saves/' + edited_name_project + '/params') as mydict:
                    mydict['params'] = enc_data_params
                    mydict['params_value'] = enc_data_params_value
                    mydict['description'] = description
                    mydict['project_color'] = self.project_color
                    mydict.commit()
        else:
            enc_data_params = []
            enc_data_params_value = []
            if edited_name_project not in ['Тарировочные_кривые', 'Примеры']:
                for params, params_value in zip(data_params, data_params_value):
                    enc_data_params.append(Secrets().symmetric_encrypt(params.encode(), password))
                    enc_data_params_value.append(Secrets().symmetric_encrypt(params_value.encode(), password))
                description = Secrets().symmetric_encrypt(description.encode(), password)
            else:
                enc_data_params = data_params
                enc_data_params_value = data_params_value

            with SqliteDict('saves/' + edited_name_project + '/params') as mydict:
                mydict['params'] = enc_data_params
                mydict['params_value'] = enc_data_params_value
                mydict['description'] = description
                mydict['project_color'] = self.project_color
                mydict.commit()

        Projects_Ui.instance.load_list_projects()
        Projects_Ui.instance.select_project(edited_name_project)
        self.closeEvent(None)
        self.destroy()

    def closeEvent(self, event):
        AddProjectWindow.instance = None

