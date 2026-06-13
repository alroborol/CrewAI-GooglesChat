# Google Chat Webhook Server in Python (FastAPI)

This project provides a minimal HTTP webhook server to receive and respond to Google Chat events using Python, FastAPI, and a CrewAI Agent.

## File Structure

- [app.py](file:///Users/albert/CrewAI-GooglesChat/app.py): The FastAPI server defining the `/webhook` endpoint, which receives Google Chat events and triggers the CrewAI agent.
- [crew.py](file:///Users/albert/CrewAI-GooglesChat/crew.py): Defines the CrewAI Agent and task logic, equipped with a simulation mode.
- [test_webhook.py](file:///Users/albert/CrewAI-GooglesChat/test_webhook.py): Local test runner to simulate Google Chat payloads and verify responses.
- [requirements.txt](file:///Users/albert/CrewAI-GooglesChat/requirements.txt): List of Python dependencies.

## Installation & Setup

1. Make sure you have Python 3.10+ installed.
2. Initialize the virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Webhook Server

Run the FastAPI application via Uvicorn:
```bash
python3 app.py
```
By default, the server runs on port `5001`. You can customize the port by setting the `PORT` environment variable:
```bash
PORT=8080 python3 app.py
```

## Local Verification

With the server running in one terminal window, execute the test script in another:
```bash
python3 test_webhook.py
```

It sends mock payloads mimicking a MESSAGE event and an ADDED_TO_SPACE event, printing the returned status and JSON replies.

## CrewAI Simulation Mode vs. Live Mode

On Python 3.14 (a pre-release python version), packages with native extensions (like `tiktoken` used by CrewAI/LiteLLM) must be built from source and require a **Rust compiler**.

- **Simulation Mode (Default)**: If CrewAI is not fully installed, the server automatically falls back to simulating the agent's output. This allows you to immediately test the webhook flow and connection to Google Chat.
- **Enabling Live Mode**:
  1. Install a Rust compiler on your system (e.g., using `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` or via your OS package manager).
  2. Install `crewai` in your virtual environment:
     ```bash
     pip install crewai
     ```
  3. Set up your LLM API Key (e.g. `export OPENAI_API_KEY="your-key-here"` or `export GEMINI_API_KEY="your-key-here"`).
  4. Once `crewai` is installed, the application will automatically switch to **Live Mode** and kickoff the real LLM agent workflow.

## Google Chat Integration

To hook this up as a Google Chat app:

1. **Expose Local Server**: Since Google Chat needs a public HTTPS URL, use a tool like `ngrok` during development:
   ```bash
   ngrok http 5001
   ```
   Copy the generated HTTPS URL (e.g., `https://xxxx.ngrok-free.app`). Your webhook endpoint will be `https://xxxx.ngrok-free.app/webhook`.

2. **Configure Google Cloud Project**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the **Google Chat API**.
   - Navigate to the **Google Chat API** dashboard -> **Configuration** tab.
   - Set the application details (App name, Avatar, etc.).
   - Under **Connection settings**, select **App URL** and paste your HTTPS URL (`https://xxxx.ngrok-free.app/webhook`).
   - Check the boxes for what features your bot supports (e.g. DM, spaces).

3. **Try It Out**:
   - Go to Google Chat.
   - Start a Direct Message with your App, or add it to a space and mention it (e.g. `@AppName Hello`).
   - The FastAPI server will receive the event, call `process_message()`, and print the sender details, body, and timestamp in the console.

## Customizing Message Logic

To implement your custom agent or bot logic, edit the `kickoff_crew()` function inside [crew.py](file:///Users/albert/CrewAI-GooglesChat/crew.py):
```python
def kickoff_crew(message_text: str, sender_name: str, space_display_name: str) -> str:
    # Your custom CrewAI Agent/Task settings here...
```
