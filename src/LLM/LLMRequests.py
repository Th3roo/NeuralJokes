import openai
import os

class LLMRequester:
    def __init__(self, api_base=None, api_key=None, model=None, system_prompt=None):

        self.api_base = api_base or os.getenv("BOT_API__BASE_URL")
        self.api_key = api_key or os.getenv("BOT_API__API_KEY")
        self.model = model or os.getenv("BOT_API__MODEL")

        if system_prompt:
            self.system_prompt = system_prompt
        else:
            system_prompt_path = os.getenv("BOT_SYSTEM_PROMT_PATH")
            if system_prompt_path:
                try:
                    with open(system_prompt_path, "r") as f:
                        self.system_prompt = f.read()
                except FileNotFoundError:
                    print(f"Warning: System prompt file not found at {system_prompt_path}")
                    self.system_prompt = ""
            else:
                self.system_prompt = ""

        openai.api_base = self.api_base
        openai.api_key = self.api_key

    def generate_response(self, user_message, temperature=None, max_tokens=None):

        temperature = temperature or float(os.getenv("BOT_GENERATION__TEMPERATURE", 0.8))
        max_tokens = max_tokens or int(os.getenv("BOT_GENERATION__MAX_TOKENS", 200))

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_message})

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error during LLM request: {e}")
            return "Sorry, an error occurred while processing the request."