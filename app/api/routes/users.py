from fastapi import APIRouter

from app.api.deps import CurrentUser, UserRepoDep
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    user: CurrentUser,
    repo: UserRepoDep,
):
    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        updated = await repo.update(user.id, **update_data)
        return updated
    return user
