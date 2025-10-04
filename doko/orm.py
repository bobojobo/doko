"""
ORM model of the crud schema. This represents all oltp tables for the doko app.

Hand and handcard are mostly used for temporary game state and contain mostly slowly changing dimensions. 
The other tables are almost append only and qualify better for the olap analytics stuff.


Model:

┌──────────┐
│ User     │
└────┬─────┘
     │1                                                                 
     │                                                                 
     │m                                                 
┌────┴─────┐1                                   1┌──────────┐1                                                     0,1,m(10)┌──────────┐
│ Player   ├─────────────────────────────────────┤ Hand     ├───────────────────────────────────────────────────────────────┤ HandCard │     
└────┬─────┘                                     └──────────┘                                                               └──────────┘                                                     
     │m(4)                                                                 
     │                                                                 
     │1                                                                 
┌────┴─────┐1       0,1,m┌──────────┐1           m┌──────────┐1       m(10)┌──────────┐1        m(4)┌─────────┐1           1┌──────────┐
│ Group    ├─────────────┤ Sitting  ├─────────────┤ Game     ├─────────────┤ Trick    ├─────────────┤ Play    ├─────────────┤playedCard│
└──────────┘             └──────────┘             └──────────┘             └──────────┘             └─────────┘             └──────────┘
"""

from __future__ import annotations
from typing import Any, Literal, get_args, Optional
from datetime import datetime
import uuid
import secrets
from random import shuffle
import asyncio

from sqlalchemy import ForeignKey, Enum, select, func, event
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    class_mapper,
    ColumnProperty,
    DeclarativeBase,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs
from pydantic import BaseModel, Field

from doko import logging, settings, exception, sse, db
from doko.game import Deck, rules
from doko.libs import case_utils
from doko.libs import password_utils


# schema = "some_name_here"

PlayerStatus = Literal["offline", "online", "waiting_for_sitting", "waiting_for_game", "waiting_for_turn", "playing"]

class Cookie(BaseModel):
    key: str = Field(default="session_token")
    value: str
    # todo: this is a str representing datetime the way browser likes it. Add validator!
    expires: str
    httponly: bool = Field(default=True)


class Crud(AsyncAttrs, DeclarativeBase):
    """Base for all tables in the crud schema. Only holds helper methods and attributes, no columns."""

    # __table_args__ = {"schema": schema}
    # __mapper_args__ = {"eager_defaults": True}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """The actual tables are in snake_case, but we model them as CamelCase, like good pythonistas 🐍!"""
        return case_utils.camel_to_snake(cls.__name__)

    @classmethod
    def columns(cls) -> list[str]:
        """Helper method to get all columns of a table."""
        return [prop.key for prop in class_mapper(cls).iterate_properties if isinstance(prop, ColumnProperty)]

    def dict(self) -> dict[str, Any]:
        """Not sure if needed. But works for now with sqlalchemy insert expecting a dict."""
        return {key: getattr(self, key) for key in self.columns() if key in self.__dict__}

    def __repr__(self) -> str:
        """Default representation, looks like Table(**columns)."""
        comma_seperated_columns = ", ".join([f"{k}={getattr(self, k)!r}" for k in self.columns()])
        return f"{self.__class__.__name__}({comma_seperated_columns})"


class IdMixin:
    """Mixin containing the id column."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True)

    @classmethod
    async def from_id(cls, session: AsyncSession, id: uuid.UUID):
        stmt = select(cls).where(cls.id == id)
        result = await session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise LookupError()
        return instance


class AuditMixin:
    """Mixin containing the audit columns. This actually resides as a real table in the public schema."""

    # todo: rethink these.
    # created_by: Mapped[str] = mapped_column(default="system")
    created_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # todo: verify tz
    # last_modified_by: Mapped[str | None] = mapped_column()
    # last_modified_date: Mapped[datetime | None] = mapped_column()


class Player(Crud, AuditMixin):
    """
    Player is an association table for the many-to-many junction between users and groups.
    A Player plays the game with a group. Not to confuse with a User. A User uses the app and can have many players.
    """

    # not using the id mixin simce id is not the primary key here
    id: Mapped[uuid.UUID] = mapped_column(unique=True, default=uuid.uuid4)
    # TODO: I think player should also have a token thats stored in frontend
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("group.id"), primary_key=True)
    # https://stackoverflow.com/questions/76268799/how-should-i-declare-enums-in-sqlalchemy-using-mapped-column-to-enable-type-hin
    status: Mapped[PlayerStatus] = mapped_column(
        Enum(
            *get_args(PlayerStatus),
            create_constraint=True,
            validate_strings=True,
            name="playerstatus"
            ),
        default="offline",
    )


    user: Mapped[User] = relationship(back_populates="players", viewonly=True)
    group: Mapped[Group] = relationship(back_populates="players", viewonly=True)
    hand: Mapped[Hand | None] = relationship(back_populates="player")

    @classmethod
    async def from_user_and_group(cls, group: Group, user: User, session: AsyncSession) -> Player:
        stmt = select(cls).filter(cls.user_id == user.id).filter(cls.group_id == group.id)
        result = await session.execute(stmt)
        player = result.scalars().first()
        if player is None:
            raise LookupError()
        return player

    @classmethod
    async def from_id(cls, id: uuid.UUID, session: AsyncSession) -> Player:
        stmt = select(cls).where(cls.id == id)
        result = await session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise LookupError()
        return instance

    async def reset(self, session: AsyncSession) -> None:
        # todo: delete the hand the right way!
        self.hand = None
        self.status: PlayerStatus = "offline"
        await session.commit()
        await session.refresh(self)
        logging.debug(f"{self.user.name}-{self.group.name} was reset")

    async def set_status(self, session: AsyncSession, status: PlayerStatus) -> None:
        if self.status != status:
            self.status = status
            await session.commit()
            await session.refresh(self)

    async def get_active_sitting(self, session: AsyncSession) -> Sitting:
        stmt = (
            select(Sitting)
            .filter(Sitting.group_id == self.group_id)
            .filter(Sitting.active == True)  # todo: DONT DO "IS" HERE! (add ruff rule)
        )
        result = await session.execute(stmt)
        active_sitting = result.scalars().first()
        if active_sitting is None:
            logging.debug("No active sitting")
            raise LookupError()
        return active_sitting

    async def get_active_game(self, session: AsyncSession) -> Game:
        sitting = await self.get_active_sitting(session=session)
        game = await sitting.get_active_game(session=session)
        return game

    async def get_other_group_users(self) -> list[User]:
        group: Group = await self.awaitable_attrs.group
        all_users = await group.get_sorted_users()
        other_users = [user for user in all_users if user != self]
        return other_users


class User(Crud, AuditMixin, IdMixin):
    """A User is someone with an account."""

    name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes] = mapped_column()
    session_token: Mapped[str | None] = mapped_column(default=None, unique=True)
    session_expiry: Mapped[datetime | None] = mapped_column(default=None)

    players: Mapped[list[Player]] = relationship(back_populates="user")
    groups: Mapped[list[Group]] = relationship(
        secondary="player",
        back_populates="users",
        lazy="joined",
    )

    @classmethod
    async def from_name(cls, session: AsyncSession, name: str) -> User:
        stmt = select(cls).where(cls.name == name)
        result = await session.execute(stmt)
        user = result.scalars().unique().first()
        if user is None:
            raise LookupError()
        return user

    @classmethod
    async def from_session_token(cls, session: AsyncSession, session_token: str) -> User:
        stmt = select(cls).where(cls.session_token == session_token)
        result = await session.execute(stmt)
        user = result.scalars().unique().first()
        if user is None:
            raise LookupError()
        return user

    @classmethod
    async def from_login(cls, session: AsyncSession, username: str, password: str) -> User:
        try:
            user = await cls.from_name(session, name=username)
        except LookupError as e:
            logging.debug(f"No user found for name: {username}")
            raise exception.InvalidUsername from e

        password_matches = password_utils.password_matches(password=password, hashed=user.password)
        del password

        if not password_matches:
            logging.debug(f"User {username} failed login due to a wrong password")
            raise exception.InvalidPassword()

        await user.update_session(session)

        players: list[Player] = await user.awaitable_attrs.players
        for player in players:
            await player.set_status(session=session, status="online")
        return user

    @classmethod
    async def from_player_id(cls, session: AsyncSession, player_id: uuid.UUID) -> User:
        player = await Player.from_id(player_id, session=session)
        user = await player.awaitable_attrs.user
        return user

    async def get_sorted_groups(self) -> list[Group]:
        groups = await self.awaitable_attrs.groups
        sorted_groups = sorted(groups, key=lambda x: getattr(x, "name"))
        return sorted_groups

    async def expire_session(self, session: AsyncSession) -> None:
        self.session_expiry = None
        self.session_token = None
        # todo: remove ready status for current game
        self.waiting_group = None
        await session.commit()
        await session.refresh(self)
        logging.info(f"Expired session for user {self.name}")

    async def update_session(self, session: AsyncSession) -> None:
        self.session_expiry = datetime.now() + settings.SESSION_TOKEN_VALIDITY
        # https://docs.python.org/3/library/secrets.html#generating-tokens
        self.session_token = secrets.token_urlsafe(64)
        await session.commit()
        await session.refresh(self)

    async def cookie(self) -> Cookie:
        return Cookie(
            value=self.session_token,
            expires=self.session_expiry.strftime("%a, %d-%b-%Y %T UTC"),
        )

    async def is_expired(self) -> bool:
        return self.session_expiry <= datetime.now()

    @classmethod
    async def is_authenticated(cls, session_token: str | None, session: AsyncSession) -> bool:
        """bit of an odd one, but no better place"""
        if session_token is None:
            return False
        try:
            user = await cls.from_session_token(session=session, session_token=session_token)
        except LookupError:
            return False
        if await user.is_expired():
            return False
        return True

    @classmethod
    async def name_is_available(cls, session: AsyncSession, name: str) -> bool:
        stmt = select(cls).where(cls.name == name)
        result = await session.execute(stmt)
        user = result.scalars().unique().first()
        return user is None

    def username_self_marked(self, other_user: User) -> str:
        # todo: should be a field on the dto, not part of the name itself
        name = self.name + " (you)" if self.id == other_user.id else self.name
        return name


class Group(Crud, AuditMixin, IdMixin):
    """A Group consists of four users. The order of the users is not realted to the sequence in each Sitting"""

    name: Mapped[str] = mapped_column(unique=True)

    sittings: Mapped[list[Sitting]] = relationship(back_populates="group")
    # todo: validator to have at least 4 players
    players: Mapped[list[Player]] = relationship(back_populates="group")
    users: Mapped[list[User]] = relationship(
        secondary="player",
        back_populates="groups",
        lazy="joined",  # other option: "selectin". But we are usually interested enough in the groups users to just join
    )

    @classmethod
    async def from_name(cls, session: AsyncSession, name: str) -> Group:
        stmt = select(cls).filter(cls.name == name)
        result = await session.execute(stmt)
        group = result.scalars().unique().first()
        if group is None:
            raise LookupError()
        return group

    async def get_sorted_users(self) -> list[User]:
        users = await self.awaitable_attrs.users
        sorted_users = sorted(users, key=lambda x: getattr(x, "name"))
        return sorted_users

    async def all_players_are_waiting(self) -> bool:
        players: list[Player] = await self.awaitable_attrs.players
        all_waiting = all([player.status not in ["offline", "online"] for player in players])
        return all_waiting

    @classmethod
    async def name_is_available(cls, session: AsyncSession, name: str) -> bool:
        stmt = select(cls).where(cls.name == name)
        result = await session.execute(stmt)
        group = result.scalars().unique().first()
        return group is None

    async def get_active_sitting(self, session: AsyncSession) -> Sitting:
        stmt = (
            select(Sitting)
            .filter(Sitting.group_id == self.id)
            .filter(Sitting.active == True)  # todo: DONT DO "IS" HERE! (add ruff rule)
        )
        result = await session.execute(stmt)
        active_sitting = result.scalars().first()
        if active_sitting is None:
            logging.debug("No active sitting")
            raise LookupError()
        return active_sitting
    
    async def has_active_sitting(self, session: AsyncSession) -> bool:
        try: 
            await self.get_active_sitting(session=session)
            return True
        except LookupError:
            return False

    async def create_sitting(self, session: AsyncSession) -> Sitting:
        users = await self.get_sorted_users()
        sequence: list[Player] = [
            await Player.from_user_and_group(group=self, user=user, session=session) for user in users
        ]
        shuffle(sequence)
        number = await self.n_sittings(session=session)

        new_sitting = Sitting(
            number=number,
            group_id=self.id,
            sequence_player_0_id=sequence[0].id,
            sequence_player_1_id=sequence[1].id,
            sequence_player_2_id=sequence[2].id,
            sequence_player_3_id=sequence[3].id,
        )

        session.add(new_sitting)
        await session.commit()
        await session.refresh(new_sitting)
        logging.info(f"Sitting {number} created for group: {self.name}")
        return new_sitting

    async def n_sittings(self, session: AsyncSession) -> int:
        """Returns the number of sittings of the group."""
        stmt = select(func.count(Sitting.id)).where(Group.id == self.id)
        result = await session.scalar(stmt)
        return result

    async def leader(self) -> User:
        sorted_users = await self.get_sorted_users()
        leader = sorted_users[0]
        return leader

    async def deal_cards(self, session: AsyncSession) -> None:
        all_users: list[User] = await self.get_sorted_users()
        players: list[Player] = [
            await Player.from_user_and_group(group=self, user=user, session=session) for user in all_users
        ]

        # Delete old hands and hand cards for all players before dealing new ones
        from sqlalchemy import delete
        for player in players:
            # Delete HandCards associated with player's hands
            stmt_cards = delete(HandCard).where(
                HandCard.hand_id.in_(
                    select(Hand.id).where(Hand.player_id == player.id)
                )
            )
            await session.execute(stmt_cards)
            
            # Delete Hands for player
            stmt_hands = delete(Hand).where(Hand.player_id == player.id)
            await session.execute(stmt_hands)
        
        await session.commit()
        logging.info(f"Deleted old hands for {self.name}")

        # Deck is not a real object. Think of it as a virtual Object that exists only briefly in the setup period and
        # then gets directly stored in Hands. Long term the cards live on in the tricks.
        deck: Deck = Deck(rules.Normal().cards)
        deck.shuffle()

        for player, cards in zip(players, deck.hand_out()):
            # todo get hand and then test and then populate, .....
            handcards = [HandCard(suit=card.suit.name, rank=card.rank.name, position=i) for i, card in enumerate(cards)]
            hand = Hand(player_id=player.id, cards=handcards)
            session.add(hand)
            session.add(player)
            session.add_all(handcards)

        await session.commit()
        logging.info(f"Dealt new cards to {self.name}")


class Card(Crud, AuditMixin, IdMixin):
    """Base Represenation of a card. Cards can exist two in differnt contexts: still in hand or aleady played out."""

    suit: Mapped[str] = mapped_column()
    rank: Mapped[str] = mapped_column()
    #   location: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "card",
        # "polymorphic_on": "location",
    }


class HandCard(Card):
    """A hand card is a card that is part of a hand."""

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("card.id"), primary_key=True, default=uuid.uuid4, unique=True)
    hand_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hand.id"), default=None)
    position: Mapped[int] = mapped_column(default=0)

    hand: Mapped[Hand] = relationship(back_populates="cards", foreign_keys=hand_id)

    __mapper_args__ = {
        "polymorphic_identity": "hand_card",
    }


class PlayedCard(Card):
    """A played card is a card that is played out and part of a play that is part if a trick."""

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("card.id"), primary_key=True, default=uuid.uuid4, unique=True)
    play_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("play.id"), default=None)

    play: Mapped[Play] = relationship(back_populates="card", foreign_keys=play_id)

    __mapper_args__ = {
        "polymorphic_identity": "played_card",
    }

    async def get_play(self) -> Play:
        play: Play = await self.awaitable_attrs.play
        return play


class Hand(Crud, AuditMixin, IdMixin):
    """A Hand holds cards."""

    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("player.id"))

    cards: Mapped[list[HandCard]] = relationship(back_populates="hand", order_by="HandCard.position")
    player: Mapped[Player] = relationship(back_populates="hand", foreign_keys=[player_id])

    # __table_args__ = (ForeignKeyConstraint([user_id, group_id],[Player.user_id, Player.group_id]),)
    
    async def get_valid_plays(self, session: AsyncSession, trick: Trick | None = None) -> list[HandCard]:

        hand_cards = await self.awaitable_attrs.cards
        player: Player = await self.awaitable_attrs.player
        logging.info(f"Found {len(hand_cards)} cards in hand")
        
        # Use provided trick if given, otherwise fetch it
        if trick is None:
            active_game: Game = await player.get_active_game(session=session)
            active_trick = await active_game.get_active_trick(session=session)
        else:
            active_trick = trick
            
        plays: list[Play] = active_trick.plays       
        trick_cards: list[PlayedCard] = []
        for play in plays:
            trick_card = await play.awaitable_attrs.card
            trick_cards.append(trick_card)
        logging.info(f"Found {len(trick_cards)} cards in the trick")

        if len(trick_cards) == 0:
            logging.info("First play in trick: all cards in hand are valid plays")
            return hand_cards

        # rule cards 
        ruled_cards = rules.Normal.cards

        # rule hand cards 
        ruled_hand_cards: list[rules.Card] = []
        for hand_card in hand_cards:
            for ruled_card in ruled_cards:
                if (hand_card.suit == ruled_card.suit.value) and (hand_card.rank == ruled_card.rank.name):
                    ruled_hand_cards.append(ruled_card)
                    break
        
        # rule trick cards
        ruled_trick_cards: list[rules.Card] = []
        for trick_card in trick_cards:
            for ruled_card in ruled_cards:
                if (trick_card.suit == ruled_card.suit.value) and (trick_card.rank == ruled_card.rank.name):
                    ruled_trick_cards.append(ruled_card)
                    break
        
        # first trick card: 
        first_ruled_trick_card = ruled_trick_cards[0]
        if first_ruled_trick_card.is_trump:
            logging.info(f"First card in trick is {first_ruled_trick_card}: a trump.")
            trump_hand_cards = [hand_card for hand_card, ruled_hand_card in zip(hand_cards, ruled_hand_cards) if ruled_hand_card.is_trump] 
            if any(trump_hand_cards):
                logging.info(f"Returning the {len(trump_hand_cards)} trumps as valid cards.")
                return trump_hand_cards
            logging.info(f"No trumps in hand. All {len(hand_cards)} non-trumps are valid cards.")
            return hand_cards
        else:
            logging.info(f"First card in trick is {first_ruled_trick_card}: not a trump")
            matching_suit_hand_cards = [hand_card for hand_card, ruled_hand_card in zip(hand_cards, ruled_hand_cards) if (not ruled_hand_card.is_trump) and (hand_card.suit == first_ruled_trick_card.suit.value)] 
            if any(matching_suit_hand_cards):
                logging.info(f"Returning the {len(matching_suit_hand_cards)} cards with matching suit as valid cards.")
                return matching_suit_hand_cards
            logging.info(f"No card with matching suit in hand. All {len(hand_cards)} non-matching-suit cards are valid cards.")
            return hand_cards


class Sitting(Crud, AuditMixin, IdMixin):
    """
    A Sitting as an arbitrary number of games of a group. Think of an evening, a Round (already overloaded with the
    round function) or a series.
    The more commonly used name for it is actually a session. But the name is already heavily overloaded with
    database sessions and client sessions, so we try to stay away from it.
    """

    number: Mapped[int] = mapped_column()
    active: Mapped[bool] = mapped_column(default=True)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("group.id"))
    # Relationship seems like an overkill here.
    sequence_player_0_id: Mapped[uuid.UUID] = mapped_column()
    sequence_player_1_id: Mapped[uuid.UUID] = mapped_column()
    sequence_player_2_id: Mapped[uuid.UUID] = mapped_column()
    sequence_player_3_id: Mapped[uuid.UUID] = mapped_column()

    games: Mapped[list[Game]] = relationship(back_populates="sitting")
    group: Mapped[Group] = relationship(back_populates="sittings", foreign_keys=[group_id])

    async def get_active_game(self, session: AsyncSession) -> Game:
        stmt = (
            select(Game)
            .filter(Game.sitting_id == self.id)
            .filter(Game.active == True)  # todo: DONT DO "IS" HERE! (add ruff rule)
        )
        result = await session.execute(stmt)
        active_game = result.scalars().first()
        if active_game is None:
            logging.debug("No active game")
            raise LookupError()
        return active_game

    async def has_active_game(self, session: AsyncSession) -> bool:
        try: 
            await self.get_active_game(session=session)
            return True
        except LookupError:
            return False

    async def get_last_game(self, session: AsyncSession) -> Game:
        stmt = (
            select(func.max(Game.number))
            .filter(Game.sitting_id == self.id)
            .filter(Game.active == False)  # todo: DONT DO "IS" HERE! (add ruff rule)
        )
        result = await session.execute(stmt)
        last_game_number = result.scalars().first()
        if last_game_number is None:
            logging.debug("No last game found.")
            raise LookupError()
        
        stmt = (
            select(Game)
            .filter(Game.number == last_game_number)
            .filter(Game.sitting_id == self.id)
        )
        result = await session.execute(stmt)
        last_game = result.scalars().first()
        if last_game is None:
            logging.debug("No last game found.")
            raise LookupError()
        return last_game

    async def create_game(self, session: AsyncSession) -> Game:
        assert self.active

        # todo: check last 3 games of sitting for any bocks to calculate new bocks
        bock = 0
        # todo: add the game_type bidding logic (parameter into the game).
        game_type = "normal"

        try:
            assert not await self.has_active_game(session=session)
            last_game = await self.get_last_game(session=session)
            sequence = [
                self.sequence_player_0_id,
                self.sequence_player_1_id,
                self.sequence_player_2_id,
                self.sequence_player_3_id,
            ]
            starting_player_id_index = sequence.index(last_game.starting_player_id) + 1
            starting_player_id = sequence[starting_player_id_index]

            number = last_game.number + 1
        except LookupError:
            number = 0
            starting_player_id = self.sequence_player_0_id

        new_game = Game(
            number=number,
            starting_player_id=starting_player_id,
            sitting_id=self.id,
            active=True,
            game_type=game_type,
            bock=bock,
        )
        session.add(new_game)
        await session.commit()
        await session.refresh(new_game)
        logging.info(f"Game {number} created")
        return new_game


class Game(Crud, AuditMixin, IdMixin):
    """A Game has 10 Turns. (12 when plaing with 9s)."""

    number: Mapped[int] = mapped_column()
    sitting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sitting.id"))
    active: Mapped[bool] = mapped_column(default=True)
    # Relationship seems like an overkill here.
    starting_player_id: Mapped[uuid.UUID] = mapped_column()
    game_type: Mapped[str] = mapped_column(default="normal")  # normal, solotype, ...
    bock: Mapped[int] = mapped_column(default=0)

    sitting: Mapped[Sitting] = relationship(back_populates="games")
    tricks: Mapped[list[Trick]] = relationship(back_populates="game")

    async def close(self, session: AsyncSession) -> Game:
        assert self.active
        self.active = False
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self
    
    async def get_active_trick(self, session: AsyncSession, with_for_update: bool = False) -> Trick:
        stmt = (
            select(Trick)
            .filter(Trick.game_id == self.id)
            .filter(Trick.active == True)  # todo: DONT DO "IS" HERE! (add ruff rule)
            .order_by(Trick.number.desc())  # Get the highest-numbered active trick
        )
        if with_for_update:
            stmt = stmt.with_for_update()  # Row-level lock to prevent concurrent modifications
        result = await session.execute(stmt)
        active_trick = result.scalars().first()
        if active_trick is None:
            logging.debug("No active trick")
            raise LookupError()
        return active_trick

    async def create_active_trick_in_transaction(self, session: AsyncSession) -> Trick:
        """Create a new active trick without committing (for atomic transactions)."""
        assert self.active
        # Get the highest trick number for this game (regardless of active status)
        from sqlalchemy import func, select
        stmt = (
            select(func.max(Trick.number))
            .filter(Trick.game_id == self.id)
        )
        result = await session.execute(stmt)
        max_number = result.scalar()
        
        if max_number is not None:
            number = max_number + 1
        else:
            number = 0

        new_trick = Trick(
            number=number,
            game_id=self.id,
            active=True,
        )
        session.add(new_trick)
        # Don't commit here - caller will commit atomically
        logging.info(f"Trick {number} created (will commit with transaction)")
        return new_trick
    
    async def create_active_trick(self, session: AsyncSession) -> Trick:
        """Create a new active trick and commit immediately."""
        new_trick = await self.create_active_trick_in_transaction(session=session)
        await session.commit()
        await session.refresh(new_trick)
        logging.info(f"Trick {new_trick.number} committed")
        return new_trick

    async def get_group(self) -> Group:
        sitting: Sitting = await self.awaitable_attrs.sitting
        group: Group = await sitting.awaitable_attrs.group
        return group


def active_index(
    game_number: int,
    trick_number: int,
    play_number: int,
    tricks_per_game: int = 10,
    plays_per_trick: int = 4,
    players: int = 4,
) -> int:
    """game_number starts at 0, trick_number starts at 0, play_number starts at 0"""

    overall_play_number = (game_number * tricks_per_game) + (trick_number * plays_per_trick) + play_number
    active_player_number = overall_play_number % players
    return active_player_number


class Trick(Crud, AuditMixin, IdMixin):
    """A Trick is what a player can win when each of the 4 players of the group played their card."""

    # todo: add validator: 0 <= number <= 9
    number: Mapped[int] = mapped_column()
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("game.id"))
    active: Mapped[bool] = mapped_column(default=True)
    winning_player_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    game: Mapped[Game] = relationship(back_populates="tricks")
    plays: Mapped[list[Play]] = relationship(back_populates="trick")

    async def next_player_up(self, session: AsyncSession) -> Player:
        """The player that is supposed to play the next card."""

        plays: list[Play] = await self.awaitable_attrs.plays
        game: Game = await self.awaitable_attrs.game
        sitting: Sitting = await game.awaitable_attrs.sitting
        order = [
            sitting.sequence_player_0_id,
            sitting.sequence_player_1_id,
            sitting.sequence_player_2_id,
            sitting.sequence_player_3_id,
        ]
        
        # If this is the first card of the trick and it's not the first trick,
        # the winner of the previous trick should start
        if len(plays) == 0 and self.number > 0:
            # Get the previous trick
            result = await session.execute(
                select(Trick).where(
                    Trick.game_id == self.game_id,
                    Trick.number == self.number - 1
                )
            )
            previous_trick = result.scalar_one_or_none()
            if previous_trick and previous_trick.winning_player_id:
                logging.info(f"Trick {self.number}: Using previous trick winner (player_id: {previous_trick.winning_player_id}) to start")
                active_player = await Player.from_id(session=session, id=previous_trick.winning_player_id)
                return active_player
            else:
                logging.warning(f"Trick {self.number}: Previous trick has no winner! previous_trick={previous_trick}")
        
        # For first card of first trick or continuing within a trick, use the existing logic
        if len(plays) == 0:
            # First card of first trick - use original rotation
            active_player_id = order[
                active_index(
                    game_number=game.number,
                    trick_number=self.number,
                    play_number=0,
                )
            ]
        else:
            # Not the first card - continue with the order from whoever started this trick
            first_play = plays[0]
            first_player_id = first_play.player_id
            first_player_index = order.index(first_player_id)
            active_player_index = (first_player_index + len(plays)) % 4
            active_player_id = order[active_player_index]
            
        active_player = await Player.from_id(session=session, id=active_player_id)
        return active_player

    async def get_game(self) -> Game:
        game: Game = await self.awaitable_attrs.game
        return game

    async def determine_winner(self, session: AsyncSession) -> uuid.UUID:
        """Determine the winner of this completed trick based on Doppelkopf rules."""
        plays: list[Play] = await self.awaitable_attrs.plays
        assert len(plays) == 4, "Trick must be complete to determine winner"
        
        # Convert plays to the format expected by the rules engine
        from doko.game.rules import Normal
        from doko.game.stack import Stack
        from doko.game.player import Player as GamePlayer
        from doko.game.card import Card, Suit, Rank
        
        ruleset = Normal()
        stack = Stack()
        
        # Build the stack with cards in play order
        for play in sorted(plays, key=lambda p: p.number):
            card_data = await play.awaitable_attrs.card
            
            # Convert string to enum values
            # Database stores suit as enum.value (e.g., "clubs") and rank as enum.name (e.g., "ace")
            suit = Suit(card_data.suit)
            rank = Rank[card_data.rank]  # Use bracket notation for enum by name
            
            # Determine if card is trump based on Doppelkopf rules
            # Trumps are: all Queens, all Jacks, all Diamonds, and Hearts Ten
            is_trump = (
                rank == Rank.queen or  # All queens are trump
                rank == Rank.jack or   # All jacks are trump
                suit == Suit.diamonds or  # All diamonds are trump
                (suit == Suit.hearts and rank == Rank.ten)  # Hearts ten is trump
            )
            card = Card(suit, rank, is_trump)
            logging.info(f"Play {play.number}: Player {play.player_id} played {rank.name} of {suit.value} - is_trump={is_trump}")
            
            # Create a simple player object for the rules engine
            game_player = GamePlayer(str(play.player_id))
            stack.add(game_player, card)
        
        # Log the stack before determining winner
        logging.info(f"Stack history: {[(p.name, str(c)) for p, c in stack.history]}")
        
        # Debug: Check if trump cards can be found in trump_rank
        for player, card in stack.history:
            if card.is_trump:
                if card in ruleset.trump_rank:
                    logging.info(f"  Trump card {card} found in trump_rank with rank {ruleset.trump_rank[card]}")
                else:
                    logging.error(f"  Trump card {card} NOT FOUND in trump_rank!")
                    # Try to find what's different
                    for trump_card in ruleset.trump_rank.keys():
                        if trump_card.suit == card.suit and trump_card.rank == card.rank:
                            logging.error(f"    Found matching trump by suit/rank: {trump_card}, is_trump={trump_card.is_trump}")
        
        # Use the rules engine to determine the winner
        winning_game_player = ruleset.winner(stack)
        winning_player_id = uuid.UUID(winning_game_player.name)
        
        logging.info(f"Winner determined: player_id={winning_player_id}, player_name={winning_game_player.name}")
        
        return winning_player_id

    async def close(self, session: AsyncSession) -> Trick:
        assert self.active
        
        # Determine the winner before closing
        plays: list[Play] = await self.awaitable_attrs.plays
        if len(plays) == 4 and not self.winning_player_id:
            self.winning_player_id = await self.determine_winner(session)
        
        self.active = False
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

class Play(Crud, AuditMixin, IdMixin):
    """A Play is the action of a player on their turn."""

    # todo: add player_id?
    # todo: add validator: 0 <= number <= 3
    number: Mapped[int] = mapped_column()
    trick_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trick.id"))
    player_id: Mapped[uuid.UUID] = mapped_column()  # no foreign key, we be fiiiine
    # bid: Mapped[int] = mapped_column()
    # ts_start: Mapped[datetime] = mapped_column()
    # ts_end: Mapped[datetime] = mapped_column()

    card: Mapped[PlayedCard] = relationship(back_populates="play")
    trick: Mapped[Trick] = relationship(back_populates="plays")

    async def get_trick(self) -> Trick:
        trick: Trick = await self.awaitable_attrs.trick
        return trick


# todo: Move the event stuff elsewhere!

async def broadcast_status_update(user_id: uuid.UUID, group_id: uuid.UUID, new_status: PlayerStatus) -> None:
    async with db.get_session() as session:
        user = await User.from_id(session=session, id=user_id)
        group = await Group.from_id(session=session, id=group_id)
        print(f'{user.name}: Changed status for {group.name} to "{new_status}"')
        all_users = await group.get_sorted_users()
        other_users = [u for u in all_users if u.id != user.id]
        for other_user in other_users:
            print(f"{user.name}: Notifying {other_user.name} about status update.")
            sse.EventStore[other_user.session_token][sse.Event.player_status_update].set()


async def broadcast_new_group(group_id: uuid.UUID) -> None:
    await asyncio.sleep(0.3)
    async with db.get_session() as session:
        group: Group = await Group.from_id(session=session, id=group_id)
        users = await group.get_sorted_users()
        for user in users:
            print(f"Notifying {user.name} about new group: {group_id}.")
            sse.EventStore[user.session_token][sse.Event.group_created].set()


async def broadcast_new_game(game_id: uuid.UUID) -> None:
    await asyncio.sleep(0.3)
    async with db.get_session() as session:
        game: Game = await Game.from_id(session=session, id=game_id)
        group = await game.get_group()
        users = await group.get_sorted_users()
        for user in users:
            print(f"Notifying {user.name} about new game: {game_id}.")
            sse.EventStore[user.session_token][sse.Event.game_created].set()

async def broadcast_game_closed(game_id: uuid.UUID) -> None:
    await asyncio.sleep(0.3)
    async with db.get_session() as session:
        game: Game = await Game.from_id(session=session, id=game_id)
        group = await game.get_group()
        users = await group.get_sorted_users()
        for user in users:
            print(f"Notifying {user.name} about closed game: {game_id}.")
            sse.EventStore[user.session_token][sse.Event.game_closed].set()



async def broadcast_new_played_card(card_id: uuid.UUID) -> None:
    await asyncio.sleep(0.3)
    async with db.get_session() as session:
        card: PlayedCard = await PlayedCard.from_id(session=session, id=card_id)
        play = await card.get_play()
        trick = await play.get_trick()
        game = await trick.get_game()
        group = await game.get_group()
        users = await group.get_sorted_users()
        for user in users:
            print(f"Notifying {user.name} about new Card: {card_id}.")
            sse.EventStore[user.session_token][sse.Event.card_played].set()


@event.listens_for(Player.status, "set", propagate=True)
def received_status_update(player: Player, new_status: PlayerStatus, *_) -> None:
    sse.add_task(broadcast_status_update(player.user_id, player.group_id, new_status))


@event.listens_for(Group, "after_insert", propagate=True)
def received_new_group(_, __, group: Group) -> None:
    sse.add_task(broadcast_new_group(group_id=group.id))


@event.listens_for(Game.active, "set", propagate=True)
def received_game_closed(game: Game, active: bool, *_) -> None:
    if not active:
        sse.add_task(broadcast_game_closed(game_id=game.id))


@event.listens_for(Game, "after_insert", propagate=True)
def received_new_game(_, __, game: Game) -> None:
    sse.add_task(broadcast_new_game(game_id=game.id))


@event.listens_for(PlayedCard, "after_insert", propagate=True)
def received_new_played_card(_, __, card: PlayedCard) -> None:
    sse.add_task(broadcast_new_played_card(card_id=card.id))
