""""""
from sqlalchemy.ext.asyncio import AsyncSession

from doko import request_dto, response_dto, orm


# async def get_selected_group(user: orm.User, group_name: str, session: AsyncSession) -> orm.Group | None:
#    """
#    Selected group > active group > first group in the list > None
#    """
#
#    # todo: assert first to check if group is a group of the user?
#    selected_group = await get_group(session, name=group_name)
#    if selected_group is None:
#        logging.debug("Selected Group is active group")
#        selected_group = user.active_group
#    if selected_group is None:
#        logging.debug("Selected Group is None")
#        selected_group = await get_first_group(user)
#    return selected_group


async def state(data: request_dto.Group, session: AsyncSession, session_token: str) -> response_dto.Group:
    user = await orm.User.from_session_token(session, session_token=session_token)
    groups = await user.get_sorted_groups()
    if data.groupname == "":
        usernames = ["", "", "", ""]
    else:
        selected_group = await orm.Group.from_name(name=data.groupname, session=session)
        selected_group_users = await selected_group.get_sorted_users()
        usernames = [selected_group_user.name for selected_group_user in selected_group_users]

    obj = response_dto.Group(
        playernames=usernames,
        username=user.name,
        has_groups=len(groups) > 0,
        groupnames=[group.name for group in groups],
    )

    return obj


async def groups(session: AsyncSession, session_token: str) -> response_dto.GroupPartialGroups:
    user = await orm.User.from_session_token(session, session_token=session_token)
    groups = await user.get_sorted_groups()

    obj = response_dto.GroupPartialGroups(
        has_groups=len(groups) > 0,
        groupnames=[group.name for group in groups],
    )

    return obj


async def players(
    data: request_dto.GroupPlayers,
    session: AsyncSession,
    session_token: str,
) -> response_dto.GroupPartialPlayers:
    # authorization
    await orm.User.from_session_token(session_token=session_token, session=session)

    if data.groupname == "":
        usernames = ["", "", "", ""]
    else:
        selected_group = await orm.Group.from_name(name=data.groupname, session=session)
        selected_group_users = await selected_group.get_sorted_users()
        usernames = [selected_group_user.name for selected_group_user in selected_group_users]

    obj = response_dto.GroupPartialPlayers(playernames=usernames)
    return obj
