# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 15:20
# @Author  : XXX
# @Site    : 
# @File    : data_ui_manager.py
# @Software: PyCharm 
# @Comment :

import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QCheckBox

import ports

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


class DataUiManager:
    def __init__(self, ui,
                 port_manager: ports.PortManager):
        self.DATA_BUFFER_MAX_SIZE = 400
        self.FFT_COLLECT_RANGE = 200  # fft采样范围，属于少于该范围不进行fft
        self.port_manager = port_manager
        self.ui = ui
        self.data_labels_ui = [
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
        self.lcd_3_sub_label = [
            [ui.x1_sub_label_lcd, ui.y1_sub_label_lcd, ui.z1_sub_label_lcd],
            [ui.x2_sub_label_lcd, ui.y2_sub_label_lcd, ui.z2_sub_label_lcd],
            [ui.x3_sub_label_lcd, ui.y3_sub_label_lcd, ui.z3_sub_label_lcd],
            [ui.x4_sub_label_lcd, ui.y4_sub_label_lcd, ui.z4_sub_label_lcd],
        ]
        self.charts_time = None
        self.charts_freq = None

        self.data_recived_from_ports_signal = pyqtSignal(str)
        self.port_manager.data_ready_signal.connect(self.handle_port_data)

        self.all_data_type_list = [
            '加速度', '角速度', '温度'
        ]
        self.ui_label_list_static = [
                (ui.data1_label, '加速度'),
                (ui.data2_label, '角速度'),
                (ui.data3_label, '标量'),
            ]
        self.ui_dict_list = [
            {
                'data_name': '加速度X',
                'lcd': (0, 0),
                'lcd_label_name': 'X ',
                'chart_time': 0,
                'chart_time_locate': [0, 0],
                'chart_freq': 0,
                'chart_freq_locate': [0, 0],
            },
            {
                'data_name': '加速度Y',
                'lcd': (0, 1),
                'lcd_label_name': 'Y ',
                'chart_time': 1,
                'chart_time_locate': [1, 0],
                'chart_freq': 1,
                'chart_freq_locate': [1, 0],
            },
            {
                'data_name': '加速度Z',
                'lcd': (0, 2),
                'lcd_label_name': 'Z ',
                'chart_time': 2,
                'chart_time_locate': [2, 0],
                'chart_freq': 2,
                'chart_freq_locate': [2, 0],
            },
            # {
            #     'data_name': '温度',
            #     'lcd': (1, 0),
            #     'lcd_label_name': '温度 ',
            #     'chart_time': 3,
            #     'chart_time_locate': [3, 0],
            #     'chart_freq': 3,
            #     'chart_freq_locate': [3, 0],
            # },
        ]
        self.data_buffer = None
        self.data_buffer_width = None   # data_buffer每条的数据个数
        self._ui_bounder = []
        self.bound_data_and_ui()

        ui.data_type_update_btn.clicked.connect(self.on_push_data_type_update_btn)

    def bound_data_and_ui(self):
        """
        静态绑定数据和对应的ui控件
        :return:
        """
        item_list = list(range(self.ui.data_type_btn_layout.count()))
        item_list.reverse()  # 倒序删除，避免影响布局顺序
        for i in item_list:
            item = self.ui.data_type_btn_layout.itemAt(i)
            self.ui.data_type_btn_layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

        for name in self.all_data_type_list:
            check_box = QCheckBox()
            font = QFont()
            check_box.setFont(font)
            check_box.setText(name)
            check_box.setChecked(True)
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
                self.lcd_3_sub_label[int(lcd[0])][lcd[1]].setText(c)
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
        i = 0
        for d, uis in zip(datas, self._ui_bounder):
            for j, ui_info in enumerate(uis):
                if ui_info is None:
                    continue
                if j == 0 and self.ui.tab_right.currentIndex() == 0:   # 懒加载
                    self.lcd_3_ui[int(ui_info[0])][ui_info[1]].display(d)

                if j == 1:
                    add_single_chart_data(self.charts_time[ui_info], d)

                if j == 2 and end_of_group:
                    if self.data_buffer.shape[0] > self.FFT_COLLECT_RANGE:
                        signal = self.data_buffer[len(self.data_buffer) - self.FFT_COLLECT_RANGE:, i]
                        fft_x, fft_y = self.calc_fft(signal)
                        if self.ui.tab_right.currentIndex() == 2:   # 懒加载
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

    def on_push_data_type_update_btn(self):
        self.ui_label_list_static.clear()
        self.ui_dict_list.clear()
        # TODO 标量矢量自动排序
        self.all_data_type_list = ['加速度', '角速度', '温度']
        data_type_is_3d_vector = [True, True, False]
        assert len(self.all_data_type_list) == len(data_type_is_3d_vector)
        # 为lcd添加矢量label
        scalar_count = 0
        i = 0
        for v_name, is_v in zip(self.all_data_type_list, data_type_is_3d_vector):
            if is_v:
                self.ui_label_list_static.append((self.data_labels_ui[i], v_name))
                i += 1
            else:
                scalar_count += 1
        # 为lcd添加标量label
        while scalar_count > 0:
            self.ui_label_list_static.append((self.data_labels_ui[i], '标量'))
            i += 1
            scalar_count -= 3
        scalar_idx = 0    # 标量
        vector_idx = 0    # 矢量
        lcd_idx = 0
        chart_time_idx = 0
        chart_freq_idx = 0
        for data_type_name, is_v in zip(self.all_data_type_list, data_type_is_3d_vector):
            if is_v:    # 只有矢量在此初始化label名称，标量送入标量区内
                for j, v_name in enumerate(['X', 'Y', 'Z']):
                    ui_dict = {'data_name': data_type_name+v_name}
                    if True:
                        ui_dict['lcd'] = (lcd_idx, j)
                        ui_dict['lcd_label_name'] = v_name + ' '    # 加空格是为了调整布局
                    if True:
                        ui_dict['chart_time'] = chart_time_idx
                        ui_dict['chart_time_locate'] = [0, chart_time_idx]
                        chart_time_idx += 1
                    if True:
                        ui_dict['chart_freq'] = chart_freq_idx
                        ui_dict['chart_freq_locate'] = [0, chart_freq_idx]
                        chart_freq_idx += 1

                    self.ui_dict_list.append(ui_dict)
                    vector_idx += 1
                if True:
                    lcd_idx += 1

            else:
                ui_dict = {'data_name': data_type_name}
                if True:
                    ui_dict['lcd'] = (int(lcd_idx + scalar_idx / 3), scalar_idx % 3)
                    ui_dict['lcd_label_name'] = data_type_name + ' '    # 加空格是为了调整布局
                if True:
                    ui_dict['chart_time'] = chart_time_idx
                    ui_dict['chart_time_locate'] = [0, chart_time_idx]
                    chart_time_idx += 1
                if True:
                    ui_dict['chart_freq'] = chart_freq_idx
                    ui_dict['chart_freq_locate'] = [0, chart_freq_idx]
                    chart_freq_idx += 1

                self.ui_dict_list.append(ui_dict)
                scalar_idx += 1
        self.bound_data_and_ui()