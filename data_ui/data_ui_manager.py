# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 15:20
# @Author  : XXX
# @Site    : 
# @File    : data_ui_manager.py
# @Software: PyCharm 
# @Comment :
from PyQt5.QtCore import pyqtSignal

import ports
from ports import SerialQThread

from data_ui.chart_manager import *


class DataUiManager:
    def __init__(self, ui,
                 port_manager: ports.PortManager):
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
        self.charts = init_charts(ui, self.graph_locate, self.chart_titles)

        self.data_recived_from_ports_signal = pyqtSignal(str)
        self.port_manager.data_ready_signal.connect(self.handle_port_data)

    def add_3d_datas(self, lcd_3_idx: int, chart_idxs: list[int], datas):
        assert len(chart_idxs) == len(datas)
        for lcd, d in zip(self.lcd_3_ui[lcd_3_idx], datas):
            lcd.display(d)
        for idx, d in zip(chart_idxs, datas):
            add_single_chart_data(self.charts[idx], d)

    def add_test_datas(self, datas):
        assert len(datas) == len(self.chart_titles)
        for lcd, chart, d in zip(self.lcd_3_ui, self.charts, datas):
            lcd[0].display(d)
            lcd[1].display(d)
            lcd[2].display(d)
            add_single_chart_data(chart, d)

    def handle_port_data(self, data: str):
        temp_list = data.split('$')
        data_list = []
        for s in temp_list:
            s = s.split(' ')
            if len(s) == 3:
                data_list.append(s)
        for d in data_list:
            d = list(map(float, d))
            self.add_3d_datas(0, [0, 1, 2], d)
