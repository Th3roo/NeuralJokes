import openai
import os
import logging
import aiohttp

from typing import Optional

# Logger setup
logger = logging.getLogger(__name__)

class LLMRequester:
    def __init__(self, api_base: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None, system_prompt: Optional[str] = None):
        logger.info("Initializing LLMRequester...")

        self.api_base = api_base or os.getenv("BOT_API__BASE_URL")
        self.api_key = api_key or os.getenv("BOT_API__API_KEY")
        self.model = model or os.getenv("BOT_API__MODEL")

        logger.debug(f"API Base: {self.api_base}")
        logger.debug(f"API Key: {self.api_key}")
        logger.debug(f"Model: {self.model}")

        if system_prompt:
            self.system_prompt = system_prompt
            logger.debug("Using system prompt from constructor argument.")
        else:
            system_prompt_path = os.getenv("BOT_SYSTEM_PROMT_PATH")

            if system_prompt_path:
                try:
                    with open(system_prompt_path, "r", encoding="UTF-8") as f:
                        self.system_prompt = f.read()

                    logger.info(f"System prompt loaded from: {system_prompt_path}")
                except FileNotFoundError:
                    logger.warning(f"System prompt file not found at {system_prompt_path}")
                    self.system_prompt = ""
            else:
                self.system_prompt = ""
                logger.warning("System prompt path not set in environment variables.")

        openai.api_base = self.api_base
        openai.api_key = self.api_key

    async def generate_response_async(self, user_message: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        logger.info("Generating response...")

        temperature = temperature or float(os.getenv("BOT_GENERATION__TEMPERATURE", 0.8))
        max_tokens = max_tokens or int(os.getenv("BOT_GENERATION__MAX_TOKENS", 200))

        logger.debug(f"Temperature: {temperature}")
        logger.debug(f"Max Tokens: {max_tokens}")

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": user_message})

        logger.debug(f"Messages: {messages}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        response_content = response_data['choices'][0]['message']['content']

                        logger.info("Response generated successfully.")
                        logger.debug(f"Response content: {response_content}")

                        return response_content
                    else:
                        logger.error(f"Error during LLM request: {response.status} - {await response.text()}")
                        return "Sorry, an error occurred while processing the request."
        except Exception as e:
            logger.error(f"Error during LLM request: {e}")
            return "Sorry, an error occurred while processing the request."