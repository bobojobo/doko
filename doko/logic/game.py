"""  
flow:
┌──┬─────────────────────┬──────────────┬──────────────────────────────┐
│  │ event / sse_event   │-> get_request│ -> response                  │
├──┼─────────────────────┼──────────────┼──────────────────────────────┤
│1)│  game_started       │ /game        │ new game                     │ <──────┐
│3)│  card_played        │ /trick       │ new trick                    │        │
│4)│  trick_full         │ /trick       │ new trick                    │        │ 
│5)│  game_over          │ /game_over   │ in between screen            │ ───────┘user clicks link to the next game
│                              ...                                     │ 
│     (game flow irrelevant events like 'ansage' or 'player_offline')  │     
└──────────────────────────────────────────────────────────────────────┘

* /waiting: all ready -> (set waiting to false), create sitting, game, hands. Send game_started event
* forward from /waiting to /game

* players plays card /game/play_card -> card_played event + db changes
* other players receive event. Call /game/trick to see the update
* last player plays card /game/play_card -> trick_full event + db changes 
* other players receive event. Call /game/trick to see update
* last trick, last player plays card. -> game_over_event -> 

--> play card has 3 possible event: 1) card_played, 2) trick_full, 3) game_over
    ----> trick_full is not event needed right now.

A Bit of a group-sitting-manager. Get the state of the game, and allow for actions.
But not implemented like a websocket session, where we are actually in live contact with everyone and have
broadcasting.
All that stays in database and we refetch it. THis makes it a bit slower but the state is always clear. Also it
should be enough for now, we can always go and refactor this and make it cool and abstract later on.

"""
from collections import deque
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from uuid import UUID
from doko import request_dto, response_dto, orm, logging, sse



async def state(session: AsyncSession, session_token: str, game_id: str) -> response_dto.Game:
    """Fetches the state of ongoing games. Initializes new a new state if neccessary."""

    user = await orm.User.from_session_token(session=session, session_token=session_token)
    game: orm.Game = await orm.Game.from_id(session=session, id=UUID(game_id))
    group = await game.get_group()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    sitting: orm.Sitting = await player.get_active_sitting(session=session)
    trick: orm.Trick = await game.get_active_trick(session=session)
    active_player = await trick.next_player_up(session=session)
    it_is_players_turn: bool = active_player.id == player.id
    hand: orm.Hand = await player.awaitable_attrs.hand
    hand_cards: list[orm.HandCard] = await hand.awaitable_attrs.cards
    plays: list[orm.Play] = await trick.awaitable_attrs.plays
    trick_cards: list[orm.PlayedCard] = []
    for play in plays:
        trick_card = await play.awaitable_attrs.card
        trick_cards.append(trick_card)

    sequence = [
        sitting.sequence_player_0_id,
        sitting.sequence_player_1_id,
        sitting.sequence_player_2_id,
        sitting.sequence_player_3_id,
    ]
    player_id_index = sequence.index(player.id)
    relative_sequence = deque(sequence)
    relative_sequence.rotate(-player_id_index)

    user1 = await orm.User.from_player_id(session=session, player_id=relative_sequence[1])
    user2 = await orm.User.from_player_id(session=session, player_id=relative_sequence[2])
    user3 = await orm.User.from_player_id(session=session, player_id=relative_sequence[3])

    await player.set_status(status="playing", session=session)

    obj = response_dto.Game(
        username=user.name,
        game_id=str(game_id),
        hand=response_dto._GamePartialHand(
            cards=[
                response_dto.GameCardHand(suit=card.suit, rank=card.rank, id=str(card.id), is_playable=it_is_players_turn)
                for card in hand_cards
            ]
        ),
        stack=response_dto._GamePartialStack(
            cards=[response_dto.GameCardTrick(suit=card.suit, rank=card.rank, id=str(card.id), blocked=False) for card in trick_cards]
        ),
        player1=user1.name,
        player2=user2.name,
        player3=user3.name,
    )

    return obj


async def stack(session: AsyncSession, session_token: str, game_id: str) -> response_dto.Game:
    """Fetches the state of ongoing games. Initializes new a new state if neccessary."""

    user = await orm.User.from_session_token(session=session, session_token=session_token)
    game: orm.Game = await orm.Game.from_id(session=session, id=UUID(game_id))
    group = await game.get_group()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    sitting: orm.Sitting = await player.get_active_sitting(session=session)
    trick: orm.Trick = await game.get_active_trick(session=session) 
    plays: list[orm.Play] = await trick.awaitable_attrs.plays
    trick_cards: list[orm.PlayedCard] = []
    for play in plays:
        trick_card = await play.awaitable_attrs.card
        trick_cards.append(trick_card)

    sequence = [
        sitting.sequence_player_0_id,
        sitting.sequence_player_1_id,
        sitting.sequence_player_2_id,
        sitting.sequence_player_3_id,
    ]
    player_id_index = sequence.index(player.id)
    relative_sequence = deque(sequence)
    relative_sequence.rotate(-player_id_index)

    obj = response_dto.GamePartialStack(
        stack=response_dto._GamePartialStack(
            cards=[response_dto.GameCardTrick(suit=card.suit, rank=card.rank, id=str(card.id), blocked=False,) for card in trick_cards]
        )
    )

    return obj

async def hand(session: AsyncSession, session_token: str, game_id: str) -> response_dto.Game:
    """Fetches the state of ongoing games. Initializes new a new state if neccessary."""

    user = await orm.User.from_session_token(session=session, session_token=session_token)
    game: orm.Game = await orm.Game.from_id(session=session, id=UUID(game_id))
    group = await game.get_group()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    sitting: orm.Sitting = await player.get_active_sitting(session=session)
    trick: orm.Trick = await game.get_active_trick(session=session)
    active_player = await trick.next_player_up(session=session)
    it_is_players_turn: bool = active_player.id == player.id
    hand: orm.Hand = await player.awaitable_attrs.hand
    hand_cards: list[orm.HandCard] = await hand.awaitable_attrs.cards
    plays: list[orm.Play] = await trick.awaitable_attrs.plays
    trick_cards: list[orm.PlayedCard] = []
    for play in plays:
        trick_card = await play.awaitable_attrs.card
        trick_cards.append(trick_card)

    sequence = [
        sitting.sequence_player_0_id,
        sitting.sequence_player_1_id,
        sitting.sequence_player_2_id,
        sitting.sequence_player_3_id,
    ]
    player_id_index = sequence.index(player.id)
    relative_sequence = deque(sequence)
    relative_sequence.rotate(-player_id_index)

    if it_is_players_turn:
        await player.set_status(status="playing", session=session)
    else:
        await player.set_status(status="waiting_for_turn", session=session)

    obj = response_dto.GamePartialHand(
        hand=response_dto._GamePartialHand(
            cards=[
                response_dto.GameCardHand(suit=card.suit, rank=card.rank, id=str(card.id), is_playable=it_is_players_turn)
                for card in hand_cards
            ]
        )
    )

    return obj



async def play_card(data: request_dto.GameHandcard, session: AsyncSession, session_token: str, game_id: str) -> None:
    """Player plays a card."""

    user = await orm.User.from_session_token(session=session, session_token=session_token)
    game: orm.Game = await orm.Game.from_id(session=session, id=UUID(game_id))
    group = await game.get_group()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    trick = await game.get_active_trick(session=session)
    active_player = await trick.next_player_up(session=session)
    hand = await player.awaitable_attrs.hand
    hand_cards: list[orm.HandCard] = await hand.awaitable_attrs.cards
    plays: list[orm.Play] = await trick.awaitable_attrs.plays

    # checks
    assert active_player.id == player.id, "illegal move: not that players turn"
    assert len(plays) < 4, "illegal move: no more than 4 cards per trick"
    card_id = None
    for i, card in enumerate(hand_cards):
        if (card.rank == data.rank) and (card.suit == data.suit):
            card_id = card.id
            break
    assert card_id is not None, "illegal move: car not in hand"

    # check if the played card is allowed by the game rules
    

    # remove card from hand
    stmt = delete(orm.HandCard).where(orm.HandCard.id == card_id)
    await session.execute(stmt)

    # add card to trick
    cc = orm.PlayedCard(suit=data.suit, rank=data.rank)
    new_play = orm.Play(
        number=len(plays),
        card=cc,
        trick=trick,
        trick_id=trick.id,
        player_id=player.id,
    )
    cc.play_id = new_play.id
    session.add(new_play)
    session.add(cc)
    await session.commit()
    await session.refresh(new_play)
    logging.info(f"{user.name} played {cc.suit} {cc.rank}")

    # additional notifications
    next_player = await trick.next_player_up(session=session)
    next_user = await orm.User.from_player_id(session=session, player_id=next_player.id)
    await asyncio.sleep(0.2)
    print(f"Notifying {user.name} about end of their turn.")
    sse.EventStore[user.session_token][sse.Event.turn_changed].set()

    was_last_play_in_trick = new_play.number == 3
    is_last_trick_in_game = trick.number == 9 
    was_last_play_in_game = was_last_play_in_trick and is_last_trick_in_game  
    
    users = await group.get_sorted_users()

    if was_last_play_in_trick:
        # TODO: make after trick time available as config 
        await asyncio.sleep(1)  # let users look at the last card of the trick, 
        if not is_last_trick_in_game:
            await game.create_active_trick(session=session)
            for user in users:
                print(f"Notifying {user.name} about new stack: {card_id}.")
                sse.EventStore[user.session_token][sse.Event.card_played].set()  # todo: should proabbly use a new event 'stack_updated', and add that one to the frontent event listener, too 
    
    if not was_last_play_in_game:
        await asyncio.sleep(0.2)  # let users look at the last card of the trick 
        print(f"Notifying {next_user.name} about start of their turn.")
        sse.EventStore[next_user.session_token][sse.Event.turn_changed].set()
    else:
        await trick.close(session=session)
        logging.info(f"{user.name}: played the last card of the game. Closing game.")
        await game.close(session=session)
        await session.refresh(game)
        
        for user in users:
            player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
            await player.set_status(session=session, status="online")
            print(f"Notifying {user.name} about end of the game.")
            sse.EventStore[user.session_token][sse.Event.game_closed].set()
