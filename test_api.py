import subprocess
import time
import requests

server = subprocess.Popen(["uvicorn", "app:api"], cwd="/media/ankit-ambasta/52545BAE545B9417/DocumentRag")

time.sleep(5)

try:
    response = requests.post("http://localhost:8000/query", json={"question": "what is the first aid procedure for a snake bite?", "session_id": "test_03"})
    print("STATUS:", response.status_code)
    try:
        print("RESPONSE:", response.json())
    except:
        print("RESPONSE TEXT:", response.text)
except Exception as e:
    print("ERROR:", e)

server.terminate()
