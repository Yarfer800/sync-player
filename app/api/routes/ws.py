from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket import manager
from app.api.deps import CurrentUserWS, RoomRepoDep, session_factory
from app.repositories import MessageRepository
from app.repositories.player_state import PlayerStateRepository
from app.db.redis import redis_client
import json

router = APIRouter(prefix="/ws", tags=["websocket"])

async def handle_send_message(payload: dict, room_id: int, user: CurrentUserWS):
    msg_data = payload.get("payload", {})
    text = msg_data.get("text")
    image = msg_data.get("image")
    
    if not text and not image:
        return
        
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


async def handle_check_desync(payload: dict, room_id: int, websocket: WebSocket):
    msg_data = payload.get("payload", {})
    timecode = msg_data.get("timecode")
    if timecode is not None:
        try:
            timecode = float(timecode)
        except ValueError:
            return
        
        repo = PlayerStateRepository(redis_client)
        state = await repo.get_state(room_id)
        room_timecode = state.current_timecode if state else 0.0
        desync = timecode - room_timecode
        
        out_msg = {
            "type": "desync_result",
            "payload": {
                "desync_seconds": desync,
                "room_timecode": room_timecode
            }
        }
        await manager.send_personal_message(out_msg, websocket)


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
                await handle_send_message(payload, room_id, user)
            elif action == "check_desync":
                await handle_check_desync(payload, room_id, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
