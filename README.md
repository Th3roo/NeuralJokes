 # NeuralJokes

## Description

NeuralJokes is a Telegram bot that generates jokes using LLM. It can generate random jokes or jokes on a given topic. The bot interacts with users through Telegram

## Commands

- `/start` - Start a conversation with the bot and receive a welcome message.
- `/generate_random_joke` - Generate a random joke.
- `/generate_joke <topic>` - Generate a joke on the specified topic. If the topic is not provided, the bot will ask for it.

## Installation

### Step-by-Step Guide

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your_username/NeuralJokes.git
    ```

2. **Navigate to the project directory:**
    ```bash
    cd NeuralJokes
    ```

3. **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    ```

4. **Activate the virtual environment:**
    - For Linux/macOS:
        ```bash
        source venv/bin/activate
        ```
    - For Windows:
        ```bash
        venv\Scripts\activate
        ```

5. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6. **Configure environment variables:**
    Create a `.env` file in the root directory of the project and add the following variables:
    ```plaintext
    BOT_TOKEN=<your bot token>
    BOT_API__BASE_URL=<llama.cpp API address>
    BOT_API__API_KEY=<llama.cpp API key>
    BOT_API__MODEL=<llama.cpp model name>
    BOT_SYSTEM_PROMT_PATH=<path to the system prompt file>
    BOT_JOKE_GENERATION__COOLDOWN=<waiting time between requests in seconds>
    BOT_JOKE_GENERATION__MAX_RETRIES=<maximum number of attempts to generate a joke>
    BOT_GENERATION__TEMPERATURE=<generation temperature>
    BOT_GENERATION__MAX_TOKENS=<maximum number of tokens in the response>
    ```
    Replace `<...>` with appropriate values.

## Running the Backend on llama.cpp

### As a Server

1. **Build llama.cpp:**
    Follow the build instructions in the official llama.cpp documentation: [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

    - **Using CMake:**
        ```bash
        cmake -B build
        cmake --build build --config Release -t llama-server
        ```

    - **Build with SSL using OpenSSL 3 (optional):**
        ```bash
        cmake -B build -DLLAMA_SERVER_SSL=ON
        cmake --build build --config Release -t llama-server
        ```

    - **Quick Start:**
        For Linux:
        ```bash
        ./llama-server -m models/7B/model.gguf -c 4096 --host 0.0.0.0 --port 1234
        ```

        For Windows:
        ```bash
        llama-server.exe -m models\7B\model.gguf -c 4096 --host 0.0.0.0 --port 1234
        ```

2. **Run the server:**
    ```bash
    ./llama-server -m <path to the model> -c <context size> --port <port>
    ```

    Example (using recommended model `[models/Llama-3.1-8B-JokesMachine](https://huggingface.co/kentfoong/Llama-3.1-8B-JokesMachine)`):
    ```bash
    ./llama-server -m models/Llama-3.1-8B-JokesMachine.gguf -c 2048 --port 8080
    ```

### As a Docker Container

1. **Build the Docker image:**
    ```bash
    docker build -t llama-cpp-server .
    ```

2. **Run the Docker container:**
    ```bash
    docker run -d -p 8080:8080 -v <path to the directory with models>:/models llama-cpp-server -m /models/<model name> -c <context size>
    ```

    Example (using recommended model `[models/Llama-3.1-8B-JokesMachine](https://huggingface.co/kentfoong/Llama-3.1-8B-JokesMachine)`):
    ```bash
    docker run -d -p 8080:8080 -v $(pwd)/models:/models llama-cpp-server -m /models/Llama-3.1-8B-JokesMachine.gguf -c 4096
    ```

## Running the Bot

```bash
python main.py
```
