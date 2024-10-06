#无dialogue structure版本#

import json
import os

from agents.llm import (
    LLM,
    Message,
    Response
)
from agents.tools import fetch_data

class InterventionAgent:
    def __init__(self, agent_name, task_input,):
        
        self.agent_name = agent_name
        self.config = self.load_config()
        self.prefix = " ".join(self.config["description"])
        self.task_input = task_input
        self.llm = LLM()

        self.tool_list = {
            "fetch_data": fetch_data
        }
        self.workflow = self.config["workflow"]
        self.tools = self.config["tools"]
        self.load_save_config()

    def load_config(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        config_file = os.path.join(script_dir, "agent_config", f"{self.agent_name}.json")

        print(f"Attempting to load config from: {config_file}")

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            try:
                config = json.load(f)
                if config is None:
                    raise ValueError(f"Config file is empty or invalid: {config_file}")
                print(f"Config loaded successfully: {config}")
                return config
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON from config file {config_file}: {e}")

    def load_save_config(self):
        script_path = os.path.abspath(__file__)
        self.script_dir = os.path.join(os.path.dirname(script_path), "output")
        if not os.path.exists(self.script_dir):
            os.makedirs(self.script_dir)

    def get_response(self, message):
        # 修改此处以直接调用 LLM 类的 generate_response 方法
        response_content, tool_calls = self.llm.generate_response(
            prompt=message.prompt,
            tools=message.tools
        ) 
        # print(response_content, tool_calls)
        response = Response(
            response_message=response_content,
            tool_calls=tool_calls
        )
        return response  
    
    def run(self):
    
        #初始化prompt模板，添加prefix和task_input
        prompt = self.prefix
        task_input = self.task_input
        # if isinstance(task_input, list):
        #     task_input = " ".join(map(str, task_input))  # 将列表转换为字符串
        # task_input = "The task you need to solve is: " + task_input
        #  print(f"{task_input}\n")
        prompt += task_input
        context = prompt  # 用于存储整个对话历史

        #循环处理workflow
        for i, step in enumerate(self.workflow):

            # 步骤1 执行工具调用
            if i == 0 :
                response = self.get_response(
                    message = Message(
                        prompt = prompt,
                        tools = self.tools
                    )
                )              

                tool_calls = response.tool_calls
                if tool_calls:
                    print(f"It starts to call external tools.") 
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_to_call = self.tool_list[function_name]

                        try:
                            function_response = function_to_call()

                            # 将 CSV 文件中的数据读取并添加到 context 中
                            with open(function_response, 'r', encoding='utf-8') as file:
                                csv_data = file.read()
                                context += "\n" + csv_data

                        except Exception as e:
                            print(f"Error calling tool {function_name}: {str(e)}")
                            continue
                else:
                    print(f"No tool calls available in the response.")

            # 步骤2 分析数据
            elif i == 1 :
                #当前步骤下的workflow加入prompt
                step_prompt = f"\nIn step {i + 1}, you need to {step}. Output should focus on current step and don't be verbose!"
                step_prompt = context + step_prompt #包含csv数据

                #获得LLM response
                response = self.get_response(
                    message = Message(
                        prompt = step_prompt,
                        tools = None #不需要调用tool
                    )
                )
                response_message = response.response_message
                print(f"Data report analysis: {response_message}") 

                # 将数据分析结果加入context和prompt,不输出response
                # print(response_message)
                context += "\n" + response_message
                prompt += "\n" + response_message #不包含csv数据但是包含数据分析结果

            # 在步骤3与用户交互
            elif i == 2:
                step_prompt = f"\nIn step {i + 1}, you need to {step}. Now, Start to talk with the user."
                prompt = prompt + step_prompt
                while True:
                    response = self.get_response(
                        message = Message(
                            prompt = prompt,
                            tools = None 
                        )
                    )
                    response_message = response.response_message
                    prompt += "\n" + response_message
                    
                    # Agent响应
                    print(f"Intervention Agent: {response_message}") 
                    
                    # User输入 
                    user_reply = input("User's response: ") 
                    prompt += "\nUser: " + user_reply
                    prompt += "\nAssistant:"

                    # Break condition to exit the loop
                    if response_message in ['Thank you for reflecting on this with me']:
                        break


# Create an instance of InterventionAgent with necessary inputs
agent = InterventionAgent(agent_name="InterventionAgent", task_input="The user has been coughing for a significant period. Let's start step by step.")

# Run the agent
agent.run()



# import json
# import os

# from llm import (
#     LLM,
#     Message,
#     Response
# )
# from tools import fetch_data

# class InterventionAgent:
#     def __init__(self, agent_name, task_input,):
        
#         self.agent_name = agent_name
#         self.config = self.load_config()
#         self.prefix = " ".join(self.config["description"])
#         self.task_input = task_input
#         self.llm = LLM()

#         self.tool_list = {
#             "fetch_data": fetch_data
#         }
#         self.workflow = self.config["workflow"]
#         self.tools = self.config["tools"]
#         self.dialogue_protocal = self.config["dialogue_protocal"] 
#         self.load_save_config()

#     def load_config(self):
#         script_path = os.path.abspath(__file__)
#         script_dir = os.path.dirname(script_path)
#         config_file = os.path.join(script_dir, "agent_config", f"{self.agent_name}.json")

#         print(f"Attempting to load config from: {config_file}")

#         if not os.path.exists(config_file):
#             raise FileNotFoundError(f"Config file not found: {config_file}")

#         with open(config_file, "r") as f:
#             try:
#                 config = json.load(f)
#                 if config is None:
#                     raise ValueError(f"Config file is empty or invalid: {config_file}")
#                 print(f"Config loaded successfully: {config}")
#                 return config
#             except json.JSONDecodeError as e:
#                 raise ValueError(f"Error decoding JSON from config file {config_file}: {e}")

#     def load_save_config(self):
#         script_path = os.path.abspath(__file__)
#         self.script_dir = os.path.join(os.path.dirname(script_path), "output")
#         if not os.path.exists(self.script_dir):
#             os.makedirs(self.script_dir)

#     def get_response(self, message):
#         # 修改此处以直接调用 LLM 类的 generate_response 方法
#         response_content, tool_calls = self.llm.generate_response(
#             prompt=message.prompt,
#             tools=message.tools
#         ) 
#         # print(response_content, tool_calls)
#         response = Response(
#             response_message=response_content,
#             tool_calls=tool_calls
#         )
#         return response  
    
    
#     def run(self):
    
#         #初始化prompt模板，添加prefix和task_input
#         prompt = self.prefix
#         task_input = self.task_input
#         prompt += task_input
#         context = prompt  # 用于存储整个对话历史

#         #循环处理workflow
#         for i, step in enumerate(self.workflow):

#             # 步骤1 执行工具调用
#             if i == 0 :
#                 response = self.get_response(
#                     message = Message(
#                         prompt = prompt,
#                         tools = self.tools
#                     )
#                 )              

#                 tool_calls = response.tool_calls
#                 if tool_calls:
#                     print(f"It starts to call external tools.") 
#                     for tool_call in tool_calls:
#                         function_name = tool_call.function.name
#                         function_to_call = self.tool_list[function_name]

#                         try:
#                             function_response = function_to_call()

#                             # 将 CSV 文件中的数据读取并添加到 context 中
#                             with open(function_response, 'r', encoding='utf-8') as file:
#                                 csv_data = file.read()
#                                 context += "\n" + csv_data

#                         except Exception as e:
#                             print(f"Error calling tool {function_name}: {str(e)}")
#                             continue
#                 else:
#                     print(f"No tool calls available in the response.")

#             # 步骤2 分析数据
#             elif i == 1 :
#                 #当前步骤下的workflow加入prompt
#                 step_prompt = f"\nIn step {i + 1}, you need to {step}. Output should focus on current step and don't be verbose!"
#                 step_prompt = context + step_prompt #包含csv数据
#                 Reflection_prompt = f""
                
#                 #获得LLM response
#                 response = self.get_response(
#                     message = Message(
#                         prompt = step_prompt,
#                         tools = None #不需要调用tool
#                     )
#                 )
#                 response_message = response.response_message
#                 print(f"Data report analysis: {response_message}") 

#                 # 将数据分析结果加入context和prompt,不输出response
#                 # print(response_message)
#                 context += "\n" + response_message
#                 prompt += "\n" + response_message #不包含csv数据但是包含数据分析结果

#             # 在步骤3与用户交互
#             elif i == 2:
#                 step_prompt = f"\nIn step {i + 1}, you need to {step}."
#                 prompt = prompt + step_prompt
                
#                 # Step 1: Start the conversation
#                 dialogue_prompt = f"[{self.dialogue_protocal[0]['step-1']['root_node']}"
#                 prompt = prompt + dialogue_prompt
                
#                 while True:
#                     response = self.get_response(
#                         message = Message(
#                             prompt = prompt,
#                             tools = None 
#                         )
#                     )
#                     response_message = response.response_message
#                     prompt += "\n" + response_message
                    
#                     # Agent响应
#                     print(f"Intervention Agent: {response_message}") 
                    
#                     # User回复
#                     user_reply = input("User's response: ") 
#                     prompt += f"\nUser: {user_reply}"
                
#                     # Step 2: Navigate through branches based on user response
#                     branches = self.dialogue_protocal[0]['step-2']['branches']
#                     selected_branch = None
                    
#                     # Use LLM to evaluate condition
#                     condition_prompt = "Based on the user's response, which condition best fits the user's current state? Choose one of the following conditions:\n"
#                     for branch in branches:
#                         condition_prompt += f"- {branch.get('condition', 'Unknown condition')}\n"

#                     condition_prompt += "Respond with the most appropriate condition."

#                     # Evaluate condition using LLM
#                     condition_evaluation = self.get_response(
#                         message=Message(
#                             prompt=prompt + "\n" + condition_prompt,
#                             tools=None
#                         )
#                     ).response_message
                    
#                     for branch in branches:
#                         condition = branch.get('condition', "")
#                         if condition in condition_evaluation:
#                             selected_branch = branch
#                             break
                        
#                     if selected_branch:
#                         sub_branches = selected_branch.get('sub_branches', [])
#                         for sub_branch in sub_branches:
#                             sub_condition = sub_branch.get('condition', "")
#                             if sub_condition in condition_evaluation:
#                                 action = sub_branch['action']
#                                 print(f"Intervention Agent: {action}")
#                                 prompt += f"\nIntervention Agent: {action}"

#                                 # Check if it's an end node
#                                 if sub_branch.get('end_node', False):
#                                     return action
#                                 break    
#                         else:
#                             action = selected_branch['action']
#                             print(f"Intervention Agent: {action}")
#                             prompt += f"\nIntervention Agent: {action}"

#                             # Check if it's an end node
#                             if selected_branch.get('end_node', False):
#                                 return action

#             # Final condition to end the loop
#             if response_message in ['Thank you for reflecting on this with me']:
#                 break

# # Create an instance of InterventionAgent with necessary inputs
# agent = InterventionAgent(agent_name="InterventionAgent", task_input="The user has been coughing for a significant period. Let's start step by step.")

# # Run the agent
# agent.run()
    
