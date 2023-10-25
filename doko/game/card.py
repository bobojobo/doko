from __future__ import annotations
from enum import Enum


class Rank(Enum):
    ace = 11
    ten = 10
    king = 4
    queen = 3
    jack = 2


class Suit(Enum):
    clubs = "clubs"  # "♣"
    spades = "spades"  # "♠"
    hearts = "hearts"  # "♥"
    diamonds = "diamonds"  # "♦"


class Card:
    suit: Suit
    rank: Rank
    is_trump: bool

    def __init__(self, suit: Suit, rank: Rank, is_trump: bool):
        self.suit = suit
        self.rank = rank
        self.is_trump = is_trump

    def __str__(self) -> str:
        return f"{self.suit.value} {self.rank.name}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Card):
            return (self.suit == other.suit) and (self.rank == other.rank)
        else:
            return False

    def __hash__(self) -> int:
        return hash(f"{self.suit.value}{self.rank.value}")


if __name__ == "__main__":
    deck: list[Card] = [
        Card(Suit.spades, Rank.ace, False),
        Card(Suit.spades, Rank.ten, False),
        Card(Suit.spades, Rank.king, False),
        Card(Suit.spades, Rank.queen, True),
        Card(Suit.spades, Rank.jack, True),
        Card(Suit.hearts, Rank.ace, False),
        Card(Suit.hearts, Rank.ten, True),
        Card(Suit.hearts, Rank.king, False),
        Card(Suit.hearts, Rank.queen, True),
        Card(Suit.hearts, Rank.jack, True),
        Card(Suit.diamonds, Rank.ace, True),
        Card(Suit.diamonds, Rank.ten, True),
        Card(Suit.diamonds, Rank.king, True),
        Card(Suit.diamonds, Rank.queen, True),
        Card(Suit.diamonds, Rank.jack, True),
        Card(Suit.clubs, Rank.ace, False),
        Card(Suit.clubs, Rank.ten, False),
        Card(Suit.clubs, Rank.king, False),
        Card(Suit.clubs, Rank.queen, True),
        Card(Suit.clubs, Rank.jack, True),
        Card(Suit.spades, Rank.ace, False),
        Card(Suit.spades, Rank.ten, False),
        Card(Suit.spades, Rank.king, False),
        Card(Suit.spades, Rank.queen, True),
        Card(Suit.spades, Rank.jack, True),
        Card(Suit.hearts, Rank.ace, False),
        Card(Suit.hearts, Rank.ten, True),
        Card(Suit.hearts, Rank.king, False),
        Card(Suit.hearts, Rank.queen, True),
        Card(Suit.hearts, Rank.jack, True),
        Card(Suit.diamonds, Rank.ace, True),
        Card(Suit.diamonds, Rank.ten, True),
        Card(Suit.diamonds, Rank.king, True),
        Card(Suit.diamonds, Rank.queen, True),
        Card(Suit.diamonds, Rank.jack, True),
        Card(Suit.clubs, Rank.ace, False),
        Card(Suit.clubs, Rank.ten, False),
        Card(Suit.clubs, Rank.king, False),
        Card(Suit.clubs, Rank.queen, True),
        Card(Suit.clubs, Rank.jack, True),
    ]

    print(len(deck))
    for card in deck:
        print(card)
