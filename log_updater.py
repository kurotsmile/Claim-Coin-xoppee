from PyQt5.QtCore import QThread, pyqtSignal, QRunnable, QObject

class LogUpdater(QThread):
    log_updated = pyqtSignal(str)

    def __init__(self, messages, parent=None):
        super().__init__(parent)
        self.messages = messages

    def run(self):
        self.log_updated.emit(self.messages)


class DeviceTableUpdaterSignals(QObject):
    device_table_updated = pyqtSignal(str, object, object, object, object, object, object, object, object, object, object)

class DeviceTableUpdater(QRunnable):
    def __init__(self, device, data):
        super().__init__()
        self.device = device
        self.data = data
        self.signals = DeviceTableUpdaterSignals()
        del device, data
    def run(self):
        self.signals.device_table_updated.emit(self.device, self.data[0], self.data[1], self.data[2], self.data[3], self.data[4], self.data[5], self.data[6], self.data[7], self.data[8], self.data[9])