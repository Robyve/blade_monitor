# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 15:20
# @Author  : XXX
# @Site    : 
# @File    : data_ui_manager.py
# @Software: PyCharm 
# @Comment :
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread

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
        self.data_buffer = np.empty((0, 3))
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
        self.charts_time = None
        self.charts_freq = None

        self.data_recived_from_ports_signal = pyqtSignal(str)
        self.port_manager.data_ready_signal.connect(self.handle_port_data)

        self.ui_label_list_static = [
                (ui.data1_label, '加速度'),
                (ui.data2_label, '角速度'),
            ]
        self.ui_dict_list = [
            {
                'data_name': '加速度X',
                'lcd': (0, 0),
                'chart_time': 0,
                'chart_time_locate': [0, 0],
                'chart_freq': 0,
                'chart_freq_locate': [0, 0],
            },
            {
                'data_name': '加速度Y',
                'lcd': (0, 1),
                'chart_time': 1,
                'chart_time_locate': [1, 0],
                'chart_freq': 1,
                'chart_freq_locate': [1, 0],
            },
            {
                'data_name': '加速度Z',
                'lcd': (0, 2),
                'chart_time': 2,
                'chart_time_locate': [2, 0],
                'chart_freq': 2,
                'chart_freq_locate': [2, 0],
            },
            # {
            #     'data_name': '角速度X',
            #     'lcd': (1, 0),
            #     'chart_time': 3,
            #     'chart_time_locate': [3, 0],
            #     'chart_freq': 3,
            #     'chart_freq_locate': [3, 0],
            # },
        ]
        self._ui_bounder = []
        self.bound_data_and_ui()

    def bound_data_and_ui(self):
        """
        绑定数据和对应的ui控件
        :return:
        """
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
                if j == 0:
                    self.lcd_3_ui[int(ui_info[0])][ui_info[1]].display(d)

                if j == 1:
                    add_single_chart_data(self.charts_time[ui_info], d)

                if j == 2 and end_of_group:
                    if self.data_buffer.shape[0] > self.FFT_COLLECT_RANGE:
                        signal = self.data_buffer[len(self.data_buffer) - self.FFT_COLLECT_RANGE:, i]
                        fft_x, fft_y = self.calc_fft(signal)
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

    @staticmethod
    def convert_data_from_port(data: str):
        try:
            temp_list = data.split('$')
        except (AttributeError, TypeError) as e:
            print(e)
            return
        data_list = []
        for s in temp_list:
            s = s.split(' ')
            if len(s) == 3:
                data_list.append(s)
        for i in range(len(data_list)):
            try:
                data_list[i] = list(map(float, data_list[i]))
            except (TypeError, ValueError) as e:
                print(e)
                return
        return data_list

    @staticmethod
    def calc_fft(signal):
        n = len(signal)
        Fs = 1. / 1e-2  # 采样频率，TODO 统一
        fft_result = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(n, d=1. / Fs)
        return freqs, fft_result

    def handle_port_data(self, data: str):
        temp_list = data.split('$')
        data_list = []
        for s in temp_list:
            s = s.split(' ')
            if len(s) == 3:     # TODO 要删
                data_list.append(s)
        for i in range(len(data_list)):
            data_list[i] = list(map(float, data_list[i]))

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
