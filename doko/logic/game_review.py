""""""
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from typing import DefaultDict

from doko import request_dto, response_dto, orm, logging, sse


async def user_status(user: orm.User, group: orm.Group, session: AsyncSession) -> response_dto.PlayerStatusSymbol:
    status = response_dto.PlayerStatusSymbol.offline
    if isinstance(user.session_expiry, datetime) and user.session_expiry > datetime.now():
        try:
            player = await orm.Player.from_user_and_group(user=user, group=group, session=session)
            if player.status == "offline":
                status = response_dto.PlayerStatusSymbol.offline
            elif player.status == "waiting_for_game":
                status = response_dto.PlayerStatusSymbol.ready
            else:
                status = response_dto.PlayerStatusSymbol.online
        except LookupError:
            status = response_dto.PlayerStatusSymbol.online
    return status


async def state(session: AsyncSession, session_token: str, game_id: str) -> response_dto.GameReview:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    review_game = await orm.Game.from_id(session=session, id=uuid.UUID(game_id))
    tricks: list[orm.Trick] = await review_game.awaitable_attrs.tricks
    sitting = await orm.Sitting.from_id(session=session, id=review_game.sitting_id)
    group = await review_game.get_group()
    all_users = await group.get_sorted_users()

    cards: DefaultDict[uuid.UUID, list[response_dto.GameReviewCard]] = defaultdict(list)    
    for trick in tricks:
        plays: list[orm.Play] = await trick.awaitable_attrs.plays
        for play in plays:
            played_card: orm.PlayedCard = await play.awaitable_attrs.card
            cards[play.player_id].append(
                response_dto.GameReviewCard(
                    suit=played_card.suit, 
                    rank=played_card.rank,
                )
            )

    players_cards = []
    players_status = []
    for u in all_users:
        status = await user_status(user=u, group=group, session=session)
        name = u.username_self_marked(user)
        player = await orm.Player.from_user_and_group(group=group, user=u, session=session)
        players_cards.append(response_dto.GameReviewPlayerCards(name=name, cards=cards[player.id]))
        players_status.append(response_dto.GameReviewPlayerStatus(name=name, status=status))


    new_game_id = ""
    all_ready = await group.all_players_are_waiting()
    
    obj = response_dto.GameReview(
        username=user.name,
        groupname=group.name,
        gamenumber=review_game.number,
        gameid=str(review_game.id),
        new_gameid=new_game_id,
        sittingnumber=sitting.number,
        players_cards=players_cards,
        players_status=players_status,
        all_ready=all_ready,
    )
    return obj


async def update(session: AsyncSession, session_token: str, game_id: str) -> response_dto.GameReviewUpdate:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    review_game = await orm.Game.from_id(session=session, id=uuid.UUID(game_id))
    sitting = await orm.Sitting.from_id(session=session, id=review_game.sitting_id)
    group = await review_game.get_group()
    all_users = await group.get_sorted_users()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)

    players_status = []
    for u in all_users:
        status = await user_status(user=u, group=group, session=session)
        name = u.username_self_marked(user)
        players_status.append(response_dto.GameReviewPlayerStatus(name=name, status=status))

    new_game_id = ""
    all_ready = await group.all_players_are_waiting()

    if all_ready:
        # START!
        leader = await group.leader()
        group_needs_active_game = not await sitting.has_active_game(session=session)
        if (user.id == leader.id) and group_needs_active_game:
            logging.info(f"{user.name}: is the leader and setting up the game.")
            assert await group.has_active_sitting(session=session)
            active_sitting = await group.get_active_sitting(session=session)
            # todo: assert no active game (should get closed at last play)
            new_game = await active_sitting.create_game(session=session)
            await group.deal_cards(session=session)
            await new_game.create_active_trick(session=session)
            new_game_id = str(new_game.id)

        async for _ in sse.EventLoop(session_token, sse.Event.game_created):
            new_game = await player.get_active_game(session=session)
            new_game_id = str(new_game.id)
            break
        await player.set_status(session=session, status="waiting_for_turn")

    obj = response_dto.GameReviewUpdate(
        new_gameid=new_game_id,
        players_status=players_status,
        all_ready=all_ready,
        groupname=group.name,
    )
    return obj

async def ready(data: request_dto.GameReviewReady, session: AsyncSession, session_token: str) -> None:
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    group = await orm.Group.from_name(session, name=data.groupname)
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    if data.status =="ready":
        await player.set_status(session=session, status="waiting_for_game")
    elif data.status=="not_ready":
        await player.set_status(session=session, status="online")
    else:
        raise Exception("UNEXPECTED!")
    await session.refresh(user)
    await session.refresh(group)
    await session.refresh(player)
