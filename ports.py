# -*- coding: utf-8 -*-
# @Time    : 2023/4/14 17:07
# @Author  : XXX
# @Site    : 
# @File    : ports.py
# @Software: PyCharm 
# @Comment :
import threading

import serial.tools.list_ports
from PyQt5 import Qt, QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


class PortManager:
    def __init__(self, ui):
        self.COM = QSerialPort()
        self.port_info = QSerialPortInfo.availablePorts()
        self.port_list = [port.portName() for port in self.port_info]

        self.com_combo = ui.com_combo
        self.baud_rate_combo = ui.baud_rate_combo
        self.com_btn = ui.com_btn
        self.com_info_label = ui.com_info_label
        self.com_info_icon_label = ui.com_info_icon_label

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timeout)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_serial_ports)
        self.update_timer.start(100)
        self.open_status = 'closed'

        for com_port in self.port_info:
            self.com_combo.addItem(com_port.portName())
            print(com_port.portName())
            print(com_port.description())
        self.COM.setPortName(self.port_info[0].portName())

        # 设置回调函数
        self.com_combo.activated[str].connect(self.on_comport_changed)
        self.baud_rate_combo.activated[str].connect(self.on_baud_rate_changed)
        self.com_btn.clicked.connect(self.on_push_com_btn)

    def on_comport_changed(self, com_port):
        self.COM.setPortName(com_port)

    def on_baud_rate_changed(self, baud_item):
        baud_rate = int(baud_item.split(' ')[0])
        self.COM.setBaudRate(baud_rate)

    def on_push_com_btn(self):
        if self.open_status == 'closed':
            flag = self.COM.open(QSerialPort.ReadWrite)
            if not flag:
                self.com_info_label.setText('连接失败')
                return
            self.com_btn.setText('断开')
            self.timer.start(200)
            self._set_com_info_label(f'连接到串口: {self.COM.portName()}', 'ok')
            self.open_status = 'opened'
        else:
            self.COM.close()
            self.timer.stop()
            self.com_btn.setText('启动')
            self.com_info_label.setText(f'')
            self._set_com_info_label(' ')
            self.open_status = 'closed'

    def update_serial_ports(self):
        new_port_info = QSerialPortInfo.availablePorts()
        new_port_list = [port.portName() for port in new_port_info]
        if new_port_list != self.port_list:
            self.port_info = new_port_info
            self.port_list = new_port_list
            self.com_combo.clear()
            for com_port in self.port_info:
                self.com_combo.addItem(com_port.portName())
            # 提示串口意外断开
            if self.open_status == 'opened' and self.COM.portName() not in self.port_list:
                self.COM.close()
                self.timer.stop()
                self.com_btn.setText('启动')
                self._set_com_info_label('与串口的连接意外断开', 'warning')
                self.open_status = 'closed'
                # 回归默认串口，会不会有问题？
                self.COM.setPortName(self.port_info[0].portName())

    def on_timeout(self):
        rcv_data = self.COM.readAll()
        if len(rcv_data) >= 2:
            print(int.from_bytes(bytes(rcv_data[0:2]), 'little'))

    def _set_com_info_label(self, text, icon=None):
        if icon is None:
            self.com_info_icon_label.setPixmap(QPixmap(''))
        else:
            self.com_info_icon_label.setPixmap(QPixmap(f'icon/{icon}.png'))
        self.com_info_icon_label.setScaledContents(True)
        self.com_info_label.setText(text)