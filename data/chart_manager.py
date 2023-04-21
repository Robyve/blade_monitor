# -*- coding: utf-8 -*-
# @Time    : 2023/4/13 22:41
# @Author  : XXX
# @Site    : 
# @File    : chart_manager.py
# @Software: PyCharm 
# @Comment :
import random

from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, QMargins, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGridLayout

charts_x_range = 300


def init_charts(ui, locates, titles):
    # TODO 折线图示例
    charts = []
    assert len(locates) == len(titles)
    scroll_area = ui.graph_tab_right_scrollArea
    layout = QGridLayout(scroll_area)
    scroll_area.setMinimumHeight(100*len(locates))
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
        # ui.graph_tab_right_layout.addWidget(chart_view, *lo)
        layout.addWidget(chart_view, *lo)
    return charts


def add_single_chart_data(chart: QChart, y):
    s = chart.series()[0]
    x = 0 if len(s.points()) == 0 else s.points()[-1].x() + 1
    x_axis = QValueAxis()
    if x < charts_x_range:
        x_axis.setRange(0, charts_x_range)
    else:
        x_axis.setRange(x + 1 - charts_x_range, x+1)
        s.remove(0)
    s.append(QPointF(x, y))
    y_axis = QValueAxis()
    y_axis_max = 1.
    y_axis_min = -1.
    for p in s.points():
        if p.y() > y_axis_max:
            y_axis_max = p.y()
        elif p.y() < y_axis_min:
            y_axis_min = p.y()
    y_axis.setRange(y_axis_min, y_axis_max)
    chart.removeAxis(chart.axisX())
    chart.addAxis(x_axis, Qt.AlignBottom)
    chart.removeAxis(chart.axisY())
    chart.addAxis(y_axis, Qt.AlignLeft)
    s.attachAxis(chart.axisX())
    s.attachAxis(chart.axisY())