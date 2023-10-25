""""""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from doko import request_dto, response_dto, orm, db, logging, sse


async def user_status(user: orm.User, group: orm.Group, session: AsyncSession) -> response_dto.PlayerStatusSymbol:
    status = response_dto.PlayerStatusSymbol.offline
    if isinstance(user.session_expiry, datetime) and user.session_expiry > datetime.now():
        try:
            player = await orm.Player.from_user_and_group(user=user, group=group, session=session)
            if player.status == "offline":
                status = response_dto.PlayerStatusSymbol.offline
            elif player.status == "online":
                status = response_dto.PlayerStatusSymbol.online
            else:
                status = response_dto.PlayerStatusSymbol.ready
        except LookupError:
            status = response_dto.PlayerStatusSymbol.online
    return status


async def state(data: request_dto.Waiting, session: AsyncSession, session_token: str) -> response_dto.Waiting:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    # todo: Add authorization to access that Group
    group = await orm.Group.from_name(session, name=data.groupname)
    all_users = await group.get_sorted_users()
    players = []
    for u in all_users:
        status = await user_status(user=u, group=group, session=session)
        name = u.username_self_marked(user)
        players.append(response_dto.WaitingPlayer(name=name, status=status))

    obj = response_dto.Waiting(
        players=players,
        all_ready=await group.all_players_are_waiting(),
        username=user.name,
        groupname=data.groupname,
    )
    return obj


async def waiting_for_group(data: request_dto.Waiting, session: AsyncSession, session_token: str) -> None:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    group = await orm.Group.from_name(session, name=data.groupname)
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    await player.set_status(session=session, status="waiting_for_sitting")
    await session.refresh(user)
    await session.refresh(group)
    await session.refresh(player)

async def stop_waiting_for_group(session: AsyncSession, session_token: str, data=request_dto.Waiting) -> None:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    group = await orm.Group.from_name(session, name=data.groupname)
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    await player.set_status(session=session, status="online")


async def update(data: request_dto.Waiting, session: AsyncSession, session_token: str) -> response_dto.WaitingUpdate:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    # todo: Add authorization to access that Group
    group = await orm.Group.from_name(session, name=data.groupname)
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)

    await session.refresh(player)
    await session.refresh(group)
    all_users = await group.get_sorted_users()
    for u in all_users:
        await session.refresh(u)

    players = []
    for u in all_users:
        status = await user_status(user=u, group=group, session=session)
        name = u.username_self_marked(user)
        players.append(response_dto.WaitingPlayer(name=name, status=status))

    game_id = ""
    all_ready = await group.all_players_are_waiting()
    if all_ready:
        # START!
        leader = await group.leader()
        group_needs_active_sitting = not await group.has_active_sitting(session=session)
        if (user.id == leader.id) and group_needs_active_sitting:
            logging.info(f"{user.name}: is the leader and setting up the game.")
            assert not await group.has_active_sitting(session=session)
            active_sitting = await group.create_sitting(session=session)
            game = await active_sitting.create_game(session=session)
            await group.deal_cards(session=session)
            await game.create_active_trick(session=session)
            game_id = str(game.id)
        else:
            async for _ in sse.EventLoop(session_token, sse.Event.game_created):
                game = await player.get_active_game(session=session)
                game_id = str(game.id)
                break
        await player.set_status(session=session, status="waiting_for_turn")

    obj = response_dto.WaitingUpdate(
        players=players,
        all_ready=all_ready,
        username=user.name,
        game_id=game_id,
    )

    return obj


async def cleanup(session_token: str, data=request_dto.Waiting) -> None:
    async with db.get_session() as session:
        await stop_waiting_for_group(session=session, session_token=session_token, data=data)
