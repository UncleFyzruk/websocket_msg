import datetime
import uuid

from pydantic import BaseModel

from src.chat.shemas import ClientChatGetDTO
from src.client_profile.models import FriendshipStatus


class ShortProfileModel(BaseModel):
    username: str


class ProfileModel(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    avatar: str
    registered_at: datetime.datetime

    class Config:
        orm_mode = True


class FriendAddDTO(BaseModel):
    friend_username: str
    status_friendship: FriendshipStatus


class UsersRelationshipGetDTO(BaseModel):
    user_username: str

    status_friendship: FriendshipStatus
    is_initiator: bool


class FriendGetDTO(BaseModel):
    id_friendship: int
    friendship_at: datetime.datetime
    useres_relationship: list["UsersRelationshipGetDTO"]


#DTO - data transfer object
class ClientProfilePostDTO(BaseModel):
    id: uuid.UUID
    username: str
    email: str

class ClientProfileGetDTO(ClientProfilePostDTO):
    avatar: str
    registered_at: datetime.datetime


class UserFriendsDTO(ClientProfilePostDTO):
    users_friends: list["FriendGetDTO"]


class AddFriendDTO(BaseModel):
    sec_username: str
    new_status: FriendshipStatus


class UsersChatsDTO(ClientProfilePostDTO):
    user_chat: list["ClientChatGetDTO"]