from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from email import parser
from email.policy import default
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import poplib
import time
# Thông tin đăng nhập email của bạn
pop3_server = 'pop-mail.outlook.com'

chrome_options = Options()
chrome_options.add_argument("--disable-webrtc")  # Tắt WebRTC
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
# Đọc dữ liệu từ file mail.txt
file_path = 'mail.txt'  # Thay đổi đường dẫn nếu cần thiết
with open(file_path, 'r') as file:
    lines = file.readlines()
class OpenMail:
	def __init__(self):
		self.tab_handles = 0

	# Hàm đệ quy để lấy nội dung email
	def get_email_content(self, msg):
		if msg.is_multipart():
			for part in msg.get_payload():
				self.get_email_content(part)
		else:
			content_type = msg.get_content_type()
			if content_type == "text/plain":
				print("Nội dung văn bản:")
				print(msg.get_payload(decode=True).decode('utf-8', errors='ignore'))
			elif content_type == "text/html":
				print("Nội dung HTML:")
				html_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
				# Phân tích cú pháp HTML và trích xuất phần body
				soup = BeautifulSoup(html_content, 'html.parser')
				# Phân tích cú pháp HTML và trích xuất phần cần thiết
				soup = BeautifulSoup(html_content, 'html.parser')
				# Tìm div có chứa văn bản cụ thể
				a_tag = soup.find('a', string=lambda string:string and "TẠI ĐÂY" in string)

				if a_tag:
					#href = 'https://stackoverflow.com/questions/46744968/how-to-suppress-console-error-warning-info-messages-when-executing-selenium-pyth'
					href = a_tag['href']
					# Mở liên kết trong trình duyệt mặc định
					self.open_link_in_new_tab(href)

	# Hàm để mở liên kết và đóng sau 5 giây
	def open_link_in_new_tab(self, url):
		# Mở liên kết trong tab mới
		driver.execute_script(f"window.open('{url}', '_blank');")
		#self.tab_handles += 1  # Thêm handle của tab mới vào danh sách
		# # Quản lý số lượng tab (chỉ giữ lại 2 tab mới nhất)
		# if self.tab_handles > 2:
			# original_window = driver.current_window_handle
			# driver.switch_to.window(driver.window_handles[1])  # Chuyển về tab đầu tiên trong danh sách
			# driver.close()  # Đóng tab đầu tiên
			# driver.switch_to.window(original_window)
			# self.tab_handles -= 1
			


	# Duyệt qua từng dòng trong file mail.txt
read_mail = OpenMail()
for line in lines:
    line = line.strip()  # Loại bỏ khoảng trắng và ký tự newline
    if '|' in line:
        email_user, email_pass = line.split('|', 1)  # Tách địa chỉ email và mật khẩu bằng dấu '|'

        # Kết nối đến máy chủ POP3
        mail = poplib.POP3_SSL(pop3_server, 995)
        mail.user(email_user)
        mail.pass_(email_pass)

        # Lấy số lượng email
        num_messages = len(mail.list()[1])

        # Xác định thời điểm cần lấy email từ (UTC+7)
        utc_plus_7 = timezone(timedelta(hours=7))
        start_date = datetime(2024, 7, 3, 20, 40, tzinfo=utc_plus_7)
        
        # Đọc các email từ máy chủ
        for i in range(num_messages):
            # Lấy một email cụ thể
            response, lines, octets = mail.retr(i + 1)
            # Ghép các dòng email lại với nhau
            msg_data = b'\r\n'.join(lines)
            # Phân tích email
            msg = parser.BytesParser(policy=default).parsebytes(msg_data)
            # Convert chuỗi ngày tháng từ email thành đối tượng datetime
            msg_date_str = msg['date']
            msg_date = datetime.strptime(msg_date_str, '%a, %d %b %Y %H:%M:%S %z')
            msg_date_utc_plus_7 = msg_date.astimezone(utc_plus_7)
            # In tiêu đề email
            print(f'msg_date: {msg_date}')
            print(f'start_date: {start_date}')
            if msg_date_utc_plus_7 >= start_date:
                print(f"Subject: {msg['subject']}")
                print(f"From: {msg['from']}")
                print(f"To: {msg['to']}")
                print(f"Date: {msg['date']}")
                print("----- Email Content -----")
                # Gọi hàm đệ quy để in nội dung email
                read_mail.get_email_content(msg)

            print("\n\n")

        # Đóng kết nối
        mail.quit()
# Đóng trình duyệt khi hoàn thành
time.sleep(10)
driver.quit()