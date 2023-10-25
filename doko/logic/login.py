""""""
from sqlalchemy.ext.asyncio import AsyncSession

from doko import request_dto, response_dto, orm, exception


async def state(session_token: str | None, session: AsyncSession) -> response_dto.Login:
    is_authenticated = await orm.User.is_authenticated(session=session, session_token=session_token)
    if is_authenticated:
        raise exception.AlreadyAuthenticated()
    obj = response_dto.Login()
    return obj


async def login(data: request_dto.Login, session: AsyncSession) -> response_dto.Login | orm.Cookie:
    try:
        user: orm.User = await orm.User.from_login(session=session, username=data.username, password=data.password)
    except (exception.InvalidPassword, exception.InvalidUsername):
        obj = response_dto.Login(failure=True)
        return obj
    cookie = await user.cookie()
    return cookie
