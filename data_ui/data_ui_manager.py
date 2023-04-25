# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 15:20
# @Author  : XXX
# @Site    : 
# @File    : data_ui_manager.py
# @Software: PyCharm 
# @Comment :
import numpy as np
from PyQt5.QtCore import pyqtSignal

import ports
from ports import SerialQThread

from data_ui.chart_manager import *


class DataUiManager:
    def __init__(self, ui,
                 port_manager: ports.PortManager):
        self.fft_collect_range = 200  # fft采样范围，属于少于该范围不进行fft
        self.data_buffer = []
        self.port_manager = port_manager
        self.chart_titles = ['加速度X', '加速度Y', '加速度Z']
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
        self.graph_locate = [
            [0, 0], [1, 0], [2, 0]
        ]
        self.charts_time, self.charts_freq = init_charts(ui, self.graph_locate, self.chart_titles)

        self.data_recived_from_ports_signal = pyqtSignal(str)
        self.port_manager.data_ready_signal.connect(self.handle_port_data)

    def add_datas(self, ui_dict: dict, datas):
        """
        高级API
        :param ui_dict:
        :param datas:
        :return:
        """
        lcd_idxs = ui_dict.get('lcd')
        if lcd_idxs is not None:
            for lcd, d in zip(self.lcd_3_ui[lcd_idxs], datas):
                lcd.display(d)
        chart_time_idx = ui_dict.get('chart_time')
        if chart_time_idx is not None:
            for cf, d in zip(self.charts_time[chart_time_idx], datas):
                add_single_chart_data(cf, d)
        chart_freq_idx = ui_dict.get('chart_freq')
        if chart_freq_idx is not None:
            for cf, d in zip(self.charts_freq[chart_freq_idx], datas):
                add_single_chart_data(cf, d)

    def add_3d_datas(self, lcd_3_idx: int, to_chart_list, chart_idxs: list[int], datas):
        assert len(chart_idxs) == len(datas)
        for lcd, d in zip(self.lcd_3_ui[lcd_3_idx], datas):
            lcd.display(d)
        for idx, d in zip(chart_idxs, datas):
            add_single_chart_data(to_chart_list[idx], d)

    def add_data_to_charts(self, to_chart_list, chart_idxs: list[int], datas):
        for idx, d in zip(chart_idxs, datas):
            add_single_chart_data(to_chart_list[idx], d)

    def add_test_datas(self, datas):
        assert len(datas) == len(self.chart_titles)
        for lcd, chart, d in zip(self.lcd_3_ui, self.charts_time, datas):
            lcd[0].display(d)
            lcd[1].display(d)
            lcd[2].display(d)
            add_single_chart_data(chart, d)

    def convert_data_from_port(self, data: str):
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

    def calc_fft(self, signal):
        # TODO fft采样范围
        n = len(signal)
        Fs = 1. / 1e-2  # 采样频率，TODO 统一
        fft_result = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(n, d=1. / Fs)
        return freqs, fft_result

    def handle_port_data(self, data: str):
        # data_list = self.convert_data_from_port(data)
        temp_list = data.split('$')
        data_list = []
        for s in temp_list:
            s = s.split(' ')
            if len(s) == 3:
                data_list.append(s)
        for i in range(len(data_list)):
            data_list[i] = list(map(float, data_list[i]))

        if data_list is None:
            return
        # 到此数据应该是清洗过的
        self.data_buffer.extend(data_list)
        for d in data_list:
            self.add_3d_datas(0, self.charts_time, [0, 1, 2], d)
        if len(self.data_buffer) > self.fft_collect_range:
            for i in range(0, 3):
                signal = [d[i] for d in self.data_buffer[len(self.data_buffer)-self.fft_collect_range:]]
                fft_x, fft_y = self.calc_fft(signal)
                set_chart_datas(self.charts_freq[i], fft_x, fft_y)
        # TODO 优化缓存清理
        if len(self.data_buffer) > 400:
            self.data_buffer = self.data_buffer[-self.fft_collect_range:]
