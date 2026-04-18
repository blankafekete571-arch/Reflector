import requests

BASE_URL = "http://localhost:8000"

# Create session
response = requests.post(f"{BASE_URL}/sessions")
session = response.json()
session_id = session["session_id"]

print(session["assistant_response"])

# Submit response
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/respond",
    json={"user_input": "I had a difficult conversation."}
)
print(response.json()["assistant_response"])

# End and save
requests.delete(f"{BASE_URL}/sessions/{session_id}?save=true")