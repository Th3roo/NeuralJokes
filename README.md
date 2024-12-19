# NeuralJokes

## Description

NeuralJokes is a Telegram bot that generates jokes. It can generate random jokes or jokes on a given topic using machine learning models.

## Commands

-   `/start` - start a conversation with the bot and get a welcome message.
-   `/generate_random_joke` - generate a random joke.
-   `/generate_joke <topic>` - generate a joke on the specified topic. If the topic is not specified, the bot will ask for it.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your_username/NeuralJokes.git    ```
2. **Go to the project directory:**
    ```bash
    cd NeuralJokes    ```
3. **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv    ```
4. **Activate the virtual environment:**

    -   **Linux/macOS:**
        ```bash
        source venv/bin/activate        ```

    -   **Windows:**
        ```bash
        venv\Scripts\activate        ```
5. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt    ```
6. **Configure environment variables:**

    Create a `.env` file in the root directory of the project and add the following variables to it:
    ```
    BOT_TOKEN=<your bot token>
    BOT_API__BASE_URL=<llama.cpp API address>
    BOT_API__API_KEY=<llama.cpp API key>
    BOT_API__MODEL=<llama.cpp model name>
    BOT_SYSTEM_PROMT_PATH=<path to the system prompt file>
    BOT_JOKE_GENERATION__COOLDOWN=<waiting time between requests in seconds>
    BOT_JOKE_GENERATION__MAX_RETRIES=<maximum number of attempts to generate a joke>
    BOT_GENERATION__TEMPERATURE=<generation temperature>
    BOT_GENERATION__MAX_TOKENS=<maximum number of tokens in the response>    ```

    Replace `<...>` with the appropriate values.

## Running the backend on llama.cpp

### As a server

1. **Build llama.cpp:**

    Follow the build instructions in the official llama.cpp documentation: [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)
    
    **Build**

    llama-server is built alongside everything else from the root of the project

        Using CMake:

        cmake -B build
        cmake --build build --config Release -t llama-server

        Binary is at ./build/bin/llama-server

    **Build with SSL**

    llama-server can also be built with SSL support using OpenSSL 3

        Using CMake:

        cmake -B build -DLLAMA_SERVER_SSL=ON
        cmake --build build --config Release -t llama-server
    
    **Web UI**

    The project includes a web-based user interface that enables interaction with the model through the /chat/completions endpoint.

    The web UI is developed using:

    -   vue framework for frontend development
    -   tailwindcss and daisyui for styling
    -   vite for build tooling

    A pre-built version is available as a single HTML file under /public directory.

    To build or to run the dev server (with hot reload):
    ```bash
    # make sure you have nodejs installed
    cd examples/server/webui
    npm i

    # to run the dev server
    npm run dev

    # to build the public/index.html
    npm run build    ```

    NOTE: if you are using the vite dev server, you can change the API base URL to llama.cpp. To do that, run this code snippet in browser's console:
    ```js
    localStorage.setItem('base', 'http://localhost:8080')    ```

    **Quick Start**

    To get started right away, run the following command, making sure to use the correct path for the model you have:
    Unix-based systems (Linux, macOS, etc.)
    ```bash
    ./llama-server -m models/7B/ggml-model.gguf -c 2048    ```
    
    Windows
    ```bash
    llama-server.exe -m models\7B\ggml-model.gguf -c 2048    ```

    The above command will start a server that by default listens on `127.0.0.1:8080`. You can consume the endpoints with Postman or NodeJS with axios library. You can visit the web front end at the same url.
2. **Run the server:**
    ```bash
    ./server -m <path to the model> -c <context size> --port <port>    ```

    For example (use **recommended model**: `models/7B/ggml-model-q4_0.bin`):
    ```bash
    ./server -m models/7B/ggml-model-q4_0.bin -c 2048 --port 8080    ```

### As a Docker container

1. **Build the Docker image:**
    ```bash
    docker build -t llama-cpp-server .    ```
2. **Run the Docker container:**
    ```bash
    docker run -d -p 8080:8080 -v <path to the directory with models>:/models llama-cpp-server -m /models/<model name> -c <context size>    ```

    For example (use **recommended model**: `models/7B/ggml-model-q4_0.bin`):
    ```bash
    docker run -d -p 8080:8080 -v $(pwd)/models:/models llama-cpp-server -m /models/7B/ggml-model-q4_0.bin -c 2048    ```

## Running the bot
