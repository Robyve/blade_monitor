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
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from scipy.signal import find_peaks

charts_x_range = 200
charts_min_height = 300

chart_time_x_zip_min = 0
chart_time_x_zip_max = 0
chart_time_y_zip_min = 1.
chart_time_y_zip_max = -1.


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


def init_mult_series_charts(scroll_area, locates, data_zip, titles, series_name):
    """

    :param scroll_area:
    :param locates
    :param data_zip: [行, 列, 系列]
    :param titles:
    :param series_name:
    :return:
    """
    assert len(data_zip) == len(titles)
    chart_group = []
    # 创建容器，用于容纳所有的 chart_view
    container = QWidget(scroll_area)
    layout = QVBoxLayout(container)
    # 确保布局被重新加载
    if len(data_zip) == 0:
        scroll_area.setWidget(container)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        container.adjustSize()
    lo_record = []
    for idx, title in zip(data_zip, titles):
        if idx[0] not in lo_record:
            lo_record.append(idx[0])
            # 创建图表并添加系列
            chart = QChart()
            chart.legend().hide()
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
    for idx, sname in zip(data_zip, series_name):
        series = QLineSeries()
        series.setName(sname)
        chart_group[idx[0]].addSeries(series)
    for c in chart_group:
        c.createDefaultAxes()
    return chart_group


def clear_chart_data(chart: QChart):
    for s in chart.series():
        s.clear()
    x_axis = chart.axisX()
    x_axis.setRange(0, charts_x_range)
    y_axis = chart.axisY()
    y_axis.setRange(-1., 1.)


def set_chart_datas(chart: QChart, series_idx, x_list, y_list, reprint=True):
    x_list = x_list[1:]
    y_list = y_list[1:]
    s = chart.series()[series_idx]
    s.clear()
    for x, y in zip(x_list, y_list):
        s.append(QPointF(x, y))
    if reprint:
        reprint_freq_chart_axis(chart)
    # peak_idxs = find_peaks(y_list, height=0.05*(y_axis_max - y_axis_min))[0]
    # for idx in peak_idxs:
    #     print(x_list[idx], end=' ')
    # print('')


def add_single_chart_data(chart: QChart, y, to_series, reprint=True):
    """
    似乎重绘坐标轴比调整坐标轴性能更好，很奇怪
    :param chart:
    :param y:
    :param to_series:
    :param reprint: 是否重绘
    :return:
    """
    s = chart.series()[to_series]
    x = 0 if len(s.points()) == 0 else s.points()[-1].x() + 1
    if x >= charts_x_range:
        s.remove(0)
    global chart_time_y_zip_max, chart_time_y_zip_min
    for p in s.points():
        if p.y() > chart_time_y_zip_max:
            chart_time_y_zip_max = p.y() + 1
        elif p.y() < chart_time_y_zip_min:
            chart_time_y_zip_min = p.y() - 1
    s.append(QPointF(x, y))
    if reprint:
        reprint_time_chart_axis(chart)


def reprint_time_chart_axis(chart):
    s = chart.series()[0]
    x_max = s.points()[-1].x() + 1
    x_min = s.points()[-1].x() + 1 - charts_x_range

    y_max = 1.
    y_min = -1.
    for s in chart.series():
        for p in s.points():
            if p.y() > y_max:
                y_max = (p.y() + 1) // 1
            elif p.y() < y_min:
                y_min = (p.y() - 1) // 1
    x_axis = QValueAxis()
    y_axis = QValueAxis()
    x_axis.setRange(x_min, x_max)
    y_axis.setRange(y_min, y_max)
    chart.removeAxis(chart.axisX())
    chart.addAxis(x_axis, Qt.AlignBottom)
    chart.removeAxis(chart.axisY())
    chart.addAxis(y_axis, Qt.AlignLeft)
    for s in chart.series():
        s.attachAxis(chart.axisX())
        s.attachAxis(chart.axisY())


def reprint_freq_chart_axis(chart):
    x_max = 1.
    x_min = 0.
    y_max = 1.
    y_min = -1.
    for s in chart.series():
        for p in s.points():
            if p.x() > x_max:
                x_max = (p.x() + 1) // 1
            elif p.x() < x_min:
                x_min = (p.x() - 1) // 1
            if p.y() > y_max:
                y_max = (p.y() + 1) // 1
            elif p.y() < y_min:
                y_min = (p.y() - 1) // 1
    x_axis = QValueAxis()
    y_axis = QValueAxis()
    x_axis.setRange(x_min, x_max)
    y_axis.setRange(y_min, y_max)
    chart.removeAxis(chart.axisX())
    chart.addAxis(x_axis, Qt.AlignBottom)
    chart.removeAxis(chart.axisY())
    chart.addAxis(y_axis, Qt.AlignLeft)
    for s in chart.series():
        s.attachAxis(chart.axisX())
        s.attachAxis(chart.axisY())
