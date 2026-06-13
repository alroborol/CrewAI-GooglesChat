import os
import logging
import json
import time
import base64
import urllib.request
import urllib.parse
import uvicorn
from fastapi import FastAPI, Request, Response, status
from pyasn1.codec.der import decoder
import rsa

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Google Chat Webhook")

# Configuration constants
SCOPES = ["https://www.googleapis.com/auth/chat.bot"]
SERVICE_ACCOUNT_FILE = "service-account.json"

def pkcs8_to_pkcs1(pem_str: str) -> bytes:
    """
    Extracts the PKCS#1 private key DER bytes from a PKCS#8 PEM string.
    Necessary because the pure-python 'rsa' library only supports PKCS#1 format.
    """
    lines = pem_str.strip().splitlines()
    body = "".join(l for l in lines if not l.startswith("---"))
    der_bytes = base64.b64decode(body)
    
    # Decode PKCS#8 DER structure
    asn1_structure, _ = decoder.decode(der_bytes)
    # The private key bytes are stored as an OCTET STRING at index 2
    private_key_octets = asn1_structure[2].asOctets()
    return private_key_octets

def get_access_token() -> str:
    """
    Exchanges the service account credentials for a Google OAuth2 access token.
    Uses pure Python (rsa, pyasn1, and urllib).
    """
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        logger.warning(
            f"Service account file '{SERVICE_ACCOUNT_FILE}' not found. "
            "Asynchronous message sending will be unavailable."
        )
        return ""

    try:
        with open(SERVICE_ACCOUNT_FILE, "r") as f:
            sa_data = json.load(f)

        client_email = sa_data["client_email"]
        private_key_pem = sa_data["private_key"]
        
        # 1. Convert private key from PKCS#8 to PKCS#1
        pkcs1_der = pkcs8_to_pkcs1(private_key_pem)
        priv_key = rsa.PrivateKey.load_pkcs1(pkcs1_der, format='DER')

        # 2. Build JWT Header and Claims
        header = {"alg": "RS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")

        now = int(time.time())
        claims = {
            "iss": client_email,
            "scope": " ".join(SCOPES),
            "aud": "https://oauth2.googleapis.com/token",
            "exp": now + 3600,
            "iat": now
        }
        claims_b64 = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")

        # 3. Sign the JWT using RS256
        signing_input = f"{header_b64}.{claims_b64}".encode()
        signature = rsa.sign(signing_input, priv_key, 'SHA-256')
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        jwt_token = f"{header_b64}.{claims_b64}.{signature_b64}"

        # 4. Exchange JWT for access token
        url = "https://oauth2.googleapis.com/token"
        data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            return resp_data.get("access_token", "")

    except Exception as e:
        logger.error(f"Failed to acquire OAuth2 access token: {e}")
        return ""

def send_message_asynchronously(space_name: str, text: str) -> dict:
    """
    Sends a message asynchronously using Google Chat REST API and standard urllib.
    
    Args:
        space_name (str): The unique space resource name (e.g., 'spaces/AAAAAA').
        text (str): The text message to send.
        
    Returns:
        dict: The API response payload from Google Chat.
    """
    access_token = get_access_token()
    if not access_token:
        logger.error("Cannot send message: Failed to acquire access token.")
        return {}

    url = f"https://chat.googleapis.com/v1/{space_name}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    payload = {"text": text}
    data = json.dumps(payload).encode("utf-8")

    try:
        logger.info(f"Sending async message to space '{space_name}'...")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            logger.info("Message sent successfully.")
            return resp_data
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP Error sending message: {e.code} - {e.read().decode('utf-8')}")
        return {}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {}

def process_message(text: str, sender: str, space_name: str, space_display_name: str, timestamp: str) -> str:
    """
    Dummy message processor. Implement your custom bot logic here.
    
    Args:
        text (str): The body of the message.
        sender (str): The display name of the message sender.
        space_name (str): The unique resource name of the chat group/space.
        space_display_name (str): The user-friendly display name of the space.
        timestamp (str): The ISO timestamp when the message was created.
        
    Returns:
        str: The reply text to send back to Google Chat.
    """
    logger.info("--- Processing Message ---")
    logger.info(f"Sender: {sender}")
    logger.info(f"Message Body: {text}")
    logger.info(f"Space/Group: {space_display_name} ({space_name})")
    logger.info(f"Timestamp: {timestamp}")
    logger.info("--------------------------")
    
    # Example: How to send a message asynchronously using the service account connector:
    # (Only runs if service-account.json is present)
    # if os.path.exists(SERVICE_ACCOUNT_FILE):
    #     send_message_asynchronously(space_name, f"Async confirmation to {sender}")

    # Synchronous reply returned directly in response to the webhook call
    reply = f"Hello {sender}! I received your message: '{text}' in space '{space_display_name}'."
    return reply

@app.post("/webhook")
async def webhook(request: Request, response: Response):
    """
    Endpoint that receives events from Google Chat.
    """
    try:
        event = await request.json()
    except Exception as e:
        logger.warning(f"Failed to parse JSON: {e}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Invalid or missing JSON payload"}

    event_type = event.get('type')
    logger.info(f"Received Google Chat event of type: {event_type}")

    # Default reply if we don't have a message or greeting
    reply_text = None

    if event_type == 'ADDED_TO_SPACE':
        # When bot is added to a space (DM or Room)
        space_display_name = event.get('space', {}).get('displayName', 'this space')
        reply_text = f"Thanks for adding me to {space_display_name}!"
        logger.info(f"Bot added to space: {space_display_name}")

    elif event_type == 'MESSAGE':
        # Extract message metadata
        message = event.get('message', {})
        text = message.get('text', '')
        sender = message.get('sender', {}).get('displayName', 'Unknown Sender')
        space = event.get('space', {})
        space_name = space.get('name', 'Unknown Space')
        space_display_name = space.get('displayName', 'Direct Message')
        timestamp = message.get('createTime', event.get('eventTime'))

        # Pass message details to the processing function
        reply_text = process_message(
            text=text,
            sender=sender,
            space_name=space_name,
            space_display_name=space_display_name,
            timestamp=timestamp
        )

    # Return synchronous response format expected by Google Chat
    if reply_text:
        return {"text": reply_text}
    
    # Return empty response if no message was processed (e.g., REMOVED_FROM_SPACE)
    response.status_code = status.HTTP_204_NO_CONTENT
    return Response()

if __name__ == '__main__':
    # Run server on port 5001 (or set via environment variable)
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Google Chat Webhook Server on port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
