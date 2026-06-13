# Google Chat Webhook Server in Python (FastAPI)

This project provides a minimal HTTP webhook server to receive and respond to Google Chat events using Python and FastAPI.

## File Structure

- [app.py](file:///Users/albert/CrewAI-GooglesChat/app.py): The FastAPI server defining the `/webhook` endpoint and the message processing function.
- [test_webhook.py](file:///Users/albert/CrewAI-GooglesChat/test_webhook.py): Local test runner to simulate Google Chat payloads and verify responses.
- [requirements.txt](file:///Users/albert/CrewAI-GooglesChat/requirements.txt): List of Python dependencies (FastAPI, Uvicorn).

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

To implement your actual logic, edit the `process_message()` function inside [app.py](file:///Users/albert/CrewAI-GooglesChat/app.py#L9-L29):
```python
def process_message(text: str, sender: str, space_name: str, space_display_name: str, timestamp: str) -> str:
    # Your custom logic here...
    return "Your custom reply message"
```
