# -*- coding: utf-8 -*-
# @Time    : 2023/4/13 22:41
# @Author  : XXX
# @Site    : 
# @File    : chart_manager.py
# @Software: PyCharm 
# @Comment :
import random

from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, QMargins, Qt, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QWidget, QVBoxLayout

charts_x_range = 10
charts_min_height = 400


def init_charts(ui, locates, titles):
    charts = []
    assert len(locates) == len(titles)
    scroll_area = ui.graph_tab_right_scrollArea

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
        charts.append(chart)
        # 创建图表视图并设置图表
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart.setMargins(QMargins(2, 2, 2, 2))
        chart.setMinimumHeight(400)
        layout.addWidget(chart_view)

    # 将容器添加到 QScrollArea 中
    scroll_area.setWidget(container)

    # 设置 QScrollArea 可伸缩，并调整大小以适应所有内容
    container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    scroll_area.setWidgetResizable(True)
    container.adjustSize()

    return charts


def add_single_chart_data(chart: QChart, y):
    s = chart.series()[0]
    x = 0 if len(s.points()) == 0 else s.points()[-1].x() + 1
    x_axis = chart.axisX()
    if x < charts_x_range:
        x_axis.setRange(0, charts_x_range)
    else:
        x_axis.setRange(x + 1 - charts_x_range, x+1)
        s.remove(0)
    s.append(QPointF(x, y))
    y_axis = chart.axisY()
    y_axis_max = 1.
    y_axis_min = -1.
    for p in s.points():
        if p.y() > y_axis_max:
            y_axis_max = p.y() + 1.
        elif p.y() < y_axis_min:
            y_axis_min = p.y() - 1.
    y_axis.setRange(y_axis_min, y_axis_max)