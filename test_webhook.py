import urllib.request
import json
import sys

def send_mock_event(payload, description):
    url = "http://127.0.0.1:5001/webhook"
    headers = {"Content-Type": "application/json"}
    
    print(f"\n--- Testing: {description} ---")
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            response_code = response.getcode()
            response_body = response.read().decode('utf-8')
            print(f"Status Code: {response_code}")
            if response_body:
                parsed_res = json.loads(response_body)
                print(f"Response JSON: {json.dumps(parsed_res, indent=2)}")
            else:
                print("Empty Response Body")
    except urllib.error.URLError as e:
        print(f"Error connecting to webhook server: {e}")
        print("Please ensure the Flask app is running (e.g., via python3 app.py)")
        sys.exit(1)

if __name__ == "__main__":
    # Test Case 1: MESSAGE event
    message_payload = {
        "type": "MESSAGE",
        "eventTime": "2026-06-13T12:00:00Z",
        "space": {
            "name": "spaces/test_room_123",
            "displayName": "Engineering Team Chat"
        },
        "message": {
            "text": "Calculate 2 + 2",
            "sender": {
                "displayName": "Alice Smith"
            },
            "createTime": "2026-06-13T12:00:00Z"
        }
    }
    send_mock_event(message_payload, "Incoming MESSAGE event")

    # Test Case 2: ADDED_TO_SPACE event
    added_payload = {
        "type": "ADDED_TO_SPACE",
        "eventTime": "2026-06-13T12:01:00Z",
        "space": {
            "name": "spaces/test_room_123",
            "displayName": "Engineering Team Chat"
        }
    }
    send_mock_event(added_payload, "Incoming ADDED_TO_SPACE event")
