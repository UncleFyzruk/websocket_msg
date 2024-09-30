import json
from typing import List, Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi_users.manager import UserManagerDependency
from src.auth.auth import current_user, auth_backend
from src.auth.userManager import get_user_manager
from src.chat.models import PrivateChatORM
from src.chat.shemas import ClientChatGetDTO, MessageGetDTO, ClientChatPlusGetDTO, AddChatDTO
from src.client_profile.models import User
from src.client_profile.shemas import UsersChatsDTO
from src.database import get_async_session
from src.database_query.orm import AsyncORM
from src.pages.router import templates

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


# менеджер веб-сокет соединений
class ConnectionManager:

    # инициализация атрибутов
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    # Принимает соединение и добавляет в словарь
    async def connect(self, client_username: str, websocket: WebSocket):
        """
        :param client_username: имя пользователя кто инициировал запрос на вебсокет соединение
        :param websocket: объект вебсокета с кем произошло соединение
        """
        await websocket.accept() # посылает клиенту сигнал, что соединение установлено
        self.active_connections[client_username] = websocket
        print(self.active_connections[client_username], "Connected")

    # Выключение веб-сокет соединения
    def disconnect(self, client_username: str):
        """
        :param client_username: имя клиента, кто отключился от веб-сокета
        """
        del self.active_connections[client_username]

    # Отправка сообщения другому пользователю
    async def send_personal_message(self, data: dict, add_to_db: bool):
        """
        :param data: необходимая информация
        :param add_to_db: если False- то сообщение не сохраняется в БД
        """
        message = data['message'] # Текст сообщения
        sender = data['client_username'] # Имя отправителя сообщения
        target = data['dest_username'] # Имя Кому отправлено
        chat_id = data['chat_id']  # К какому чату принадлежит сообщение
        if add_to_db:
            await AsyncORM.add_message(message, sender, chat_id)
        if target in self.active_connections:
            data_json = json.dumps(data)
            await self.active_connections[target].send_text(data_json)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("messages")
    return token


@router.get("/history", response_model=List[MessageGetDTO])
async def get_dialog_history(chat_id: int, offset: int, limit: int, session: AsyncSession = Depends(get_async_session),
                             user: User = Depends(current_user)):

    result = await AsyncORM.get_dialog_history(chat_id, session, offset, limit)

    return result


# Получение чатов пользователя
@router.get("/getChat", response_model=Optional[List[UsersChatsDTO]])
async def get_all_chat_current_user(session: AsyncSession = Depends(get_async_session),
                                    user: User = Depends(current_user)):
    if user is None:
        raise HTTPException(status_code=500, detail="User not found")
    result = await AsyncORM.get_chats(user.username, session)
    return result


# Получение чатов пользователя
@router.get("/getChatPlus") # декоратор
async def get_all_chat_current_user(session: AsyncSession = Depends(get_async_session),
                                    user: User = Depends(current_user)):
    """
    :param session: получение сессии для работы с БД
    :param user: получение данных текущего пользователя
    :return: ClientChatPlusGetDTO
    """
    if user is None:
        raise HTTPException(status_code=500, detail="User not found")
    result = await AsyncORM.get_chatsPlus(user.username, session) # асинхронный запрос к БД
    return result


@router.post("/createChat")
async def add_private_chat(sec_username: AddChatDTO, session: AsyncSession = Depends(get_async_session),
                           user: User = Depends(current_user)):
    if user is None:
        return {
            "status": "NonAuthorized",
            "data": "Sosi",
            "details": None
        }
    result = await AsyncORM.add_chat(user.username, sec_username.sec_username, session)
    return result


# Создание веб-сокет соединения
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_username: str):
    """
    :param websocket: веб-сокет инициатора
    :param client_username: имя того, кто инициировал соединение
    """
    await manager.connect(client_username, websocket) # принимаем соединение
    try:
        while True: # бесконечно прослушиваем сообщения
            data_json = await websocket.receive_text() # Ожидание сообщения
            data = json.loads(data_json) # Преобразование JSON в dict
            await manager.send_personal_message(data, add_to_db=True)

    except WebSocketDisconnect: # При обрыве вебсокет соединения
        manager.disconnect(client_username)
