import copy
import logging
from decimal import Decimal
from functools import reduce

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QRegularExpression, QSize
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QCompleter
from sqlitedict import SqliteDict

from common.secrets import Secrets
from common.ui_elements import HoverableButton, MenuButton, ColorButton, CustomMenu, CustomRadioBtn, generate_color
from component_card import CustomEntry, CustomCombobox
from database import DB
from typing import List, Tuple
import xml.etree.ElementTree as ET
import requests
from newReactives import InfoWindow, DarkBtn_Ui
from settings import get_suhoi_type, update_config_param


def create_w_lo(parent_w: QtWidgets.QWidget, parent_lo: QtWidgets.QBoxLayout) -> \
        Tuple[QtWidgets.QWidget, QtWidgets.QBoxLayout]:
    w = QtWidgets.QWidget(parent=parent_w)
    lo = QtWidgets.QHBoxLayout(w)
    lo.setSpacing(5)
    lo.setContentsMargins(0,0,0,0)
    parent_lo.addWidget(w)
    return w, lo


class ReceptureWindow(QtWidgets.QWidget):

    def __init__(self, project_name: str, iter_name: str, name: str):
        super(ReceptureWindow, self).__init__()
        self.project = project_name
        self.iter = iter_name
        self.name = name
        self.db = DB()
        self.setWindowTitle(f"{self.project} - {self.iter} - {self.name}")
        self.recepture_data = ReceptureDataModel(project_name, iter_name, name)
        self.recepture_data.load_data()
        self.settings_window = None
        self.additive_window = None
        self.list_comp_row_obj = []
        self.list_comp_2_row_obj = []

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

        self.component_one = Ui_Component(self.recepture, self.recepture_data)
        # self.component_one.setGeometry(QtCore.QRect(0, 0, 403, 485))
        # self.component_one.setObjectName("recepture")
        # self.component_one_l = QtWidgets.QVBoxLayout(self.recepture)
        # self.component_one_l.setContentsMargins(0, 0, 0, 0)
        # self.component_one_l.setSpacing(2)

        self.buttons = QtWidgets.QWidget(parent=self.recepture)
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


        self.verticalLayout.addWidget(self.component_one)
        self.verticalLayout.addWidget(self.buttons)

        self.component_two = Ui_Component(self.recepture, self.recepture_data)
        # self.component_two.setGeometry(QtCore.QRect(0, 0, 403, 485))
        # self.component_two.setObjectName("recepture")
        # self.component_two_l = QtWidgets.QVBoxLayout(self.component_two)
        # self.component_two_l.setContentsMargins(0, 0, 0, 0)
        # self.component_two_l.setSpacing(2)

        self.plus_2 = MenuButton(self.recepture, "plus_2", (20, 20))
        self.plus_2.clicked.connect(lambda x: self.add_row("two"))
        self.plus_2.hide()
        self.verticalLayout.addWidget(self.component_two)
        self.verticalLayout.addWidget(self.plus_2, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
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

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_params_l = QtWidgets.QLabel(parent=w)
        self.count_params_l.setText("Расчетные параметры")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.count_params_l.setFont(font)
        lo.addWidget(self.count_params_l)
        self.setting_count = HoverableButton(w, "settings", (16,16))
        self.setting_count.clicked.connect(lambda: self.open_r_settings())
        lo.addWidget(self.setting_count, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        lo.setContentsMargins(0,0,0,9)


        self.price_l = QtWidgets.QLabel(parent=self.right_side)
        self.price_l.setText("Стоимость:")
        self.verticalLayout_6.addWidget(self.price_l)

        self.density_l = QtWidgets.QLabel(parent=self.right_side)
        self.density_l.setText("Плотность:")
        self.verticalLayout_6.addWidget(self.density_l)

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
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

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
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

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_btn = DarkBtn_Ui(w, "calc")
        self.count_btn.clicked.connect(self.count_all)
        lo.addWidget(self.count_btn)
        lo.setContentsMargins(0,9,0,9)


        l = QtWidgets.QLabel(parent=self.right_side)
        l.setText("Дополнительные функции")
        font = QtGui.QFont()
        font.setPointSize(11)
        l.setFont(font)
        self.verticalLayout_6.addWidget(l,alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_components_btn = ColorButton(w,  "blue")
        self.count_components_btn.setText("Расчет компонентов")
        menu = CustomMenu(self)
        menu.addAction('Расчет функц. добавок', lambda: self.open_count_additives())
        menu.addAction('Расчет отвердителя', lambda: print(1))
        menu.addAction('Заменить по маслоемкости', lambda: print(1))
        self.count_components_btn.setMenu(menu)
        lo.addWidget(self.count_components_btn)

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
        self.count_new_recepture = ColorButton(w,  "blue")
        self.count_new_recepture.setText("Расчет рецептур")
        menu = CustomMenu(self)
        menu.addAction('По константе наполнения', lambda: print(1))
        menu.addAction('Комбинированный расчет', lambda: print(1))
        self.count_new_recepture.setMenu(menu)
        lo.addWidget(self.count_new_recepture)

        w, lo = create_w_lo(self.right_side, self.verticalLayout_6)
        self.others = ColorButton(w,  "blue")
        self.others.setText("Разное")
        menu = CustomMenu(self)
        menu.addAction('Филумы пигментов', lambda: print(1))
        self.others.setMenu(menu)
        lo.addWidget(self.others)


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
        self.amount_all_l.setText("Итого:")
        self.horizontalLayout_8.addWidget(self.amount_all_l)
        self.amount_all_value = QtWidgets.QLabel(parent=self.all_amount_w)
        self.horizontalLayout_8.addWidget(self.amount_all_value)
        self.recount_btn = HoverableButton(self.all_amount_w, "menu", (16,16))
        menu = CustomMenu(self)

        menu.addAction('Списать компоненты', lambda : self.subtract_warehouse())
        menu.addAction('Пересчитать массу', lambda : self.recount_mass())
        menu.addAction('Довести растворителем', lambda :self.add_solvent())

        self.recount_btn.setMenu(menu)

        self.horizontalLayout_8.addWidget(self.recount_btn)
        self.left_vertical_lo.addWidget(self.all_amount_w)
        self.tabWidget.addTab(self.recepture_tab, "Рецептура")



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

        l = QtWidgets.QLabel(parent=self.exp_params_w)
        l.setText("Экспериментальные значения")
        font = QtGui.QFont()
        font.setPointSize(12)
        l.setFont(font)
        self.gridLayout_2.addWidget(l, 0, 0, 1, 2)

        self.scrollArea_2 = QtWidgets.QScrollArea(parent=self.exp_params_w)
        self.scrollArea_2.setMinimumSize(QtCore.QSize(475, 350))
        self.scrollArea_2.setMaximumSize(QtCore.QSize(700, 16777215))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea")
        self.exp_params_w.setStyleSheet("""
                                QWidget#recepture{
                                          background: #f9f9f9;
                                          border: 0px solid black;
                                          }
                                QScrollArea#scrollArea{
                                   background: #f9f9f9;
                                   border: 0px solid #bbb;
                                   }          
                                          """)
        self.exp_s_area = QtWidgets.QWidget()
        self.exp_s_area.setGeometry(QtCore.QRect(0, 0, 500, 700))
        self.exp_s_area.setObjectName("recepture")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.exp_s_area)
        self.gridLayout_3.setVerticalSpacing(3)
        l = QtWidgets.QLabel(parent=self.exp_s_area)
        l.setText("Название")
        font = QtGui.QFont()
        font.setPointSize(10)
        l.setFont(font)
        self.gridLayout_3.addWidget(l, 1, 0, 1, 1)

        l = QtWidgets.QLabel(parent=self.exp_s_area)
        l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        l.setText("Требуемое \n"  "значение")
        font = QtGui.QFont()
        font.setPointSize(10)
        l.setFont(font)
        self.gridLayout_3.addWidget(l, 1, 1, 1, 1)

        l = QtWidgets.QLabel(parent=self.exp_s_area)
        l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        l.setText("Полученное \nзначение")
        font = QtGui.QFont()
        font.setPointSize(10)
        l.setFont(font)
        self.gridLayout_3.addWidget(l, 1, 2, 1, 1)

        l = QtWidgets.QLabel(parent=self.exp_s_area)
        l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        l.setText("Успех")
        font = QtGui.QFont()
        font.setPointSize(10)
        l.setFont(font)
        self.gridLayout_3.addWidget(l, 1, 3, 1, 3)

        for row in self.recepture_data.experiment_list:
            self.add_exp_row(*row)

        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_3.addItem(spacerItem3, 100, 0, 1, 1)

        self.scrollArea_2.setWidget(self.exp_s_area)
        self.gridLayout_2.addWidget(self.scrollArea_2, 2, 0, 1, 4)

        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 100, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.exp_params_w)




        self.color_w = QtWidgets.QWidget(parent=self.exp_body_w)
        self.gridLayout_4 = QtWidgets.QGridLayout(self.color_w)

        self.lable_name = QtWidgets.QLabel(parent=self.color_w)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lable_name.setFont(font)
        self.lable_name.setText("Цвет")
        self.gridLayout_4.addWidget(self.lable_name, 0, 0, 1, 1)

        self.lable_color1 = QtWidgets.QLabel(parent=self.color_w)
        self.lable_color1.setText("Требуемый цвет")
        self.gridLayout_4.addWidget(self.lable_color1, 1, 0, 1, 1)

        self.color1 = QtWidgets.QLabel(parent=self.color_w)
        image = QtGui.QPixmap(generate_color(self.recepture_data.project_color))
        self.color1.setPixmap(image)
        self.color1.setMaximumSize(QSize(82, 80))
        self.color1.setStyleSheet("""
        QLabel{
        border: 1px solid #ddd;
        }
        """)
        self.gridLayout_4.addWidget(self.color1, 2, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.lable_color2 = QtWidgets.QLabel(parent=self.color_w)
        self.lable_color2.setText("Полученный цвет")
        self.gridLayout_4.addWidget(self.lable_color2, 1, 1, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.color2 = QtWidgets.QLabel(parent=self.color_w)
        image = QtGui.QPixmap(generate_color(self.recepture_data.recepture_color))
        self.color2.setPixmap(image)
        self.color2.setMaximumSize(QSize(82, 80))
        self.color2.setStyleSheet("""
        QLabel{
        border: 1px solid #ddd;
        }
        """)
        self.gridLayout_4.addWidget(self.color2, 2, 1, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.select_color_btn = ColorButton(self.color_w, "blue")
        self.select_color_btn.setText("Выбрать цвет")
        self.gridLayout_4.addWidget(self.select_color_btn, 5, 1, 1, 1)


        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_4.addItem(spacerItem4, 6, 0, 1, 1)


        self.horizontalLayout_2.addWidget(self.color_w)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.verticalLayout_4.addWidget(self.exp_body_w)
        self.tabWidget.addTab(self.experimental_tab, "Эксперимент")

        self.description_tab = QtWidgets.QWidget()
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.description_tab)
        self.verticalLayout_5.setContentsMargins(9, 0, 9, 9)
        self.description = QtWidgets.QTextEdit(parent=self.description_tab)
        self.description.setText(self.recepture_data.notes)
        self.verticalLayout_5.addWidget(self.description)
        self.tabWidget.addTab(self.description_tab, "Заметки")
        self.verticalLayout_3.addWidget(self.tabWidget)

        self.tabWidget.setCurrentIndex(0)

        self.count_mass()

    def closeEvent(self, event):
        Ui_Component.list_obj.remove(self.component_one)
        Ui_Component.list_obj.remove(self.component_two)

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
            self.plus_2.hide()
            self.recepture_data.flag_2k = False
        else:
            self.component_two.show()
            self.plus_2.show()
            self.recepture_data.flag_2k = True
        self.btn_2k.set_pressed()
        self.count_mass()

    def add_row(self, _type, name="", value=""):
        if _type == "one":
            self.component_one.add_row(name=name, value=value, callback_mass=self.count_mass)
        else:
            self.component_two.add_row(name=name, value=value, callback_mass=self.count_mass)


        # parent = self.component_one if _type == "one" else self.component_two
        # list_obj = self.list_comp_row_obj if _type == "one" else self.list_comp_2_row_obj
        # loyout = self.component_one_l if _type == "one" else self.component_two_l
        # add_widget = self.buttons if _type == "one" else self.plus_2
        # loyout.removeWidget(add_widget)
        # _index = len(list_obj)
        # row = ComponentRow(parent, _index, name=name, amount=value, list_obj=list_obj, callback_mass=self.count_mass)
        # loyout.addWidget(row)
        # loyout.addWidget(add_widget)
        # list_obj.append(row)
        #
        # self.reset_row_number(_type)

    def add_exp_row(self, name, needed, value, state):
        ExperimentRow(self.exp_s_area, self.gridLayout_3, name, needed, value, state)

    def reset_row_number(self, _type: str):
        list_obj: List[ComponentRow]
        list_obj = self.list_comp_row_obj if _type == "one" else self.list_comp_2_row_obj
        number = 1
        for obj in list_obj:
            if obj is not None:
                obj.set_number(number)
                number += 1

    def collect_rows_data(self):
        list_1 = list(filter(lambda x: x!= None, self.component_one.get_list_obj()))
        list_2 = list(filter(lambda x: x!= None, self.component_two.get_list_obj()))

        list_comp_1 = [i.get_data() for i in list_1]
        list_comp_category_1 = [i.get_category() for i in list_1]
        list_comp_2 = [i.get_data() for i in list_2]
        list_comp_category_2 = [i.get_category() for i in list_2]

        self.recepture_data.component_list = list_comp_1
        self.recepture_data.component_list_2 = list_comp_2
        self.recepture_data.category_list = list_comp_category_1
        self.recepture_data.category_list_2 = list_comp_category_2

    def count_mass(self, collected=False):
        if not collected:
            self.collect_rows_data()
        mass = self.recepture_data.count_mass(all=True)
        mass = normalize_number(mass)
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

    def update_lable_param(self, lable: QtWidgets.QLabel, new_value: Decimal, size: str):
        text = lable.text()
        value = normalize_number(new_value)
        _index = text.index(":") + 1
        text =  f"{text[:_index]} {value} {size}"
        lable.setText(text)

    def recount_mass(self):
        dialog = QtWidgets.QInputDialog()
        new_summ, ok = dialog.getDouble(self, "Пересчитать массу на новую",
                                          "Новая масса:", 100.00, min=1.0, decimals=2, step=5)
        if ok and new_summ:
            summ = Decimal(0)
            new_summ = Decimal(new_summ)
            list_obj = self.component_one.get_list_obj()
            if self.recepture_data.flag_2k:
                list_obj += self.component_two.get_list_obj()

            valid_list_obj = []
            for row in list_obj:
                row: ComponentRow
                row_data = row.get_data()
                if len(row_data) == 2:
                    mass = row_data[1].replace(",",".").strip()
                    if mass == "" or mass == ".":
                        continue
                    summ += Decimal(mass)
                    valid_list_obj.append(row)

            for row in valid_list_obj:
                row_data = row.get_data()
                mass = Decimal(row_data[1].replace(",", ".").strip())

                new_mass = (mass / summ) * new_summ
                row.set_amount(normalize_number(new_mass))

    def add_solvent(self):
        dialog = QtWidgets.QInputDialog()
        goal_mass, ok = dialog.getDouble(self, "Довести растворителем до массы",
                                        "Новая масса:", 100.00, min=1.0, decimals=2, step=5)
        if ok and goal_mass:
            goal_mass = Decimal(goal_mass)
            mass_suhoi = Decimal(0)
            mass_solvent = Decimal(0)
            chech_solvent_exist = False
            amount_solvents = Decimal(0)
            list_obj = self.component_one.get_list_obj()
            if self.recepture_data.flag_2k:
                list_obj += self.component_two.get_list_obj()

            solvent_list_obj = []
            for row in list_obj:
                row: ComponentRow
                row_data = row.get_data()
                if len(row_data) == 2:
                    mass = row_data[1].replace(",", ".").strip()
                    category = row.get_category()
                    if (mass == "" or mass == "." or category == "") and category != 'Solvents':
                        continue
                    if category == 'Solvents':
                        if mass == "" or mass == ".":
                            mass = "0"
                            row.set_amount(mass)
                        amount_solvents += 1
                        chech_solvent_exist = True
                        mass_solvent += Decimal(mass.replace(",", "."))
                        solvent_list_obj.append(row)
                    else:
                        mass_suhoi += Decimal(mass.replace(",", "."))

            need_solvent = goal_mass - mass_suhoi
            if need_solvent < 0 or not chech_solvent_exist:
                InfoWindow("В рецептуре не указаны растворители,\nлибо желаемая масса меньше возможной.").exec()
                return

            for row in solvent_list_obj:
                row_data = row.get_data()
                mass = Decimal(row_data[1].replace(",", ".").strip())

                if mass_solvent != 0:
                    mass = (mass * need_solvent) / mass_solvent
                else:
                    mass = need_solvent / amount_solvents

                row.set_amount(normalize_number(mass))

    def subtract_warehouse(self):
        if InfoWindow(f"Вычесть массы компонентов со склада?").exec():
            list_error_comp = []
            warehouse_error_check = False

            list_obj = self.component_one.get_list_obj()
            if self.recepture_data.flag_2k:
                list_obj += self.component_two.get_list_obj()

            actual_list_obj = []
            for row in list_obj:
                row: ComponentRow
                row_data = row.get_data()
                if len(row_data) == 2:
                    mass = row_data[1].replace(",", ".").strip()
                    name = row_data[0]
                    category = row.get_category()
                    if category != "":
                        if mass == '' or mass == ".":
                            mass = "0"
                            row.set_amount(mass)
                        mass = Decimal(mass)
                        warehouse = self.db.get_info_reactive(category, name, 'warehouse')[0][0]
                        warehouse = warehouse.replace(",", ".").strip()
                        if warehouse == '' or warehouse == ".":
                            warehouse = "0"
                        warehouse = Decimal(warehouse)
                        deffer = warehouse - mass
                        if deffer < 0:
                            warehouse_error_check = True
                            list_error_comp.append(name)
                        actual_list_obj.append((row, warehouse))

            if warehouse_error_check:
                str_comp = ",\n".join(list_error_comp)
                InfoWindow(f"Массы не вычтены. Не хватает \nследующих компонентов:\n{str_comp}").exec()
                return

            for row, warehouse in actual_list_obj:
                row: ComponentRow
                row_data = row.get_data()

                mass = Decimal(row_data[1].replace(",", ".").strip())
                name = row_data[0]
                category = row.get_category()

                deffer = warehouse - mass
                deffer = normalize_number(deffer)
                self.db.update_warehouse(category, name, deffer)
            InfoWindow("Остатки реактивов изменены.").exec()

    def open_r_settings(self):
        if self.settings_window is None:
            self.settings_window = ReceptureSettings(self)
            self.settings_window.show()

    def open_count_additives(self):
        if self.additive_window is None:
            self.collect_rows_data()
            self.additive_window = CountAdditiveWindow(self)
            self.additive_window.show()


class ComponentRow(QtWidgets.QFrame):
    def __init__(self, parent, _index, name="", amount="", callback_get_list_obj=None, callback_mass=None):
        super(ComponentRow, self).__init__(parent=parent)
        self.callback_mass = callback_mass
        self.db = DB()
        self.category = ""
        self.callback_get_list_obj = callback_get_list_obj
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
        self.amount.setValidator(get_numeric_validator())
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

        menu = CustomMenu(self)
        menu.addAction('Сделать комментарием', self.change_state)
        menu.addAction('Удалить', self.delete)

        self.swap.setMenu(menu)
        self.horizontalLayout_4.addWidget(self.swap)

    def change_state(self):
        if self.flag_comment:
            self.flag_comment = False
            self.category_icon.show()
            self.number_l.show()
            self.name_comp.show()
            self.amount.show()
            self.assign_category(self.name_comp.text())

            self.comment.hide()
            self.comment_spacer.changeSize(0, 0)
            menu = QtWidgets.QMenu(self)
            menu.addAction('Сделать комментарием', self.change_state)
            menu.addAction('Удалить', self.delete)

            self.swap.setMenu(menu)
            self.reset_row_number()

        else:
            self.flag_comment = True
            self.category = ""
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
        # self.hide()
        parent: Ui_Component = self.parent()
        print(self)
        list_obj = parent.get_list_obj(raw=True)
        _index = list_obj.index(self)
        print(list_obj)
        for_delete = parent.gridLayout.takeAt(_index)

        print(for_delete.layout().deleteLater())
        print(parent.get_list_obj(raw=True))

        self.hide()
        self.reset_row_number()
        self.name_comp.setFocus()

    def name_changed(self, event):
        self.assign_category(event)

    def reset_row_number(self):
        self.list_obj: List[ComponentRow]
        number = 1
        for obj in self.callback_get_list_obj():
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

    def set_amount(self, amount: str):
        self.amount.setText(amount)

    def get_category(self):
        return self.category


class Ui_Component(QtWidgets.QWidget):

    list_obj = []

    @staticmethod
    def set_drop_false(obj = None):
        for i in Ui_Component.list_obj:
            if i is not None and i is not obj:
                i.setAcceptDrops(False)

    def __init__(self, parent, recepture_data):
        super(Ui_Component, self).__init__(parent=parent)
        self.target = None
        Ui_Component.list_obj.append(self)
        self.setAcceptDrops(False)
        self.list_comp_row_obj = []
        # self.recepture_data = recepture_data
        self.row = 0
        self.setGeometry(QtCore.QRect(0, 0, 403, 485))
        self.setObjectName("recepture")
        # self.component_one_l = QtWidgets.QVBoxLayout(self)
        # self.component_one_l.setContentsMargins(0, 0, 0, 0)
        # self.component_one_l.setSpacing(2)

        # self.layout = QtWidgets.QHBoxLayout(self)
        # self.scrollArea = QtWidgets.QScrollArea(self)
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setContentsMargins(0,0,0,0)

        # self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # self.layout.addWidget(self.scrollArea)
        # for name, value in self.recepture_data.component_list:
        #     self.add_row("one", name=name, value=value)

        # for i in range(3):
        #     for j in range(3):
        #         self.Frame = QtWidgets.QFrame(self)
        #         self.Frame.setStyleSheet("background-color: white;")
        #
        #         self.Frame.setLineWidth(2)
        #         self.layout = QtWidgets.QHBoxLayout(self.Frame)
        #         l = QtWidgets.QLabel(parent=self.Frame)
        #         l.setText(str(i) + str(j))
        #         Box = QtWidgets.QVBoxLayout()
        #
        #         Box.addWidget(self.Frame)
        #
        #         self.gridLayout.addLayout(Box, i, j)
        #         self.gridLayout.setColumnStretch(i % 3, 1)
        #         self.gridLayout.setRowStretch(j, 1)

    def add_row(self, name="", value="", callback_mass=None):
        parent = self
        list_obj = self.list_comp_row_obj
        loyout = self.gridLayout

        _index = len(list_obj)
        row = ComponentRow(parent, _index, name=name, amount=value, callback_get_list_obj=self.get_list_obj, callback_mass=callback_mass)

        Box = QtWidgets.QVBoxLayout()
        Box.addWidget(row)

        loyout.addLayout(Box, self.row, 0)
        # loyout.setColumnStretch(i % 3, 1)
        # loyout.setRowStretch(j, 1)

        list_obj.append(row)
        self.row += 1
        self.reset_row_number()

    def get_list_obj(self, raw=False):
        list_obj = []
        raw_list_obj = []
        for i in range(self.gridLayout.count()):
            component_row_obj: QtWidgets.QWidgetItem = self.gridLayout.itemAt(i).itemAt(0)
            if component_row_obj.widget():
                list_obj.append((component_row_obj.widget(), self.gridLayout.getItemPosition(i)[0]))
                raw_list_obj.append(component_row_obj.widget())
        if raw:
            return raw_list_obj

        list_obj.sort(key=lambda x: x[1])
        list_obj = list(map(lambda x:x[0], list_obj))
        return list_obj

    def reset_row_number(self):
        list_obj: List[ComponentRow]
        list_obj = self.get_list_obj()
        number = 1
        for obj in list_obj:
            if obj is not None and not obj.isHidden():
                if not obj.flag_comment:
                    obj.set_number(number)
                    number += 1

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QtCore.QEvent.Type.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def get_index(self, pos):
        for i in range(self.gridLayout.count()):
            if self.gridLayout.itemAt(i).geometry().contains(pos) and i != self.target:
                return i

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setAcceptDrops(True)
            self.target = self.get_index(event.position().toPoint())
            Ui_Component.set_drop_false(obj=self)
        else:
            self.target = None
            Ui_Component.set_drop_false()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.target is not None:
            drag = QtGui.QDrag(self.gridLayout.itemAt(self.target))
            pix = self.gridLayout.itemAt(self.target).itemAt(0).widget().grab()
            mimedata = QtCore.QMimeData()
            mimedata.setImageData(pix)
            drag.setMimeData(mimedata)
            drag.setPixmap(pix)
            # drag.setHotSpot(event.pos())
            drag.exec()

    def mouseReleaseEvent(self, event):
        self.target = None
        Ui_Component.set_drop_false()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QMouseEvent):
        test:QtWidgets.QVBoxLayout = event.source()
        print(test.parentWidget())
        if not event.source().geometry().contains(event.position().toPoint()):
            source = self.get_index(event.position().toPoint())
            if source is None:
                return
            list_obj = self.get_list_obj()
            raw_list_obj = self.get_list_obj(raw=True)
            s = list_obj.index(self.gridLayout.itemAt(source).itemAt(0).widget())
            f = list_obj.index(self.gridLayout.itemAt(self.target).itemAt(0).widget())

            if s > f:
                for i in range(f + 1, s + 1):
                    raw_index = self.get_list_obj(raw=True).index(list_obj[i])
                    p1 = list(self.gridLayout.getItemPosition(raw_index))
                    p1[0] = i - 1
                    self.gridLayout.addItem(self.gridLayout.takeAt(raw_index), *p1)
                raw_index = self.get_list_obj(raw=True).index(list_obj[f])
                self.gridLayout.addItem(self.gridLayout.takeAt(raw_index), s, 0, 1, 1)
            elif s < f:
                for i in range(s, f):
                    raw_index = self.get_list_obj(raw=True).index(list_obj[i])
                    p1 = list(self.gridLayout.getItemPosition(raw_index))
                    p1[0] = i + 1
                    self.gridLayout.addItem(self.gridLayout.takeAt(raw_index), *p1)
                raw_index = self.get_list_obj(raw=True).index(list_obj[f])
                self.gridLayout.addItem(self.gridLayout.takeAt(raw_index), s, 0, 1, 1)


            # i, j = max(self.target, source), min(self.target, source)
            # p1, p2 = self.gridLayout.getItemPosition(i), self.gridLayout.getItemPosition(j)
            # print(p1)
            # self.gridLayout.addItem(self.gridLayout.takeAt(i), *p2)
            # self.gridLayout.addItem(self.gridLayout.takeAt(j), *p1)
            self.reset_row_number()
        Ui_Component.set_drop_false()



class ExperimentRow:
    row = 2

    def __init__(self, parent, lo: QtWidgets.QGridLayout, name: str, needed: str, value: str, state: int):
        name_l = QtWidgets.QLabel(parent=parent)
        name_l.setMinimumSize(QtCore.QSize(200, 0))
        name_l.setText(name)
        lo.addWidget(name_l, ExperimentRow.row, 0, 1, 1)

        needed_l = QtWidgets.QLabel(parent=parent)
        needed_l.setMaximumSize(QtCore.QSize(100, 16777215))
        needed_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        needed_l.setText(needed)
        lo.addWidget(needed_l, ExperimentRow.row, 1, 1, 1)

        self.value = CustomEntry(parent=parent)
        self.value.setMaximumSize(QtCore.QSize(100, 16777215))
        self.value.setText(value)
        lo.addWidget(self.value, ExperimentRow.row, 2, 1, 1)

        number_group = QtWidgets.QButtonGroup(parent)
        self.gray_rb = CustomRadioBtn("grey")
        self.gray_rb.setText("")
        self.gray_rb.setObjectName("gray_rb")
        number_group.addButton(self.gray_rb)
        lo.addWidget(self.gray_rb, ExperimentRow.row, 4, 1, 1)

        self.green_rb = CustomRadioBtn("green")
        self.green_rb.setText("")
        self.green_rb.setObjectName("green_rb")
        number_group.addButton(self.green_rb)
        lo.addWidget(self.green_rb, ExperimentRow.row, 3, 1, 1)

        self.red_rb = CustomRadioBtn("red")
        self.red_rb.setText("")
        self.red_rb.setObjectName("red_rb")
        number_group.addButton(self.red_rb)
        lo.addWidget(self.red_rb, ExperimentRow.row, 5, 1, 1)


        if state == 0:
            self.gray_rb.setChecked(True)
        elif state == 1:
            self.green_rb.setChecked(True)
        elif state == -1:
            self.red_rb.setChecked(True)

        ExperimentRow.row += 1

    def get(self):
        return self.value.text()


class ReceptureDataModel:
    def __init__(self, project, iteration, name):
        self.project = project
        self.iteration = iteration
        self.name = name
        self.not_encoded_projects = ['Тарировочные_кривые', 'Тарировочные кривые', 'Примеры']

        self.project_params = []
        self.project_params_value = []
        self.project_color = "#00ffffff"
        self.recepture_color = "#00ffffff"
        self.password = ""
        self.component_list = [("", "") for _ in range(7)]
        self.category_list = ["" for _ in range(7)]
        self.component_list_2 = [("", "") for _ in range(3)]
        self.category_list_2 = ["" for _ in range(7)]
        self.experiment_list = []
        self.exp_list_status = None
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
            self.project_color = mydict.get("color", "#00ffffff")


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
            self.exp_list_status = configs.get('exp_list_status', None)

        for i, param in enumerate(self.data):
            self.data[i] = list(map(self.map_decrypt, param))

        if self.exp_list_status == None:
            self.exp_list_status = [0 for _ in self.data[2]]

        self.component_list = list(zip(self.data[0], self.data[1]))
        self.component_list_2 = list(zip(self.data[7], self.data[8]))
        self.experiment_list = list(zip(self.data[2], self.data[5], self.data[3], self.exp_list_status))

        notes = self.data[4]
        if isinstance(notes, list):
            notes = notes[0]
        self.notes = notes

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
            print(data)

        else:
            data = list(filter(lambda foo: foo[1] != "", data))

        data = list(filter(lambda foo: type(foo[0]) == tuple, data))

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

    def get_components_obj(self):
        self.create_category_objs()

        return self.list_of_solvent_objects + self.list_of_pigment_objects + self.list_of_filler_objects + \
        self.list_of_film_objects + self.list_of_additive_objects + self.list_of_pigmpast_objects +\
        self.list_of_hardener_objects

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
        suhoi_check = int(get_suhoi_type())

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
            suhoi_check = int(get_suhoi_type())

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


class ReceptureSettings(QtWidgets.QWidget):

    def __init__(self, parent: ReceptureWindow):
        super(ReceptureSettings, self).__init__()
        self.parent_obj = parent
        self.setObjectName("rec_settings")
        self.setStyleSheet("""
        QWidget#rec_settings{
        background: #f9f9f9;
        }
        """)
        self.resize(400, 300)
        self.dry_type = int(get_suhoi_type())
        self.accurate_density = str(self.parent_obj.recepture_data.accurate_density).replace(".", ",")
        self.k_price = str(self.parent_obj.recepture_data.price_K).replace(".", ",")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.dry_mass_w = QtWidgets.QWidget(parent=self)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dry_mass_w)
        self.type_l = QtWidgets.QLabel(parent=self.dry_mass_w)
        self.type_l.setText("Тип расчета м.д.н.в.")
        self.horizontalLayout.addWidget(self.type_l)

        self.type_dry_mass_count = CustomCombobox(self.dry_mass_w)
        self.type_dry_mass_count.addItem("Все компоненты", userData=1)
        self.type_dry_mass_count.addItem("Ограниченный 1", userData=2)
        self.type_dry_mass_count.addItem("Ограниченный 2", userData=3)
        self.type_dry_mass_count.setCurrentIndex(self.dry_type - 1)
        self.type_dry_mass_count.currentIndexChanged.connect(self.show_description)
        self.horizontalLayout.addWidget(self.type_dry_mass_count)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.dry_mass_w)

        self.descript_type_l = QtWidgets.QLabel(parent=self)
        self.descript_type_l.setText("Опиание")
        self.descript_type_l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.descript_type_l.setWordWrap(False)
        self.verticalLayout.addWidget(self.descript_type_l)

        self.price_k_w = QtWidgets.QWidget(parent=self)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.price_k_w)
        self.price_k_l = QtWidgets.QLabel(parent=self.price_k_w)
        self.price_k_l.setText("Коэффициент стоимости")
        tooltip = "Коэффициент, на который будет домножаться стоимость"
        self.price_k_l.setToolTip(tooltip)
        self.horizontalLayout_2.addWidget(self.price_k_l)
        self.price_k_e = CustomEntry(self.price_k_w, padding=False)
        self.price_k_e.setToolTip(tooltip)
        self.price_k_e.setMaximumSize(50, 999)
        self.price_k_e.setValidator(get_numeric_validator())
        self.price_k_e.setText(self.k_price)
        self.horizontalLayout_2.addWidget(self.price_k_e)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.price_k_w)

        self.density_w = QtWidgets.QWidget(parent=self)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.density_w)
        self.density_l = QtWidgets.QLabel(parent=self.density_w)
        self.density_l.setText("Экспериментальная плотность, г/мл³")
        tooltip = "Плотность, полученная экспериментально. \nНеобходимо для более точного \nрасчета."
        self.density_l.setToolTip(tooltip)
        self.horizontalLayout_3.addWidget(self.density_l)
        self.density_e = CustomEntry(self.density_w, padding=False)
        self.density_e.setMaximumSize(50, 999)
        self.density_e.setToolTip(tooltip)
        self.density_e.setValidator(get_numeric_validator())
        self.density_e.setText(self.accurate_density)
        self.horizontalLayout_3.addWidget(self.density_e)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addWidget(self.density_w)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.save_btn = DarkBtn_Ui(self, "save_settings")
        self.save_btn.clicked.connect(lambda : self.save())
        self.verticalLayout.addWidget(self.save_btn)

        self.show_description()

        self.setWindowTitle("Настройки расчета рецептур")

    def closeEvent(self, event):
        self.parent_obj.settings_window = None

    def show_description(self, event=None):
        if self.type_dry_mass_count.currentData() == 1:
            self.descript_type_l.setText('При расчете учитываются все категории компонентов')
        if self.type_dry_mass_count.currentData() == 2:
            self.descript_type_l.setText('При расчете не учитываются функциональные добавки,\nкроме пластификаторов')
        if self.type_dry_mass_count.currentData() == 3:
            self.descript_type_l.setText(
                'При расчете не учитываются функциональные добавки \nи отвердители, кроме пластификаторов')

    def save(self):
        price_k = float(self.price_k_e.text().replace(",","."))
        self.parent_obj.recepture_data.price_K = price_k
        density = float(self.density_e.text().replace(",","."))
        self.parent_obj.recepture_data.accurate_density = density

        update_config_param("suhoi_type",str(self.type_dry_mass_count.currentIndex() + 1))
        self.closeEvent(None)
        self.destroy()




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
        self.dry_mass = None

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
        self.dry_mass = Decimal('0')


class Pigments(Component):
    def __init__(self, name, mass):
        super(Pigments, self).__init__(name, mass, 'Pigments')
        self.density = Decimal(self.db.get_info_reactive('Pigments', self.name, 'density')[0][0].replace(",", "."))
        self.maslo = Decimal(self.db.get_info_reactive('Pigments', self.name, 'maslo')[0][0].replace(",", "."))
        self.hiding = Decimal(self.db.get_info_reactive('Pigments', self.name, 'hiding')[0][0].replace(",", "."))
        self.suhoi = Decimal("1")
        self.dry_mass = Decimal(mass.replace(",", "."))

class Fillers(Component):
    def __init__(self, name, mass):
        super(Fillers, self).__init__(name, mass, 'Fillers')
        self.density = Decimal(self.db.get_info_reactive('Fillers', self.name, 'density')[0][0].replace(",", "."))
        self.maslo = Decimal(self.db.get_info_reactive('Fillers', self.name, 'maslo')[0][0].replace(",", "."))
        self.suhoi = Decimal("1")
        self.dry_mass = Decimal(mass.replace(",", "."))

class Films(Component):
    def __init__(self, name, mass):
        super(Films, self).__init__(name, mass, 'Films')
        self.suhoi = Decimal(self.db.get_info_reactive('Films', self.name, 'suhoi')[0][0].replace(",", "."))
        self.density_dry = Decimal(self.db.get_info_reactive('Films', self.name, 'density_dry')[0][0].replace(",", "."))
        self.density = Decimal(self.db.get_info_reactive('Films', self.name, 'density')[0][0].replace(",", "."))
        self.density_solvent = Decimal(self.db.get_info_reactive('Films', self.name, 'density_solvent')[0][0].replace(",", "."))
        self.dry_mass = Decimal(mass.replace(",", ".")) * self.suhoi

class Additives(Component):
    def __init__(self, name, mass):
        super(Additives, self).__init__(name, mass, 'Additives')
        self.suhoi = Decimal(self.db.get_info_reactive('Additives', self.name, 'suhoi')[0][0].replace(",", "."))
        self.dosage = self.db.get_info_reactive('Additives', self.name, 'dosage')[0][0]
        self.density = Decimal(self.db.get_info_reactive('Additives', self.name, 'density')[0][0].replace(",", "."))
        self.type = self.db.get_info_reactive('Additives', self.name, 'type')[0][0]
        self.density_solvent = Decimal(self.db.get_info_reactive('Additives', self.name, 'density_solvent')[0][0].replace(",", "."))
        self.dry_mass = Decimal(mass.replace(",", ".")) * self.suhoi

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
        self.dry_mass = Decimal(mass.replace(",", ".")) * self.suhoi

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
        self.dry_mass = Decimal(mass.replace(",", ".")) * self.suhoi

class CountAdditiveWindow(QtWidgets.QWidget):
    def __init__(self, parent: ReceptureWindow):
        super(CountAdditiveWindow, self).__init__()
        self.recepture = parent
        self.first_row = 2
        self.list_checkbox = []
        self.list_components = self.recepture.recepture_data.get_components_obj()
        self.additive_obj = None
        self.db = DB()
        self.type = None

        self.setObjectName("CountAdditiveWindow")
        self.setStyleSheet("""
        QWidget#CountAdditiveWindow{
        background: #f9f9f9;
        }
        """)

        self.resize(537, 366)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.list_comp_w = QtWidgets.QWidget(parent=self)
        self.list_comp_w.setObjectName("list_comp_w")
        self.gridLayout = QtWidgets.QGridLayout(self.list_comp_w)
        self.gridLayout.setObjectName("gridLayout")

        self.check_l = QtWidgets.QLabel(parent=self.list_comp_w)
        self.gridLayout.addWidget(self.check_l, 1, 0, 1, 1)
        self.mass_l = QtWidgets.QLabel(parent=self.list_comp_w)
        self.gridLayout.addWidget(self.mass_l, 1, 1, 1, 1)

        self.comp_l = QtWidgets.QLabel(parent=self.list_comp_w)
        self.gridLayout.addWidget(self.comp_l, 0, 0, 1, 2)

        self.dry_mass_l = QtWidgets.QLabel(parent=self.list_comp_w)
        self.dry_mass_l.setObjectName("dry_mass_l")
        self.gridLayout.addWidget(self.dry_mass_l, 1, 2, 1, 1)

        for obj in self.list_components:
            self.add_row_component(obj)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem, self.first_row, 1, 1, 1)
        self.horizontalLayout.addWidget(self.list_comp_w)

# right part:
        self.count_w = QtWidgets.QWidget(parent=self)
        self.gridLayout_2 = QtWidgets.QGridLayout(self.count_w)
        self.gridLayout_2.setVerticalSpacing(2)

        self.list_all_names = self.db.load_reactives("Additives", "name")
        self.list_all_names = list(map(lambda x: x[0], self.list_all_names))
        self.component_e = SearchCombobox(self, self.list_all_names)
        self.component_e.setMinimumSize(QtCore.QSize(250, 0))
        self.component_e.textChanged.connect(self.name_changed)
        self.gridLayout_2.addWidget(self.component_e, 1, 0, 1, 4)

        self.dry_rb = QtWidgets.QRadioButton(parent=self.count_w)
        self.dry_rb.setChecked(True)
        self.gridLayout_2.addWidget(self.dry_rb, 5, 0, 1, 3)
        self.all_mass_rb = QtWidgets.QRadioButton(parent=self.count_w)
        self.gridLayout_2.addWidget(self.all_mass_rb, 6, 0, 1, 3)

        self.metal_w = QtWidgets.QWidget(parent=self.count_w)
        lo = QtWidgets.QHBoxLayout(self.metal_w)
        lo.setContentsMargins(0,0,0,0)

        metal_l = QtWidgets.QLabel(self.metal_w)
        metal_l.setText("Содержание металла, %")
        lo.addWidget(metal_l)
        self.metal_e = CustomEntry(self.metal_w, padding=False)
        self.metal_e.setMaximumSize(50, 22)
        self.metal_e.setValidator(get_numeric_validator())
        lo.addWidget(self.metal_e)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        lo.addItem(spacerItem1)
        self.gridLayout_2.addWidget(self.metal_w, 6, 0, 1, 4)
        self.metal_w.hide()

        dosage_w = QtWidgets.QWidget(parent=self.count_w)
        lo = QtWidgets.QHBoxLayout(dosage_w)
        lo.setContentsMargins(0, 0, 0, 0)
        dosage_l = QtWidgets.QLabel(parent=dosage_w)
        dosage_l.setText("Дозировка, %")
        lo.addWidget(dosage_l)
        self.dosage_e = CustomEntry(dosage_w, padding=False)
        self.dosage_e.setMaximumSize(50, 22)
        self.dosage_e.setValidator(get_numeric_validator())
        lo.addWidget(self.dosage_e)
        count_new_b = ColorButton(parent=dosage_w, color="blue")
        count_new_b.clicked.connect(lambda: self.count())
        count_new_b.setText("Рассчитать")
        lo.addWidget(count_new_b)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        lo.addItem(spacerItem1)
        self.gridLayout_2.addWidget(dosage_w, 7, 0, 1, 4)

        self.info = QtWidgets.QLabel(parent=self.count_w)
        self.gridLayout_2.addWidget(self.info, 4, 0, 1, 5)

        result_w = QtWidgets.QWidget(parent=self.count_w)
        lo = QtWidgets.QHBoxLayout(result_w)
        lo.setContentsMargins(0, 0, 0, 0)
        result_l = QtWidgets.QLabel(parent=result_w)
        result_l.setText("Результат:")
        lo.addWidget(result_l)
        self.result_e = CustomEntry(self.count_w, padding=False)
        self.result_e.setMaximumSize(50, 22)
        self.result_e.setReadOnly(True)
        lo.addWidget(self.result_e)
        add_count_b = ColorButton(parent=result_w, color="blue")
        add_count_b.setText("Очистить")
        add_count_b.clicked.connect(lambda: self.clear())
        lo.addWidget(add_count_b)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        lo.addItem(spacerItem1)
        self.gridLayout_2.addWidget(result_w, 9, 0, 1, 1)

        self.additive_name_l = QtWidgets.QLabel(parent=self.count_w)
        self.gridLayout_2.addWidget(self.additive_name_l, 0, 0, 1, 4)
        self.info_l = QtWidgets.QLabel(parent=self.count_w)
        self.gridLayout_2.addWidget(self.info_l, 2, 0, 1, 3)

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 4, 0, 1, 1)
        self.horizontalLayout.addWidget(self.count_w)

        self.setWindowTitle("Расчет функциональных добавок")

        self.check_l.setText("Учитывать")
        self.mass_l.setText("Масса")
        self.comp_l.setText("Компоненты")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comp_l.setFont(font)

        self.dry_mass_l.setText("м.н.в.")
        self.dry_rb.setText("По массе нелетучих веществ")
        self.additive_name_l.setText("Функциональная добавка:")
        self.additive_name_l.setFont(font)
        self.info_l.setText("Информация о дозировке:")
        self.all_mass_rb.setText("По всей массе")

    def closeEvent(self, event):
        self.recepture.additive_window = None

    def add_row_component(self, comp_obj: Component):
        component_chek = QtWidgets.QCheckBox(parent=self.list_comp_w)
        component_chek.user_data = comp_obj
        self.list_checkbox.append(component_chek)
        component_chek.setText(comp_obj.name)

        self.gridLayout.addWidget(component_chek, self.first_row, 0, 1, 1)

        mass = QtWidgets.QLabel(parent=self.list_comp_w)
        mass.setText(normalize_number(comp_obj.mass))
        self.gridLayout.addWidget(mass, self.first_row, 1, 1, 1)

        dry_mass = QtWidgets.QLabel(parent=self.list_comp_w)
        dry_mass.setText(normalize_number(comp_obj.dry_mass))
        self.gridLayout.addWidget(dry_mass, self.first_row, 2, 1, 1)

        self.first_row += 1

    def name_changed(self, text):
        if text in self.list_all_names:
            self.additive_obj = Additives(text, "0")
            info = self.additive_obj.dosage

            if self.additive_obj.type.lower() == "сиккатив":
                self.type = "Cиккатив"
                self.dry_rb.hide()
                self.all_mass_rb.hide()
                self.metal_w.show()
                info += '\n\nСправочная дозировка для сухого алкида: \nКобальт - 0,03-0,05%' \
                              ' \tМарганец - 0,02-0,04% \tСвинец - 0,06-0,08%' \
                              ' \nЦирконий - 0,08-0,15% \tКальций - 0,05-2,00% ' \
                              ' \tВанадий - 0,02-0,07% \nЖелезо - 0,02-0,05% \tЦерий - 0,1-0,2% \tКальций - 0,05-2,0% ' \
                              '\nАлюминий - 0,2-1,0% \tЦинк - 0,05-0,25% \tВисмут - 0,02-0,1% ' \
                              '\nСтронций - 0,1-0,5% \tБарий - 0,1-0,25% \tЛитий - 0,1-0,02% ' \
                              '\nРедкоземельные(La, Nd) - 0,1-0,3%' \
                              '\nДля смесевых сиккативов расчет ведется по ' \
                              'основному металлу \n(дающему наиболее желаемые свойства).' \
                              ' \nАнтипленка,например, МЕКО добавляется в количестве 10% от массы сиккатива.'
            else:
                self.dry_rb.show()
                self.all_mass_rb.show()
                self.metal_w.hide()
                self.type = "Добавка"

            self.info.setText(info)
        else:
            self.additive_obj = None
            self.type = None
            self.info.setText("")
            self.clear()

    def count(self):
        if self.type == "Добавка":
            self.count_additive()
        elif self.type == "Cиккатив":
            self.count_sickative()
        else:
            print(self.type)
            InfoWindow("Укажите название имеющейся функциональной добавки").exec()


    def collect_mass(self) -> Decimal:
        mass = Decimal(0)
        checkbox: QtWidgets.QCheckBox
        for checkbox in self.list_checkbox:
            if checkbox.isChecked():
                comp_obj: Component = checkbox.user_data
                if self.dry_rb.isChecked() or self.type == "Сиккатив":
                    mass += comp_obj.dry_mass
                else:
                    mass += comp_obj.mass
        return mass

    def count_sickative(self):
        mass = self.collect_mass()
        metal = self.metal_e.text().replace(",", ".")
        if metal.strip() in ["", "."]:
            metal = "0"
        metal = Decimal(metal)

        dosage = self.dosage_e.text().replace(",", ".")
        if dosage.strip() in ["", "."]:
            dosage = "0"
        dosage = Decimal(dosage)

        result = mass * dosage / metal

        old = self.result_e.text().replace(",", ".")
        if old.strip() in ["", "."]:
            old = "0"
        old = Decimal(old)
        result += old

        result = normalize_number(result)
        self.result_e.setText(result)

    def count_additive(self):
        mass = self.collect_mass()
        dosage = self.dosage_e.text().replace(",", ".")
        if dosage.strip() in ["", "."]:
            dosage = "0"
        dosage = Decimal(dosage)
        result = (mass * dosage) / Decimal(100)
        old = self.result_e.text().replace(",", ".")
        if old.strip() in ["", "."]:
            old = "0"
        old = Decimal(old)
        result += old

        result = normalize_number(result)
        self.result_e.setText(result)

    def clear(self):
        self.result_e.setText("")


def normalize_number(number: Decimal) -> str:
    normalized = number.normalize()
    sign, digit, exponent = normalized.as_tuple()
    normalized = normalized if exponent <= 0 else normalized.quantize(1)
    normalized = normalized.quantize(Decimal("1.00"), "ROUND_HALF_EVEN")
    normalized = str(normalized).replace(".", ",")
    return normalized


def get_numeric_validator():
    reg_ex = QRegularExpression(r"[0-9]*[\,,.]{1}[0-9]*")
    validator = QRegularExpressionValidator(reg_ex)
    return validator