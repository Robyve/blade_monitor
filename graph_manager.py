# -*- coding: utf-8 -*-
# @Time    : 2023/4/13 22:41
# @Author  : XXX
# @Site    : 
# @File    : graph_manager.py
# @Software: PyCharm 
# @Comment :
import random

import numpy as np
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, QMargins, Qt
from PyQt5.QtGui import QIcon, QPainter
from main import RuntimeStylesheets


charts = []
charts_x_range = 20


def init_charts(layout, locates, titles):
    # TODO 折线图示例
    assert len(locates) == len(titles)
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
        layout.addWidget(chart_view, *lo)


def add_chart_data(chart: QChart, y):
    y = random.randint(0, 10)
    s = chart.series()[0]
    x = 0 if len(s.points()) == 0 else s.points()[-1].x() + 1
    x_axis = QValueAxis()
    if x < charts_x_range:
        x_axis.setRange(0, charts_x_range)
    else:
        x_axis.setRange(x + 1 - charts_x_range, x+1)
    s.append(QPointF(x, y))
    chart.removeSeries(chart.series()[0])
    chart.addSeries(s)
    y_axis = QValueAxis()
    y_axis_max = 0
    y_axis_min = 0
    for p in s.points():
        if p.y() > y_axis_max:
            y_axis_max = p.y()
        elif p.y() < y_axis_min:
            y_axis_min = p.y()
    y_axis.setRange(0, y_axis_max)
    chart.removeAxis(chart.axisX())
    chart.addAxis(x_axis, Qt.AlignBottom)
    chart.removeAxis(chart.axisY())
    chart.addAxis(y_axis, Qt.AlignLeft)
    s.attachAxis(chart.axisX())
    s.attachAxis(chart.axisY())