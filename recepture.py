import copy

from PyQt6 import QtCore, QtGui, QtWidgets
from sqlitedict import SqliteDict

from common.secrets import Secrets
from common.ui_elements import HoverableButton, MenuButton
from database import DB
from typing import List

class ReceptureWindow(QtWidgets.QWidget):
    def __init__(self, project_name: str, iter_name: str, name: str):
        super(ReceptureWindow, self).__init__()
        self.project = project_name
        self.iter = iter_name
        self.name = name
        self.recepture_data = ReceptureDataModel(project_name, iter_name, name)
        self.recepture_data.load_data()

        self.list_comp_row_obj = []
        self.list_comp_2_row_obj = []

        self.setWindowTitle(self.name)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        toolbar = self.add_toolbar(self)
        self.verticalLayout_3.addWidget(toolbar)


        self.tabWidget = QtWidgets.QTabWidget(parent=self)
        self.tabWidget.setObjectName("tabWidget")

        self.recepture_tab = QtWidgets.QWidget()
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.recepture_tab)
        self.verticalLayout_2.setContentsMargins(9,0,9,9)
        self.verticalLayout_2.setSpacing(0)


        self.widget = QtWidgets.QWidget(parent=self.recepture_tab)
        self.widget.setObjectName("widget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        self.scrollArea = QtWidgets.QScrollArea(parent=self.widget)
        self.scrollArea.setMinimumSize(QtCore.QSize(400, 0))
        self.scrollArea.setMaximumSize(QtCore.QSize(400, 16777215))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.widget.setStyleSheet("""
                        QWidget#recepture{
                                  background: #f9f9f9;
                                  border: 0px solid black;
                                  }
                        QScrollArea#scrollArea{
                           background: #f9f9f9;
                           border: 0px solid #bbb;
                           }          
                                  """)
        self.recepture = QtWidgets.QWidget()
        self.recepture.setGeometry(QtCore.QRect(0, 0, 403, 485))
        self.recepture.setObjectName("recepture")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.recepture)
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.verticalLayout.setSpacing(2)




        # self.row_comment = QtWidgets.QWidget(parent=self.recepture)
        # self.row_comment.setObjectName("row_comment")
        # self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.row_comment)
        # self.horizontalLayout_5.setContentsMargins(25, 0, 0, 0)
        # self.horizontalLayout_5.setSpacing(0)
        # self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        # self.comment = QtWidgets.QPlainTextEdit(parent=self.row_comment)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.comment.sizePolicy().hasHeightForWidth())
        # self.comment.setSizePolicy(sizePolicy)
        # self.comment.setMaximumSize(QtCore.QSize(350, 40))
        # self.comment.setObjectName("comment")
        # self.horizontalLayout_5.addWidget(self.comment)
        # self.swap_2 = QtWidgets.QToolButton(parent=self.row_comment)
        # self.swap_2.setObjectName("swap_2")
        # self.horizontalLayout_5.addWidget(self.swap_2)
        # self.minus_2 = QtWidgets.QToolButton(parent=self.row_comment)
        # self.minus_2.setObjectName("minus_2")
        # self.horizontalLayout_5.addWidget(self.minus_2)
        # self.verticalLayout.addWidget(self.row_comment)

        self.component_one = QtWidgets.QWidget(self.recepture)
        self.component_one.setGeometry(QtCore.QRect(0, 0, 403, 485))
        self.component_one.setObjectName("recepture")
        self.component_one_l = QtWidgets.QVBoxLayout(self.component_one)
        self.component_one_l.setContentsMargins(0, 0, 0, 0)
        self.component_one_l.setSpacing(2)

        self.buttons = QtWidgets.QWidget(parent=self.component_one)
        self.buttons.setObjectName("buttons")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.buttons)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.btn_2k = HoverableButton(self.buttons, "2k", (20, 20))
        self.btn_2k.clicked.connect(self.show_2k)
        self.horizontalLayout_7.addWidget(self.btn_2k, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.plus = HoverableButton(self.buttons, "plus_2", (20, 20))
        self.plus.clicked.connect(lambda x: self.add_row("one"))
        self.horizontalLayout_7.addWidget(self.plus, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        self.component_one_l.addWidget(self.buttons)

        self.verticalLayout.addWidget(self.component_one)


        self.component_two = QtWidgets.QWidget(self.recepture)
        self.component_two.setGeometry(QtCore.QRect(0, 0, 403, 485))
        self.component_two.setObjectName("recepture")
        self.component_two_l = QtWidgets.QVBoxLayout(self.component_two)
        self.component_two_l.setContentsMargins(0, 0, 0, 0)
        self.component_two_l.setSpacing(2)

        self.plus_2 = MenuButton(self.component_two, "plus_2", (20, 20))
        self.plus_2.clicked.connect(lambda x: self.add_row("two"))
        self.component_two_l.addWidget(self.plus_2, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.component_two)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        for name, value in self.recepture_data.component_list:
            self.add_row("one", name=name, value=value)
        for name, value in self.recepture_data.component_list_2:
            self.add_row("two", name=name, value=value)

        if not self.recepture_data.flag_2k:
            self.component_two.hide()

        self.scrollArea.setWidget(self.recepture)
        self.horizontalLayout_6.addWidget(self.scrollArea)

        self.right_side = QtWidgets.QWidget(parent=self.widget)
        self.right_side.setObjectName("right_side")
        self.gridLayout = QtWidgets.QGridLayout(self.right_side)
        self.gridLayout.setObjectName("gridLayout")
        self.dict_data_l = QtWidgets.QLabel(parent=self.right_side)
        self.dict_data_l.setText("Дополнительные функции")
        self.gridLayout.addWidget(self.dict_data_l, 9, 0, 1, 1)
        self.count_para_l = QtWidgets.QLabel(parent=self.right_side)
        self.count_para_l.setObjectName("count_para_l")
        self.gridLayout.addWidget(self.count_para_l, 0, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem2, 11, 0, 1, 1)
        self.setting_count = QtWidgets.QPushButton(parent=self.right_side)
        self.setting_count.setObjectName("setting_count")
        self.gridLayout.addWidget(self.setting_count, 0, 1, 1, 1)
        self.recount_maslo_btn = QtWidgets.QPushButton(parent=self.right_side)
        self.recount_maslo_btn.setObjectName("recount_maslo_btn")
        self.gridLayout.addWidget(self.recount_maslo_btn, 6, 0, 1, 1)
        self.count_additives_btn = QtWidgets.QPushButton(parent=self.right_side)
        self.count_additives_btn.setObjectName("count_additives_btn")
        self.gridLayout.addWidget(self.count_additives_btn, 5, 0, 1, 1)
        self.count_btn = QtWidgets.QPushButton(parent=self.right_side)
        self.count_btn.setObjectName("count_btn")
        self.gridLayout.addWidget(self.count_btn, 3, 0, 1, 2)
        self.label_8 = QtWidgets.QLabel(parent=self.right_side)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 1, 1, 1, 1)
        self.recount_const = QtWidgets.QPushButton(parent=self.right_side)
        self.recount_const.setObjectName("recount_const")
        self.gridLayout.addWidget(self.recount_const, 8, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(parent=self.right_side)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.count_component_l = QtWidgets.QLabel(parent=self.right_side)
        self.count_component_l.setObjectName("count_component_l")
        self.gridLayout.addWidget(self.count_component_l, 4, 0, 1, 1)
        self.count_recepture_l = QtWidgets.QLabel(parent=self.right_side)
        self.count_recepture_l.setObjectName("count_recepture_l")
        self.gridLayout.addWidget(self.count_recepture_l, 7, 0, 1, 1)
        self.hardener_btn = QtWidgets.QPushButton(parent=self.right_side)
        self.hardener_btn.setObjectName("hardener_btn")
        self.gridLayout.addWidget(self.hardener_btn, 5, 1, 1, 1)
        self.recont_comb = QtWidgets.QPushButton(parent=self.right_side)
        self.recont_comb.setObjectName("recont_comb")
        self.gridLayout.addWidget(self.recont_comb, 8, 1, 1, 1)
        self.philum_btn = QtWidgets.QPushButton(parent=self.right_side)
        self.philum_btn.setObjectName("philum_btn")
        self.gridLayout.addWidget(self.philum_btn, 10, 0, 1, 1)
        take_account_btn = QtWidgets.QPushButton(parent=self.right_side)
        take_account_btn.setText("Списать компоненты")
        self.gridLayout.addWidget(take_account_btn, 10, 1, 1, 1)
        self.horizontalLayout_6.addWidget(self.right_side)
        self.verticalLayout_2.addWidget(self.widget)

        self.all_amount_w = QtWidgets.QWidget(parent=self.recepture_tab)
        self.all_amount_w.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.all_amount_w.setAutoFillBackground(False)
        self.all_amount_w.setObjectName("all_amount_w")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.all_amount_w)
        self.horizontalLayout_8.setSpacing(9)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.amount_all_l = QtWidgets.QLabel(parent=self.all_amount_w)
        self.amount_all_l.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.amount_all_l.setObjectName("amount_all_l")
        self.horizontalLayout_8.addWidget(self.amount_all_l)
        self.amount_all_value = QtWidgets.QLabel(parent=self.all_amount_w)
        self.amount_all_value.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.amount_all_value.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading | QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.amount_all_value.setObjectName("amount_all_value")
        self.horizontalLayout_8.addWidget(self.amount_all_value)
        self.recount_btn = QtWidgets.QToolButton(parent=self.all_amount_w)
        self.recount_btn.setObjectName("recount_btn")
        self.horizontalLayout_8.addWidget(self.recount_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        self.verticalLayout_2.addWidget(self.all_amount_w)

        self.tabWidget.addTab(self.recepture_tab, "")

        self.experimental_tab = QtWidgets.QWidget()
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.experimental_tab)
        self.verticalLayout_4.setContentsMargins(9, 0, 9, 9)
        self.exp_body_w = QtWidgets.QWidget(parent=self.experimental_tab)
        self.exp_body_w.setObjectName("exp_body_w")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.exp_body_w)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.exp_params_w = QtWidgets.QWidget(parent=self.exp_body_w)
        self.exp_params_w.setObjectName("exp_params_w")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.exp_params_w)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.name_l = QtWidgets.QLabel(parent=self.exp_params_w)
        self.name_l.setObjectName("name_l")
        self.gridLayout_2.addWidget(self.name_l, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 3, 0, 1, 1)
        self.gray_rb = QtWidgets.QRadioButton(parent=self.exp_params_w)
        self.gray_rb.setText("")
        self.gray_rb.setObjectName("gray_rb")
        self.gridLayout_2.addWidget(self.gray_rb, 2, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(parent=self.exp_params_w)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(parent=self.exp_params_w)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.green_rb = QtWidgets.QRadioButton(parent=self.exp_params_w)
        self.green_rb.setText("")
        self.green_rb.setObjectName("green_rb")
        self.gridLayout_2.addWidget(self.green_rb, 2, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(parent=self.exp_params_w)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 2, 1, 1)
        self.required_value_l = QtWidgets.QLabel(parent=self.exp_params_w)
        self.required_value_l.setMaximumSize(QtCore.QSize(100, 16777215))
        self.required_value_l.setObjectName("required_value_l")
        self.gridLayout_2.addWidget(self.required_value_l, 2, 1, 1, 1)
        self.exp_param_name_l = QtWidgets.QLabel(parent=self.exp_params_w)
        self.exp_param_name_l.setMinimumSize(QtCore.QSize(200, 0))
        self.exp_param_name_l.setObjectName("exp_param_name_l")
        self.gridLayout_2.addWidget(self.exp_param_name_l, 2, 0, 1, 1)
        self.recived_value_entry = QtWidgets.QLineEdit(parent=self.exp_params_w)
        self.recived_value_entry.setMaximumSize(QtCore.QSize(100, 16777215))
        self.recived_value_entry.setObjectName("recived_value_entry")
        self.gridLayout_2.addWidget(self.recived_value_entry, 2, 2, 1, 1)
        self.red_rb = QtWidgets.QRadioButton(parent=self.exp_params_w)
        self.red_rb.setText("")
        self.red_rb.setObjectName("red_rb")
        self.gridLayout_2.addWidget(self.red_rb, 2, 5, 1, 1)
        self.horizontalLayout_2.addWidget(self.exp_params_w)
        self.color_w = QtWidgets.QWidget(parent=self.exp_body_w)
        self.color_w.setObjectName("color_w")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.color_w)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.select_color_btn = QtWidgets.QPushButton(parent=self.color_w)
        self.select_color_btn.setObjectName("select_color_btn")
        self.gridLayout_3.addWidget(self.select_color_btn, 3, 0, 1, 2)
        self.lable_color2 = QtWidgets.QLabel(parent=self.color_w)
        self.lable_color2.setObjectName("lable_color2")
        self.gridLayout_3.addWidget(self.lable_color2, 1, 1, 1, 1)
        self.color1 = QtWidgets.QLabel(parent=self.color_w)
        self.color1.setObjectName("color1")
        self.gridLayout_3.addWidget(self.color1, 2, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_3.addItem(spacerItem4, 4, 0, 1, 1)
        self.lable_name = QtWidgets.QLabel(parent=self.color_w)
        self.lable_name.setObjectName("lable_name")
        self.gridLayout_3.addWidget(self.lable_name, 0, 0, 1, 1)
        self.color2 = QtWidgets.QLabel(parent=self.color_w)
        self.color2.setObjectName("color2")
        self.gridLayout_3.addWidget(self.color2, 2, 1, 1, 1)
        self.lable_color1 = QtWidgets.QLabel(parent=self.color_w)
        self.lable_color1.setObjectName("lable_color1")
        self.gridLayout_3.addWidget(self.lable_color1, 1, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.color_w)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.verticalLayout_4.addWidget(self.exp_body_w)
        self.tabWidget.addTab(self.experimental_tab, "")

        self.description_tab = QtWidgets.QWidget()
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.description_tab)
        self.verticalLayout_5.setContentsMargins(9, 0, 9, 9)
        self.description = QtWidgets.QTextEdit(parent=self.description_tab)
        self.description.setObjectName("description")
        self.verticalLayout_5.addWidget(self.description)
        self.tabWidget.addTab(self.description_tab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)

        self.retranslateUi(self)
        self.tabWidget.setCurrentIndex(0)

    def add_toolbar(self, parent: QtWidgets) -> QtWidgets.QFrame:
        toolbar = QtWidgets.QFrame(parent=parent)
        toolbar.setObjectName("toolbarBg")
        toolbar.setStyleSheet("""
        QFrame#toolbarBg{
        }
        
        """)
        toolbar.setContentsMargins(9,0,9,0)

        horizontalLayout_3 = QtWidgets.QHBoxLayout(toolbar)
        horizontalLayout_3.setSpacing(4)
        name_recepture = QtWidgets.QLabel(parent=toolbar)
        name_recepture.setContentsMargins(5,0,25,0)
        name_recepture.setText(self.name)
        horizontalLayout_3.addWidget(name_recepture)
        font = QtGui.QFont()
        font.setPointSize(18)
        name_recepture.setFont(font)
        save_btn = HoverableButton(toolbar, "save", (20,20))
        horizontalLayout_3.addWidget(save_btn)
        save_as_btn = HoverableButton(toolbar, "save_as", (20,20))
        horizontalLayout_3.addWidget(save_as_btn)
        word_btn = HoverableButton(toolbar, "word", (20,20))
        horizontalLayout_3.addWidget(word_btn)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        horizontalLayout_3.addItem(spacerItem)
        delete_btn = HoverableButton(toolbar, "del_rec", (20,20))
        horizontalLayout_3.addWidget(delete_btn)



        return toolbar

    def show_2k(self, event):
        check = self.recepture_data.flag_2k
        if check:
            self.component_two.hide()
            self.recepture_data.flag_2k = False
        else:
            self.component_two.show()
            self.recepture_data.flag_2k = True

    def add_row(self, _type, name="", value=""):
        parent = self.component_one if _type == "one" else self.component_two
        list_obj = self.list_comp_row_obj if _type == "one" else self.list_comp_2_row_obj
        loyout = self.component_one_l if _type == "one" else self.component_two_l
        add_widget = self.buttons if _type == "one" else self.plus_2
        loyout.removeWidget(add_widget)

        _index = len(list_obj)
        row = ComponentRow(parent, _index, name=name, amount=value, list_obj=list_obj)
        loyout.addWidget(row)
        loyout.addWidget(add_widget)
        list_obj.append(row)
        self.reset_row_number(_type)

    def reset_row_number(self, _type: str):
        list_obj: List[ComponentRow]
        list_obj = self.list_comp_row_obj if _type == "one" else self.list_comp_2_row_obj
        number = 1
        for obj in list_obj:
            if obj is not None:
                obj.set_number(number)
                number += 1





    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


        # self.swap_2.setText(_translate("MainWindow", "..."))
        # self.minus_2.setText(_translate("MainWindow", "..."))
        # self.btn_2k.setText(_translate("MainWindow", "2k"))
        # self.plus.setText(_translate("MainWindow", "+"))
        self.amount_all_l.setText(_translate("MainWindow", "Итого:"))
        self.amount_all_value.setText(_translate("MainWindow", "100.00"))
        self.recount_btn.setText(_translate("MainWindow", "..."))

        self.count_para_l.setText(_translate("MainWindow", "Расчетные параметры"))
        self.setting_count.setText(_translate("MainWindow", "Настройки"))
        self.recount_maslo_btn.setText(_translate("MainWindow", "Заменить по маслоемкости"))
        self.count_additives_btn.setText(_translate("MainWindow", "Расчет функц. добавок"))
        self.count_btn.setText(_translate("MainWindow", "Рассчитать"))
        self.label_8.setText(_translate("MainWindow", "TextLabel"))
        self.recount_const.setText(_translate("MainWindow", "По константе наполнения"))
        self.label_7.setText(_translate("MainWindow", "TextLabel"))
        self.count_component_l.setText(_translate("MainWindow", "Расчет компонентов"))
        self.count_recepture_l.setText(_translate("MainWindow", "Расчет рецептур"))
        self.hardener_btn.setText(_translate("MainWindow", "Расчет отвердителя"))
        self.recont_comb.setText(_translate("MainWindow", "Комбинированный"))
        self.philum_btn.setText(_translate("MainWindow", "Филумы пигментов"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.recepture_tab), _translate("MainWindow", "Рецептура"))
        self.name_l.setText(_translate("MainWindow", "Название"))
        self.label_3.setText(_translate("MainWindow", "Требуемое \n"
                                                      "значение"))
        self.label.setText(_translate("MainWindow", "Экспериментальные значения"))
        self.label_4.setText(_translate("MainWindow", "Полученное \n"
                                                      "значение"))
        self.required_value_l.setText(_translate("MainWindow", "50"))
        self.exp_param_name_l.setText(_translate("MainWindow", "Укрывистость"))
        self.select_color_btn.setText(_translate("MainWindow", "Выбрать цвет"))
        self.lable_color2.setText(_translate("MainWindow", "Полученный цвет"))
        self.color1.setText(_translate("MainWindow", "цвет1"))
        self.lable_name.setText(_translate("MainWindow", "Цвет"))
        self.color2.setText(_translate("MainWindow", "цвет2"))
        self.lable_color1.setText(_translate("MainWindow", "Требуемый цвет"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.experimental_tab),
                                  _translate("MainWindow", "Эксперимент"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.description_tab), _translate("MainWindow", "Заметки"))


class ComponentRow(QtWidgets.QWidget):
    def __init__(self, parent, _index, name="aa", amount="", list_obj=None):
        super(ComponentRow, self).__init__(parent=parent)
        self.db = DB()
        self.category = ""
        self.list_obj = list_obj

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(3)

        self.category_icon = QtWidgets.QLabel(parent=self)
        self.category_icon.setMaximumSize(QtCore.QSize(16, 16))
        self.category_icon.setMinimumSize(QtCore.QSize(16, 16))
        self.category_icon.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.category_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.category_icon.setScaledContents(True)
        self.horizontalLayout_4.addWidget(self.category_icon)
        self.assign_category(name)

        self.number_l = QtWidgets.QLabel(parent=self)
        self.number_l.setMaximumSize(QtCore.QSize(16, 16))
        self.number_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.number_l.setMinimumSize(QtCore.QSize(16, 16))
        self.horizontalLayout_4.addWidget(self.number_l)

        self.name_comp = QtWidgets.QComboBox(parent=self)
        self.name_comp.setEditable(True)
        self.name_comp.setEditText(name)
        self.name_comp.setMinimumSize(QtCore.QSize(250, 0))

        self.horizontalLayout_4.addWidget(self.name_comp)
        self.amount = QtWidgets.QLineEdit(parent=self)
        self.amount.setText(amount)
        self.amount.setMaximumSize(QtCore.QSize(50, 16777215))
        self.horizontalLayout_4.addWidget(self.amount)

        # self.minus = HoverableButton(self, "minus_2", (10, 10))
        # self.minus.clicked.connect(self.delete)
        # self.horizontalLayout_4.addWidget(self.minus)

        self.swap = HoverableButton(self, "swap", (5, 15))
        menu = QtWidgets.QMenu(self)
        menu.addAction('Сделать комментарием', self.delete)
        menu.addAction('Удалить', self.delete)

        self.swap.setMenu(menu)
        self.horizontalLayout_4.addWidget(self.swap)

        spacerItem5 = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(spacerItem5)

    def assign_category(self, name):
        text = ""
        tooltip = ""
        if len(self.db.check_group_reactives("Solvents", name)) == 1:
            self.category = "Solvents"
            icon_path = "images/solvent.png"
            tooltip = "Растворитель"
        elif len(self.db.check_group_reactives("Pigments", name)) == 1:
            self.category = "Pigments"
            icon_path = "images/pigment.png"
            tooltip = "Пигмент"
        elif len(self.db.check_group_reactives("Fillers", name)) == 1:
            self.category = "Fillers"
            icon_path = "images/filler.png"
            tooltip = "Наполнитель"
        elif len(self.db.check_group_reactives("Films", name)) == 1:
            self.category = "Films"
            icon_path = "images/film.png"
            tooltip = "Пленкообразователь"
        elif len(self.db.check_group_reactives("Additives", name)) == 1:
            self.category = "Additives"
            icon_path = "images/additive.png"
            tooltip = "Функц. добавка"
        elif len(self.db.check_group_reactives("PigmPast", name)) == 1:
            self.category = "PigmPast"
            icon_path = "images/pigm_past.png"
            tooltip = "Пигментная паста"
        elif len(self.db.check_group_reactives("Hardener", name)) == 1:
            self.category = "Hardener"
            icon_path = "images/hardener.png"
            tooltip = "Отвердитель"
        else:
            self.category = ""
            icon_path = ""
            text = "?"
            tooltip = "Поле пустое или компонент не найден"

        self.category_icon.setText(text) if text != "" else self.category_icon.setPixmap(QtGui.QPixmap(icon_path))
        self.category_icon.setToolTip(tooltip)

    def set_number(self, number: int):
        self.number_l.setText(str(number))

    def delete(self, event=None):
        index = self.list_obj.index(self)
        self.list_obj[index] = None
        self.hide()
        self.reset_row_number()
        self.name_comp.setFocus()

    def reset_row_number(self):
        number = 1
        for obj in self.list_obj:
            if obj is not None:
                obj.set_number(number)
                number += 1

class ReceptureDataModel:
    def __init__(self, project, iteration, name):
        self.project = project
        self.iteration = iteration
        self.name = name
        self.not_encoded_projects = ['Тарировочные_кривые', 'Тарировочные кривые', 'Примеры']

        self.project_params = []
        self.project_params_value = []
        self.password = ""
        self.component_list = [("", "") for i in range(7)]
        self.component_list_2 =  [("", "") for i in range(3)]
        self.experiment_list = []
        self.notes = ""

        self.flag_2k = False
        self.price_K = 1.0
        self.accurate_density = 0.0

        self.price = 0
        self.mass_unflyable = 0
        self.sp = 0
        self.okp = 0
        self.oil = 0
        self.kn = 0
        self.hiding_pigm = 0
        self.hiding_wet = 0
        self.philum = 0
        self.kokp = 0
        self.hiding_dry = 0
        self.density = 0

    def map_encrypt(self, str):
        global password
        if self.project not in self.not_encoded_projects:
            result = Secrets().symmetric_encrypt(str.encode(), password)
        else:
            result = str
        return result

    def map_decrypt(self, byte):
        if self.project not in self.not_encoded_projects:
            result = Secrets().symmetric_decrypt(byte, password).decode()
        else:
            result = byte
        return result

    def load_data(self):
        with SqliteDict('saves/' + self.project + '/params') as mydict:
            enc_data_params = mydict['params']
            enc_data_params_value = mydict['params_value']
            if self.project not in self.not_encoded_projects:
                for params, params_value in zip(enc_data_params, enc_data_params_value):
                    self.project_params.append(Secrets().symmetric_decrypt(params, self.password).decode())
                    self.project_params_value.append(Secrets().symmetric_decrypt(params_value, self.password).decode())
            else:
                self.project_params = enc_data_params
                self.project_params_value = enc_data_params_value


        with SqliteDict('saves/' + self.project + '/' + self.iteration) as mydict:
            data_iteraton = dict(mydict)
            self.data = data_iteraton.get(self.name, None)

            # [0] - реактивы, [1]- масса реактивов, [2] - эксперимент параметры,
            # [3] - полученны значения, [4] - заметки, [5] - ТЗ, [6] - расчетные характеристики,
            # [7] - реактивы 2к, [8] - масса реактивов 2к, [9] - dict params
        if self.data is None:
            return

        if len(self.data) > 9:
            configs = self.data.pop(9)
            self.price_K = configs.get('price_K', 1.0)
            self.accurate_density = configs.get('accurate_density', 0.0)

        for i, param in enumerate(self.data):
            self.data[i] = list(map(self.map_decrypt, param))

        self.component_list = list(zip(self.data[0], self.data[1]))
        self.component_list_2 = list(zip(self.data[7], self.data[8]))
        self.experiment_list = list(zip(self.data[2], self.data[5], self.data[3]))
        self.notes = self.data[4]

        # self.properies=['Цена','м.д.н.в','СП','ОКП','Масло','Кп','Ср укрыв','Укрыв сух пленки','Филум', 'КОКП', 'Укр мокрой пл', 'плотность']
        properties = self.data[6]
        self.price = properties[0]
        self.mass_unflyable = properties[1]
        self.sp = properties[2]
        self.okp = properties[3]
        self.oil = properties[4]
        self.kn = properties[5]
        self.hiding_pigm = properties[6]
        self.hiding_wet = properties[7]
        self.philum = properties[8]
        self.kokp = properties[9]
        self.hiding_dry = properties[10]
        self.density = properties[11]

        for comp in self.component_list_2:
            if comp[0] != '' and comp[1] != '':
                self.flag_2k = True

    def collect_data(self):
        pass

    def save_data(self, event=None):
        self.collect_data()

        # [0] - реактивы, [1]- масса реактивов, [2] - эксперимент параметры,
        # [3] - полученны значения, [4] - заметки, [5] - ТЗ, [6] - расчетные характеристики,
        # [7] - реактивы 2к, [8] - масса реактивов 2к, [9] - dict params

        reactives = []
        reactives_mass = []
        reactives_2 = []
        reactives_mass_2 = []
        experiment_params = []
        experiment_value = []
        needed_experiment_value = []
        dict_params = {}

        for name, value in self.component_list:
            reactives.append(name)
            reactives_mass.append(value)
        for name, value in self.component_list_2:
            reactives_2.append(name)
            reactives_mass_2.append(value)
        for name, need, value in self.experiment_list:
            experiment_params.append(name)
            experiment_value.append(value)
            needed_experiment_value.append(need)

        properies = [
            self.price,
            self.mass_unflyable,
            self.sp,
            self.okp,
            self.oil,
            self.kn,
            self.hiding_pigm,
            self.hiding_wet,
            self.philum,
            self.kokp,
            self.hiding_dry,
            self.density,
        ]

        dict_params['price_K'] = self.price_K
        dict_params['accurate_density'] =  self.accurate_density

        with SqliteDict('saves/' + self.project + '/' + self.iteration) as mydict:
            mydict[self.name] = [list(map(self.map_encrypt, reactives)),
                                 list(map(self.map_encrypt, reactives_mass)),
                                 list(map(self.map_encrypt, experiment_params)),
                                 list(map(self.map_encrypt, experiment_value)),
                                 list(map(self.map_encrypt, [self.notes, ]))[0],
                                 list(map(self.map_encrypt, needed_experiment_value)),
                                 list(map(self.map_encrypt, properies)),
                                 list(map(self.map_encrypt, reactives_2)),
                                 list(map(self.map_encrypt, reactives_mass_2)),
                                 dict_params,
                                 ]
            mydict.commit()
