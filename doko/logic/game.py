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
        valid_play_ids = [p.id for p in await hand.get_valid_plays(session=session)]
        cards=[
            response_dto.GameCardHand(suit=card.suit, rank=card.rank, id=str(card.id), is_playable=card.id in valid_play_ids)
            for card in hand_cards
        ]

    else:
        await player.set_status(status="waiting_for_turn", session=session)
        cards=[
            response_dto.GameCardHand(suit=card.suit, rank=card.rank, id=str(card.id), is_playable=False)
            for card in hand_cards
        ]

    obj = response_dto.GamePartialHand(hand=response_dto._GamePartialHand(cards=cards))

    return obj



async def play_card(data: request_dto.GameHandcard, session: AsyncSession, session_token: str, game_id: str) -> None:
    """Player plays a card."""

    user = await orm.User.from_session_token(session=session, session_token=session_token)
    game: orm.Game = await orm.Game.from_id(session=session, id=UUID(game_id))
    group = await game.get_group()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    
    # Get active trick with row-level lock to prevent concurrent plays
    trick = await game.get_active_trick(session=session, with_for_update=True)
    logging.info(f"{user.name}: acquired lock on trick {trick.number}")
    
    # Query plays directly to avoid cached relationship data
    from sqlalchemy import select
    plays_stmt = select(orm.Play).where(orm.Play.trick_id == trick.id).with_for_update()
    plays_result = await session.execute(plays_stmt)
    plays: list[orm.Play] = list(plays_result.scalars().all())
    logging.info(f"{user.name}: found {len(plays)} existing plays in trick {trick.number}")
    
    active_player = await trick.next_player_up(session=session)
    active_user = await orm.User.from_player_id(session=session, player_id=active_player.id)
    hand: orm.Hand = await player.awaitable_attrs.hand
    hand_cards: list[orm.HandCard] = await hand.awaitable_attrs.cards

    logging.info(f"{user.name}: tries to play {data.rank} {data.suit} (active player is: {active_user.name})")

    # checks
    assert active_player.id == player.id, f"illegal move: not that players turn (expected {active_user.name}, got {user.name})"
    assert len(plays) < 4, "illegal move: no more than 4 cards per trick"
    card_id = None
    for i, card in enumerate(hand_cards):
        if (card.rank == data.rank) and (card.suit == data.suit):
            card_id = card.id
            logging.info(f"Found the card in hand: {card_id}")
    assert card_id is not None, "illegal move: card not in hand"

    # check if the played card is allowed by the game rules (pass locked trick to avoid refetching)
    valid_plays = await hand.get_valid_plays(session=session, trick=trick)
    logging.info(f"Received these valid plays: {valid_plays}")
    assert card_id in [valid_card.id for valid_card in valid_plays], "illegal move: card not in valid cards"

    
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
    
    logging.info(f"Game end check: trick.number={trick.number}, new_play.number={new_play.number}, was_last_play_in_trick={was_last_play_in_trick}, is_last_trick_in_game={is_last_trick_in_game}, was_last_play_in_game={was_last_play_in_game}")
    
    users = await group.get_sorted_users()

    if was_last_play_in_trick:
        logging.info(f"Last play in trick detected! Trick {trick.number} completed.")
        # Determine the winner of the completed trick
        winning_player_id = await trick.determine_winner(session=session)
        winning_user = await orm.User.from_player_id(session=session, player_id=winning_player_id)
        logging.info(f"Trick {trick.number} winner: {winning_user.name} (player_id: {winning_player_id})")
        trick.winning_player_id = winning_player_id
        trick.active = False  # Mark old trick inactive immediately
        session.add(trick)
        
        # Create new trick in SAME transaction to avoid gaps
        new_trick = None
        if not is_last_trick_in_game:
            logging.info(f"Creating new trick after trick {trick.number}")
            # Create new trick without committing (handled by create_active_trick_in_transaction)
            new_trick = await game.create_active_trick_in_transaction(session=session)
        else:
            # Last trick completed - mark game inactive
            logging.info(f"Game {game.id} completed! Marking game inactive.")
            game.active = False
            session.add(game)
        
        # Single atomic commit: old trick inactive + (new trick active OR game inactive)
        await session.commit()
        
        # TODO: make after trick time available as config 
        await asyncio.sleep(1)  # let users look at the last card of the trick, 
        if not is_last_trick_in_game:
            # After creating the new trick, get the correct first player
            new_first_player = await new_trick.next_player_up(session=session)
            new_first_user = await orm.User.from_player_id(session=session, player_id=new_first_player.id)
            
            for user in users:
                print(f"Notifying {user.name} about new stack: {card_id}.")
                sse.EventStore[user.session_token][sse.Event.card_played].set()  # todo: should proabbly use a new event 'stack_updated', and add that one to the frontent event listener, too 
            
            # Notify the winning player (first player of new trick) that it's their turn
            await asyncio.sleep(0.2)
            print(f"Notifying {new_first_user.name} about start of their turn in new trick.")
            sse.EventStore[new_first_user.session_token][sse.Event.turn_changed].set()
        else:
            # This was the last trick of the game
            logging.info("GAME ENDING: Last trick completed!")
            await trick.close(session=session)
            logging.info(f"{user.name}: played the last card of the game. Closing game.")
            await game.close(session=session)
            await session.refresh(game)
            
            for user in users:
                player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
                await player.set_status(session=session, status="online")
                print(f"Notifying {user.name} about end of the game.")
                sse.EventStore[user.session_token][sse.Event.game_closed].set()
    
    else:
        logging.info(f"Continuing with next player in current trick {trick.number}")
        # Not the last play in trick, continue with next player in current trick
        await asyncio.sleep(0.2)  # let users look at the last card of the trick 
        print(f"Notifying {next_user.name} about start of their turn.")
        sse.EventStore[next_user.session_token][sse.Event.turn_changed].set()


async def update_hand_order(data: request_dto.GameHandOrder, session: AsyncSession, session_token: str, game_id: str) -> None:
    """Update the order of cards in the player's hand."""
    
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    game: orm.Game = await orm.Game.from_id(session=session, id=UUID(game_id))
    group = await game.get_group()
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    hand: orm.Hand = await player.awaitable_attrs.hand
    hand_cards: list[orm.HandCard] = await hand.awaitable_attrs.cards
    
    # Create a mapping of card ID to card object
    card_map = {str(card.id): card for card in hand_cards}
    
    # Update positions based on the new order
    for new_position, card_id in enumerate(data.card_ids):
        if card_id in card_map:
            card_map[card_id].position = new_position
    
    await session.commit()
    logging.info(f"Updated hand order for {user.name}")
