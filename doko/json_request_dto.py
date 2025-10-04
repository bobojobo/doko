"""
REST API request DTOs
These are the Pydantic models for JSON requests to the REST API.
They define the expected JSON structure for each endpoint.
"""

from pydantic import BaseModel
from typing import List, Optional


# Authentication
class JsonLogin(BaseModel):
    username: str
    password: str


# User registration
class JsonRegister(BaseModel):
    username: str
    password: str
    password_validation: str


# Groups
class JsonGroupCreate(BaseModel):
    groupname: str
    username_0: str = ""
    username_1: str = ""
    username_2: str = ""


class JsonWaiting(BaseModel):
    groupname: str


# Games
class JsonGameHandcard(BaseModel):
    suit: str
    rank: str


class JsonGameHandOrder(BaseModel):
    card_ids: List[str]  # List of card IDs in the new order


# Game Review
class JsonGameReviewReady(BaseModel):
    status: str
    groupname: str


# Legacy DTOs (kept for compatibility with existing logic)
class JsonGroup(BaseModel):
    groupname: str = ""


class JsonGroupPlayers(BaseModel):
    groupname: str = ""


class JsonRegistrationUsername(BaseModel):
    username: str


class JsonRegistrationPassword(BaseModel):
    password: str = ""


class JsonRegistrationPasswordValidation(BaseModel):
    password: str = ""
    password_validation: str = ""


class JsonGroupCreateGroupname(BaseModel):
    groupname: str


class JsonGroupCreateUsername(BaseModel):
    username_0: str = ""
    username_1: str = ""
    username_2: str = ""
    player_number: str = ""


class JsonGameCard(BaseModel):
    suit: str
    rank: str


class JsonGameStackcard(JsonGameCard):
    pass