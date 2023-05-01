# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 10:44
# @Author  : XXX
# @Site    : 
# @File    : console_manager.py
# @Software: PyCharm 
# @Comment :

from enum import Enum
from datetime import datetime

from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor


class ConsoleName(Enum):
    PORT = 0,
    DATA = 1,


class ConsoleManager:
    instance = None

    def __init__(self, ui):
        self.ui = ui
        if not ConsoleManager.instance:
            ConsoleManager.instance = self

    @staticmethod
    def print_on(to_console: ConsoleName, message: str, level='Normal'):
        instance = ConsoleManager.instance
        text_format = QTextCharFormat()
        if level == 'Normal':
            text_format.setForeground(QColor("color: #555555;"))
        elif level == 'Warning':
            text_format.setForeground(QColor("color: #ffc107;"))
        elif level == 'Error':
            text_format.setForeground(QColor("color: #dc3545;"))
        elif level == 'Success':
            text_format.setForeground(QColor("color: #17a2b8;"))
        else:
            assert False

        if to_console == ConsoleName.PORT:
            # 插入新的字符串行
            new_line_text = f'[{datetime.now().strftime("%H:%M:%S")}]  {message}'
            cursor = instance.ui.port_console_port_textEdit.textCursor()
            cursor.insertText(new_line_text + "\n")
            cursor.setPosition(cursor.position() - len(new_line_text) - 1)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(text_format)
        elif to_console == ConsoleName.DATA:
            instance.ui.port_console_data_textEdit.append(f'[{datetime.now().strftime("%H:%M:%S")}]  {message}')
        else:
            assert False