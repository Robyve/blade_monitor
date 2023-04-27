# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 15:20
# @Author  : XXX
# @Site    : 
# @File    : data_ui_manager.py
# @Software: PyCharm 
# @Comment :

import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread, QSize
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QCheckBox, QTreeWidgetItem, QTreeWidget

import ports
from data_ui import data_type_db

from data_ui.chart_manager import *


class FftQThread(QThread):
    def __init__(self, chart_freq, data):
        super().__init__()
        self.chart_freq = chart_freq
        self.data = data

    def run(self):
        signal = self.data
        fft_x, fft_y = DataUiManager.calc_fft(signal)
        set_chart_datas(self.chart_freq, fft_x, fft_y)


class MyTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)

    # def mousePressEvent(self, event):
    #     QTreeWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        # 禁用鼠标拖动事件，防止出现选中暴露原始布局
        pass

    def contextMenuEvent(self, event):
        # 禁用右键事件，防止出现选中暴露原始布局
        pass


class DataUiManager:
    def __init__(self, ui,
                 port_manager: ports.PortManager):
        self.all_data_type_tree_widget = None
        self.DATA_BUFFER_MAX_SIZE = 400
        self.FFT_COLLECT_RANGE = 200  # fft采样范围，属于少于该范围不进行fft
        self.port_manager = port_manager
        self.ui = ui
        self.lcd_top_labels_ui = [
            ui.data1_label,
            ui.data2_label,
            ui.data3_label,
            ui.data4_label,
        ]
        self.lcd_3_ui = [
            [ui.x1_lcd, ui.y1_lcd, ui.z1_lcd],
            [ui.x2_lcd, ui.y2_lcd, ui.z2_lcd],
            [ui.x3_lcd, ui.y3_lcd, ui.z3_lcd],
            [ui.x4_lcd, ui.y4_lcd, ui.z4_lcd],
        ]
        self.lcd_3_sub_label_ui = [
            [ui.x1_sub_label_lcd, ui.y1_sub_label_lcd, ui.z1_sub_label_lcd],
            [ui.x2_sub_label_lcd, ui.y2_sub_label_lcd, ui.z2_sub_label_lcd],
            [ui.x3_sub_label_lcd, ui.y3_sub_label_lcd, ui.z3_sub_label_lcd],
            [ui.x4_sub_label_lcd, ui.y4_sub_label_lcd, ui.z4_sub_label_lcd],
        ]
        self.charts_time = None
        self.charts_freq = None

        self.data_recived_from_ports_signal = pyqtSignal(str)
        self.port_manager.data_ready_signal.connect(self.handle_port_data)

        self.all_data_type_list = []
        self.ui_label_list_static = []
        self.ui_dict_list = []
        self.data_buffer = None
        self.data_buffer_width = None  # data_buffer每条的数据个数
        self._ui_bounder = []

        self._init_data_type_tree()
        self.on_push_data_type_update_btn()

        self.DATA_TYPE_MAX_NUM = 3 * len(self.lcd_3_ui)
        self.data_type_select_counter = 0   # data_type选择计数器，防止选取过多，布局盛不下
        self._bound_data_and_ui()
        self._init_data_type_tree()
        self.ui.data_type_select_counter_label.setText(
            f'已选取({self.data_type_select_counter}/{self.DATA_TYPE_MAX_NUM})个数据项')

        ui.data_type_update_btn.clicked.connect(self.on_push_data_type_update_btn)

    def _bound_data_and_ui(self):
        """
        静态绑定数据和对应的ui控件
        :return:
        """
        item_list = list(range(self.ui.data_type_btn_layout.count()))
        item_list.reverse()  # 倒序删除，避免影响布局顺序
        for i in item_list:
            check_box_to_delete = self.ui.data_type_btn_layout.itemAt(i)
            self.ui.data_type_btn_layout.removeItem(check_box_to_delete)
            if check_box_to_delete.widget():
                check_box_to_delete.widget().deleteLater()

        # 隐藏所有lcd，之后显示
        for top_label, lcd_3, label_3 in zip(self.lcd_top_labels_ui, self.lcd_3_ui, self.lcd_3_sub_label_ui):
            top_label.setHidden(True)
            for lcd, label in zip(lcd_3, label_3):
                lcd.setHidden(True)
                label.setHidden(True)

        for dt in self.all_data_type_list:
            check_box = QCheckBox()
            font = QFont()
            check_box.setFont(font)
            check_box.setText(dt['name'])
            check_box.setChecked(True)
            check_box.setFixedSize(QSize(250, 30))
            self.ui.data_type_btn_layout.addWidget(check_box)

        for label_ui, label_name in self.ui_label_list_static:
            label_ui.setText(label_name)

        self._ui_bounder.clear()
        chart_time_locate = []
        chart_time_names = []
        chart_freq_locate = []
        chart_freq_names = []
        for i, ud in enumerate(self.ui_dict_list):
            ls = [ud.get('lcd'),
                  ud.get('chart_time'),
                  ud.get('chart_freq'),
                  ]
            if ud.get('lcd') is not None:
                lcd = ud.get('lcd')
                c = ud.get('lcd_label_name')
                assert c is not None
                self.lcd_top_labels_ui[int(lcd[0])].setHidden(False)
                self.lcd_3_ui[int(lcd[0])][lcd[1]].setHidden(False)
                self.lcd_3_sub_label_ui[int(lcd[0])][lcd[1]].setHidden(False)
                self.lcd_3_sub_label_ui[int(lcd[0])][lcd[1]].setText(c)
            if ud.get('chart_time') is not None:
                c = ud.get('chart_time_locate')
                assert c is not None
                chart_time_locate.append(c)
                n = ud.get('data_name')
                assert n is not None
                chart_time_names.append(n)
            if ud.get('chart_freq') is not None:
                c = ud.get('chart_freq_locate')
                assert c is not None
                chart_freq_locate.append(c)
                n = ud.get('data_name')
                assert n is not None
                chart_freq_names.append(n)
            self._ui_bounder.append(ls)
        self.data_buffer_width = len(self.ui_dict_list)
        self.data_buffer = np.empty((0, len(self.ui_dict_list)))
        self.charts_time = init_charts(self.ui.graph_tab_time_scrollArea, chart_time_locate, chart_time_names)
        self.charts_freq = init_charts(self.ui.graph_tab_freq_scrollArea, chart_freq_locate, chart_freq_names)

    def add_datas(self, datas: list, end_of_group):
        """
        高级API
        :param datas:
        :param end_of_group: 是否是一次串口读取中的最后一组数据，如果是，进行额外的耗时操作
        :return:
        """
        temp = []
        i = 0
        for d, uis in zip(datas, self._ui_bounder):
            for j, ui_info in enumerate(uis):
                if ui_info is None:
                    continue
                if j == 0 and self.ui.tab_right.currentIndex() == 0:  # 懒加载
                    self.lcd_3_ui[int(ui_info[0])][ui_info[1]].display(d)

                if j == 1:
                    add_single_chart_data(self.charts_time[ui_info], d)

                if j == 2 and end_of_group:
                    if self.data_buffer.shape[0] > self.FFT_COLLECT_RANGE:
                        signal = self.data_buffer[len(self.data_buffer) - self.FFT_COLLECT_RANGE:, i]
                        fft_x, fft_y = self.calc_fft(signal)
                        if self.ui.tab_right.currentIndex() == 2:  # 懒加载
                            set_chart_datas(self.charts_freq[ui_info], fft_x, fft_y)
            i += 1

    def add_3d_datas(self, lcd_3_idx: int, to_chart_list, chart_idxs: list[int], datas):
        assert len(chart_idxs) == len(datas)
        for lcd, d in zip(self.lcd_3_ui[lcd_3_idx], datas):
            lcd.display(d)
        for idx, d in zip(chart_idxs, datas):
            add_single_chart_data(to_chart_list[idx], d)

    @staticmethod
    def add_data_to_charts(to_chart_list, chart_idxs: list[int], datas):
        for idx, d in zip(chart_idxs, datas):
            add_single_chart_data(to_chart_list[idx], d)

    def convert_data_from_port(self, data: str):
        try:
            temp_list = data.split('$')
        except (AttributeError, TypeError) as e:
            print(e)
            return
        data_list = []
        for s in temp_list:
            s = s.split(' ')
            if len(s) != self.data_buffer_width:
                continue
            try:
                s = list(map(float, s))
            except (TypeError, ValueError) as e:
                print(e)
                continue
            data_list.append(s)
        return data_list

    @staticmethod
    def calc_fft(signal):
        n = len(signal)
        Fs = 1. / 1e-2  # 采样频率，TODO 统一
        fft_result = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(n, d=1. / Fs)
        return freqs, fft_result

    def handle_port_data(self, data: str):
        data_list = self.convert_data_from_port(data)
        if data_list is None or not data_list:
            return
        # 到此数据应该是清洗过的
        self.data_buffer = np.concatenate((self.data_buffer, data_list))
        for d in data_list[:-1]:
            self.add_datas(d, end_of_group=False)
        self.add_datas(data_list[-1], end_of_group=True)

        # TODO 优化缓存清理
        if len(self.data_buffer) > self.DATA_BUFFER_MAX_SIZE:
            self.data_buffer = self.data_buffer[-self.FFT_COLLECT_RANGE:]

    def _init_data_type_tree(self):
        if self.all_data_type_tree_widget:
            self.all_data_type_tree_widget.deleteLater()
        self.all_data_type_tree_widget = MyTreeWidget()
        self.all_data_type_tree_widget.setMinimumHeight(200)
        self.ui.all_data_type_vLayout.addWidget(self.all_data_type_tree_widget)
        for dt in data_type_db.DATA_TYPE_DB:
            item = QTreeWidgetItem()
            item.setFlags(item.flags())
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setSizeHint(0, QSize(250, 25))
            checkbox = QCheckBox()
            checkbox.setText(dt['name'])
            checkbox.setFixedSize(QSize(250, 25))
            if dt['is_v'] == 'V':
                checkbox.stateChanged.connect(self.on_tree_check_box_state_change_vector)
            else:
                checkbox.stateChanged.connect(self.on_tree_check_box_state_change_scalar)
            self.all_data_type_tree_widget.addTopLevelItem(item)
            self.all_data_type_tree_widget.setItemWidget(item, 0, checkbox)

    def on_tree_check_box_state_change_vector(self, state):
        if state == 2:
            self.data_type_select_counter += 3
        else:
            self.data_type_select_counter -= 3
        if self.data_type_select_counter > self.DATA_TYPE_MAX_NUM:
            self.ui.data_type_update_btn.setEnabled(False)
            self.ui.data_type_select_counter_label.setStyleSheet("color: #dc3545;")
        else:
            self.ui.data_type_update_btn.setEnabled(True)
            self.ui.data_type_select_counter_label.setStyleSheet("color: #555555;")
        self.ui.data_type_select_counter_label.setText(
            f'已选取({self.data_type_select_counter}/{self.DATA_TYPE_MAX_NUM})个数据项')

    def on_tree_check_box_state_change_scalar(self, state):
        if state == 2:
            self.data_type_select_counter += 1
        else:
            self.data_type_select_counter -= 1
        if self.data_type_select_counter > self.DATA_TYPE_MAX_NUM:
            self.ui.data_type_update_btn.setEnabled(False)
            self.ui.data_type_select_counter_label.setStyleSheet("color: #dc3545;")
        else:
            self.ui.data_type_update_btn.setEnabled(True)
            self.ui.data_type_select_counter_label.setStyleSheet("color: #555555;")
        self.ui.data_type_select_counter_label.setText(
            f'已选取({self.data_type_select_counter}/{self.DATA_TYPE_MAX_NUM})个数据项')

    def on_push_data_type_update_btn(self):
        # TODO 单片机
        self.all_data_type_list.clear()
        root = self.all_data_type_tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            checkbox = self.all_data_type_tree_widget.itemWidget(item, 0)
            if checkbox.isChecked():
                dt_info = data_type_db.get_data_type_from_name(checkbox.text())
                if dt_info['is_v'] == 'V':
                    self.all_data_type_list.insert(0, dt_info)
                else:
                    self.all_data_type_list.append(dt_info)
            # for j in range(item.childCount()):
            #     child = item.child(j)

        self.ui_label_list_static.clear()
        self.ui_dict_list.clear()

        # 为lcd添加矢量label
        scalar_count = 0
        i = 0
        for dt in self.all_data_type_list:
            if dt['is_v'] == 'V':
                self.ui_label_list_static.append((self.lcd_top_labels_ui[i], dt['name']))
                i += 1
            else:
                scalar_count += 1

        # 为lcd添加标量label
        while scalar_count > 0:
            self.ui_label_list_static.append((self.lcd_top_labels_ui[i], '标量'))
            i += 1
            scalar_count -= 3
        scalar_idx = 0  # 标量
        vector_idx = 0  # 矢量
        lcd_idx = 0
        chart_time_idx = 0
        chart_freq_idx = 0
        for dt in self.all_data_type_list:
            if dt['is_v'] == 'V':  # 只有矢量在此初始化label名称，标量送入标量区内
                for j, v_name in enumerate(['X', 'Y', 'Z']):
                    ui_dict = {'data_name': dt['name'] + '-' + v_name}
                    if True:
                        ui_dict['lcd'] = (lcd_idx, j)
                        ui_dict['lcd_label_name'] = v_name + '  '  # 加空格是为了调整布局
                    if True:
                        ui_dict['chart_time'] = chart_time_idx
                        ui_dict['chart_time_locate'] = [0, chart_time_idx]
                        chart_time_idx += 1
                    if dt['show_freq']:
                        ui_dict['chart_freq'] = chart_freq_idx
                        ui_dict['chart_freq_locate'] = [0, chart_freq_idx]
                        chart_freq_idx += 1

                    self.ui_dict_list.append(ui_dict)
                    vector_idx += 1
                if True:
                    lcd_idx += 1

            else:
                ui_dict = {'data_name': dt['name']}
                if True:
                    ui_dict['lcd'] = (int(lcd_idx + scalar_idx / 3), scalar_idx % 3)
                    ui_dict['lcd_label_name'] = dt['name'] + '  '  # 加空格是为了调整布局
                if True:
                    ui_dict['chart_time'] = chart_time_idx
                    ui_dict['chart_time_locate'] = [0, chart_time_idx]
                    chart_time_idx += 1
                if dt['show_freq']:
                    ui_dict['chart_freq'] = chart_freq_idx
                    ui_dict['chart_freq_locate'] = [0, chart_freq_idx]
                    chart_freq_idx += 1

                self.ui_dict_list.append(ui_dict)
                scalar_idx += 1
        self._bound_data_and_ui()
