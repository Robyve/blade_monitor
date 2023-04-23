import os
import random
import sys
import logging
from multiprocessing import freeze_support

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer, Qt, QCoreApplication
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtGui import QIcon, QPainter
from qt_material import apply_stylesheet, QtStyleTools, density

from data_ui.data_ui_manager import DataUiManager
from ports import PortManager

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
        self.data_ui_manager = None
        self.main = uic.loadUi('main_window.ui', self)
        self.port_manager = None

        try:
            self.main.setWindowTitle(f'STM32上位机-BJUT')
        except:
            self.main.window_title = f'STM32上位机-BJUT'

        self.custom_styles()
        self.init_widgets()

        self.set_extra(extra)
        self.add_menu_theme(self.main, self.main.menuStyles)
        # self.show_dock_theme(self.main)

        logo = QIcon("qt_material:/logo/logo.svg")
        logo_frame = QIcon("qt_material:/logo/logo_frame.svg")

        try:
            self.main.setWindowIcon(logo)
            self.main.actionToolbar.setIcon(logo)
            [
                self.main.listWidget_2.item(i).setIcon(logo_frame)
                for i in range(self.main.listWidget_2.count())
            ]
        except:
            self.main.window_icon = logo
            self.main.actionToolbar.icon = logo
            [
                setattr(self.main.listWidget_2.item(i), 'icon', logo_frame)
                for i in range(self.main.listWidget_2.count)
            ]

    def custom_styles(self):
        """"""
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
        try:
            for r in range(self.main.tableWidget.rowCount()):
                self.main.tableWidget.setRowHeight(r, 36)

            for r in range(self.main.tableWidget_2.rowCount()):
                self.main.tableWidget_2.setRowHeight(r, 36)

        except:
            for r in range(self.main.tableWidget.row_count):
                self.main.tableWidget.set_row_height(r, 36)

            for r in range(self.main.tableWidget_2.row_count):
                self.main.tableWidget_2.set_row_height(r, 36)

    def init_widgets(self):
        self.port_manager = PortManager(self)
        self.data_ui_manager = DataUiManager(self, self.port_manager)

        def rand_add_data():
            datas = []
            for i in range(4):
                datas.append(float(random.randint(0, 100)) / float(random.randint(1, 10)))
            self.data_ui_manager.add_test_datas(datas)
        self.test_action.triggered.connect(rand_add_data)

        def rand_add_data_2():
            datas = []
            for i in range(3):
                datas.append(float(random.randint(0, 100)) / float(random.randint(1, 10)))
            self.data_ui_manager.add_3d_datas(0, [0, 1, 2], datas)
        self.test_action_2.triggered.connect(rand_add_data_2)




T0 = 1000

if __name__ == "__main__":
    def take_screenshot():
        pixmap = frame.main.grab()
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

    frame = RuntimeStylesheets()
    try:
        frame.main.showMaximized()
    except:
        frame.main.show_maximized()

    if hasattr(app, 'exec'):
        app.exec()
    else:
        app.exec_()
