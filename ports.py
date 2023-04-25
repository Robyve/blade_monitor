# -*- coding: utf-8 -*-
# @Time    : 2023/4/14 17:07
# @Author  : XXX
# @Site    : 
# @File    : ports.py
# @Software: PyCharm 
# @Comment :
import threading
import time

import serial
import serial.tools.list_ports
from PyQt5 import Qt, QtGui, QtCore
from PyQt5.QtCore import QThread, QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap

import data_ui.data_ui_manager as data_ui_manager


class SerialQThread(QThread):
    data_ready_signal = pyqtSignal(str)

    def __init__(self,
                 curr_serial: serial.Serial,
                 collect_dtime
                 ):
        super().__init__()
        self.curr_serial = curr_serial
        self.stop_flag = False
        self.buffer_str = ''
        self.collect_dtime = collect_dtime

    def run(self):
        while True:
            if self.stop_flag:
                return
            if self.curr_serial.in_waiting:
                try:
                    self.buffer_str += self.curr_serial.readline(self.curr_serial.in_waiting).decode(errors='ignore')
                    self.curr_serial.flushOutput()
                except:
                    return
            else:
                self.data_ready_signal.emit(self.buffer_str)
                self.buffer_str = ''
                self.curr_serial.flushOutput()
                time.sleep(self.collect_dtime)

    def stop(self):
        self.stop_flag = True


class PortManager(QObject):
    data_ready_signal = pyqtSignal(str)

    def __init__(self, ui):
        super().__init__()
        self.collect_dtime = 0.1    # 采样频率

        self.curr_serial = None     # 串口实例
        self.port_list = []
        self.curr_baud_rate = None
        self.curr_port = None
        self.open_status = 'closed'

        self.com_combo = ui.com_combo
        self.baud_rate_combo = ui.baud_rate_combo

        self.com_btn = ui.com_btn
        self.com_info_label = ui.com_info_label
        self.com_info_icon_label = ui.com_info_icon_label
        self.com_info_label_new_connect = ui.com_info_label_new_connect
        self.com_info_icon_label_new_connect = ui.com_info_icon_label_new_connect

        self.update_serial_ports(is_init=True)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_serial_ports)
        self.update_timer.start(100)

        self.new_connect_info_timer = QTimer()

        self.serialthread = None
        self.serialwork = None

        self.read_port_thread = None

        # 设置回调函数
        self.com_combo.activated[str].connect(self.on_comport_changed)
        self.baud_rate_combo.activated[str].connect(self.on_baud_rate_changed)
        self.com_btn.clicked.connect(self.on_push_com_btn)

    def on_comport_changed(self, com_port):
        self.curr_port = com_port
        print(f'selected{com_port}')

    def on_baud_rate_changed(self, baud_item):
        self.curr_baud_rate = int(baud_item.split(' ')[0])

    def on_push_com_btn(self):
        if self.open_status == 'closed':
            self.curr_serial = serial.Serial(self.curr_port, self.curr_baud_rate, timeout=60)

            self.com_btn.setText('断开')
            self._set_com_info_label(f'连接到串口: {self.curr_port}', 'main', 'ok')
            self.open_status = 'opened'
            self.com_combo.setEnabled(False)
            self.baud_rate_combo.setEnabled(False)

            self.serialthread = SerialQThread(self.curr_serial, collect_dtime=self.collect_dtime)
            self.serialthread.data_ready_signal.connect(self.handle_data_from_thread)
            self.serialthread.start()

        else:
            self.serialthread.stop()
            self.curr_serial.close()
            self.curr_serial = None
            self.com_btn.setText('启动')
            self._set_com_info_label(' ', 'main')
            self.open_status = 'closed'
            self.com_combo.setEnabled(True)
            self.baud_rate_combo.setEnabled(True)
            self.serialthread.stop()

    def update_serial_ports(self, is_init=False):
        new_port_list = list(serial.tools.list_ports.comports())
        new_port_list = [p.device for p in new_port_list]
        if is_init:
            self.baud_rate_combo.setCurrentIndex(6)
            self.curr_baud_rate = 115200
            if len(new_port_list) > 0:
                self.curr_port = new_port_list[0]
            else:
                self.curr_port = None
                self.com_btn.setEnabled(False)
        if is_init or new_port_list != self.port_list:
            if not is_init and len(new_port_list) > len(self.port_list):
                new_com = next(iter(set(new_port_list) - set(self.port_list)))
                self.new_connect_info_timer.setSingleShot(True)
                self.new_connect_info_timer.timeout.connect(
                    lambda: self._set_com_info_label(f'', 'new_connect', ''))
                self._set_com_info_label(f'新串口{new_com}', 'new_connect', 'info')
                self.new_connect_info_timer.start(1500)
            self.port_list = new_port_list
            self.com_combo.clear()
            for com_port in self.port_list:
                self.com_combo.addItem(com_port)
            if len(new_port_list) > 0:
                self.com_btn.setEnabled(True)
            else:
                self.com_btn.setEnabled(False)
            # 提示串口意外断开
            if self.open_status == 'opened' and self.curr_port not in self.port_list:
                self.serialthread.stop()
                self.curr_serial.close()
                self.curr_serial = None
                self.com_btn.setText('启动')
                self._set_com_info_label('与串口的连接意外断开', 'main', 'warning')
                self.open_status = 'closed'
                self.com_combo.setEnabled(True)
                self.baud_rate_combo.setEnabled(True)
                if len(new_port_list) > 0:
                    self.curr_port = self.port_list[0]
                else:
                    self.curr_port = None

    def send_hex_message(self, message: str):
        # TODO 发送功能待完善
        if self.curr_serial and self.curr_serial.isOpen():
            message = bytes.fromhex(message)
            self.curr_serial.write(message)
            print(f'send to port: {message}')

    def _set_com_info_label(self, text, to_ui='main', icon=None):
        if to_ui == 'main':
            icon_label = self.com_info_icon_label
            info_label = self.com_info_label
        elif to_ui == 'new_connect':
            icon_label = self.com_info_icon_label_new_connect
            info_label = self.com_info_label_new_connect
        else:
            assert False
        if icon is None:
            icon_label.setPixmap(QPixmap(''))
        else:
            icon_label.setPixmap(QPixmap(f'icon/{icon}.png'))
        icon_label.setScaledContents(True)
        info_label.setText(text)

    def handle_data_from_thread(self, data):
        self.data_ready_signal.emit(data)
