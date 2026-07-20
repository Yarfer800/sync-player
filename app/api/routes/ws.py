from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket import manager
from app.api.deps import CurrentUserWS, RoomRepoDep, session_factory
from app.repositories import MessageRepository
import json

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/rooms/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    user: CurrentUserWS,
    room_repo: RoomRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        await websocket.close(code=4004, reason="Room not found")
        return

    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue
                
            action = payload.get("action")
            
            if action == "send_message":
                msg_data = payload.get("payload", {})
                text = msg_data.get("text")
                image = msg_data.get("image")
                
                if not text and not image:
                    continue
                    
                async with session_factory() as session:
                    async with session.begin():
                        repo = MessageRepository(session)
                        msg = await repo.create(
                            text=text,
                            image=image,
                            user_id=user.user_id,
                            room_id=room_id,
                        )
                        
                        out_msg = {
                            "type": "new_message",
                            "message": {
                                "id": msg.id,
                                "text": msg.text,
                                "image": msg.image,
                                "user_id": msg.user_id,
                                "username": user.username,
                                "room_id": msg.room_id,
                                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                            }
                        }
                        await manager.broadcast_to_room(room_id, out_msg)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
