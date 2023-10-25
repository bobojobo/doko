""""""
from sqlalchemy.ext.asyncio import AsyncSession

from doko import request_dto, response_dto, orm, exception, logging


async def state(data: request_dto.GroupCreate, session: AsyncSession, session_token: str) -> response_dto.GroupCreate:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    obj = response_dto.GroupCreate(
        username=user.name,
        users=[
            response_dto._GroupCreatePartialUsername(
                number=0, name=data.username_0, exists=True, is_the_user=False, is_already_used=False
            ),
            response_dto._GroupCreatePartialUsername(
                number=1, name=data.username_1, exists=True, is_the_user=False, is_already_used=False
            ),
            response_dto._GroupCreatePartialUsername(
                number=2, name=data.username_2, exists=True, is_the_user=False, is_already_used=False
            ),
        ],
    )
    return obj


async def groupname(
    data: request_dto.GroupCreateGroupname,
    session: AsyncSession,
    session_token: str,
) -> response_dto.GroupCreatePartialGroupname:
    # todo: make regex and whatnot.. on pydantic!
    assert data.groupname not in ["", None], "Invalid Groupname"
    groupname_is_available = await orm.Group.name_is_available(name=data.groupname, session=session)
    obj = response_dto.GroupCreatePartialGroupname(
        groupname_is_taken=not groupname_is_available,
        groupname=data.groupname,
    )
    return obj


async def playername(
    data: request_dto.GroupCreateUsername,
    session: AsyncSession,
    session_token: str,
) -> response_dto.GroupCreatePartialUsername:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    try:
        user_0 = await orm.User.from_name(session=session, name=data.username_0)
    except LookupError:
        user_0 = None
    try:
        user_1 = await orm.User.from_name(session=session, name=data.username_1)
    except LookupError:
        user_1 = None
    try:
        user_2 = await orm.User.from_name(session=session, name=data.username_2)
    except LookupError:
        user_2 = None

    username: str = ""
    others: list[orm.User | None] = []
    if data.player_number == "0":
        username = data.username_0
        others = [user_1, user_2]
    elif data.player_number == "1":
        username = data.username_1
        others = [user_0, user_2]
    elif data.player_number == "2":
        username = data.username_2
        others = [user_0, user_1]
    else:
        raise Exception("invalid player_number")

    try:
        other_user = await orm.User.from_name(session=session, name=username)
        other_user_exists = True
    except LookupError:
        other_user_exists = False
    if other_user_exists:
        user_is_self = user is other_user
        other_user_is_already_used = other_user in others
    else:
        user_is_self = False
        other_user_is_already_used = False

    obj = response_dto.GroupCreatePartialUsername(
        user=response_dto._GroupCreatePartialUsername(
            name=username,
            number=int(data.player_number),
            exists=other_user_exists,
            is_the_user=user_is_self,
            is_already_used=other_user_is_already_used,
        ),
    )

    return obj


async def create(data: request_dto.GroupCreate, session: AsyncSession, session_token: str) -> None:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    assert len(set([user, data.username_0, data.username_1, data.username_2])) == 4, "Need 4 unique players"
    groupname_is_available = await orm.Group.name_is_available(name=data.groupname, session=session)
    assert groupname_is_available, f"{data.groupname} is already taken"

    user_0 = await orm.User.from_name(session=session, name=data.username_0)
    user_1 = await orm.User.from_name(session=session, name=data.username_1)
    user_2 = await orm.User.from_name(session=session, name=data.username_2)

    assert user_0 is not None, f"{data.username_0} does not exist"
    assert user_1 is not None, f"{data.username_1} does not exist"
    assert user_2 is not None, f"{data.username_2} does not exist"

    new_group = orm.Group(name=data.groupname, users=[user, user_0, user_1, user_2])
    session.add(new_group)
    await session.commit()
    logging.info(f"New group created: {new_group.name}")
