""" 
Client request dtos
These are the models of the data received from the user/client/browser/frontend/.
These are simple dataclasses and we don't do custom validation on them. We prefer to act accordingly on each error
since there is no one solution fits all for this. Some validation is done by FastAPI already, since these models get 
translated into pydantic which provides runtime type validation.     

Also note how we see these two cases in our models:
    * var = Form("") 
    * var = "" 
One is from actual forms and the other from additional htmx functionalilty using non-standard html keywords.

No Inheritance here. Why? take a form like the group creation as example. We want to check that 4 different players
are entered in the form before we allow the user to click the submit/create button. So for we early validation we need
to allow for a default value. But for the final button we need to receive the same data on the backeend, but we can't
allow for default values here. This needs to raise.    
"""

from dataclasses import dataclass
from fastapi import Form

# todo: do I need to add some security validation in a baseclass here?
# todo: add docstings to these.


# /login
@dataclass(frozen=True, kw_only=True)
class Login:
    username: str = Form(...)
    password: str = Form(...)


# /registration
# todo: rename the /register to registration. only difference is: one is a post and the other is a get.
#       Or reanme the other way around
@dataclass(frozen=True, kw_only=True)
class Register:
    username: str = Form(...)
    password: str = Form(...)
    password_validation: str = Form(...)


@dataclass(frozen=True, kw_only=True)
class RegistrationUsername:
    username: str = Form(...)


@dataclass(frozen=True, kw_only=True)
class RegistrationPassword:
    password: str = Form("")


@dataclass(frozen=True, kw_only=True)
class RegistrationPasswordValidation:
    password: str = Form("")
    password_validation: str = Form("")


# /group
@dataclass(frozen=True, kw_only=True)
class Group:
    groupname: str = ""


@dataclass(frozen=True, kw_only=True)
class GroupPlayers:
    groupname: str = ""


@dataclass(frozen=True, kw_only=True)
class GroupUpdatePlayers:
    groupname: str = ""


@dataclass(frozen=True, kw_only=True)
class GroupCreate:
    groupname: str = Form("")
    username_0: str = Form("")
    username_1: str = Form("")
    username_2: str = Form("")


@dataclass(frozen=True, kw_only=True)
class GroupCreateGroupname:
    groupname: str = Form()


@dataclass(frozen=True, kw_only=True)
class GroupCreateUsername:
    username_0: str = Form("")
    username_1: str = Form("")
    username_2: str = Form("")
    player_number: str = ""


# /waiting
@dataclass(frozen=True, kw_only=True)
class Waiting:
    groupname: str = ""


# /game
@dataclass(frozen=True, kw_only=True)
class GameCard:
    suit: str = Form(...)
    rank: str = Form(...)


@dataclass(frozen=True, kw_only=True)
class GameHandcard(GameCard):
    pass


@dataclass(frozen=True, kw_only=True)
class GameStackcard(GameCard):
    pass


@dataclass(frozen=True, kw_only=True)
class Game:
    my_turn: bool
    handcards: list[GameHandcard]
    stackcards: list[GameStackcard]
    player: str
    player1: str
    player2: str
    player3: str
