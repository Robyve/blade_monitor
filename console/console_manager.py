# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 10:44
# @Author  : XXX
# @Site    : 
# @File    : console_manager.py
# @Software: PyCharm 
# @Comment :

from enum import Enum
from datetime import datetime

from PyQt5.QtGui import QFont


class ConsoleName(Enum):
    PORT = 0


class ConsoleManager:
    def __init__(self, ui):
        self.ui = ui

    def print_on(self, to_console: ConsoleName, message: str):
        if to_console == ConsoleName.PORT:
            self.ui.port_console_textEdit.append(f'[{datetime.now().strftime("%H:%M:%S")}]  {message}')
        else:
            assert False