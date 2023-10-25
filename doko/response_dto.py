"""
Server Response DTOs. These are the models that are used to fill in the templates. Inheriting from _Context marks first 
level objects. 

Rule of thumb here is favoring composition over inheritance if we iterate ovet the partial in the parent template. 
The reasoning behind this is how the template filling works. Putting a one-off Object into a dto for a partial 
template and putting a collection of these Objects into the Dto for the Parent Template makes the namespacing very 
clear and avoid annoying extractions of thes objects in the parent template.     

# todo: naming convention? Prefix everything accordingly? Probably a good idea....
"""

from enum import StrEnum

from pydantic import BaseModel, Field, computed_field

from doko.libs import password_utils


class ResponseDto(BaseModel):
    """Subclasses of this are first level models for the html templates."""


class PlayerStatusSymbol(StrEnum):
    offline = "🔴"
    online = "🟡"
    ready = "🟢"


class Login(ResponseDto):
    failure: bool = Field(default=False)


class RegistrationPartialUsername(ResponseDto):
    first_load: bool = Field(default=True)
    username: str = Field(default="")
    username_is_taken: bool = Field(default=False)

    @computed_field  # type: ignore
    @property
    def username_is_invalid(self) -> bool:
        # todo: make regex and a real function and whatnot
        return self.username in ["#", "+", ""]


class RegistrationPartialPassword(ResponseDto):
    password: str = Field(default="")

    @computed_field  # type: ignore
    @property
    def password_is_valid(self) -> bool:
        return password_utils.is_valid_password(self.password)


class RegistrationPartialPasswordValidation(RegistrationPartialPassword):
    password_validation: str = Field(default="")

    @computed_field  # type: ignore
    @property
    def password_matches(self) -> bool:
        return self.password_validation == self.password


class Registration(RegistrationPartialUsername, RegistrationPartialPasswordValidation):
    ...


class RegistrationPartialSuccess(ResponseDto):
    ...


class GroupPartialPlayers(ResponseDto):
    playernames: list[str]
    # todo: use pydantic validator here? Should be 4


class GroupPartialGroups(ResponseDto):
    groupnames: list[str]
    has_groups: bool
    # todo: use pydantic validator here


class Group(GroupPartialPlayers, GroupPartialGroups):
    username: str


class GroupCreatePartialGroupname(ResponseDto):
    groupname_is_taken: bool
    groupname: str


class _GroupCreatePartialUsername(BaseModel):
    name: str
    number: int  # 0, 1 or 2     -> todo: pydantic validator
    exists: bool
    is_the_user: bool
    is_already_used: bool


# no inheritance, because it doesnt work well with the list of users in the non partial
class GroupCreatePartialUsername(ResponseDto):
    user: _GroupCreatePartialUsername


class GroupCreate(ResponseDto):
    username: str
    users: list[_GroupCreatePartialUsername]


class WaitingPlayer(BaseModel):
    name: str
    status: str


class WaitingUpdate(ResponseDto):
    username: str
    players: list[WaitingPlayer]
    all_ready: bool
    game_id: str = Field(default="")


class Waiting(WaitingUpdate):
    groupname: str


class GameCard(BaseModel):
    suit: str
    rank: str
    id: str

class GameCardTrick(GameCard):
    blocked: bool
    # player/owner
    # is_winning


class GameCardHand(GameCard):
    is_playable: bool


class _GamePartialStack(BaseModel):
    cards: list[GameCardTrick]
    # next player?

    @computed_field  # type: ignore
    @property
    def is_full(self) -> bool:
        return len(self.cards) == 4

    @computed_field  # type: ignore
    @property
    def is_empty(self) -> bool:
        return len(self.cards) == 0

    @computed_field  # type: ignore
    @property
    def n_cards(self) -> int:
        return len(self.cards)


class _GamePartialHand(BaseModel):
    cards: list[GameCardHand]


class GamePartialHand(ResponseDto):
    hand: _GamePartialHand


class GamePartialStack(ResponseDto):
    stack: _GamePartialStack


class Game(ResponseDto):
    username: str
    game_id: str
    hand: _GamePartialHand
    stack: _GamePartialStack
    player1: str
    player2: str
    player3: str


class Error(ResponseDto):
    reason: str
    status_code: int
    status_code_description: str
