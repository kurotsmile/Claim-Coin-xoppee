
import sys
import time
from datetime import datetime, timedelta
import subprocess
import json
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QTextEdit, QMainWindow, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QCheckBox, QStyledItemDelegate, QHBoxLayout, QComboBox, QHeaderView
from PyQt5.QtGui import QColor
from config import CONFIG
from log_updater import LogUpdater, DeviceTableUpdater
from worker.worker_close import WorkerClose
from worker.worker_scroll import WorkerScrollRun
from worker.worker_hunter import WorkerHunterRun
import threading
import queue
import random
from concurrent.futures import ThreadPoolExecutor
JSON_FILE_PATH = 'device_data.json'
BOX_JSON_FILE_PATH = 'box.json'
class CenterCheckBoxDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if index.column() == 0:
            option.displayAlignment = Qt.AlignCenter

class CenterCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QCheckBox::indicator {"
                           "    subcontrol-origin: padding;"
                           "    subcontrol-position: center;"
                           "}")
  

class MyMainWindow(QMainWindow):
    update_table_signal = pyqtSignal(str, list)
    send_link_signal = pyqtSignal(str)
    send_log_signal = pyqtSignal(str)
    closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shopee Coin Auto Claimer - nospk")
        self.workers = {}
        self.box_mappings = {}
        self.total_coin = 0
        self.total_count = 0
        self.total_devices = 0
        self.limit_app = 'No'
        self.APP_PACKAGE = CONFIG.APP_PACKAGE
        self.thread_update1 = QThreadPool.globalInstance()
        self.thread_update2 = QThreadPool.globalInstance()
        self.thread_worker1 = QThreadPool.globalInstance()
        self.thread_worker2 = QThreadPool.globalInstance()
        self.thread_reset = QThreadPool.globalInstance()
        self.thread_reset.setMaxThreadCount(10)
        self.thread_update1.setMaxThreadCount(100)
        self.thread_update2.setMaxThreadCount(100)
        self.thread_worker1.setMaxThreadCount(200)
        self.thread_worker2.setMaxThreadCount(200)
        self.col_checkbox = 0
        self.col_device = 1
        self.col_device_number = 2
        self.col_coins = 3
        self.col_counts = 4
        self.col_status = 5
        self.col_timestop = 6
        self.col_min = 7
        self.col_max = 8
        self.col_error = 9
        self.col_fail = 10
        self.col_open = 11
        self.col_action = 12
        # Create log Windown
        self.log_window = LogWindow()
        self.log_window.setGeometry(300, 300, 400, 300)
        self.send_log_signal.connect(self.log_window.append_log)
        self.log_window.show()
        self.closed.connect(self.log_window.close)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.table_widget = QTableWidget()
        self.table_widget.setItemDelegateForColumn(0, CenterCheckBoxDelegate())
        self.table_widget.setColumnCount(13)
        self.table_widget.setHorizontalHeaderLabels(
            ['Select', 'Device', 'Phone', 'Coins', 'Counts', 'Status', 'Time Stop', 'Min', 'Max','Error', 'Fail', 'Open', 'Action'])
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_widget)
        
        # Thiết lập kích thước cột Select để vừa với checkbox
        self.table_widget.setColumnWidth(self.col_checkbox, 45)
        self.table_widget.setColumnWidth(self.col_device_number, 45)
        self.table_widget.setColumnWidth(self.col_device, 110)
        self.table_widget.setColumnWidth(self.col_coins, 60)
        self.table_widget.setColumnWidth(self.col_counts, 50)
        self.table_widget.setColumnWidth(self.col_status, 120)
        self.table_widget.setColumnWidth(self.col_timestop, 110)
        self.table_widget.setColumnWidth(self.col_min, 45)
        self.table_widget.setColumnWidth(self.col_max, 45)
        self.table_widget.setColumnWidth(self.col_error, 45)
        self.table_widget.setColumnWidth(self.col_fail, 45)
        self.table_widget.setColumnWidth(self.col_open, 45)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        
        # Set time
        time_layout = QHBoxLayout()

        self.checkbox_time = QCheckBox("Set Time")
        time_layout.addWidget(self.checkbox_time)

        self.comboBox_hours = QComboBox()
        for i in range(0, 13):
            self.comboBox_hours.addItem(str(i))
        time_layout.addWidget(self.comboBox_hours)

        self.label = QLabel("Hours")
        time_layout.addWidget(self.label)

        self.comboBox_minutes = QComboBox()
        for i in range(0, 61):
            self.comboBox_minutes.addItem(str(i))
        time_layout.addWidget(self.comboBox_minutes)
        
        self.label = QLabel("Minitues")
        time_layout.addWidget(self.label)
        

        self.button = QPushButton("Update")
        self.button.clicked.connect(self.update_devies)
        time_layout.addWidget(self.button)

        # Add the row layout to the main layout
        layout.addLayout(time_layout)

        #Check claim coin 100
        mode_coin_layout= QHBoxLayout()
        
        self.min_coin = QComboBox()
        self.label_min_coin = QLabel('Min Coin')
        for i in range(1, 5):
            self.min_coin.addItem(str(i*100))
        mode_coin_layout.addWidget(self.label_min_coin)
        mode_coin_layout.addWidget(self.min_coin)
        #self.min_coin.setCurrentIndex(1)
        
        self.label_max_minute = QLabel('Max Minute')
        self.max_minute = QComboBox()
        for i in range(1, 5):
            self.max_minute.addItem(str(i*5))
        mode_coin_layout.addWidget(self.label_max_minute)
        mode_coin_layout.addWidget(self.max_minute)
        #self.max_minute.setCurrentIndex(1)
        
        self.label_reset_app = QLabel('Reset App')
        self.reset_app = QComboBox()
        self.reset_app.addItem(str('No'))
        for i in range(1, 10):
            self.reset_app.addItem(str(i*50))
        mode_coin_layout.addWidget(self.label_reset_app)
        mode_coin_layout.addWidget(self.reset_app)
        self.reset_app.currentIndexChanged.connect(self.on_reset_app_changed)
        self.limit_app = self.reset_app.currentText()
        
        coin_layout = QHBoxLayout()
        coin_layout.addLayout(mode_coin_layout)
        self.input_link = QLineEdit()
        self.button_open_link = QPushButton("Open Link")
        self.label_total_coin = QLabel(f'Total: {self.total_coin} coins   Progress:0% ')
        self.button_open_link.clicked.connect(self.open_link_devices)
        coin_layout.addWidget(self.input_link)
        coin_layout.addWidget(self.button_open_link)
        coin_layout.addWidget(self.label_total_coin)
        layout.addLayout(coin_layout)        
        #Button command
        button_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        self.select_all_button.setFixedSize(80, 40)
        
        self.unselect_all_button = QPushButton("Unselect All")
        self.unselect_all_button.clicked.connect(self.select_all)
        self.unselect_all_button.setFixedSize(80, 40)
        
        self.bill_button = QPushButton("Bill")
        self.bill_button.clicked.connect(self.bill_action)
        self.bill_button.setFixedHeight(40)
        self.bill_button.setStyleSheet("background-color: blue; color: white;")
        
        self.start_button_scroll = QPushButton("Start Scroll")
        self.start_button_scroll.clicked.connect(self.start_action_scroll)
        self.start_button_scroll.setFixedHeight(40)
        self.start_button_scroll.setStyleSheet("background-color: green; color: white;")
        
        self.start_button_hunter = QPushButton("Start Hunter")
        self.start_button_hunter.clicked.connect(self.start_action_hunter)
        self.start_button_hunter.setFixedHeight(40)
        self.start_button_hunter.setStyleSheet("background-color: rgba(147, 143, 20, 0.8); color: white;")
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_action)
        self.stop_button.setFixedHeight(40)
        self.stop_button.setStyleSheet("background-color: red; color: white;")
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_table)
        self.refresh_button.setFixedHeight(40)
        
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.unselect_all_button)
        
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.bill_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.start_button_scroll)
        if hasattr(CONFIG, 'key') and CONFIG.key == 'admin':
            button_layout.addWidget(self.start_button_hunter)
        layout.addLayout(button_layout)



        
        self.load_box_mappings()
        self.refresh_table()
        self.load_data()
        
    def on_reset_app_changed(self):
        self.limit_app = self.reset_app.currentText()
           
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
        raise Exception("Closed App")
        
    def refresh_table(self):
        self.table_widget.setRowCount(0)
        devices = self.get_devices_list()
        for device in devices:
            self.add_row(True, device, 0, 0, 'Ready')
        del devices   
    def load_box_mappings(self):
        try:
            with open(BOX_JSON_FILE_PATH, 'r') as f:
                self.box_mappings = json.load(f)
        except FileNotFoundError:
            self.box_mappings = {}

    def add_row(self, is_select, device, total_coin, claim_count, status):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        checkbox = CenterCheckBox()
        checkbox.setChecked(is_select)
        self.table_widget.setCellWidget(row_position, self.col_checkbox, checkbox)

        device_item = QTableWidgetItem(device)
        device_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_device, device_item)

        total_coin_item = QTableWidgetItem(str(total_coin))
        total_coin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_coins, total_coin_item)
        
        claim_count_item = QTableWidgetItem(str(claim_count))
        claim_count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_counts, claim_count_item)

        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_status, status_item)
        
        time_off = QTableWidgetItem(None)
        time_off.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_timestop, time_off)
        
        
        min_coin = QTableWidgetItem(None)
        min_coin.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_min, min_coin)
        
        max_minute = QTableWidgetItem(None)
        max_minute.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_max, max_minute)
        
        error = QTableWidgetItem(str(0))
        error.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_error, error)
        
        fail = QTableWidgetItem(str(0))
        fail.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_fail, fail)
        
        open_app = QTableWidgetItem(str(0))
        open_app.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row_position, self.col_open, open_app)
        
        container_widget = QWidget()
        layout = QHBoxLayout(container_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        button_get_link = QPushButton('Link')
        button_reset_count = QPushButton('Reset')
        button_stop_run = QPushButton('Stop')
        button_close_shopee = QPushButton('Close')
        button_get_link.setStyleSheet("background-color: blue; color: black;")
        button_reset_count.setStyleSheet("background-color: yellow; color: black;")
        button_close_shopee.setStyleSheet("background-color: black; color: white;")
        button_stop_run.setStyleSheet("background-color: red; color: white;")
        button_get_link.clicked.connect(lambda _, device=device: self.get_link_action(device))
        button_reset_count.clicked.connect(lambda _, device=device: self.reset_count_action(device))
        button_stop_run.clicked.connect(lambda _, device=device: self.stop_button_action(device))
        button_close_shopee.clicked.connect(lambda _, device=device: self.close_button_action(device))
        if hasattr(CONFIG, 'key') and CONFIG.key == 'admin':
            layout.addWidget(button_get_link)
        layout.addWidget(button_reset_count)
        layout.addWidget(button_close_shopee)
        layout.addWidget(button_stop_run)
        self.table_widget.setCellWidget(row_position, self.col_action, container_widget)
        
        
        self.set_number_in_box(row_position, device)
    def get_link_action(self, device):
        if device in self.workers:
            worker_info = self.workers[device]
            worker_info["worker"].get_link()
        del device
    def stop_button_action(self,device):
        if device in self.workers:
            worker_info = self.workers[device]
            worker_info["worker"].stop()
        del device
    def close_button_action(self,device):
        if device in self.workers:
            self.close_app(device)
        del device
    def reset_count_action(self,device):
        min_coin = self.min_coin.currentText()
        max_minute = self.max_minute.currentText()
        self.update_status_by_device(device, 0, 0, None, min_coin, max_minute, 0, 0, 'Reset', False)
        del device, min_coin, max_minute
    
    def set_number_in_box(self, row_position, device):
        for mapping in self.box_mappings:
            if mapping["phone"] == device:
                number = mapping["number"]
                item_number = QTableWidgetItem(str(number))
                item_number.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table_widget.setItem(row_position, self.col_device_number, item_number)
                if number <= 20:
                    self.table_widget.item(row_position, self.col_device).setBackground(QColor(183,189,175))
                elif number > 20 and number <= 40: 
                    self.table_widget.item(row_position, self.col_device).setBackground(QColor(153,255,153))
                elif number > 40 and number <= 60: 
                    self.table_widget.item(row_position, self.col_device).setBackground(QColor(204,255,255))
                elif number > 60 and number <= 80: 
                    self.table_widget.item(row_position, self.col_device).setBackground(QColor(240, 187, 168))
                elif number > 80 and number <= 100: 
                    self.table_widget.item(row_position, self.col_device).setBackground(QColor(215, 179, 201))
                elif number > 100 and number <= 120: 
                    self.table_widget.item(row_position, self.col_device).setBackground(QColor(140, 179, 201))
                break
    def get_devices_list(self):
        output = subprocess.run(
            f'{CONFIG.ADB_PATH} devices', shell=True, capture_output=True, text=True).stdout.strip()

        lines = output.split('\n')
        devices = [line.split('\t')[0]
                   for line in lines[1:] if 'device' in line]
        self.total_devices = len(devices)
        return devices

    def update_status_by_device(self, device, phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, not_coin, open_app, status, type_log):
        for row in range(self.table_widget.rowCount()):
            device_item = self.table_widget.item(row, 1)          
            if device_item.text() == device:
                if not type_log:
                    if total_coin is not None:
                        coin = int(total_coin) - int(self.table_widget.item(row, self.col_coins).text())
                        count = int(claim_count) - int(self.table_widget.item(row, self.col_counts).text())
                        self.total_coin += coin
                        self.total_count += count
                        self.table_widget.item(row, self.col_coins).setText(str(total_coin))
                        self.table_widget.item(row, self.col_counts).setText(str(claim_count))
                        self.save_data()
                        self.update_total_coin_label()
                        del coin, count
                    if stop_time is not None:
                        self.table_widget.item(row, self.col_timestop).setText(str(stop_time))
                    else:
                        self.table_widget.setItem(row, self.col_timestop, QTableWidgetItem(None))

                    self.table_widget.item(row, self.col_min).setText(str(min_coin))
                    self.table_widget.item(row, self.col_max).setText(str(max_minute))
                
                if self.limit_app.isdigit() and int(not_coin) >= int(self.limit_app):                
                    self.close_app(device)   

                self.table_widget.item(row, self.col_fail).setText(str(not_coin))
                self.table_widget.item(row, self.col_open).setText(str(open_app))                 
                self.table_widget.item(row, self.col_status).setText(status)
                if 'Scrolling' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(Qt.yellow))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.black))
                elif 'Status:' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(76, 236, 255))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.black))
                elif 'Claim' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(87, 228, 147))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.black))
                elif 'Success' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(Qt.blue))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.white))
                elif 'Stop' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(Qt.black))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.white))
                elif 'Cant' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(Qt.black))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.white))
                elif 'Error' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(Qt.red))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.white))
                elif 'Limit' in status:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(242, 187, 216))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.black))
                else:
                    self.table_widget.item(row, self.col_status).setBackground(QColor(Qt.white))
                    self.table_widget.item(row, self.col_status).setForeground(QColor(Qt.black))
                break
            del device_item       
        del device, phone_number, row, total_coin, claim_count, stop_time, min_coin, status, type_log, max_minute, not_coin, open_app
    def send_data_to_table(self, device, data):
        device_table_updater = DeviceTableUpdater(device, data)
        device_table_updater.signals.device_table_updated.connect(
            self.update_status_by_device)
        if int(data[0]) % 2 == 0:
            self.thread_update1.start(device_table_updater)
        else:
            self.thread_update2.start(device_table_updater)
        del device, data, device_table_updater
    def select_all(self):
        sender = self.sender()
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
            if sender == self.select_all_button:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
    def open_link_devices(self):
        link = self.input_link.text()
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
            if checkbox.isChecked():
                device_item = self.table_widget.item(row, self.col_device)
                device = device_item.text()
                if device in self.workers:
                    worker_info = self.workers[device]
                    worker_info["worker"].open_link(link)
                    del worker_info
                del device_item, device
            del checkbox
        del link, row
    def final_action(self, device, data):
        self.update_table_signal.emit(device, data)
        self.stop_device(device)
    def send_link_to_view(self, link):
        cleaned_link = link.split('copy_link')[0]
        self.input_link.setText(cleaned_link)
        del cleaned_link, link
    def start_action_scroll(self):
        min_coin = self.min_coin.currentText()
        max_minute = self.max_minute.currentText()
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
            if checkbox.isChecked():
                device_item = self.table_widget.item(row, self.col_device)
                total_coin = self.table_widget.item(row, self.col_coins).text()
                claim_count = self.table_widget.item(row, self.col_counts).text()
                stop_time = self.table_widget.item(row, self.col_timestop).text()
                device = device_item.text()
                item = self.table_widget.item(row, self.col_device_number)
                if item is not None:
                    phone_number = item.text()
                else:
                    phone_number = str(random.randint(0, 10))
                if device not in self.workers:
                    worker = WorkerScrollRun(self.update_table_signal, self.send_link_signal, device, phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, 0)
                    worker.update_table_signal.connect(self.send_data_to_table)
                    worker.send_link_signal.connect(self.send_link_to_view)
                    worker.signals.finished.connect(lambda device, data: self.final_action(device, data))
                    worker.signals.error.connect(lambda device, data: self.restart_task_scroll(device, data))
                    self.workers[device] = {"worker": worker}
                    self.send_log(f'Device start: {device}')
                    # Bắt đầu thread mới
                    if int(phone_number) % 2 == 0:
                        self.thread_worker1.start(worker)
                    else:
                        self.thread_worker2.start(worker)
                    del worker
                del device_item, total_coin, claim_count, stop_time, device
            del checkbox
        del min_coin, max_minute    
    def start_action_hunter(self):
        min_coin = self.min_coin.currentText()
        max_minute = self.max_minute.currentText()
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
            if checkbox.isChecked():
                device_item = self.table_widget.item(row, self.col_device)
                total_coin = self.table_widget.item(row, self.col_coins).text()
                claim_count = self.table_widget.item(row, self.col_counts).text()
                stop_time = self.table_widget.item(row, self.col_timestop).text()
                device = device_item.text()
                phone_number = self.table_widget.item(row, self.col_device_number).text()
                if device not in self.workers:
                    worker = WorkerHunterRun(self.update_table_signal, self.send_link_signal, device, phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, 0)
                    worker.update_table_signal.connect(self.send_data_to_table)
                    worker.send_link_signal.connect(self.send_link_to_view)
                    worker.signals.finished.connect(lambda device, data: self.final_action(device, data))
                    worker.signals.error.connect(lambda device, data: self.restart_task_hunter(device, data))
                    self.workers[device] = {"worker": worker}
                    self.send_log(f'Device start: {device}')
                    # Bắt đầu thread mới
                    if int(phone_number) % 2 == 0:
                        self.thread_worker1.start(worker)
                    else:
                        self.thread_worker2.start(worker)
                    del worker
                del device_item, total_coin, claim_count, stop_time, device
            del checkbox
        del min_coin, max_minute
    def stop_device(self, device):
        if device in self.workers:  
            del self.workers[device]
            del device
    def run_subprocess(self, command):
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return ("success", result.stdout)
        except subprocess.CalledProcessError as e:
            return ("error", e.stderr)
    def close_app(self, device):
        worker_close = WorkerClose(device, self.workers, self.APP_PACKAGE)
        self.thread_reset.start(worker_close)
        del device, worker_close
    def bill_action(self):
        deep_link = "https://shopee.vn/digital-product/shop/others"
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
            if checkbox.isChecked():
                device_item = self.table_widget.item(row, self.col_device)
                device_id = device_item.text()
                command = ['adb', '-s', device_id, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', deep_link]
                thread = threading.Thread(target=self.run_subprocess, args=(command,))
                thread.start()
                del device_item, device_id, command, thread
            del checkbox
        del deep_link
    
    def stop_action(self):
        self.devices_to_stop = []

        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
            if checkbox.isChecked():
                device_item = self.table_widget.item(row, self.col_device)
                self.devices_to_stop.append(device_item.text())

        for device in self.devices_to_stop:
            if device in self.workers:
                worker_info = self.workers[device]
                worker_info["worker"].stop()

                
    def update_devies(self):
        min_coin = self.min_coin.currentText()
        max_minute = self.max_minute.currentText()
        if self.checkbox_time.isChecked(): 
            current_time = datetime.now()
            # Thêm 2 tiếng vào thời gian hiện tại
            selected_hours = int(self.comboBox_hours.currentText())
            selected_minutes = int(self.comboBox_minutes.currentText())
            new_time = current_time + timedelta(hours=selected_hours) + timedelta(minutes=selected_minutes)   
            formatted_time = new_time.strftime('%Y-%m-%d %H:%M:%S')     
            for row in range(self.table_widget.rowCount()):
                checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
                if checkbox.isChecked():
                    device = self.table_widget.item(row, self.col_device).text()
                    if device in self.workers:
                        worker_info = self.workers[device]
                        worker_info["worker"].update_device(True,str(formatted_time), min_coin, max_minute)
                    else: 
                        self.table_widget.item(row, self.col_timestop).setText(str(formatted_time))
                    del device
                del checkbox
            del current_time, selected_hours, selected_minutes, new_time, formatted_time, row
        else:
            for row in range(self.table_widget.rowCount()):
                checkbox = self.table_widget.cellWidget(row, self.col_checkbox)
                if checkbox.isChecked():
                    device = self.table_widget.item(row, self.col_device).text()
                    if device in self.workers:
                        worker_info = self.workers[device]
                        worker_info["worker"].update_device(False,None, min_coin, max_minute)  
                    else: 
                        self.table_widget.setItem(row, self.col_timestop, QTableWidgetItem(None))
                    del device
                del checkbox
        del min_coin, max_minute
                    
    def restart_task_scroll(self, device, data):
        #print(device)
        if device in self.workers and not self.workers[device]["worker"].is_stop:
            print('Restarting thread for device:', device)
            subprocess.run(['adb', '-s', device, 'shell', 'am', 'force-stop', CONFIG.APP_PACKAGE], check=False)
            for row in range(self.table_widget.rowCount()):
                device_item = self.table_widget.item(row, self.col_device)          
                if device_item.text() == device:
                    error = int(self.table_widget.item(row, self.col_error).text()) + 1
                    self.table_widget.item(row, self.col_error).setText(str(error))  
            worker_info = self.workers[device]

            # Xóa worker và thread hiện tại
            del worker_info["worker"]

            phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, open_app, error = data
            self.send_log(f'Device serial: {device}, Error: {error}')
            # Tạo worker mới
            worker = WorkerScrollRun(self.update_table_signal, self.send_link_signal, device, phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, open_app)
            worker.send_link_signal.connect(self.send_link_to_view)
            worker.update_table_signal.connect(self.send_data_to_table)
            worker.signals.finished.connect(lambda device, data: self.final_action(device, data))
            worker.signals.error.connect(lambda device, data: self.restart_task_scroll(device, data))

            # Lưu trữ thông tin về worker và thread mới
            self.workers[device] = {"worker": worker}
            # Bắt đầu thread mới
            if int(phone_number) % 2 == 0:
                self.thread_worker1.start(worker)
            else:
                self.thread_worker2.start(worker)      
            del total_coin, claim_count, phone_number, stop_time, min_coin, open_app, error, device, data, row, max_minute
    def restart_task_hunter(self, device, data):
        #print(device)
        if device in self.workers and not self.workers[device]["worker"].is_stop:
            print('Restarting thread for device:', device)
            subprocess.run(['adb', '-s', device, 'shell', 'am', 'force-stop', CONFIG.APP_PACKAGE], check=False)
            for row in range(self.table_widget.rowCount()):
                device_item = self.table_widget.item(row, self.col_device)          
                if device_item.text() == device:
                    error = int(self.table_widget.item(row, self.col_error).text()) + 1
                    self.table_widget.item(row, self.col_error).setText(str(error))  
            worker_info = self.workers[device]

            # Xóa worker và thread hiện tại
            del worker_info["worker"]

            phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, open_app, error = data
            self.send_log(f'Device serial: {device}, Error: {error}')
            # Tạo worker mới
            worker = WorkerScrollRun(self.update_table_signal, self.send_link_signal, device, phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, open_app)
            worker.send_link_signal.connect(self.send_link_to_view)
            worker.update_table_signal.connect(self.send_data_to_table)
            worker.signals.finished.connect(lambda device, data: self.final_action(device, data))
            worker.signals.error.connect(lambda device, data: self.restart_task_hunter(device, data))

            # Lưu trữ thông tin về worker và thread mới
            self.workers[device] = {"worker": worker}

            # Bắt đầu thread mới
            if int(phone_number) % 2 == 0:
                self.thread_worker1.start(worker)
            else:
                self.thread_worker2.start(worker) 
            del total_coin, claim_count, phone_number, stop_time, min_coin, open_app, error, device, data, row, max_minute
    def send_log(self, msg):
        # Gửi lệnh đến LogWindow thông qua tín hiệu
        self.send_log_signal.emit(msg)
        
    def save_data(self):
        data = []
        for row in range(self.table_widget.rowCount()):
            device = self.table_widget.item(row, self.col_device).text()
            total_coin = self.table_widget.item(row, self.col_coins).text()
            claim_count = self.table_widget.item(row, self.col_counts).text()
            data.append({
                "device": device,
                "total_coin": total_coin,
                "claim_count": claim_count,
            })
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        del data
           
    def update_row(self, entry):
        # Kiểm tra xem thiết bị đã tồn tại trong bảng hay chưa
        for row in range(self.table_widget.rowCount()):
            device_item = self.table_widget.item(row, self.col_device)
            if device_item.text() == entry['device']:
                # Nếu đã tồn tại, cập nhật dữ liệu của hàng
                self.total_coin += int(entry['total_coin'])
                self.total_count += int(entry['claim_count'])
                self.table_widget.item(row, self.col_coins).setText(str(entry['total_coin']))
                self.table_widget.item(row, self.col_counts).setText(str(entry['claim_count']))
                return
            del device_item

    def update_total_coin_label(self):
        #print(self.count_lowest)
        
        if self.total_devices == 0 :
            self.label_total_coin.setText('Total: {} coins       Progress: {:.2f}%'.format(0, 0))
        else:
            formatted_coin = f'{self.total_coin:,}'.replace(',', '.')
            process = (self.total_count / (self.total_devices * 200)) * 100
            self.label_total_coin.setText('Total: {} coins       Progress: {:.2f}%'.format(formatted_coin, process))
        
            del formatted_coin, process
        
    def load_data(self):
        device_dict = {}  # Tạo một từ điển để lưu trữ dữ liệu từ tệp JSON
        try:
            with open(JSON_FILE_PATH, 'r') as f:
                data = json.load(f)
                for entry in data:
                    device_dict[entry['device']] = entry  # Thêm dữ liệu từ tệp JSON vào từ điển
                    self.update_row(entry)  # Cập nhật dữ liệu trong bảng
            self.update_total_coin_label()
            del device_dict
        except FileNotFoundError:
            # If the file is not found, create a new empty file
            with open(JSON_FILE_PATH, 'w') as f:
                json.dump([], f)
        
class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_widget = QTextEdit()
        self.setCentralWidget(self.log_widget)
        self.setWindowTitle("Log Window")

    def append_log(self, text):
        self.log_widget.append(text)               
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.setGeometry(100, 100, 980, 600)
    
    
    window.show()

    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    window.send_log(f'Start at: {formatted_time}')
    sys.exit(app.exec_())