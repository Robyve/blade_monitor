import os
import random
import sys
import logging
from multiprocessing import freeze_support

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, Qt, QCoreApplication
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from qt_material import apply_stylesheet, QtStyleTools

from data_ui.data_ui_manager import DataUiManager
from ports import PortManager
from console.console_manager import ConsoleManager
from data_saver.data_saver import DataSaver


if hasattr(Qt, 'AA_ShareOpenGLContexts'):
    try:
        QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    except:
        QCoreApplication.set_attribute(Qt.AA_ShareOpenGLContexts)
else:
    print("'Qt' object has no attribute 'AA_ShareOpenGLContexts'")

app = QApplication([])
freeze_support()
try:
    app.processEvents()
    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(app.quit)
except:
    app.process_events()
    app.quit_on_last_window_closed = False
    app.lastWindowClosed.connect(app.quit)

# Extra stylesheets
extra = {
    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',
    # Font
    'font_family': 'Roboto',
    # Density
    'density_scale': '0',
    # Button Shape
    'button_shape': 'default',
}


class RuntimeStylesheets(QMainWindow, QtStyleTools):
    def __init__(self):
        """Constructor"""
        super().__init__()
        self.data_saver = None
        self.console_manager = None
        self.data_ui_manager = None
        self.main = uic.loadUi('main_window.ui', self)
        self.port_manager = None

        try:
            self.main.setWindowTitle(f'上位机')
        except:
            self.main.window_title = f'上位机'

        self.custom_styles()
        self.init_widgets()

        self.set_extra(extra)
        self.add_menu_theme(self.main, self.main.menuStyles)
        self.add_menu_density(self.main, self.main.menuDensity)
        # self.show_dock_theme(self.main)

        logo = QIcon("qt_material:/logo/logo.svg")
        # logo = QIcon("icon/bjut.jpeg")
        logo_frame = QIcon("qt_material:/logo/logo_frame.svg")

        try:
            self.main.setWindowIcon(logo)
            self.main.actionToolbar.setIcon(logo)
        except:
            self.main.window_icon = logo
            self.main.actionToolbar.icon = logo

    def custom_styles(self):
        for i in range(self.main.toolBar_vertical.layout().count()):

            try:
                tool_button = (
                    self.main.toolBar_vertical.layout().itemAt(i).widget()
                )
                tool_button.setMaximumWidth(150)
                tool_button.setMinimumWidth(150)
            except:
                tool_button = (
                    self.main.toolBar_vertical.layout().item_at(i).widget()
                )
                tool_button.maximum_width = 150
                tool_button.minimum_width = 150

    def init_widgets(self):
        # 顺序不可变
        self.console_manager = ConsoleManager(self)
        self.data_saver = DataSaver(self)
        self.port_manager = PortManager(self)
        self.data_ui_manager = DataUiManager(self, self.port_manager)

        # 生成具有一定周期性的随机序列
        self.t = 0

        def test_port():
            self.port_manager.send_hex_message('77 03 01 02 03')

        self.test_action.triggered.connect(test_port)

        def rand_add_data_2():
            # 设定随机序列的参数
            freq_list = [1250, 500, 300, 200]
            a_list = [9, 5, 3, 8]
            datas = ''
            for i in range(random.randint(1, 3)):
                for j in range(3):
                    datas += '$' if j == 0 else ' '
                    # datas += str(float(random.randint(3, 300)) / float(random.randint(7, 50)))
                    datas_f = 0.
                    for a, f in zip(a_list, freq_list):
                        datas_f += a * np.sin(2 * f * self.t)
                    datas_f += float(0.1 * random.randint(-10, 10)) * np.mean(a_list) * 0.1   # 噪声项
                    datas += str(datas_f)
                    self.t += 1e-4
            self.data_ui_manager.handle_port_data(datas)
        # self.test_timer = QTimer()
        # self.test_timer.start(1)
        # self.test_action_2.triggered.connect(rand_add_data_2)
        # self.test_timer.timeout.connect(rand_add_data_2)


T0 = 1000
main_ui = None

if __name__ == "__main__":
    def take_screenshot():
        pixmap = main_ui.main.grab()
        pixmap.save(os.path.join('screenshots', f'{theme}.png'))
        print(f'Saving {theme}')

    if len(sys.argv) > 2:
        theme = sys.argv[2]
        try:
            QTimer.singleShot(T0, take_screenshot)
            QTimer.singleShot(T0 * 2, app.closeAllWindows)
        except:
            QTimer.single_shot(T0, take_screenshot)
            QTimer.single_shot(T0 * 2, app.closeAllWindows)
    else:
        theme = 'default'

    # Set theme on in itialization
    apply_stylesheet(
        app,
        theme + '.xml',
        invert_secondary=('light' in theme and 'dark' not in theme),
        extra=extra,
    )

    main_ui = RuntimeStylesheets()
    try:
        main_ui.main.showMaximized()
    except:
        main_ui.main.show_maximized()

    if hasattr(app, 'exec'):
        app.exec()
    else:
        app.exec_()
