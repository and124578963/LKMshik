import copy
import logging
from decimal import Decimal
from functools import reduce

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QCompleter
from sqlitedict import SqliteDict

from common.secrets import Secrets
from common.ui_elements import HoverableButton, MenuButton
from component_card import CustomEntry
from database import DB
from typing import List, Tuple
import xml.etree.ElementTree as ET
import requests
from newReactives import InfoWindow, DarkBtn_Ui
from settings import get_suhoi_type


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

        self.left_side =  QtWidgets.QWidget(parent=self.widget)
        self.left_side.setMaximumSize(QtCore.QSize(390, 16777215))
        self.horizontalLayout_6.addWidget(self.left_side)
        self.left_vertical_lo = QtWidgets.QVBoxLayout(self.left_side)
        self.left_vertical_lo.setContentsMargins(0,0,0,0)
        self.left_vertical_lo.setSpacing(0)

        self.scrollArea = QtWidgets.QScrollArea(parent=self.widget)
        self.scrollArea.setMinimumSize(QtCore.QSize(390, 0))
        self.scrollArea.setMaximumSize(QtCore.QSize(390, 16777215))
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
        self.left_vertical_lo.addWidget(self.scrollArea)

        self.right_side = QtWidgets.QWidget(parent=self.widget)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.right_side)
        self.verticalLayout_6.setSpacing(3)
        self.verticalLayout_6.setContentsMargins(0,0,0,0)
        self.right_side.setMaximumSize(350, 999999)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_params_l = QtWidgets.QLabel(parent=w)
        self.count_params_l.setText("Расчетные параметры")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.count_params_l.setFont(font)
        lo.addWidget(self.count_params_l)
        self.setting_count = HoverableButton(w, "settings", (16,16))
        lo.addWidget(self.setting_count, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        lo.setContentsMargins(0,0,0,9)


        self.price_l = QtWidgets.QLabel(parent=self.right_side)
        self.price_l.setText("Стоимость:")
        self.verticalLayout_6.addWidget(self.price_l)

        self.density_l = QtWidgets.QLabel(parent=self.right_side)
        self.density_l.setText("Плотность:")
        self.verticalLayout_6.addWidget(self.density_l)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.suhoi_l = QtWidgets.QLabel(parent=w)
        self.suhoi_l.setText("Масс.д.н.в:")
        lo.addWidget(self.suhoi_l)

        self.volume_suhoi_l = QtWidgets.QLabel(parent=w)
        self.volume_suhoi_l.setText("Объем.д.н.в:")
        lo.addWidget(self.volume_suhoi_l)


        self.oil_l = QtWidgets.QLabel(parent=self.right_side)
        self.oil_l.setText("Маслоемкость 1-го рода:")
        self.verticalLayout_6.addWidget(self.oil_l)

        self.philum_l = QtWidgets.QLabel(parent=self.right_side)
        self.philum_l.setText("Филум пигментов:")
        self.verticalLayout_6.addWidget(self.philum_l)

        self.degree_pigm_l = QtWidgets.QLabel(parent=self.right_side)
        self.degree_pigm_l.setText("Степень пигментирования:")
        self.verticalLayout_6.addWidget(self.degree_pigm_l)

        self.const_pigm_l = QtWidgets.QLabel(parent=self.right_side)
        self.const_pigm_l.setText("Константа наполнения:")
        self.verticalLayout_6.addWidget(self.const_pigm_l)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.okp_l = QtWidgets.QLabel(parent=w)
        self.okp_l.setText("ОКП:")
        lo.addWidget(self.okp_l)

        self.kokp_l = QtWidgets.QLabel(parent=w)
        self.kokp_l.setText("КОКП:")
        lo.addWidget(self.kokp_l)

        self.okp_kokp_l = QtWidgets.QLabel(parent=w)
        self.okp_kokp_l.setText("ОКП/КОКП:")
        lo.addWidget(self.okp_kokp_l)

        self.hiding_pigm_l = QtWidgets.QLabel(parent=self.right_side)
        self.hiding_pigm_l.setText("Укрывистость пигментов:")
        self.verticalLayout_6.addWidget(self.hiding_pigm_l)

        self.hiding_wet_l = QtWidgets.QLabel(parent=self.right_side)
        self.hiding_wet_l.setText("Укрывистость мокрой пленки:")
        self.verticalLayout_6.addWidget(self.hiding_wet_l)

        self.hiding_dry_l = QtWidgets.QLabel(parent=self.right_side)
        self.hiding_dry_l.setText("Укрывистость сухой пленки:")
        self.verticalLayout_6.addWidget(self.hiding_dry_l)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_btn = DarkBtn_Ui(w, "calc")
        self.count_btn.clicked.connect(self.count_all)
        lo.addWidget(self.count_btn)
        lo.setContentsMargins(0,9,0,9)


        l = QtWidgets.QLabel(parent=self.right_side)
        l.setText("Расчет компонентов")
        self.verticalLayout_6.addWidget(l,alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_additives_btn = QtWidgets.QPushButton(parent=w)
        self.count_additives_btn.setText("Расчет функц. добавок")
        lo.addWidget(self.count_additives_btn)

        self.hardener_btn = QtWidgets.QPushButton(parent=w)
        self.hardener_btn.setText("Расчет отвердителя")
        lo.addWidget(self.hardener_btn)


        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.recount_maslo_btn = QtWidgets.QPushButton(parent=w)
        self.recount_maslo_btn.setText("Заменить по маслоемкости")
        lo.addWidget(self.recount_maslo_btn)

        l = QtWidgets.QLabel(parent=self.right_side)
        l.setText("Расчет рецептур")
        self.verticalLayout_6.addWidget(l, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.recount_const = QtWidgets.QPushButton(parent=w)
        self.recount_const.setText("По константе наполнения")
        lo.addWidget(self.recount_const)

        self.recont_comb = QtWidgets.QPushButton(parent=w)
        self.recont_comb.setText( "Комбинированный")
        lo.addWidget(self.recont_comb)


        l = QtWidgets.QLabel(parent=self.right_side)
        l.setText("Дополнительные функции")
        self.verticalLayout_6.addWidget(l, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        w, lo = self.create_w_lo(self.right_side, self.verticalLayout_6)
        self.philum_btn = QtWidgets.QPushButton(w)
        self.philum_btn.setText("Филумы пигментов")
        lo.addWidget(self.philum_btn)


        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_6.addItem(spacerItem2)
        self.horizontalLayout_6.addWidget(self.right_side)
        self.verticalLayout_2.addWidget(self.widget)

        self.all_amount_w = QtWidgets.QWidget(parent=self.left_side)
        space = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.all_amount_w)
        self.horizontalLayout_8.setContentsMargins(0,9,30,9)
        self.horizontalLayout_8.setSpacing(9)
        self.horizontalLayout_8.addItem(space)
        self.amount_all_l = QtWidgets.QLabel(parent=self.all_amount_w)
        self.amount_all_l.setText( "Итого:")
        self.horizontalLayout_8.addWidget(self.amount_all_l)
        self.amount_all_value = QtWidgets.QLabel(parent=self.all_amount_w)
        self.horizontalLayout_8.addWidget(self.amount_all_value)
        self.recount_btn = HoverableButton(self.all_amount_w, "menu", (16,16))
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(
            """
            QMenu
            {
                font: 12pt;
                background-color: #eee;
            }
            QMenu::item:selected
            {
                background-color: #209fa6
            }
            """
        )
        menu.addAction('Списать компоненты', lambda :print(1))
        menu.addAction('Пересчитать массу', lambda :print(1))
        menu.addAction('Довести растворителем', lambda :print(1))

        self.recount_btn.setMenu(menu)

        self.horizontalLayout_8.addWidget(self.recount_btn)
        self.left_vertical_lo.addWidget(self.all_amount_w)

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

        self.count_mass()

    def create_w_lo(self, parent_w: QtWidgets.QWidget, parent_lo: QtWidgets.QBoxLayout) -> \
            Tuple[QtWidgets.QWidget, QtWidgets.QBoxLayout]:
        w = QtWidgets.QWidget(parent=parent_w)
        lo = QtWidgets.QHBoxLayout(w)
        lo.setSpacing(5)
        lo.setContentsMargins(0,0,0,0)
        parent_lo.addWidget(w)
        return w, lo


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
        self.btn_2k.set_pressed()
        self.count_mass()

    def add_row(self, _type, name="", value=""):
        parent = self.component_one if _type == "one" else self.component_two
        list_obj = self.list_comp_row_obj if _type == "one" else self.list_comp_2_row_obj
        loyout = self.component_one_l if _type == "one" else self.component_two_l
        add_widget = self.buttons if _type == "one" else self.plus_2
        loyout.removeWidget(add_widget)

        _index = len(list_obj)
        row = ComponentRow(parent, _index, name=name, amount=value, list_obj=list_obj, callback_mass=self.count_mass)
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

    def collect_rows_data(self):
        list_comp_1 = [i.get_data() for i in self.list_comp_row_obj]
        list_comp_category_1 = [i.get_category() for i in self.list_comp_row_obj]
        list_comp_2 = [i.get_data() for i in self.list_comp_2_row_obj]
        list_comp_category_2 = [i.get_category() for i in self.list_comp_2_row_obj]
        self.recepture_data.component_list = list_comp_1
        self.recepture_data.component_list_2 = list_comp_2
        self.recepture_data.category_list = list_comp_category_1
        self.recepture_data.category_list_2 = list_comp_category_2

    def count_mass(self, collected=False):
        print(collected)
        if not collected:
            self.collect_rows_data()
        mass = self.recepture_data.count_mass(all=True)
        mass = self.normalize_number(mass)
        self.amount_all_value.setText(mass)

    def count_all(self):
        self.collect_rows_data()
        self.count_mass(collected=True)
        self.recepture_data.all_count()
        data = self.recepture_data
        list_update_lable_value = (
            (self.price_l, data.price, "руб/кг"),
            (self.oil_l, data.oil, "г/100 г"),
            (self.suhoi_l, data.suhoi, "%"),
            (self.volume_suhoi_l, data.volume_suhoi, "%"),
            (self.okp_l, data.okp, "%"),
            (self.kokp_l, data.kokp, "%"),
            (self.okp_kokp_l, data.okp_kokp, "%"),
            (self.hiding_pigm_l, data.hiding_pigm, "г/м²"),
            (self.hiding_wet_l, data.hiding_wet, "г/м²"),
            (self.hiding_dry_l, data.hiding_dry, "г/м²"),
            (self.philum_l, data.philum, ""),
            (self.density_l, data.get_density(), "г/см³"),
            (self.degree_pigm_l, data.degree_pigm, ""),
            (self.const_pigm_l, data.const_pigm, ""),
        )
        for lable, value, size in list_update_lable_value:
            self.update_lable_param(lable, value, size)


    def normalize_number(self, number: Decimal) -> str:
        normalized = number.normalize()
        sign, digit, exponent = normalized.as_tuple()
        normalized = normalized if exponent <= 0 else normalized.quantize(1)
        normalized = normalized.quantize(Decimal("1.00"), "ROUND_HALF_EVEN")
        normalized = str(normalized).replace(".", ",")
        return normalized

    def update_lable_param(self, lable: QtWidgets.QLabel, new_value: Decimal, size: str):
        text = lable.text()
        value = self.normalize_number(new_value)
        _index = text.index(":") + 1
        text =  f"{text[:_index]} {value} {size}"
        lable.setText(text)



class ComponentRow(QtWidgets.QWidget):
    def __init__(self, parent, _index, name="", amount="", list_obj=None, callback_mass=None):
        super(ComponentRow, self).__init__(parent=parent)
        self.callback_mass = callback_mass
        self.db = DB()
        self.category = ""
        self.list_obj = list_obj
        self.flag_comment = False
        self.component_list = []
        self.event_list = []

        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeAllCursor))
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

        list_all_names = self.db.search("%%")
        self.name_comp = SearchCombobox(self, list_all_names)
        self.name_comp.setText(name)
        self.name_comp.setMinimumSize(QtCore.QSize(250, 0))
        self.name_comp.textChanged.connect(self.name_changed)


        self.horizontalLayout_4.addWidget(self.name_comp)
        self.amount = CustomEntry(self, padding=False)
        self.amount.setText(amount)
        self.amount.setMaximumSize(QtCore.QSize(50, 16777215))
        self.amount.setMinimumSize(QtCore.QSize(50, 16777215))
        self.amount.textChanged.connect(lambda event: callback_mass())
        reg_ex = QRegularExpression(r"[0-9]*[\,,.]{1}[0-9]*")
        validator = QRegularExpressionValidator(reg_ex)
        self.amount.setValidator(validator)
        self.horizontalLayout_4.addWidget(self.amount)

        self.comment_spacer = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Fixed,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.comment_spacer.changeSize(0, 0)
        self.horizontalLayout_4.addItem(self.comment_spacer)
        self.comment = QtWidgets.QPlainTextEdit(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comment.sizePolicy().hasHeightForWidth())
        self.comment.setSizePolicy(sizePolicy)
        # self.comment.setContentsMargins(32,0,0,0)
        self.comment.setMinimumSize(QtCore.QSize(303, 40))
        self.horizontalLayout_4.addWidget(self.comment)
        self.comment.hide()

        self.swap = MenuButton(self, "swap", (20, 20))
        self.swap.setMaximumSize(QtCore.QSize(20, 20))

        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(
            """
            QMenu
            {
                font: 12pt;
                background-color: #eee;
            }
            QMenu::item:selected
            {
                background-color: #209fa6
            }
            """
            )
        menu.addAction('Сделать комментарием', self.change_state)
        menu.addAction('Удалить', self.delete)

        self.swap.setMenu(menu)
        self.horizontalLayout_4.addWidget(self.swap)

        spacerItem5 = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(spacerItem5)

    def change_state(self):
        if self.flag_comment:
            self.flag_comment = False
            self.category_icon.show()
            self.number_l.show()
            self.name_comp.show()
            self.amount.show()

            self.comment.hide()
            self.comment_spacer.changeSize(0, 0)
            menu = QtWidgets.QMenu(self)
            menu.addAction('Сделать комментарием', self.change_state)
            menu.addAction('Удалить', self.delete)

            self.swap.setMenu(menu)
            self.reset_row_number()

        else:
            self.flag_comment = True
            self.category_icon.hide()
            self.number_l.hide()
            self.name_comp.hide()
            self.amount.hide()

            self.comment.show()
            self.comment_spacer.changeSize(38, 10)
            menu = QtWidgets.QMenu(self)
            menu.addAction('Сделать компонентом', self.change_state)
            menu.addAction('Удалить', self.delete)

            self.swap.setMenu(menu)
            self.reset_row_number()
        self.callback_mass()

        menu.setStyleSheet(
            """
            QMenu
            {
                font: 10pt;
                background-color: #eee;
            }
            QMenu::item:selected
            {
                background-color: #209fa6
            }
            """
            )

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

    def name_changed(self, event):
        self.assign_category(event)

    def reset_row_number(self):
        self.list_obj: List[ComponentRow]
        number = 1
        for obj in self.list_obj:
            if obj is not None:
                if not obj.flag_comment:
                    obj.set_number(number)
                    number += 1

    def get_data(self):
        #если 1 элемент, то комментарий, если 2, то компонент
        if self.flag_comment:
            return self.comment.toPlainText()
        else:
            return self.name_comp.text(),  self.amount.text()

    def get_category(self):
        return self.category


class ReceptureDataModel:
    def __init__(self, project, iteration, name):
        self.project = project
        self.iteration = iteration
        self.name = name
        self.not_encoded_projects = ['Тарировочные_кривые', 'Тарировочные кривые', 'Примеры']

        self.project_params = []
        self.project_params_value = []
        self.password = ""
        self.component_list = [("", "") for _ in range(7)]
        self.category_list = ["" for _ in range(7)]
        self.component_list_2 = [("", "") for _ in range(3)]
        self.category_list_2 = ["" for _ in range(7)]
        self.experiment_list = []
        self.notes = ""

        self.flag_2k = False
        self.price_K = 1.0
        self.accurate_density = 0.0

        self.mass = Decimal(0)
        self.price = Decimal(0)
        self.suhoi = Decimal(0)
        self.degree_pigm = Decimal(0)
        self.oil = Decimal(0)
        self.const_pigm = Decimal(0)
        self.hiding_pigm = Decimal(0)
        self.hiding_wet = Decimal(0)
        self.hiding_dry = Decimal(0)
        self.philum = Decimal(0)
        self.okp = Decimal(0)
        self.kokp = Decimal(0)
        self.okp_kokp = Decimal(0)
        self.hiding_dry = Decimal(0)
        self.density = Decimal(0)
        self.volume_suhoi = Decimal(0)

    def get_density(self):
        if self.accurate_density > 0.0:
            return Decimal(self.accurate_density)
        else:
            return self.density

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

    def count_mass(self, all=False) -> Decimal:
        components, _ = self.get_actual_data_for_count(all=all)
        components = list(map(lambda x: Decimal(x[1].replace(",", ".")), components))
        summ = reduce(lambda x, y: x + y, components)
        self.mass = summ
        return self.mass

    def get_actual_data_for_count(self, all=False) -> Tuple[tuple, str]:
        # retrun [((name, value), category), ...]
        # retrun [((comment,), category), ...]

        if self.flag_2k:
            components = self.component_list + self.component_list_2
            categories = self.category_list + self.category_list_2
        else:
            components = self.component_list
            categories = self.category_list

        data = list(zip(components, categories))
        data = list(filter(lambda foo: len(foo[0]) > 1, data))
        if all:
            data = list(filter(lambda foo: len(foo[0][1]) > 0, data))
        else:
            data = list(filter(lambda foo: foo[1] != "", data))

        components, categories = list(zip(*data))
        return components, categories

    def create_category_objs(self):
        components, categories = self.get_actual_data_for_count()

        self.list_of_solvent_objects = []
        self.list_of_pigment_objects = []
        self.list_of_filler_objects = []
        self.list_of_film_objects = []
        self.list_of_additive_objects = []
        self.list_of_pigmpast_objects = []
        self.list_of_hardener_objects = []

        for (name, mass), cat in zip(components, categories):
            if cat == "Solvents":
                self.list_of_solvent_objects.append(Solvents(name, mass))
            elif cat == "Pigments":
                self.list_of_pigment_objects.append(Pigments(name, mass))
            elif cat == "Fillers":
                self.list_of_filler_objects.append(Fillers(name, mass))
            elif cat == "Films":
                self.list_of_film_objects.append(Films(name, mass))
            elif cat == "Additives":
                self.list_of_additive_objects.append(Additives(name, mass))
            elif cat == "PigmPast":
                self.list_of_pigmpast_objects.append(Pigmpasts(name, mass))
            elif cat == "Hardener":
                self.list_of_hardener_objects.append(Hardeners(name, mass))
            else:
                pass

    def all_count(self):
        info_text = ""
        self.count_mass()
        self.create_category_objs()

        list_count_funcs = [(self.count_price, "Ошибка в расчете цены. Переведите валюту в Руб."),
                            (self.all_mass_for_suhoi_f, "Ошибка в расчете массы"),
                            (self.all_suhoi_in_objects, "Ошибка при расчете м.д.н.в."),
                            (lambda: self.all_suhoi_in_objects(for_volume=True), "Ошибка при расчете м.д.н.в."),
                            (self.all_density_in_objects, "Ошибка в расчете плотности"),
                            (self.all_degree_pigm_in_objects, "Ошибка в расчете степени пигм."),
                            (self.all_okp_in_objects, "Ошибка в расчете ОКП"),
                            (self.all_oil_in_objects, "Ошибка в расчете маслоемкости"),
                            (self.all_const_pigm_in_objects, "Ошибка в расчете кН"),
                            (self.all_hiding_in_objects, "Ошибка в расчете укрывистости"),
                            (self.filum_in_objects, "Ошибка в расчете филума"),
                            (self.all_kokp_maslo_in_objects, "Ошибка в расчете КОКП"),
                            (self.all_volume_suhoi_in_objects, 'Ошибка в расчете об. доли нелетучих в-в'),
                            ]


        for count_func, error_text in list_count_funcs:
            try:
                count_func()
            except Exception as e:
                # logging.error(e, exc_info=True)
                info_text = info_text + error_text + "\n"

                raise e

        if info_text != "":
            info_text = 'ОШИБКА ПРИ РАСЧЕТЕ! \nПроверьте расчетные значения используемых ' \
                        '\nкомпонентов в Моя лаборатория.\n' + info_text
            InfoWindow(info_text).exec()

    def count_price(self):
        all_mass = self.mass
        all_price = Decimal(0)

        for i in self.list_of_solvent_objects:
            all_price += (i.mass * i.price) / all_mass
        for i in self.list_of_pigment_objects:
            all_price += (i.mass * i.price) / all_mass
        for i in self.list_of_filler_objects:
            all_price += (i.mass * i.price) / all_mass
        for i in self.list_of_film_objects:
            all_price += (i.mass * i.price) / all_mass
        for i in self.list_of_additive_objects:
            all_price += (i.mass * i.price) / all_mass
        for i in self.list_of_pigmpast_objects:
            all_price += (i.mass * i.price) / all_mass
        for i in self.list_of_hardener_objects:
            all_price += (i.mass * i.price) / all_mass
        all_price *= Decimal(self.price_K)

        self.price = all_price

    def all_mass_for_suhoi_f(self):
        all_mass = Decimal(0)
        suhoi_check = get_suhoi_type()

        for i in self.list_of_solvent_objects:
            i = i.mass
            all_mass += i
        for i in self.list_of_pigment_objects:
            i = i.mass
            all_mass += i
        for i in self.list_of_filler_objects:
            i = i.mass
            all_mass += i
        for i in self.list_of_film_objects:
            i = i.mass
            all_mass += i
        for i in self.list_of_pigmpast_objects:
            i = i.mass
            all_mass += i

        if suhoi_check == 1:
            for i in self.list_of_additive_objects:
                all_mass += i.mass
        else:
            for i in self.list_of_additive_objects:
                if i.type.lower() == 'пластификатор':
                    all_mass += i.mass
        if suhoi_check == 1 or suhoi_check == 2:
            for i in self.list_of_hardener_objects:
                all_mass += i.mass

        self.all_mass_for_suhoi = all_mass

    def all_suhoi_in_objects(self, for_volume=False):
        if for_volume:
            all_mass = self.mass
        else:
            all_mass = self.all_mass_for_suhoi

        all_suhoi = Decimal(0)
        if for_volume:
            suhoi_check = 1  # учитывать всё
        else:
            suhoi_check = get_suhoi_type()

        for i in self.list_of_solvent_objects:
            all_suhoi += (i.mass * i.suhoi) / all_mass

        for i in self.list_of_pigment_objects:
            all_suhoi += i.mass / all_mass

        for i in self.list_of_filler_objects:
            all_suhoi += i.mass / all_mass

        for i in self.list_of_film_objects:
            all_suhoi += (i.mass * i.suhoi) / all_mass

        for i in self.list_of_additive_objects:
            if suhoi_check == 1:
                all_suhoi += (i.mass * i.suhoi) / all_mass
            if suhoi_check == 2 or suhoi_check == 3:
                if i.type.lower() == 'пластификатор':
                    all_suhoi += (i.mass * i.suhoi) / all_mass

        for i in self.list_of_pigmpast_objects:
            all_suhoi += (i.mass * i.suhoi) / all_mass

        if suhoi_check == 1 or suhoi_check == 2:
            for i in self.list_of_hardener_objects:
                all_suhoi += (i.mass * i.suhoi) / all_mass

        if not for_volume:
            all_suhoi = all_suhoi * 100
            # all_suhoi = self.normalize_number(all_suhoi)
            self.suhoi = all_suhoi
        else:
            self.all_suhoi_for_volume = all_suhoi

    def all_density_in_objects(self):
        all_mass = self.mass
        density = Decimal(0)
        for i in self.list_of_solvent_objects:
            i = i.mass * i.density / all_mass
            density += i
        for i in self.list_of_pigment_objects:
            i = i.mass * i.density / all_mass
            density += i
        for i in self.list_of_filler_objects:
            i = i.mass * i.density / all_mass
            density += i
        for i in self.list_of_film_objects:
            i = i.mass * i.density / all_mass
            density += i
        for i in self.list_of_pigmpast_objects:
            i = i.mass * i.density / all_mass
            density += i
        for i in self.list_of_additive_objects:
            i = i.mass * i.density / all_mass
            density += i
        for i in self.list_of_hardener_objects:
            i = i.mass * i.density / all_mass
            density += i

        self.density = density

    def all_volume_suhoi_in_objects(self):
        suhoi = self.all_suhoi_for_volume
        if self.accurate_density > 0.0:
            lkm_volume = Decimal(100) / Decimal(self.accurate_density)
        else:
            if self.density > 0:
                lkm_volume = Decimal(100) / Decimal(self.density)
            else:
                lkm_volume = 0
        # print('лкм объем:'+str(lkm_volume))

        all_solvent_mass = Decimal(0)
        list_same = self.list_of_film_objects + self.list_of_hardener_objects + \
                    self.list_of_pigmpast_objects + self.list_of_solvent_objects
        for i in list_same:
            all_solvent_mass += i.mass * (Decimal(1.0) - i.suhoi)

        for i in self.list_of_additive_objects:
            if i.density_solvent > 0:
                all_solvent_mass += i.mass * (Decimal(1.0) - i.suhoi)

        # print('масса растворителя:' + str(all_solvent_mass))

        density_solvent = Decimal(0)
        for i in list_same:
            i = i.mass * (Decimal(1.0) - i.suhoi) * i.density_solvent / all_solvent_mass
            density_solvent += i

        for i in self.list_of_additive_objects:
            if i.density_solvent > 0:
                i = i.mass * (Decimal(1.0) - i.suhoi) * i.density_solvent / all_solvent_mass
                density_solvent += i
        # print('плотность растворителя:' + str(density_solvent))

        try:
            solvent_volume = (Decimal(1.0) - suhoi) * 100 / density_solvent
            # print('объем растворителя:' + str(solvent_volume))
            volume_suhoi = (lkm_volume - solvent_volume) * 100 / lkm_volume

        except Exception as e:
            logging.error(e, exc_info=True)

            volume_suhoi = Decimal(0)

        self.volume_suhoi = volume_suhoi

    def all_degree_pigm_in_objects(self):
        pigm = Decimal(0)
        film = Decimal(0)
        for i in self.list_of_pigment_objects:
            pigm += i.mass
        for i in self.list_of_filler_objects:
            pigm += i.mass
        for i in self.list_of_pigmpast_objects:
            pigm += (i.mass * i.suhoi_pigm)

        for i in self.list_of_film_objects:
            film += (i.mass * i.suhoi)
        for i in self.list_of_hardener_objects:
            film += (i.mass_for_params * i.suhoi)
        for i in self.list_of_pigmpast_objects:
            film += (i.mass * i.suhoi_film)
        for i in self.list_of_additive_objects:
            if i.type.lower() == 'пластификатор':
                film += (i.mass * i.suhoi)

        try:
            degree_pigm = Decimal(pigm / film).quantize(Decimal("1.00"), "ROUND_HALF_EVEN")
        except Exception as e:
            logging.error(e, exc_info=True)
            degree_pigm = Decimal(0)

        self.degree_pigm = degree_pigm

    def all_okp_in_objects(self):

        filler_and_pigm_volume = Decimal(0)
        film_volume = Decimal(0)

        for i in self.list_of_pigment_objects:
            filler_and_pigm_volume += (
                    (i.mass) / (i.density))
        for i in self.list_of_filler_objects:
            filler_and_pigm_volume += (
                    (i.mass) / (i.density))
        for i in self.list_of_pigmpast_objects:
            filler_and_pigm_volume += (
                    (i.mass * i.suhoi_pigm) / (
                i.density_pigm))

        for i in self.list_of_film_objects:
            film_volume += ((i.mass * i.suhoi) / (
                i.density_dry))
        for i in self.list_of_hardener_objects:
            film_volume += ((i.mass_for_params * i.suhoi) / (
                i.density_dry))
        for i in self.list_of_pigmpast_objects:
            film_volume += (
                    i.mass * i.suhoi_film /
                    i.density_dry)

        for i in self.list_of_additive_objects:
            if i.type.lower() == 'пластификатор':
                film_volume += ((i.mass * i.suhoi) / (
                    i.density))

        try:
            okp = (filler_and_pigm_volume * 100) / (filler_and_pigm_volume + film_volume)
        except Exception as e:
            logging.error(e, exc_info=True)
            okp = Decimal(0)

        self.okp = okp

    def all_oil_in_objects(self):
        all_mass = 0
        all_maslo = 0
        for i in self.list_of_pigment_objects:
            i = i.mass
            all_mass += i
        for i in self.list_of_filler_objects:
            i = i.mass
            all_mass += i
        for i in self.list_of_pigmpast_objects:
            i = i.mass * i.suhoi_pigm
            all_mass += i

        for i in self.list_of_pigment_objects:
            all_maslo += (i.mass * i.maslo) / all_mass

        for i in self.list_of_filler_objects:
            all_maslo += (i.mass * i.maslo) / all_mass

        for i in self.list_of_pigmpast_objects:
            all_maslo += (i.mass * i.suhoi_pigm
                          * i.maslo) / all_mass

        self.oil = all_maslo

    def all_const_pigm_in_objects(self):
        all_maslo = self.oil
        degree_pigm = self.degree_pigm
        const_pigm = all_maslo * degree_pigm
        self.const_pigm = const_pigm

    def all_hiding_in_objects(self):
        all_mass = self.all_mass_for_suhoi
        all_mass_pigm = Decimal(0)
        all_hiding = Decimal(0)
        for i in self.list_of_pigment_objects:
            i = i.mass
            all_mass_pigm += i
        for i in self.list_of_pigmpast_objects:
            i = i.mass * i.suhoi_pigm
            all_mass_pigm += i

        for i in self.list_of_pigment_objects:
            all_hiding += (i.mass * i.hiding) / all_mass_pigm

        for i in self.list_of_pigmpast_objects:
            all_hiding += (i.mass * i.suhoi_pigm
                           * i.hiding) / all_mass_pigm

        self.hiding_pigm = all_hiding

        suhoi = self.suhoi
        hiding_lkp = (all_hiding * suhoi * 100) / (all_mass_pigm * 100 / all_mass)
        self.hiding_dry = hiding_lkp / 100

        wet_hiding_lkp = hiding_lkp / suhoi
        self.hiding_wet = wet_hiding_lkp

    def filum_in_objects(self):
        all_mass_pigm = Decimal(0)
        filum = Decimal(0)

        try:
            for i in self.list_of_pigment_objects:
                i = i.mass
                all_mass_pigm += i
            for i in self.list_of_pigmpast_objects:
                i = i.mass * i.suhoi_pigm
                all_mass_pigm += i

            for i in self.list_of_pigment_objects:
                filum += (i.mass * i.maslo *
                          i.hiding) / all_mass_pigm
            for i in self.list_of_pigmpast_objects:
                filum += (i.mass * i.suhoi_pigm *
                          i.hiding
                          * i.maslo) / all_mass_pigm
        except Exception as e:
            logging.error(e, exc_info=True)

            filum = Decimal(0)
        filum = filum / Decimal(100)

        self.philum = filum

    def all_kokp_maslo_in_objects(self):
        all_maslo = self.oil
        filler_and_pigm_mass = Decimal(0)
        film_mass = Decimal(0)
        filler_and_pigm_density = Decimal(0)
        film_density = Decimal(0)

        for i in self.list_of_pigment_objects:
            filler_and_pigm_mass += i.mass
        for i in self.list_of_filler_objects:
            filler_and_pigm_mass += i.mass
        for i in self.list_of_pigmpast_objects:
            filler_and_pigm_mass += i.mass * i.suhoi_pigm

        for i in self.list_of_film_objects:
            film_mass += i.mass * i.suhoi
        for i in self.list_of_hardener_objects:
            film_mass += i.mass_for_params * i.suhoi
        for i in self.list_of_pigmpast_objects:
            film_mass += i.mass * i.suhoi_film
        for i in self.list_of_additive_objects:
            if i.type.lower() == 'пластификатор':
                film_mass += i.mass * i.suhoi

        for i in self.list_of_pigment_objects:
            filler_and_pigm_density += ((i.mass * i.density)
                                        / filler_and_pigm_mass)
        for i in self.list_of_filler_objects:
            filler_and_pigm_density += ((i.mass * i.density)
                                        / filler_and_pigm_mass)
        for i in self.list_of_pigmpast_objects:
            filler_and_pigm_density += ((i.mass * i.suhoi_pigm
                                         * i.density_pigm) / filler_and_pigm_mass)

        for i in self.list_of_film_objects:
            film_density += ((i.mass * i.suhoi
                              * i.density_dry) / film_mass)
        for i in self.list_of_hardener_objects:
            film_density += ((i.mass_for_params * i.suhoi
                              * i.density_dry) / film_mass)
        for i in self.list_of_solvent_objects:
            film_density += ((i.mass * i.suhoi
                              * i.density) / film_mass)
        for i in self.list_of_pigmpast_objects:
            film_density += ((i.mass * i.suhoi_film
                              * i.density_dry) / film_mass)
        for i in self.list_of_additive_objects:
            if i.type.lower() == 'пластификатор':
                film_density += ((i.mass * i.suhoi
                                  * i.density) / film_mass)

        try:
            kokp = 100 / (1 + ((all_maslo * filler_and_pigm_density) / (100 * film_density)))
        except Exception as e:
            logging.error(e, exc_info=True)

            kokp = Decimal(0)

        self.kokp = kokp

        try:
            okp_kokp = self.okp / self.kokp
        except Exception as e:
            logging.error(e, exc_info=True)
            okp_kokp = Decimal(0)

        self.okp_kokp = okp_kokp * Decimal(100)


class SearchCombobox(CustomEntry):
    def __init__(self, parent, list_names):
        super(SearchCombobox, self).__init__(parent)
        self.db = DB()
        # self.setEditable(True)
        # self.setDuplicatesEnabled(False)
        # self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        word_set = set(list_names)
        completer = QCompleter(word_set)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(completer)
        self.update()


class Component:
    db = DB()

    def __init__(self, name, mass, category):
        self.db = Component.db
        self.name = name
        self.mass = Decimal(mass.replace(",", "."))
        valuta = self.db.get_info_reactive(category, self.name, 'valuta')[0][0]
        price = Decimal(self.db.get_info_reactive(category, self.name, 'price')[0][0].replace(",", "."))
        if valuta != 'Руб':
            self.price = self.convert_price(valuta, price)
        else:
            self.price = price

    def convert_price(self, valuta: str, price: Decimal) -> Decimal:
        get_xml = requests.get(
            'http://www.cbr.ru/scripts/XML_daily.asp'
        )
        exchange_rate = {}
        # Парсинг XML используя ElementTree
        structure = ET.fromstring(get_xml.content)

        # Поиск курса доллара (USD ID: R01235)
        dollar = structure.find("./*[@ID='R01235']/Value")
        exchange_rate['$'] = dollar.text.replace(',', '.')

        # Поиск курса евро (EUR ID: R01239)
        euro = structure.find("./*[@ID='R01239']/Value")
        exchange_rate['€'] = euro.text.replace(',', '.')
        converted_price = price * Decimal(exchange_rate[valuta])

        return converted_price


class Solvents(Component):
    def __init__(self, name, mass):
        super(Solvents, self).__init__(name, mass, 'Solvents')
        self.density = Decimal(self.db.get_info_reactive('Solvents', self.name, 'density')[0][0].replace(",", "."))
        self.density_solvent = self.density
        self.suhoi = Decimal('0')


class Pigments(Component):
    def __init__(self, name, mass):
        super(Pigments, self).__init__(name, mass, 'Pigments')
        self.density = Decimal(self.db.get_info_reactive('Pigments', self.name, 'density')[0][0].replace(",", "."))
        self.maslo = Decimal(self.db.get_info_reactive('Pigments', self.name, 'maslo')[0][0].replace(",", "."))
        self.hiding = Decimal(self.db.get_info_reactive('Pigments', self.name, 'hiding')[0][0].replace(",", "."))


class Fillers(Component):
    def __init__(self, name, mass):
        super(Fillers, self).__init__(name, mass, 'Fillers')
        self.density = Decimal(self.db.get_info_reactive('Fillers', self.name, 'density')[0][0].replace(",", "."))
        self.maslo = Decimal(self.db.get_info_reactive('Fillers', self.name, 'maslo')[0][0].replace(",", "."))


class Films(Component):
    def __init__(self, name, mass):
        super(Films, self).__init__(name, mass, 'Films')
        self.suhoi = Decimal(self.db.get_info_reactive('Films', self.name, 'suhoi')[0][0].replace(",", "."))
        self.density_dry = Decimal(self.db.get_info_reactive('Films', self.name, 'density_dry')[0][0].replace(",", "."))
        self.density = Decimal(self.db.get_info_reactive('Films', self.name, 'density')[0][0].replace(",", "."))
        self.density_solvent = Decimal(self.db.get_info_reactive('Films', self.name, 'density_solvent')[0][0].replace(",", "."))


class Additives(Component):
    def __init__(self, name, mass):
        super(Additives, self).__init__(name, mass, 'Additives')
        self.suhoi = Decimal(self.db.get_info_reactive('Additives', self.name, 'suhoi')[0][0].replace(",", "."))
        self.dosage = self.db.get_info_reactive('Additives', self.name, 'dosage')[0][0]
        self.density = Decimal(self.db.get_info_reactive('Additives', self.name, 'density')[0][0].replace(",", "."))
        self.type = self.db.get_info_reactive('Additives', self.name, 'type')[0][0]
        self.density_solvent = Decimal(self.db.get_info_reactive('Additives', self.name, 'density_solvent')[0][0].replace(",", "."))


class Pigmpasts(Component):
    def __init__(self, name, mass):
        super(Pigmpasts, self).__init__(name, mass, 'Pigmpast')
        self.suhoi = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'suhoi')[0][0].replace(",", "."))
        self.suhoi_pigm = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'suhoi_pigm')[0][0].replace(",", "."))
        self.suhoi_film = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'suhoi_film')[0][0].replace(",", "."))
        self.maslo = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'maslo')[0][0].replace(",", "."))
        self.density = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'density')[0][0].replace(",", "."))
        self.density_dry = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'density_dry')[0][0].replace(",", "."))
        self.density_pigm = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'density_pigm')[0][0].replace(",", "."))
        self.hiding = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'hiding')[0][0].replace(",", "."))
        self.density_solvent = Decimal(self.db.get_info_reactive('Pigmpast', self.name, 'density_solvent')[0][0].replace(",", "."))


class Hardeners(Component):
    def __init__(self, name, mass):
        super(Hardeners, self).__init__(name, mass, 'Hardener')
        self.suhoi = Decimal(self.db.get_info_reactive('Hardener', self.name, 'suhoi')[0][0].replace(",", "."))
        self.func_groups = self.db.get_info_reactive('Hardener', self.name, 'func_groups')[0][0]
        self.density = Decimal(self.db.get_info_reactive('Hardener', self.name, 'density')[0][0].replace(",", "."))
        self.density_dry = Decimal(self.db.get_info_reactive('Hardener', self.name, 'density_dry')[0][0].replace(",", "."))
        countable = self.db.get_info_reactive('Hardener', self.name, 'countable')[0][0]
        if countable.lower().strip() == 'да':
            self.mass_for_params = self.mass
        else:
            self.mass_for_params = Decimal('0')  # для расчета окп кокп СП
        self.density_solvent = Decimal(self.db.get_info_reactive('Hardener', self.name, 'density_solvent')[0][0].replace(",", "."))


