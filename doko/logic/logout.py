""""""
from sqlalchemy.ext.asyncio import AsyncSession

from doko import orm


async def logout(session_token: str, session: AsyncSession) -> None:
    user = await orm.User.from_session_token(session_token=session_token, session=session)
    await user.expire_session(session=session)
