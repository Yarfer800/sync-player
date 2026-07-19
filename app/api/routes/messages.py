from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, MessageRepoDep, RoomRepoDep
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/rooms/{room_id}/messages", tags=["messages"])


@router.get("", response_model=list[MessageOut])
async def list_messages(
    room_id: int,
    repo: MessageRepoDep,
    room_repo: RoomRepoDep,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    messages = await repo.get_by_room(room_id, limit=limit, offset=offset)
    return [
        MessageOut(
            id=m.id,
            text=m.text,
            image=m.image,
            user_id=m.user_id,
            username=m.user.username if m.user else None,
            room_id=m.room_id,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("", response_model=MessageOut, status_code=201)
async def send_message(
    room_id: int,
    body: MessageCreate,
    user: CurrentUser,
    repo: MessageRepoDep,
    room_repo: RoomRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    msg = await repo.create(
        text=body.text,
        image=body.image,
        user_id=user.user_id,
        room_id=room_id,
    )
    return MessageOut(
        id=msg.id,
        text=msg.text,
        image=msg.image,
        user_id=msg.user_id,
        username=user.username,
        room_id=msg.room_id,
        created_at=msg.created_at,
    )


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    room_id: int,
    message_id: int,
    user: CurrentUser,
    repo: MessageRepoDep,
):
    msg = await repo.get_by_id(message_id)
    if not msg or msg.room_id != room_id:
        raise HTTPException(status_code=404, detail="Message not found")

    if msg.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Can only delete your own messages")

    await repo.delete(message_id)
