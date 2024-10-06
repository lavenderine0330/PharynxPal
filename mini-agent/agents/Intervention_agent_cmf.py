import json
import os
from agents.llm import LLM, Message, Response
from agents.tools import fetch_data

class InterventionAgent:
    def __init__(self, agent_name, task_input, send_output_callback=None):
        self.agent_name = agent_name
        self.config = self.load_config()
        self.prefix = " ".join(self.config["description"])
        self.task_input = task_input
        self.llm = LLM()
        self.send_output_callback = send_output_callback  # 增加 send_output_callback 回调函数

        self.tool_list = {"fetch_data": fetch_data}
        self.workflow = self.config["workflow"]
        self.tools = self.config["tools"]
        self.load_save_config()
        self.user_reply = None
    def load_config(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        config_file = os.path.join(script_dir, "agent_config", f"{self.agent_name}.json")

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            try:
                config = json.load(f)
                return config
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON from config file {config_file}: {e}")

    def load_save_config(self):
        script_path = os.path.abspath(__file__)
        self.script_dir = os.path.join(os.path.dirname(script_path), "output")
        if not os.path.exists(self.script_dir):
            os.makedirs(self.script_dir)

    def get_response(self, message):
        response_content, tool_calls = self.llm.generate_response(prompt=message.prompt, tools=message.tools)
        response = Response(response_message=response_content, tool_calls=tool_calls)
        return response  
    def set_user_reply(self, user_reply):
        self.user_reply = user_reply
    def run(self):
        prompt = self.prefix + self.task_input
        context = prompt

        for i, step in enumerate(self.workflow):
            if i == 0:
                response = self.get_response(
                    message=Message(prompt=prompt, tools=self.tools)
                )
                tool_calls = response.tool_calls
                if tool_calls:
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_to_call = self.tool_list[function_name]
                        try:
                            function_response = function_to_call()
                            with open(function_response, 'r', encoding='utf-8') as file:
                                csv_data = file.read()
                                context += "\n" + csv_data
                        except Exception as e:
                            continue
            elif i == 1:
                step_prompt = context + f"\nIn step {i + 1}, you need to {step}."
                response = self.get_response(
                    message=Message(prompt=step_prompt, tools=None)
                )
                response_message = response.response_message
                context += "\n" + response_message
                prompt += "\n" + response_message
            elif i == 2:
                step_prompt = prompt + f"\nIn step {i + 1}, you need to {step}. Now, start to talk with the user."
                prompt = step_prompt

                while True:
                    response = self.get_response(
                        message=Message(prompt=prompt, tools=None)
                    )
                    response_message = response.response_message
                    prompt += "\n" + response_message
                    # print(self.send_output_callback)
                    # 这里是新增的部分，实时传回输出到 send_output_callback
                    if self.send_output_callback:
                        # print(response_message)
                        self.send_output_callback(response_message)

                    # 检查是否结束对话
                    if response_message in ['Thank you for reflecting on this with me']:
                        break
                    while True:
                        if self.user_reply:
                            print(self.user_reply)
                            prompt += "\nUser: " + self.user_reply
                            prompt += "\nAssistant:"
                            self.user_reply = None  # 重置 user_reply 以便接收新的回复
                            break

