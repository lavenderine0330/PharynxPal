import openai
import os
openai.proxy = None
class LLM:
    def __init__(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        self.model_name = "gpt-4o-mini" 

    def generate_response(self, prompt: str, tools=None) -> dict:
        try:
            # print('tools',tools)
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                tools=tools,
                tool_choice="required" if tools else None
            )
            # print('response',response)
            # Extract content and tool calls from the response
            return response.choices[0].message['content'], response.choices[0].message.get('tool_calls')
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")

class Message:
    def __init__(self, prompt, context=None, tools=None) -> None:
        self.prompt = prompt
        self.context = context
        self.tools = tools

class Response:
    def __init__(self, response_message, tool_calls=None) -> None:
        self.response_message = response_message
        self.tool_calls = tool_calls
