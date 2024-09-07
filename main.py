from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Dictionary to store connected WebSocket clients
connected_users = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(user_id: str, websocket: WebSocket):
    await websocket.accept()
    # Store the WebSocket connection in the dictionary
    connected_users[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Parse the received data as JSON
            message_data = json.loads(data)
            
            # Add the sender's user_id to the message data
            message_data['sender_id'] = user_id
            
            # Send the received data to all other users
            for other_user_id, user_ws in connected_users.items():
                if other_user_id != user_id:
                    await user_ws.send_text(json.dumps(message_data))
    except WebSocketDisconnect:
        # If a user disconnects, remove them from the dictionary
        del connected_users[user_id]
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)