# -*- coding: utf-8 -*-
# @Time    : 2023/4/13 22:41
# @Author  : XXX
# @Site    : 
# @File    : chart_manager.py
# @Software: PyCharm 
# @Comment :
import random

import numpy as np
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, QMargins, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from scipy.signal import find_peaks

charts_x_range = 100
charts_min_height = 300


def init_charts(scroll_area, locates, titles):
    assert len(locates) == len(titles)
    chart_group = []
    # 创建容器，用于容纳所有的 chart_view
    container = QWidget(scroll_area)
    layout = QVBoxLayout(container)
    # 确保布局被重新加载
    if len(locates) == 0:
        scroll_area.setWidget(container)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        container.adjustSize()
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

    return chart_group


def clear_chart_data(chart: QChart):
    s = chart.series()[0]
    s.clear()
    x_axis = chart.axisX()
    x_axis.setRange(0, charts_x_range)
    y_axis = chart.axisY()
    y_axis.setRange(-1., 1.)


def set_chart_datas(chart: QChart, x_list, y_list):
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
    chart.axisX().setRange(x_axis_min, x_axis_max)
    chart.axisY().setRange(y_axis_min, y_axis_max)
    # peak_idxs = find_peaks(y_list, height=0.05*(y_axis_max - y_axis_min))[0]
    # for idx in peak_idxs:
    #     print(x_list[idx], end=' ')
    # print('')


def add_single_chart_data(chart: QChart, y):
    """
    似乎重绘坐标轴比调整坐标轴性能更好，很奇怪
    :param chart:
    :param y:
    :return:
    """
    s = chart.series()[0]
    x_axis_max = 0
    x_axis_min = charts_x_range
    x = 0 if len(s.points()) == 0 else s.points()[-1].x() + 1
    if x >= charts_x_range:
        x_axis_min = x + 1 - charts_x_range
        x_axis_max = x + 1
        s.remove(0)

    y_axis_max = 1.
    y_axis_min = -1.
    for p in s.points():
        if p.y() > y_axis_max:
            y_axis_max = p.y()
        elif p.y() < y_axis_min:
            y_axis_min = p.y()
    s.append(QPointF(x, y))
    _reprint_chart_axis(chart, x_axis_min, x_axis_max, y_axis_min, y_axis_max)


def _reprint_chart_axis(chart, x_min, x_max, y_min, y_max):
    x_axis = QValueAxis()
    y_axis = QValueAxis()
    x_axis.setRange(x_min, x_max)
    y_axis.setRange(y_min, y_max)
    chart.removeAxis(chart.axisX())
    chart.addAxis(x_axis, Qt.AlignBottom)
    chart.removeAxis(chart.axisY())
    chart.addAxis(y_axis, Qt.AlignLeft)
    s = chart.series()[0]
    s.attachAxis(chart.axisX())
    s.attachAxis(chart.axisY())