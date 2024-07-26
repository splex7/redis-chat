from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from redis import Redis
import asyncio
import json

app = FastAPI()
redis = Redis(host='localhost', port=6379, db=0)

connected_clients = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    connected_clients[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            recipient_id = message["recipient_id"]
            if recipient_id in connected_clients:
                await connected_clients[recipient_id].send_text(data)
            redis.publish("chat", data)
    except WebSocketDisconnect:
        del connected_clients[user_id]
        await websocket.close()

async def redis_listener():
    pubsub = redis.pubsub()
    pubsub.subscribe("chat")
    while True:
        message = pubsub.get_message()
        if message:
            data = json.loads(message['data'])
            for user_id, websocket in connected_clients.items():
                await websocket.send_text(data)
        await asyncio.sleep(0.01)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(redis_listener())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
