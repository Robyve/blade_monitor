# -*- coding: utf-8 -*-
# @Time    : 2023/4/14 17:07
# @Author  : XXX
# @Site    : 
# @File    : ports.py
# @Software: PyCharm 
# @Comment :

import serial.tools.list_ports
from PyQt5 import Qt, QtGui, QtCore, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


class PortManager:
    def __init__(self, ui):
        self.COM = QSerialPort()
        self.port_list = QSerialPortInfo.availablePorts()
        self.com_combo = ui.com_combo
        self.baud_rate_combo = ui.baud_rate_combo
        self.com_btn = ui.com_btn
        self.com_info_label = ui.com_info_label

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.open_status = 'closed'

        for com_port in self.port_list:
            self.com_combo.addItem(com_port.portName())
            print(com_port.portName())
            print(com_port.description())
        self.COM.setPortName(self.port_list[0].portName())

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
            if not self.COM.open(QSerialPort.ReadWrite):
                self.com_info_label.setText('连接失败')
                return
            self.timer.start(100)
            self.com_btn.setText('断开')
            self.open_status = 'opened'
        else:
            self.COM.close()
            self.timer.stop()
            self.com_btn.setText('启动')
            self.open_status = 'closed'

    def on_timeout(self):
        rcv_data = self.COM.readAll()
        if len(rcv_data) >= 2:
            print(int.from_bytes(bytes(rcv_data[0:2]), 'little'))