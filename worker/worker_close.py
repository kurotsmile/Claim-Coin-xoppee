import time
import sys
import subprocess

from PyQt5.QtCore import QRunnable




class WorkerClose(QRunnable):
    def __init__(self, device, workers, app_package):
        super().__init__()
        self.device = device
        self.workers = workers
        self.app_package = app_package

    def run(self):
        worker_info = self.workers[self.device]
        worker_info["worker"].shopee.close_app()
        command = ['adb', '-s', self.device, 'shell', 'am', 'force-stop', self.app_package]
        self.run_subprocess(command)
        del worker_info, command

    def run_subprocess(self, command):
        try:
            result = subprocess.run(command, check=False)
            del result
        except subprocess.CalledProcessError as e:
            print(e.stderr) 
        
