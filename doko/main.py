from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Request, HTTPException
from starlette import status

from doko import settings, statics, router, db, orm, logging
from doko.libs import password_utils
from doko.http_exception import exception_handlers

app = FastAPI(title="Doko", exception_handlers=exception_handlers)
app.mount(path=statics.PATH, app=statics.statics(), name=statics.NAME)
app.include_router(router=router.router)


async def authentication(session: AsyncSession, session_token: str | None) -> tuple[bool, str]:
    """
    Returns if the session_token is valid and a string with a description why in case of False or an empty
    string in case of True.
    """

    if session_token is None:
        return (False, "No 🍪")
    try:
        user = await orm.User.from_session_token(session, session_token=session_token)
    except LookupError:
        return (False, "Unknown 🍪")
    if await user.is_expired():
        return (False, "Expired 🍪")
    return (True, "")


@app.on_event("startup")
async def init_models() -> None:
    from doko.orm import Crud

    async with db.engine().begin() as conn:
        if settings.RESET_DB_ON_STARTUP:
            await conn.run_sync(Crud.metadata.drop_all)
        await conn.run_sync(Crud.metadata.create_all)

    from asyncio import sleep

    await sleep(1)

    if settings.DB_TEST_SETUP:
        async with db.get_session() as session:
            await test_setup(session)


@lru_cache(maxsize=100)
def login_required(path: str) -> bool:
    """Check if the route needs login"""
    # todo: these should be defined elsewhere. We might also need url parsing à la urllib

    always_accessible_routes = (
        "/registration",
        "/register",
        "/login",
        "/statics",
        "/favicon",
    )

    wildcard_404 = "/{_:path}"
    routes = [route.path for route in app.routes if route.path != wildcard_404]

    if path in routes:
        no_login_required = (path == "/") or path.startswith(always_accessible_routes)
        return not no_login_required
    return False


@app.middleware("http")
async def middleware(request: Request, call_next):
    """
    Middlewhere:
      * Authorization: Check if there is a valid cookie set for authorization. Else return a 401 error page.

    ### Authentication:
    * Registration + login and a session token in a cookie
    * passwords get onewayhashed with bcrypt
    * 64 bit session tokens get generated with the python secrets buildin
    """

    if login_required(request.url.path):
        session_token: str | None = request.cookies.get("session_token")

        async with db.get_session() as session:
            is_authenticated, detail = await authentication(session=session, session_token=session_token)

        if not is_authenticated:
            response = exception_handlers[status.HTTP_401_UNAUTHORIZED](
                request=request,
                exc=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail),
            )
            return response

    response = await call_next(request)
    return response


async def test_setup(session: AsyncSession) -> None:
    user_rene = orm.User(name="rene", password=password_utils.hash_password("123456789"))
    user_simon = orm.User(name="simon", password=password_utils.hash_password("123456789"))
    user_nadiem = orm.User(name="nadiem", password=password_utils.hash_password("123456789"))
    user_florian = orm.User(name="florian", password=password_utils.hash_password("123456789"))
    user_david = orm.User(name="david", password=password_utils.hash_password("123456789"))

    session.add_all([user_rene, user_nadiem, user_florian, user_simon, user_david])
    await session.commit()

    group_1 = orm.Group(name="waargh", users=[user_rene, user_nadiem, user_florian, user_simon])
    group_2 = orm.Group(name="da_wargh", users=[user_rene, user_nadiem, user_florian, user_david])

    session.add_all([group_1, group_2])
    await session.commit()
    logging.info("Database test-setup initialized")


if __name__ == "__main__":
    import uvicorn

    config = uvicorn.Config("main:app", log_level="info")
    server = uvicorn.Server(config)
    server.run()
