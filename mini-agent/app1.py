# from flask import Flask, request, jsonify
# from agents.Intervention_agent_cmf import InterventionAgent
# import pandas as pd
# from datetime import datetime, timedelta

# app = Flask(__name__)
# agent = InterventionAgent(agent_name="InterventionAgent", task_input="")

# def analyze_csv(file_path):
#     # 读取CSV文件
#     df = pd.read_csv(file_path)

#     # 过滤出最近30分钟的数据
#     now = datetime.now()
#     df['time'] = pd.to_datetime(df['time'])
#     recent_data = df[df['time'] >= now - timedelta(minutes=30)]

#     # 检查持续的咳嗽或清嗓
#     if recent_data['coughing'].sum() >= 30:  # 例如: 30秒持续咳嗽
#         return 'lasting_cough_detected'
#     elif recent_data['throat_clearing'].sum() >= 30:  # 例如: 30秒持续清嗓
#         return 'throat_clear_detected'
#     else:
#         return 'others'

# def receive_trigger(agent, event_type):
#     print(event_type)
#     if event_type == 'lasting_cough_detected':
#         agent.task_input = ("The user has been coughing for a significant period. Let's start step by step.")
#     elif event_type == 'throat_clear_detected':
#         agent.task_input = ("The user has been clearing their throat frequently. Let's start step by step.")
#     else:
#         agent.task_input = ("Let's start step by step.") 
#     return agent.run()

# @app.route('/trigger', methods=['POST'])
# def trigger():
#     # 从请求中获取CSV文件路径
#     csv_file_path = "/home/user/zxyx/EarSAVAS_github/EarSAVAS/detection_results.csv"  # 这里是CSV文件路径

#     # 分析CSV文件
#     event_type = analyze_csv(csv_file_path)

#     # 获取分析结果
#     response = receive_trigger(agent, event_type)
    
#     return jsonify({"response": response})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001)



from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from agents.Intervention_agent_cmf import InterventionAgent
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import websockets
import threading
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
op=[]
# 回调函数，用于实时传回agent的输出
def send_output_to_frontend(output):
    # print(output)
    op.append(output)
    # print(op)
    # socketio.emit('agent_output', {'response': output})

async def conversation(websocket, path):
    while True:
        if len(op) == 0:
            await asyncio.sleep(1)  # 避免忙等待
            continue
        message = op.pop(0)  # 从列表中取出消息
        await websocket.send(message)  # 将消息发送给客户端

        # 接收用户回复
        response = await websocket.recv()
        print(f"Received: {response}")
        if response:
        # 调用 InterventionAgent 的 set_user_reply 方法
            if hasattr(agent, 'set_user_reply'):
                agent.set_user_reply(response)



agent = InterventionAgent(agent_name="InterventionAgent", task_input="", send_output_callback=send_output_to_frontend)

def analyze_csv(file_path):
    df = pd.read_csv(file_path)
    now = datetime.now()
    df['time'] = pd.to_datetime(df['time'])
    recent_data = df[df['time'] >= now - timedelta(minutes=30)]
    if recent_data['coughing'].sum() >= 30:
        return 'lasting_cough_detected'
    elif recent_data['throat_clearing'].sum() >= 30:
        return 'throat_clear_detected'
    else:
        return 'others'

def receive_trigger(agent, event_type):
    if event_type == 'lasting_cough_detected':
        agent.task_input = ("The user has been coughing for a significant period. Let's start step by step.")
    elif event_type == 'throat_clear_detected':
        agent.task_input = ("The user has been clearing their throat frequently. Let's start step by step.")
    else:
        agent.task_input = ("Let's start step by step.") 
    return agent.run()

@app.route('/trigger', methods=['POST'])
def trigger():
    csv_file_path = "../detection_results.csv"
    event_type = analyze_csv(csv_file_path)
    receive_trigger(agent, event_type)
    return jsonify({"status": "triggered"})
async def main():
    async with websockets.serve(conversation, "118.186.244.221", 5003):
        await asyncio.Future()  # 运行直到被手动停止

if __name__ == "__main__":
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5001))
    websocket_thread = threading.Thread(target=lambda: asyncio.run(main()))

    flask_thread.start()
    websocket_thread.start()

    flask_thread.join()
    websocket_thread.join()
