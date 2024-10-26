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
#import traceback
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
        self.random_sleep = random.uniform(1, 2)
        self.APP_PACKAGE = CONFIG.APP_PACKAGE
        self.CLAIM_TIMES = CONFIG.CLAIM_TIMES
        self.POPUP_AD = XPATHS.POPUP_AD
        self.COIN_NUM = '//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/tv_coin_num"]'
        self.COIN_STATE = '//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/tv_status"]'
        self.CLAIM_REMAINING = XPATHS.CLAIM_REMAINING
        self.MORE_BTN = XPATHS.MORE_BTN 
        self.CLAIM_POPUP_CLOSE = XPATHS.CLAIM_POPUP_CLOSE
        self.POPUP_BANNER = XPATHS.POPUP_BANNER
        self.LIVE_STREAM_TAB = '//*[@resource-id="com.shopee.vn:id/sp_bottom_tab_layout"]/android.widget.FrameLayout[3]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.ImageView[2]'
        self.FIRST_STREAM = '//android.widget.ScrollView/android.view.ViewGroup[1]/android.view.ViewGroup[4]/android.view.ViewGroup[1]/android.view.ViewGroup[1]'
        self.POPUP_CLOSE = XPATHS.POPUP_CLOSE
        self.CLAIM_COUNT_DOWN = XPATHS.CLAIM_COUNT_DOWN
        self.CON_BUT = XPATHS.CON_BUT
        self.CLAIM_BTN = '//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/tv_claim"]'
        self.SHOP_NAME = '//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/ll_name"]'
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
        
        self.send_log('Starting app')
        print(f'{self.device_serial} - {self.phone_number}: open app by scroll v2 {msg}')
        self.d.app_start(self.APP_PACKAGE, stop=True, use_monkey=True)
        time.sleep(1)
        self.d.freeze_rotation()
        time.sleep(5)
        element = self.d(resourceId='com.shopee.vn:id/icon', description='tab_bar_button_live_streaming')
        if element.exists:
            element.click()
            print("Clicked on the element successfully!")
        else:
            if self.d.xpath(self.POPUP_BANNER + '|' + self.LIVE_STREAM_TAB).wait(25):
                if self.d.xpath(self.POPUP_BANNER).wait(1):
                    self.click_exist(self.POPUP_CLOSE)
            if self.d.xpath('//*[@resource-id="com.shopee.vn:id/title_text"]').wait(5):
                check = self.get_text_xpath('//*[@resource-id="com.shopee.vn:id/title_text"]')
                if check == 'Xác nhận':
                    self.close = False
                    self.update_stop_status(True, 'Captcha')
                    self.send_log('Captcha')
                    return False
            if not self.d.xpath(self.LIVE_STREAM_TAB).wait(25):
                self.send_log('App not started')
                self.update_stop_status(True, 'captcha - login')
                return False
            
        self.click_exist(self.LIVE_STREAM_TAB)
        if self.d.xpath(self.FIRST_STREAM).wait(5):
            self.click_exist(self.FIRST_STREAM)
        #time.sleep(0.5)
        #self.click_exist(self.LIVE_STREAM_TAB)
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
        if not self.d.xpath(xpath).wait(2):
            return None
        try:
            return self.d.xpath(xpath).get_text()
        except Exception as e:
            return None 

    def check_network_connection(self):
        if self.d.xpath('//*[@resource-id="com.shopee.vn:id/home_btn"]').wait(1):
            self.d.click(0.129, 0.774)
            return True
        if self.d.xpath('//*[@resource-id="com.shopee.vn:id/title_text"]').wait(5):
            check = self.get_text_xpath('//*[@resource-id="com.shopee.vn:id/title_text"]')
            if check == 'Xác nhận':
                self.close = False
                self.update_stop_status(True, 'Captcha')
                self.send_log('Captcha')
                return False
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
        time_get_coin = None
        pending_coin = None
        min_get_coin = None
        while not self.is_stop:

            coin_value = None
            coin_status = None
            time_get_coin = None
            min_get_coin = None
            pending_coin = 0

            #print('step 1')
            self.send_log('Scrolling down')
            if not self.d.xpath(self.MORE_BTN).wait(20):
                self.check_network_connection()
  
                
            
            self.click_exist(self.POPUP_AD,1)
            self.check_stop_time()
            
            #print('step 2')
            if not self.first_start:
                self.first_start = True
            else:
                self.scroll_down()
                self.not_coin += 1

            if self.go_to_link is not None:
                self.open_link()
                time.sleep(45)
                self.go_to_link = None
            time.sleep(1)    
            
            #print('step 3')
            if self.shop_name == '':
                self.shop_name  = self.get_text_xpath(self.SHOP_NAME)
            else:
                if self.shop_name  == self.get_text_xpath(self.SHOP_NAME):
                    self.send_log('Cant scroll')
                    print(f'{self.device_serial} - {self.phone_number} same shop name')
                    time.sleep(3)
                    continue
                
            #print('step 4')
            
            #chờ xem có box_view_coin
            if not self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/box_view_coin"]').wait(10):
                #nếu không có box_view_coin là không có xu 
                self.send_log(f'Status: (Live không xu)')
                time.sleep(self.random_sleep)
                continue   
            else:# nếu có box_view_coin thì xem tv_coin_num có xu không
                #nếu không có xu thì kiểm tra giới hạn hoặc live đã hết xu
                if not self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/tv_coin_num"]').wait(5):
                    coin_status = self.get_text_xpath(self.COIN_STATE)
                    if coin_status == 'Đã đạt giới hạn\nlấy của phiên này':
                        if(self.limit <= 10 ):
                            self.send_log(f'Limit times: {self.limit}')
                            self.limit += 1
                        else:
                            self.update_stop_status(True, 'Limit count Setp1')
                        time.sleep(self.random_sleep)
                        continue
                    self.send_log(f'Status: (Live hết xu)')
                    time.sleep(self.random_sleep)
                    continue
                #nếu có xu thì kiểm tra số xu và có nút nhận hay không
                else:
                    coin_value = self.get_text_xpath(self.COIN_NUM)
                    if coin_value is not None and int(coin_value) < int(self.min_coin):
                        time.sleep(self.random_sleep)
                        continue  
                    if not self.d.xpath(self.CLAIM_BTN).wait(0.5):
                        time.sleep(5)
                        time_get_coin = self.get_text_xpath(self.CLAIM_COUNT_DOWN)
                        if time_get_coin == None:
                            continue
                        else:
                            time_get_coin = time_get_coin[-5:]
                            min_get_coin = time_get_coin[:2]
                            #print(min_get_coin)
                        if min_get_coin.isdigit() and int(min_get_coin) > int(self.max_minute):
                            time.sleep(self.random_sleep)
                            continue
            #print('step 5')
            while not self.is_stop:

                #print('step 6')
                self.click_exist(self.POPUP_AD,1)
                if self.go_to_link is not None:
                    self.open_link()
                    time.sleep(45)
                    self.go_to_link = None
                    
                if not self.d.xpath(self.MORE_BTN).wait(20):
                    self.check_network_connection()

                if self.do_get_link_shop:
                    self.action_get_link()
                    time.sleep(1)
                
                #print('step 7')
                #nếu không có xu thì kiểm tra giới hạn hoặc live đã hết xu
                if not self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/tv_coin_num"]').wait(5):
                    self.send_log(f'Status: (Live hết xu)')
                    time.sleep(self.random_sleep)
                    break
                #nếu có xu thì kiểm tra số xu và có nút nhận hay không
                else:
                    #coin_value = self.get_text_xpath(self.COIN_NUM)
                    #if coin_value is not None and int(coin_value) < int(self.min_coin):
                        #time.sleep(self.random_sleep)
                        #break  
                    if not self.d.xpath(self.CLAIM_BTN).wait(0.5):
                        time_get_coin = self.get_text_xpath(self.CLAIM_COUNT_DOWN)
                        if time_get_coin == None:
                            break
                        else:
                            time_get_coin = time_get_coin[-5:]
                            min_get_coin = time_get_coin[:2]
                        if min_get_coin.isdigit() and int(min_get_coin) > int(self.max_minute):
                            time.sleep(self.random_sleep)
                            break
                    
                #print('step 8')
                self.send_log(f'Claim: {coin_value} ({time_get_coin})')
                if pending_coin > 3:
                    pending_coin = 0
                    time.sleep(1)
                    break
                
                #print('step 9')
                if self.d.xpath(self.CLAIM_BTN).wait(1):
                    #print('step 10')
                    pending_coin +=1
                    self.click_exist(self.POPUP_AD,2)
                    self.d.xpath(self.CLAIM_BTN).click_exists(1)
                    
                    if not self.d.xpath(self.CLAIM_REMAINING).wait(20):        
                        continue
                    #print('step 11')
                    time.sleep(5)
                    if self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/img_bg"]').wait(5):
                        self.d.click(0.496, 0.646)
                    #print('step 12')   
                    self.claim_counts += 1
                    self.not_coin = 0

                    # update to title here with coin_value
                    self.total_coin_claimed += int(coin_value)
                    self.update_status(f'Success {coin_value}')
                    pending_coin = 0
                    
                    #print('step 13')
                    if(self.limit > 0 ):
                        self.limit = 0
                    #subprocess.run("cls", shell=True)
                    if self.claim_counts >= self.CLAIM_TIMES:
                        self.update_stop_status(True, 'claim count Setp1')
                        break

                    time.sleep(5)
                    

                    if not self.d.xpath('//*[@resource-id="com.shopee.vn.dfpluginshopee7:id/tv_coin_num"]').wait(5):
                        time.sleep(1)
                        break
                    coin_value = self.get_text_xpath(self.COIN_NUM)
                    if coin_value is not None and int(coin_value) < int(self.min_coin):
                        time.sleep(1)
                        break  
                    

                time.sleep(5)
            
            if int(self.claim_counts) >= int(self.CLAIM_TIMES):
                self.update_stop_status(True, 'claim count Setp2')
                break
            time.sleep(3)

            
        if self.close == True:
            subprocess.run(['adb', '-s', self.device_serial, 'shell', 'am', 'force-stop', self.APP_PACKAGE], check=True)
        return True
    
# if __name__ == '__main__':
    # shopee = Shopee('42004ff0d630a4d9', None, None)
    # shopee.claim_coin()
