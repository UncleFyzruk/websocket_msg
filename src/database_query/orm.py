from pprint import pprint

from fastapi import Depends
from sqlalchemy import select, insert, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from src.chat.models import MessageORM, PrivateChatORM, UsersPrivateChatOrm
from src.chat.shemas import MessageGetDTO, ClientChatPlusGetDTO
from src.client_profile.models import User, FriendsOrm, UsersRelationshipOrm, FriendshipStatus
from src.client_profile.shemas import ClientProfileGetDTO, UserFriendsDTO, UsersChatsDTO
from src.database import get_async_session, async_session_maker


class AsyncORM:
    # Получение информации о пользователе
    @staticmethod # Декоратор "для вызова метода, не требуется экземпляр класса
    async def get_user_info(cur_user: User, session: AsyncSession):
        """
        :param cur_user: пользователь у которого получаем информацию
        :param session: сессия для работы с БД
        :return result_dto: провалидированный кортеж в JSON формат с использованием
        схемы ClientProfileGetDTO
        """
        query = (
            select(User)
            .filter(User.id == cur_user.id)
        )
        result = await session.execute(query)
        result_orm = result.scalars().all()
        result_dto = [ClientProfileGetDTO.model_validate(row, from_attributes=True) for row in result_orm]
        return result_dto

    # Получение списка друзей
    @staticmethod
    async def get_friends(cur_user: User, friendship_status: str, session: AsyncSession):
        if friendship_status == "friend":
            query = (
                select(User)
                .options(
                    selectinload(User.users_friends).
                    selectinload(FriendsOrm.useres_relationship.and_
                                 (UsersRelationshipOrm.user_username != cur_user.username,
                                  UsersRelationshipOrm.status_friendship == friendship_status
                                  ))
                )
                .filter(
                    User.username == cur_user.username
                )
                .filter(
                    and_(
                        UsersRelationshipOrm.status_friendship == friendship_status
                    )

                )
            )
        else:
            check = False
            query = (
                select(User)
                .options(
                    selectinload(User.users_friends).
                    selectinload(FriendsOrm.useres_relationship.and_
                                 (UsersRelationshipOrm.user_username != cur_user.username,
                                  UsersRelationshipOrm.is_initiator != check,
                                  UsersRelationshipOrm.status_friendship == friendship_status
                                  ))
                )
                .filter(
                    User.username == cur_user.username
                )
                .filter(
                    and_(
                        UsersRelationshipOrm.status_friendship == friendship_status,
                        UsersRelationshipOrm.is_initiator == check
                    )

                )
            )
        result = await session.execute(query)
        result_orm = result.scalars().unique().all()
        result_dto = [UserFriendsDTO.model_validate(row, from_attributes=True) for row in result_orm]
        return result_dto

    # Добавление связи между пользователями (добавление друзей)
    @staticmethod
    async def add_users_friendship(f_user: str, s_user: str, status: FriendshipStatus, session: AsyncSession):
        query_user1 = select(User).where(User.username == f_user)
        query_user2 = select(User).where(User.username == s_user)

        user1 = (await session.execute(query_user1)).scalar_one()
        user2 = (await session.execute(query_user2)).scalar_one()

        if user1 is None or user2 is None:
            return {
                "status": "error",
                "data": "error",
                "details": None
            }
        # Проверяем если ли дружба между этими пользователями
        subquery = (
            select(UsersRelationshipOrm.friendship_id)
            .where(UsersRelationshipOrm.user_username == s_user)
        )

        # Основной запрос для проверки наличия дружбы между username1 и любым из friendship_id из подзапроса
        query = (
            select(UsersRelationshipOrm)
            .where(
                and_(
                    UsersRelationshipOrm.user_username == f_user,
                    UsersRelationshipOrm.friendship_id.in_(subquery)
                )
            )
        )


        print(1)
        checking_friendship = await session.execute(query)
        print(2)
        chk_res = checking_friendship.first()
        print(3)
        # print(chk_res[0].id_friendship)
        if chk_res is not None:
            return {
                "status": "error",
                "data": "error",
                "details": None
            }
        friendship = FriendsOrm()

        session.add(friendship)
        await session.commit()

        f_user_relationship = UsersRelationshipOrm(
            friendship_id=friendship.id_friendship,
            user_username=f_user,
            status_friendship=status,
            is_initiator=True
        )

        s_user_relationship = UsersRelationshipOrm(
            friendship_id=friendship.id_friendship,
            user_username=s_user,
            status_friendship=status,
            is_initiator=False
        )

        session.add_all([f_user_relationship, s_user_relationship])
        await session.commit()
        return {
            "status": "successfully",
            "data": "successfully",
            "details": None
        }

    @staticmethod
    async def change_friend_status(id_friendship: int, new_status: FriendshipStatus, session:AsyncSession):
        stmt = (
            update(UsersRelationshipOrm)
            .filter(UsersRelationshipOrm.friendship_id == id_friendship)
            .values(status_friendship=new_status)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.commit()

    # Получаем историю диалога\чата
    @staticmethod
    async def get_dialog_history(chat_id: int, session: AsyncSession, offset: int = 0, limit: int = 10):
        """
        :param limit:
        :param offset:
        :param chat_id: ID чата из которого получаем записи
        :param session: Сессия для обращения к бд
        :return: данные в формате MessageGetDTO
        """
        user_id = "1; DROP TABLE users CASCADE;" # SQL-вредоносная SQL-инъекция
        query = f"SELECT * FROM users WHERE id = {user_id}" # Тело запроса к бд

        query = (
            select(
                MessageORM
            )
            .filter(MessageORM.chat_id == chat_id)
            .order_by(MessageORM.message_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        result_orm = result.scalars().all()
        result_orm = list(reversed(result_orm))
        result_dto = [MessageGetDTO.model_validate(row, from_attributes=True) for row in result_orm]
        return result_dto

    @staticmethod
    async def get_chatsPlus(initiator: str, session: AsyncSession):
        """

        :param initiator:
        :param session:
        :return:
        """

        subq = (
            select(UsersPrivateChatOrm.chat_id)
            .filter(UsersPrivateChatOrm.user_username == initiator)
            .subquery()
        )
        query = (
            select(User.username, UsersPrivateChatOrm.chat_id, PrivateChatORM.created_at)
            .join(UsersPrivateChatOrm, User.username == UsersPrivateChatOrm.user_username)
            .join(PrivateChatORM, UsersPrivateChatOrm.chat_id == PrivateChatORM.chat_id)
            .filter(UsersPrivateChatOrm.chat_id.in_(select(subq.c.chat_id)))
            .filter(User.username != initiator)
        )

        result_orm = (await session.execute(query)).all()
        result_dto = [ClientChatPlusGetDTO(user_username=row[0], chat_id=row[1], created_at=row[2]) for row in
                      result_orm]
        return result_dto

    # Получаем чаты пользователя
    @staticmethod
    async def get_chats(initiator: str, session: AsyncSession):
        """

        :param initiator:
        :param session:
        :return:
        """
        query = (
            select(User)
            .options(selectinload(User.user_chat))
            .filter(User.username == initiator)
        )

        result_orm = (await session.execute(query)).scalars().all()
        result_dto = [UsersChatsDTO.model_validate(row, from_attributes=True) for row in result_orm]
        return result_dto

    # Создание чата между двумя пользователями
    @staticmethod
    async def add_chat(f_user: str, s_user: str, session: AsyncSession):
        """
        Надо будет добавить проверку на состояние дружбы
        """
        UserChat1 = aliased(UsersPrivateChatOrm)
        UserChat2 = aliased(UsersPrivateChatOrm)

        query = (
            select(PrivateChatORM)
            .join(UserChat1, UserChat1.chat_id == PrivateChatORM.chat_id)
            .join(UserChat2, UserChat2.chat_id == PrivateChatORM.chat_id)
            .filter(
                and_(
                    UserChat1.user_username == f_user,
                    UserChat2.user_username == s_user
                )
            )
        )

        chat_exists = await session.execute(query)
        chat_exists = chat_exists.scalar_one_or_none()
        if chat_exists:
            return {
                "status": "neponyatno",
                "data": "Chat yje est",
                "details": None
            }

        new_chat = PrivateChatORM()
        session.add(new_chat)
        await session.flush()

        f_user_chat = UsersPrivateChatOrm(
            chat_id=new_chat.chat_id,
            user_username=f_user
        )

        s_user_chat = UsersPrivateChatOrm(
            chat_id=new_chat.chat_id,
            user_username=s_user
        )

        session.add_all([f_user_chat, s_user_chat])
        await session.commit()
        return {
            "status": "successfully",
            "data": "successfully",
            "details": None
        }

    # Добавление сообщения в БД
    @staticmethod
    async def add_message(text_message: str, initiator: str, chat_id: int):
        async with async_session_maker() as session:
            message = MessageORM(
                chat_id=chat_id,
                text_message=text_message,
                username_sender=initiator
            )
            session.add(message)
            await session.commit()
