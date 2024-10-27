import time
import sys
import subprocess
import traceback

#sys.path.append('/service/shopee')
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
#from service.shopee.shopee_version_1 import ShopeeVersion1
from service.shopee_scroll.scroll_v2 import Shopee
class WorkerSignals(QObject):
    finished = pyqtSignal(str, list)
    error = pyqtSignal(str, list)
class WorkerScrollRun(QRunnable):
    def __init__(self, update_table_signal, send_link_signal, phone_serial, phone_number, total_coin, claim_count, stop_time, min_coin, max_minute, open_app):
        super().__init__()
        self.phone_serial = phone_serial
        self.update_table_signal = update_table_signal
        self.send_link_signal = send_link_signal
        self.shopee = Shopee(self.phone_serial, phone_number, self.update_table_signal, self.send_link_signal, total_coin, claim_count, stop_time, min_coin, max_minute, open_app)
        self.is_stop = False
        self.signals = WorkerSignals()
    def stop(self):
        self.is_stop = True
        self.shopee.update_stop_status(True, 'Main')  
    def update_device(self, stop, time, min_coin, max_minute):
        self.shopee.update_device(stop, time, min_coin, max_minute)
    def open_link(self, link):
        self.shopee.set_link(link)
    def get_link(self):
        self.shopee.get_link()
    def run(self): 
        try:
            self.shopee.claim_coin()
            #print(f'{self.phone_serial} done')
            self.signals.finished.emit(self.phone_serial, [self.shopee.phone_number, self.shopee.total_coin_claimed, self.shopee.claim_counts, self.shopee.stop_time, self.shopee.min_coin, self.shopee.max_minute, self.shopee.not_coin, self.shopee.open_app, 'Stopped', False])
        except Exception as e:
            # Get the current time
            current_time = time.localtime()

            # Format the current time as a string
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            error_details = traceback.format_exc()
            print(f'{formatted_time} --- {self.phone_serial} error: {error_details}')
            self.update_table_signal.emit(self.phone_serial, [self.shopee.phone_number, self.shopee.total_coin_claimed, self.shopee.claim_counts, self.shopee.stop_time, self.shopee.min_coin, self.shopee.max_minute, self.shopee.not_coin, self.shopee.open_app, 'Error, waiting 10s to retry...', False])
            time.sleep(2)
            self.signals.error.emit(self.phone_serial, [self.shopee.phone_number, self.shopee.total_coin_claimed, self.shopee.claim_counts, self.shopee.stop_time, self.shopee.min_coin, self.shopee.max_minute, self.shopee.open_app, e])
        
