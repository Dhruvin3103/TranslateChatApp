from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from easygoogletranslate import EasyGoogleTranslate

app = FastAPI()


# Dictionary to store connected WebSocket clients and their language preferences
connected_users = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def translate_mess(mess, src, trg):
    translator = EasyGoogleTranslate(
        source_language=src,
        target_language=trg,
    )
    result = translator.translate(mess)
    print(f"Translated from {src} to {trg}: {result}")
    return result

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(user_id: str, websocket: WebSocket):
    await websocket.accept()
    
    # Get the user's preferred language
    lang_data = await websocket.receive_text()
    user_lang = json.loads(lang_data)['language']
    
    connected_users[user_id] = {"websocket": websocket, "language": user_lang}
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Add the sender's user_id to the message data
            message_data['sender_id'] = user_id
            
            # Translate and send the message to all other users
            for other_user_id, user_info in connected_users.items():
                if other_user_id != user_id:
                    target_lang = user_info['language']
                    translated_content = translate_mess(message_data['content'], message_data['language'], target_lang)
                    translated_message = {
                        'sender_id': message_data['sender_id'],
                        'name': message_data['name'],
                        'content': translated_content,
                        'original_language': message_data['language'],
                        'translated_language': target_lang
                    }
                    await user_info['websocket'].send_text(json.dumps(translated_message))
    except WebSocketDisconnect:
        del connected_users[user_id]
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)