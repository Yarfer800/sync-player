from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, RoomRepoDep, ParticipantRepoDep, UserRepoDep, PlayerStateServiceDep
from app.db.models import ParticipantRole
from app.schemas.player_state import PlayerState
from app.schemas.room import (
    RoomCreate, RoomOut, RoomDetail, ParticipantOut,
    RoomJoin, RoomInviteResponse, RoomJoinByInvite
)
import secrets

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomOut])
async def list_rooms(repo: RoomRepoDep):
    rooms = await repo.get_all()
    result = []
    for room in rooms:
        result.append(RoomOut(
            room_id=room.room_id,
            title=room.title,
            content_title=room.content_title,
            created_at=room.created_at,
            participant_count=len(room.participants),
            is_private=bool(room.password),
        ))
    return result


@router.post("", response_model=RoomDetail, status_code=status.HTTP_201_CREATED)
async def create_room(
    body: RoomCreate,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
):
    room = await room_repo.create(
        content_title=body.content_title,
        title=body.title,
        password=body.password,
    )
    await participant_repo.create(
        room_id=room.room_id,
        user_id=user.user_id,
        role=ParticipantRole.OWNER,
    )
    return await _build_room_detail(room_repo, participant_repo, room.room_id)


@router.post("/join/invite", response_model=RoomDetail)
async def join_by_invite(
    body: RoomJoinByInvite,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
    user_repo: UserRepoDep,
):
    room = await room_repo.get_by_invite_code(body.invite_code)
    if not room:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    existing = await participant_repo.get_by_room_and_user(room.room_id, user.user_id)
    if existing:
        raise HTTPException(status_code=409, detail="Already in this room")

    await participant_repo.create(
        room_id=room.room_id,
        user_id=user.user_id,
        role=ParticipantRole.GUEST,
    )
    await user_repo.update(user.id, in_room=room.room_id)

    return await _build_room_detail(room_repo, participant_repo, room.room_id)


@router.get("/{room_id}", response_model=RoomDetail)
async def get_room(
    room_id: int,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return await _build_room_detail(room_repo, participant_repo, room_id)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    participant = await participant_repo.get_by_room_and_user(room_id, user.user_id)
    if not participant or participant.role != ParticipantRole.OWNER:
        raise HTTPException(status_code=403, detail="Only the owner can delete the room")

    await room_repo.delete(room_id)


@router.post("/{room_id}/join", response_model=RoomDetail)
async def join_room(
    room_id: int,
    body: RoomJoin,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
    user_repo: UserRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.password and room.password != body.password:
        raise HTTPException(status_code=403, detail="Invalid password")

    existing = await participant_repo.get_by_room_and_user(room_id, user.user_id)
    if existing:
        raise HTTPException(status_code=409, detail="Already in this room")

    await participant_repo.create(
        room_id=room_id,
        user_id=user.user_id,
        role=ParticipantRole.GUEST,
    )
    await user_repo.update(user.id, in_room=room_id)

    return await _build_room_detail(room_repo, participant_repo, room_id)


@router.post("/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    room_id: int,
    user: CurrentUser,
    participant_repo: ParticipantRepoDep,
    user_repo: UserRepoDep,
):
    removed = await participant_repo.delete_by_room_and_user(room_id, user.user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Not a participant")

    if user.in_room == room_id:
        await user_repo.update(user.id, in_room=None)


@router.post("/{room_id}/invite", response_model=RoomInviteResponse)
async def generate_invite(
    room_id: int,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    participant = await participant_repo.get_by_room_and_user(room_id, user.user_id)
    if not participant or participant.role != ParticipantRole.OWNER:
        raise HTTPException(status_code=403, detail="Only the owner can generate an invite link")

    new_code = secrets.token_urlsafe(16)
    await room_repo.update(room_id, invite_code=new_code)
    return RoomInviteResponse(invite_code=new_code)





@router.get("/{room_id}/participants", response_model=list[ParticipantOut])
async def list_participants(
    room_id: int,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    participants = await participant_repo.get_by_room(room_id)
    return [
        ParticipantOut(
            id=p.id,
            user_id=p.user_id,
            username=p.user.username if p.user else None,
            role=p.role.value,
            joined_at=p.created_at,
        )
        for p in participants
    ]


async def _build_room_detail(room_repo, participant_repo, room_id: int) -> RoomDetail:
    room = await room_repo.get_by_id(room_id)
    participants = await participant_repo.get_by_room(room_id)
    return RoomDetail(
        room_id=room.room_id,
        title=room.title,
        content_title=room.content_title,
        created_at=room.created_at,
        is_private=bool(room.password),
        invite_code=room.invite_code,
        participants=[
            ParticipantOut(
                id=p.id,
                user_id=p.user_id,
                username=p.user.username if p.user else None,
                role=p.role.value,
                joined_at=p.created_at,
            )
            for p in participants
        ],
    )


@router.get("/{room_id}/player/state", response_model=PlayerState)
async def get_player_state(
    room_id: int,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
    player_service: PlayerStateServiceDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participant = await participant_repo.get_by_room_and_user(room_id, user.user_id)
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")

    return await player_service.get_room_state(room_id)


@router.post("/{room_id}/player/state", response_model=PlayerState, status_code=status.HTTP_201_CREATED)
async def create_player_state(
    room_id: int,
    state: PlayerState,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
    player_service: PlayerStateServiceDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participant = await participant_repo.get_by_room_and_user(room_id, user.user_id)
    if not participant or participant.role != ParticipantRole.OWNER:
        raise HTTPException(status_code=403, detail="Only the room owner can create the player state")

    return await player_service.update_room_state(room_id, state)


@router.put("/{room_id}/player/state", response_model=PlayerState)
async def update_player_state(
    room_id: int,
    state: PlayerState,
    user: CurrentUser,
    room_repo: RoomRepoDep,
    participant_repo: ParticipantRepoDep,
    player_service: PlayerStateServiceDep,
):
    room = await room_repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participant = await participant_repo.get_by_room_and_user(room_id, user.user_id)
    if not participant or participant.role != ParticipantRole.OWNER:
        raise HTTPException(status_code=403, detail="Only the room owner can update the player state")

    updated = await player_service.update_room_state(room_id, state)
    
    from app.services.websocket import manager
    await manager.broadcast_to_room(room_id, {
        "type": "player_state_updated",
        "payload": updated.model_dump()
    })
    
    return updated
