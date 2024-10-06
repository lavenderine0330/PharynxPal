# import requests
# import os


# # 发送HTTP请求并保存正确格式的数据
# def fetch_data(time_range, format):

#     url = "http://localhost:5000/history" # 外部路径-改成端的路径
#     params = {
#             "time_range": time_range,
#             "format": format
#     }
#     try:
#         response = requests.get(url,params=params)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         return f"Failed to fetch data:{str(e)}"

#     if format == 'csv':
#         with open("behavior_data.csv","wb") as f:
#             f.write(response.content) #save csv data to "behavior_data.csv"
#     elif format == 'json':
#         return response.json()

# import pandas as pd
# import json

# def fetch_data(time_range, format): #改成向/history发送请求，return csv数据，参考InterventionAgent run（）步骤1_执行工具调用中的function_responses
#     file_path = "/home/user/zxyx/EarSAVAS_github/EarSAVAS/detection_results.csv"
#     if format not in ['csv', 'json']:
#         return f"Invalid format. Only 'csv' and 'json' are supported."

#     try:
#         # 读取 CSV 文件
#         data = pd.read_csv(file_path)
        
#         # 处理时间范围
#         if time_range == "last 30 minutes":
#             data['time'] = pd.to_datetime(data['time'])
#             end_time = data['time'].max()
#             start_time = end_time - pd.Timedelta(minutes=30)
#             filtered_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]
#         else:
#             filtered_data = data

#         if format == 'csv':
#             # 将过滤后的数据保存为 CSV 格式的字符串
#             csv_data = filtered_data.to_csv(index=False)
#             # print(csv_data)
#             return csv_data
#         elif format == 'json':
#             # 将过滤后的数据转换为 JSON 格式的字符串
#             json_data = filtered_data.to_json(orient='records')
#             return json_data

#     except Exception as e:
#         return f"Failed to fetch data: {str(e)}"


import requests
from datetime import datetime, timedelta

def fetch_data():
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)

    start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M')

    #construct the request URL
    url = f"http://127.0.0.1:5002/history?time_range={start_time_str},{end_time_str}&format=csv"

    # Send the GET request to the /history endpoint
    response = requests.get(url)

    if response.status_code == 200:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'fetched_data_{timestamp}.csv'
        with open(filename, 'wb') as f:
            f.write(response.content)
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                print(line, end='')
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    return filename
