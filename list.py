import asyncio
import websockets
import json

async def get_list():
    uri = "ws://127.0.0.1:22222/"
    async with websockets.connect(uri) as websocket:
        # Gửi yêu cầu "list"
        request = {"action": "list"}
        await websocket.send(json.dumps(request))
        
        # Nhận phản hồi
        response = await websocket.recv()
        print("Received:", response)

        # Phân tích cú pháp dữ liệu JSON
        response_data = json.loads(response)
        
        # Truy cập vào trường "data"
        if "data" in response_data:
            data_list = response_data["data"]
            print("Data List:")
            
            # Trích xuất chỉ các trường 'serial' và 'sort'
            filtered_data = [{'phone': item['serial'], 'number': item['sort']} for item in data_list]
            
            # Lưu dữ liệu vào box.json
            with open('box.json', 'w') as file:
                json.dump(filtered_data, file, indent=4)
            
            print("Filtered data has been written to box.json")
        else:
            print("No 'data' field found in the response.")

# Chạy hàm get_list
asyncio.run(get_list())
