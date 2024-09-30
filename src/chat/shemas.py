import datetime

from pydantic import BaseModel


class MessageAddDTO(BaseModel):
    chat_id: int
    username_sender: str
    text_message: str


class MessageGetDTO(MessageAddDTO):
    id_message: int
    message_at: datetime.datetime


#DTO - data transfer object

class ClientChatGetDTO(BaseModel):
    chat_id: int
    created_at: datetime.datetime

class ClientChatPlusGetDTO(BaseModel):
    user_username: str
    chat_id: int
    created_at: datetime.datetime


class AddChatDTO(BaseModel):
    sec_username: str

