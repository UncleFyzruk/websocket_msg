import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from src.auth.auth import current_user
from src.chat.shemas import AddChatDTO
from src.client_profile.shemas import ProfileModel, ClientProfileGetDTO, UserFriendsDTO, AddFriendDTO
from src.database import get_async_session
from src.client_profile.models import User, FriendshipStatus
from src.database_query.orm import AsyncORM

router = APIRouter(
    tags=["Pages"]
)


@router.get("/profile")
async def get_current_user_profile(session: AsyncSession = Depends(get_async_session),
                                   user: User = Depends(current_user)) -> List[ProfileModel]:
    if user is None:
        raise HTTPException(status_code=500, detail="User not found")
    try:
        result = await AsyncORM.get_user_info(user, session)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


# Получение друзей текущего пользователя
@router.get("/friends") # Декоратор маршрута .get HTTP операция
async def get_friends_current_user(friendship_status: str, session: AsyncSession = Depends(get_async_session),
                                   user: User = Depends(current_user)) -> List[UserFriendsDTO]:
    """
    :param friendship_status:фильтр для получения друзей: friend_request или friend
    :param session: получение сессии для работы с БД
    :param user: получение текущего авторизованного пользователя
    :return: UserFriendsDTO
    """
    if user is None: # если пользователь не авторизован
        raise HTTPException(status_code=500, detail="User not found")
    try:
        result = await AsyncORM.get_friends(user, friendship_status, session)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "Error",
            "data": "Inavalid data",
            "details": None
        })


@router.post("/addfriends")
async def add_friendship_user(friend: AddFriendDTO, session: AsyncSession = Depends(get_async_session),
                                   user: User = Depends(current_user)):
    if user is None:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": "Tvoya mat shlyxa",
            "details": None
        })

    try:
        result = await AsyncORM.add_users_friendship(user.username, friend.sec_username, friend.new_status, session)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": "xyi poimi pochemy",
            "details": None
        })


@router.get("/acceptfriendship")
async def accept_friendship(id_friendship: int, new_status: FriendshipStatus, session: AsyncSession = Depends(get_async_session),
                            user: User = Depends(current_user)):
    try:
        await AsyncORM.change_friend_status(id_friendship, new_status, session)
    except Exception:
        raise HTTPException(status_code=552, detail={
            "status": "error",
            "data": "ERROR_CHANGE_STATUS",
            "details": None
        })
