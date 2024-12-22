import openai
import os
import logging
import aiohttp
import json

from typing import Optional, AsyncIterator

# Logger setup
logger = logging.getLogger(__name__)

class LLMRequester:
    def __init__(self, api_base: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None, system_prompt: Optional[str] = None):
        logger.info("Initializing LLMRequester...")

        self.api_base = self._get_config_value("BOT_API__BASE_URL", api_base)
        self.api_key = self._get_config_value("BOT_API__API_KEY", api_key)
        self.model = self._get_config_value("BOT_API__MODEL", model)

        logger.debug(f"API Base: {self.api_base}")
        logger.debug(f"API Key: {'SET' if self.api_key else 'NOT SET'}") # Improved display of API Key status
        logger.debug(f"Model: {self.model}")

        self.system_prompt = self._load_system_prompt(system_prompt)

        if not self.api_base:
            logger.critical("BOT_API__BASE_URL is not set.")
            raise ValueError("BOT_API__BASE_URL is not set.")
        if not self.api_key:
            logger.critical("BOT_API__API_KEY is not set.")
            raise ValueError("BOT_API__API_KEY is not set.")

        openai.api_base = self.api_base
        openai.api_key = self.api_key

    def _get_config_value(self, env_var: str, constructor_value: Optional[str]) -> Optional[str]:
        """
        Gets the value from the environment variable or constructor argument.
        """
        value = constructor_value or os.getenv(env_var)
        if not value:
            logger.warning(f"{env_var} is not set.")
        return value

    def _load_system_prompt(self, system_prompt: Optional[str]) -> str:
        """
        Loads the system prompt from a file or uses the provided one.
        """
        if system_prompt:
            logger.debug("Using system prompt from constructor argument.")
            return system_prompt

        system_prompt_path = os.getenv("BOT_SYSTEM_PROMT_PATH")
        if system_prompt_path:
            try:
                with open(system_prompt_path, "r", encoding="UTF-8") as f:
                    logger.info(f"System prompt loaded from: {system_prompt_path}")
                    return f.read()
            except FileNotFoundError:
                logger.warning(f"System prompt file not found at {system_prompt_path}")
                return ""
        else:
            logger.warning("System prompt path not set in environment variables.")
            return ""

    async def generate_response_streaming(self, user_message: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> AsyncIterator[str]:
        """
        Generates a response in streaming mode, returning an iterator over the response parts.
        """
        logger.info("Generating streaming response...")

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
                        "max_tokens": max_tokens,
                        "stream": True
                    }
                ) as response:
                    if response.status == 200:
                        full_response = ""

                        async for line in response.content:
                            line = line.decode('utf-8').strip()

                            if line.startswith("data:"):
                                data = line[5:].strip()

                                if data == "[DONE]":
                                    logger.info("Streaming response completed.")
                                    return

                                try:
                                    data_json = json.loads(data)

                                    if 'choices' in data_json and data_json['choices']:
                                        delta = data_json['choices'][0].get('delta', {})

                                        if delta.get('content'):
                                            full_response += delta['content']
                                            yield delta['content']

                                        finish_reason = data_json['choices'][0].get('finish_reason')

                                        if finish_reason == "stop":
                                            logger.info(f"Streaming response completed with stop reason. Full response: {full_response}")
                                            return
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to decode JSON from line: {data}")
                    else:
                        logger.error(f"Error during LLM request: {response.status} - {await response.text()}")
                        yield "Sorry, there was an error processing your request."

        except Exception as e:
            logger.error(f"Error during LLM request: {e}")
            yield "Sorry, there was an error processing your request."