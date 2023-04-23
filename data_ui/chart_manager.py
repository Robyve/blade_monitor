# -*- coding: utf-8 -*-
# @Time    : 2023/4/13 22:41
# @Author  : XXX
# @Site    : 
# @File    : chart_manager.py
# @Software: PyCharm 
# @Comment :
import random

from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF, QMargins, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout

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
            chart.setMargins(QMargins(0, 0, 0, 0))
            chart.setMinimumHeight(charts_min_height)
            layout.addWidget(chart_view)
            chart_group.append(chart)

        scroll_area.setWidget(container)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setWidgetResizable(True)
        container.adjustSize()
        charts_list.append(chart_group)

    return charts_list


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