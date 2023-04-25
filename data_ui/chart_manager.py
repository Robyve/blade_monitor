# -*- coding: utf-8 -*-
# @Time    : 2023/4/13 22:41
# @Author  : XXX
# @Site    : 
# @File    : chart_manager.py
# @Software: PyCharm 
# @Comment :
import random

import numpy as np
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF, QMargins, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from scipy.signal import find_peaks

charts_x_range = 100
charts_min_height = 300


def init_charts(ui, locates, titles):
    charts_list = []
    assert len(locates) == len(titles)
    scroll_area_list = [
        ui.graph_tab_time_scrollArea, 
        ui.graph_tab_feq_scrollArea
    ]
    for scroll_area in scroll_area_list:
        chart_group = []
        # 创建容器，用于容纳所有的 chart_view
        container = QWidget(scroll_area)
        layout = QVBoxLayout(container)
        for lo, title in zip(locates, titles):
            series = QLineSeries()
            # 创建图表并添加系列
            chart = QChart()
            chart.legend().hide()
            chart.addSeries(series)
            chart.createDefaultAxes()
            chart.setTitle(title)
            # 创建图表视图并设置图表
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.setMargins(QMargins(2, 0, 2, 0))
            chart.setMinimumHeight(charts_min_height)
            layout.addWidget(chart_view)
            chart_group.append(chart)

        scroll_area.setWidget(container)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        container.adjustSize()
        charts_list.append(chart_group)

    return charts_list


def clear_chart_data(chart: QChart):
    s = chart.series()[0]
    s.clear()
    x_axis = chart.axisX()
    x_axis.setRange(0, charts_x_range)
    y_axis = chart.axisY()
    y_axis.setRange(-1., 1.)


def set_chart_datas(chart: QChart, x_list, y_list, axis_range_mode=None):
    s = chart.series()[0]
    s.clear()
    x_axis_max = 0.
    x_axis_min = 0.
    y_axis_max_idx = 0
    y_axis_max = 1.
    y_axis_min = -1.
    for x, y in zip(x_list, y_list):
        if x > x_axis_max:
            x_axis_max = x
        elif x < x_axis_min:
            x_axis_min = x
        if y > y_axis_max:
            y_axis_max_idx = x
            y_axis_max = y
        elif y < y_axis_min:
            y_axis_min = y
        s.append(QPointF(x, y))
    if axis_range_mode is None:
        chart.axisX().setRange(x_axis_min, x_axis_max)
        chart.axisY().setRange(y_axis_min, y_axis_max)
    elif axis_range_mode == 'x_0_symmetry':
        x = max(abs(x_axis_min), abs(x_axis_max))
        chart.axisX().setRange(-x, x)
        chart.axisY().setRange(y_axis_min, y_axis_max)
    peak_idxs = find_peaks(y_list, height=0.05*(y_axis_max - y_axis_min))[0]
    # for idx in peak_idxs:
    #     print(x_list[idx], end=' ')
    # print('')


def add_single_chart_data(chart: QChart, y):
    s = chart.series()[0]
    x = 0 if len(s.points()) == 0 else s.points()[-1].x() + 1
    x_axis = chart.axisX()
    if x < charts_x_range:
        x_axis.setRange(0, charts_x_range)
    else:
        x_axis.setRange(x + 1 - charts_x_range, x+1)
        s.remove(0)
    y_axis = chart.axisY()
    y_axis_max = 1.
    y_axis_min = -1.
    for p in s.points():
        if p.y() > y_axis_max:
            y_axis_max = p.y() + 1.
        elif p.y() < y_axis_min:
            y_axis_min = p.y() - 1.
    y_axis.setRange(y_axis_min, y_axis_max)
    # red_pen = QPen(QColor(255, 0, 0))
    # red_brush = QBrush(QColor(255, 0, 0))
    # blue_pen = QPen(QColor(0, 0, 255))
    # blue_brush = QBrush(QColor(0, 0, 255))
    # if y > 20.:
    #     s.setPen(red_pen)
    # else:
    #     s.setPen(blue_pen)
    s.append(QPointF(x, y))