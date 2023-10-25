from typing import List
from random import shuffle

from doko.game.card import Card


class Deck:
    cards: List[Card]

    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards
        self.shuffle()

    def shuffle(self) -> None:
        shuffle(self.cards)

    def hand_out(self) -> List[List[Card]]:
        assert len(self.cards) % 4 == 0, "This deck is not evenly divisible by the four players."
        cards_per_player: int = int(len(self.cards) / 4)
        return [
            self.cards[:cards_per_player],
            self.cards[cards_per_player : 2 * cards_per_player],
            self.cards[2 * cards_per_player : 3 * cards_per_player],
            self.cards[3 * cards_per_player :],
        ]


if __name__ == "__main__":
    from doko.game.card import Card, Suit, Rank

    cards: List[Card] = [
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
    deck = Deck(cards)

    print(len(deck.cards))
    print(deck.cards[0])

    deck.shuffle()

    print(len(deck.cards))
    print(deck.cards[0])
