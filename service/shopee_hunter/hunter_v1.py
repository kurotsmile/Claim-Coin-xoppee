import re
import time
#import ctypes
import random
#import base64
#import logging
#import threading
import uiautomator2 as u2
import subprocess
from xpaths import XPATHS
from config import CONFIG
from datetime import datetime
import traceback
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


class Shopee:
    def __init__(self, device_serial: str, phone_number, update_signal, send_signal, total_coin, claim_count, stop_time, min_coin, max_minute, open_app) -> None:
        self.device_serial = device_serial
        self.update_signal = update_signal
        self.send_signal = send_signal
        self.phone_number = phone_number
        self.d = None
        self.total_coin_claimed = int(total_coin)
        self.is_stop = False
        self.first_start = False
        self.claim_counts = int(claim_count)
        self.limit = 0
        self.close = True
        self.stop_time = stop_time
        self.not_coin = 0
        self.width = 0
        self.height = 0
        self.open_app = int(open_app)
        self.min_coin = int(min_coin)
        self.max_minute = int(max_minute)
        self.shop_name = ''
        self.do_get_link_shop = False
        self.go_to_link = None
        self.random_sleep = random.uniform(8, 15)
        self.WAIT_COIN_TIME = CONFIG.WAIT_COIN_TIME
        self.APP_PACKAGE = CONFIG.APP_PACKAGE
        self.CLAIM_TIMES = CONFIG.CLAIM_TIMES
        self.POPUP_AD = XPATHS.POPUP_AD
        self.COIN_NUM = XPATHS.COIN_NUM
        self.COIN_STATE = XPATHS.COIN_STATE
        self.CLAIM_REMAINING = XPATHS.CLAIM_REMAINING
        self.MORE_BTN = XPATHS.MORE_BTN
        self.CLAIM_POPUP_CLOSE = XPATHS.CLAIM_POPUP_CLOSE
        self.POPUP_BANNER = XPATHS.POPUP_BANNER
        self.LIVE_STREAM_TAB = XPATHS.LIVE_STREAM_TAB
        self.POPUP_CLOSE = XPATHS.POPUP_CLOSE
        self.CON_BUT = XPATHS.CON_BUT
        self.APP_MENU = XPATHS.APP_MENU
        self.SHOP_NAME = XPATHS.SHOP_NAME
        self.TRY_AGAIN = XPATHS.TRY_AGAIN
    def set_link(self, link):
        self.go_to_link = link
    def open_link(self):
        self.d.shell(f'am start -a android.intent.action.VIEW -d {self.go_to_link} -n {self.APP_PACKAGE}/com.shopee.app.ui.proxy.ProxyActivity') 
    def update_device(self, stop, time, min_coin, max_minute):
        if stop:
            self.stop_time = time
        else:
            self.stop_time = None
        self.min_coin = int(min_coin)
        self.max_minute = int(max_minute)
        self.update_status("Update")
        del stop, time, min_coin, max_minute
    def update_stop_status(self, is_stop, reason):
        print(f'{self.device_serial} - {self.phone_number} stop by: {reason}')
        self.is_stop = is_stop  
        del is_stop, reason
    def send_link(self, link):
        self.send_signal.emit(link)
    def update_status(self, status: str):
        if self.update_signal != None:
            self.update_signal.emit(self.device_serial, [self.phone_number, self.total_coin_claimed, self.claim_counts, self.stop_time, self.min_coin, self.max_minute, self.not_coin, self.open_app, status, False])
        # write to log file
        #current_time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        del status
    def send_log(self, log_message: str):
        if self.update_signal != None:
            self.update_signal.emit(self.device_serial, [self.phone_number, None, None, None, None, None, self.not_coin, self.open_app, log_message, True])
        del log_message
    def click_exist(self, xpath: str, time_click: int = 10, adding_xpath: str = None):
        #self.send_log(f'Finding {xpath}')
        if adding_xpath:
            if self.d.xpath(adding_xpath).wait(0.5):
                self.d.xpath(adding_xpath).click_exists(1)

        self.d.xpath(xpath).click_exists(timeout=time_click)

    def clickText(self, identifier='', desc='', count=5, index=0, x=0, y=0, click=True):
        try:
            for t in range(count):
                try:
                    #print(f'Finding {identifier}')
                    if identifier.startswith("text="):
                        element = self.d(
                            text=identifier.replace("text=", ""))[index]
                    elif identifier.startswith("resourceId="):
                        element = self.d(resourceId=identifier.replace(
                            "resourceId=", ""))[index]
                    elif identifier.startswith("className="):
                        element = self.d(className=identifier.replace(
                            "className=", ""), description=desc)[index]
                    else:
                        raise ValueError("Loại identifier không được hỗ trợ")

                    if element.exists:
                        x1, y1 = element.info['bounds']['left'], element.info['bounds']['top']
                        if click:
                            self.d.click(x1+x, y1+y)
                        del x1, y1, element  
                        return True
                except Exception as e:
                    self.send_log(f'Error: {e}')
                time.sleep(1)
            return False
        except Exception as e:
            return False

    # def sendText(self, text):
        # try:
            # """Nhập văn bản ADB"""
            # self.d.shell('ime set com.android.adbkeyboard/.AdbIME')
            # text = str(base64.b64encode(text.encode('utf-8')))[1:]
            # self.d.shell(f'am broadcast -a ADB_INPUT_B64 --es msg {text}')

        # except Exception as e:
            # return False

    # def find_and_set_text(self, xpath: str, text: str, time_click: int = 10):
        # self.send_log(f'Finding {xpath}')
        # time.sleep(0.5)
        # if self.d.xpath(xpath).wait(time_click):
            # self.d.xpath(xpath).set_text(text)


    #def scroll_down(self, min: int = 1, max: int = 1):
    def scroll_down(self):    
        #for _ in range(random.randint(min, max)):
        self.d.swipe(self.width - self.width // 7, self.height - self.height // 5, self.width - self.width // 7, self.height // 9, 0.15)
        
    def start_app(self, msg):       
        
        self.send_log('Starting app pee')
        print(f'{self.device_serial} - {self.phone_number}: open app by {msg}')
        time.sleep(1)
        self.d.app_start(self.APP_PACKAGE, stop=True, use_monkey=True)
        time.sleep(1)
        
        element = d(resourceId='com.shopee.vn:id/icon', description='tab_bar_button_live_streaming')
        if element.exists:
            element.click()  # Click vào phần tử
            print("Clicked on the element successfully!")

        if self.d.xpath(self.LIVE_STREAM_TAB).wait(3):
            self.click_exist(self.LIVE_STREAM_TAB)
            print("Tim thay nut live")
        else:
            print("Kho co nut live tream")


        self.d.freeze_rotation()
        time.sleep(1)
        if self.d.xpath(self.POPUP_BANNER + '|' + self.LIVE_STREAM_TAB).wait(6):
            if self.d.xpath(self.POPUP_BANNER).wait(1):
                self.click_exist(self.POPUP_CLOSE)

        if self.d.xpath(self.TITLE_TEXT).wait(5):
            check = self.get_text_xpath(self.TITLE_TEXT)
            if check == 'Xác nhận':
                self.close = False
                self.update_stop_status(True, 'Captcha')
                self.send_log('Captcha')
                return False
        if not self.d.xpath(self.LIVE_STREAM_TAB).wait(10):
            self.send_log('App not started')
            self.update_stop_status(True, 'captcha - login')
            return False
            
        self.click_exist(self.LIVE_STREAM_TAB)
        time.sleep(0.5)
        self.click_exist(self.LIVE_STREAM_TAB)
        if not self.d.xpath(self.MORE_BTN).wait(15):
            check_live = self.d.xpath(self.MORE_BTN).exists
            try_times = 0
            while check_live:
                time.sleep(10)
                self.click_exist(self.LIVE_STREAM_TAB)
                check_live = self.d.xpath(self.MORE_BTN).exists
                try_times += 1
                if try_times > 5:
                    subprocess.run(['adb', '-s', self.device_serial, 'shell', 'am', 'force-stop', self.APP_PACKAGE], check=True)
                    break
            del check_live, try_times
        else :
            self.send_log('Processing claim')
            self.open_app +=1
            #self.d.shell('settings put system accelerometer_rotation 0')

    
    # def _test(self):
        # while True:
            # self.send_log('Test')
            # self.total_coin_claimed += 1
            # time.sleep(5)
    def check_stop_time(self):
        if self.stop_time is not None and self.stop_time != "":
            stop_time = datetime.strptime(self.stop_time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            if current_time > stop_time:
                self.update_stop_status(True, 'stop time')

    def get_text_xpath(self, xpath):
        try:
            return self.d.xpath(xpath).get_text()
        except Exception as e:
            return None 

    def check_network_connection(self):
        #self.d.click(487, 3)
        #time.sleep(7)
        self.d.shell('svc wifi disable')
        time.sleep(5)
        self.d.shell('svc wifi enable')
        time.sleep(20)
        # Kiểm tra có biểu tượng sóng trên thanh trạng thái không
        network_icon = self.d(resourceId="com.android.systemui:id/wifi_combo").exists
        if self.d.app_current()['package'] != self.APP_PACKAGE:
            self.start_app('Disconnect App 1')
        if network_icon:
            pass
        else:
            print(f'{self.device_serial} - {self.phone_number} offline')
            if network_icon:
                self.d.shell('svc wifi disable')
                time.sleep(5)
                self.d.shell('svc wifi enable')
                time.sleep(20)
                self.click_exist(self.TRY_AGAIN,1)
                self.click_exist(self.CON_BUT,1)
        del network_icon
        time.sleep(5)
        check_try_again = self.d.xpath(self.CON_BUT).exists or self.d.xpath(self.TRY_AGAIN).exists
        while check_try_again:
            self.click_exist(self.CON_BUT,5)
            self.click_exist(self.TRY_AGAIN,5)
            time.sleep(2)
            check_try_again = self.d.xpath(self.CON_BUT).exists or self.d.xpath(self.TRY_AGAIN).exists
        del check_try_again
        time.sleep(2)
        self.scroll_down()
        if not self.d.xpath(self.MORE_BTN).wait(20):
            self.start_app('Disconnect App 2')
    def close_app(self):
        #subprocess.run(['adb', '-s', self.device_serial, 'shell', 'am', 'force-stop', self.APP_PACKAGE], check=False)
        self.not_coin = 0
        #return True
    def get_link(self):
        self.do_get_link_shop = True
    def action_get_link(self):
        self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/iv_share"]').click()
        time.sleep(2)
        self.d.xpath('//*[@resource-id="com.shopee.vn:id/bottom_sheet_gridview"]/android.widget.LinearLayout[10]/android.widget.ImageView[1]').click()
        self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/iv_share"]').click()
        time.sleep(2)
        self.d.xpath('//*[@resource-id="com.shopee.vn:id/bottom_sheet_gridview"]/android.widget.LinearLayout[10]/android.widget.ImageView[1]').click()
        self.send_link(self.d.clipboard)
        self.do_get_link_shop = False

    def claim_coin(self):
        #print(self.total_coin_claimed)
        self.d = u2.connect(self.device_serial)
        self.d.freeze_rotation()
        time.sleep(4)
        self.d.shell('dumpsys battery set level 100')
        self.not_coin = 0
        screen_size = self.d.window_size()
        self.width, self.height = screen_size[0], screen_size[1]
        self.update_status('Running')
        time.sleep(self.random_sleep)
        #count_times = 0
        del screen_size
        if self.is_stop:
            if self.close == True:
                subprocess.run(['adb', '-s', self.device_serial, 'shell', 'am', 'force-stop', self.APP_PACKAGE], check=True)
            return True
        if not self.d.xpath(self.MORE_BTN).wait(20):
            self.start_app('Start')
        coin_value = None
        coin_status = None
        current_status = None
        time_get_coin = None
        pending_coin = None
        while not self.is_stop:

            coin_value = None
            coin_status = None
            current_status = None
            time_get_coin = None
 
            
            coin_value = self.get_text_xpath(self.COIN_NUM)
            #print('Coin Value')
             
            
            while not self.is_stop:

                if self.do_get_link_shop:
                    self.action_get_link()
                    self.action_get_link()
                    time.sleep(1)
                self.click_exist(self.POPUP_AD,1)
                if self.go_to_link is not None:
                    self.open_link()
                    time.sleep(45)
                    self.go_to_link = None
                if not self.d.xpath(self.MORE_BTN).wait(20):
                    self.check_network_connection()
                    #self.start_app('Step 2 MORE_BTN')
                    #break
                if self.do_get_link_shop:
                    self.action_get_link()
                    time.sleep(1)
                current_status = self.get_text_xpath(self.COIN_STATE)
                #print('Status')
                if current_status == None or current_status == '' or current_status == 'Kết thúc' or current_status == 'Giới hạn' or current_status == 'Đăng nhập':
                    time.sleep(1)
                    break
                if current_status == 'Thử lại':
                    self.d.xpath(self.COIN_NUM).click_exists(1)
                if int(coin_value) < int(self.min_coin):
                    time.sleep(1)
                    break  

                self.send_log(f'Claim: {coin_value} ({current_status})')
                #print('Kiểm tra chữ Lưu')
                if self.get_text_xpath(self.COIN_STATE) == 'Lưu':
                    self.click_exist(self.POPUP_AD,2)
                    self.d.xpath(self.COIN_NUM).click_exists(1)
                    
                    if not self.d.xpath(self.CLAIM_REMAINING).wait(20):        
                        continue
                    
                    time.sleep(self.WAIT_COIN_TIME)
                    self.click_exist(self.CLAIM_POPUP_CLOSE,5)
                    self.clickText('resourceId=com.shopee.vn.dfpluginshopee7:id/tv_claim_count', x=200, y=150, click=True, count=2)
                    self.claim_counts += 1
                    self.click_exist(self.CLAIM_POPUP_CLOSE,5)
                    # update to title here with coin_value
                    self.total_coin_claimed += int(coin_value)
                    self.update_status(f'Success {coin_value}')



                    time.sleep(5)

                    

                time.sleep(7)
            
            time.sleep(3)

            
        #print(f'Check {self.device_serial} - {self.phone_number}: {self.is_stop}') 
        #self.d.press("home")
        if self.close == True:
            subprocess.run(['adb', '-s', self.device_serial, 'shell', 'am', 'force-stop', self.APP_PACKAGE], check=True)
        return True
    
# if __name__ == '__main__':
    # shopee = Shopee('42004ff0d630a4d9', None, None)
    # shopee.claim_coin()
