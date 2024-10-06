# import os

# import json

# from llm import (
#     LLM,
#     Message,
#     Response
# )

# class BaseAgent:
#     def __init__(self,
#                 agent_name,
#                 task_input,
#         ):
#         self.agent_name = agent_name
#         self.config = self.load_config()
#         self.prefix = " ".join(self.config["description"])
#         self.task_input = task_input
#         self.llm = LLM()

#     def run(self):
#         '''Execute each step to finish the task.'''
#         pass

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
        
#     def get_response(self, message):
#         response = self.llm.model.chat.completions.create(
#             model=self.llm.model_name,
#             messages=[
#                 {"role": "user", "content": message.prompt}
#             ],
#             tools = message.tools,
#             tool_choice = "required" if message.tools else None
#         )

#         response = Response(
#             response_message = response.choices[0].message.content,
#             tool_calls = response.choices[0].message.tool_calls
#         )
#         return response