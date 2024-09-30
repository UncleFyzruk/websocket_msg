from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from src.auth.auth import current_user
from src.client_profile.models import User

"""
Этот файл нужен для добавления теймплейтов
"""


router = APIRouter(
    tags=["Pages"]
)

templates = Jinja2Templates(directory="src/templates")


@router.get("/")
def get_base_pages(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


# @router.get("/chat")
# def get_chat_pages(request: Request):
#     return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/aut")
def post_login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

# @router.get("/profile")
# async def get_profile_pages(request: Request,
#                       user: User = Depends(current_user)):
#     print(user.id)
#     profile_data = await get_current_user_profile(),
#     if user is None:
#         return RedirectResponse("/")
#     else:
#         return templates.TemplateResponse("profile.html", {"request": request, "profile_data": profile_data})
