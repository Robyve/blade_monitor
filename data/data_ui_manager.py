# -*- coding: utf-8 -*-
# @Time    : 2023/4/16 15:20
# @Author  : XXX
# @Site    : 
# @File    : data_ui_manager.py
# @Software: PyCharm 
# @Comment :

from data.chart_manager import *


class DataUiManager:
    def __init__(self, ui):
        self.data_titles = ['加速度角度', '角度', '陀螺仪', '磁场']
        self.data_labels_ui = [
            ui.data1_label,
            ui.data2_label,
            ui.data3_label,
            ui.data4_label,
        ]
        self.data_lcd_ui = [
            [ui.x1_lcd, ui.y1_lcd, ui.z1_lcd],
            [ui.x2_lcd, ui.y2_lcd, ui.z2_lcd],
            [ui.x3_lcd, ui.y3_lcd, ui.z3_lcd],
            [ui.x4_lcd, ui.y4_lcd, ui.z4_lcd],
        ]
        self.graph_locate = [
            [0, 0], [1, 0], [2, 0], [3, 0]
        ]
        self.charts = init_charts(ui, self.graph_locate, self.data_titles)

    def add_datas(self, datas):
        assert len(datas) == len(self.data_titles)
        for lcd, chart, d in zip(self.data_lcd_ui, self.charts, datas):
            lcd[0].display(d)
            lcd[1].display(d)
            lcd[2].display(d)
            add_chart_data(chart, d)
