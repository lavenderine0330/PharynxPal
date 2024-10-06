# import asyncio
# import csv
# import websockets
# import json

# # 用于存储 WebSocket 连接
# clients = set()

# async def monitor_csv(file_path):
#     while True:
#         await asyncio.sleep(5)  # 每5秒检查一次文件

#         # 统计 'eating' 的次数
#         eating_count = 0
#         with open(file_path, mode='r') as file:
#             reader = list(csv.DictReader(file))
#             if reader:
#                 last_row = reader[-1]  # 获取最后一行的数据
#                 eating_count = int(last_row.get('eating', 0))  # 获取 'eating' 的值

#         if eating_count > 20:
#             print(147)
#             await trigger_photo_take()

# async def trigger_photo_take():
#     if clients:  # 如果有连接的客户端
#         message = json.dumps({"action": "takePhoto"})
#         await asyncio.wait([client.send(message) for client in clients])

# async def handler(websocket, path):
#     clients.add(websocket)
#     try:
#         async for message in websocket:
#             pass  # 这里可以处理从客户端发来的消息
#     finally:
#         clients.remove(websocket)

# async def main():
#     file_path = '/home/user/zxyx/EarSAVAS_github/EarSAVAS/detection_results.csv'
#     asyncio.create_task(monitor_csv(file_path))
    
#     async with websockets.serve(handler, "118.186.244.221", 5003):
#         await asyncio.Future()  # 运行直到取消

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
import websockets
import pandas as pd
import os
import time

CSV_FILE_PATH = 'detection_results.csv'

async def monitor_csv(websocket, path):
    """
    Monitors a CSV file every second. If 'eating_count' > 1 is detected,
    sends a 'TAKE_PHOTO' signal to the frontend via WebSocket.
    After sending the signal, waits for X minutes before monitoring again.
    """
    
    # Initialize the last sent time to None
    last_sent_time = None
    # Define the cooldown period in seconds
    COOLDOWN_PERIOD = 60  
    
    while True:
        try:
            await asyncio.sleep(1)  # 每1s检查一次 CSV 文件
            if os.path.exists(CSV_FILE_PATH):
                df = pd.read_csv(CSV_FILE_PATH)
                if not df.empty:
                    last_row = df.iloc[-1]
                    eating_count = last_row['eating']
                    if eating_count >= 1:
                        current_time = time.time()
                        # Check if cooldown period has passed
                        if (last_sent_time is None) or (current_time - last_sent_time > COOLDOWN_PERIOD):
                            # 发送拍照信号到前端
                            if websocket.open:
                                await websocket.send('{"type": "TAKE_PHOTO"}')
                                print("TAKE_PHOTO signal sent.")
                            # Update the last sent time
                                last_sent_time = current_time
                            # Start the cooldown period
                                print("Entering cooldown period of 5 minutes.")
                            else:
                                print("WebSocket connection is not open. Cannot send TAKE_PHOTO signal.")
                        else:
                            # Calculate remaining cooldown time
                            remaining_time = COOLDOWN_PERIOD - (current_time - last_sent_time)
                            print(f"Cooldown active. Next signal available in {int(remaining_time)} seconds.")
                    else:
                        print("eating_count < 1. No action needed.")
                else:
                    print("CSV file is empty. Waiting for data...")
            else:
                print(f"CSV file not found at {CSV_FILE_PATH}. Waiting for the file to be available...")
        
        
        except websockets.ConnectionClosed:
            print("WebSocket 连接已关闭，重新建立连接...")
            break  # 跳出循环，重新建立连接

async def handle_connection(websocket, path):
    while True:
        try:
            await monitor_csv(websocket, path)
        except Exception as e:
            print(f"处理连接时发生错误: {e}")
            await asyncio.sleep(1)  # 等待一段时间后重新尝试

async def main():
    async with websockets.serve(handle_connection, "118.186.244.221", 5004):
        print("WebSocket server started on ws://118.186.244.221:5004")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
