from typing import List, Tuple

from doko.game.card import Card
from doko.game.player import Player


class Stack:
    history: List[Tuple[Player, Card]]

    def __init__(self) -> None:
        self.history: List[Tuple[Player, Card]] = []

    def add(self, player: Player, card: Card) -> None:
        self.history.append((player, card))

    def cards(self) -> List[Card]:
        return [card[1] for card in self.history]

    def first_non_trump(self) -> Tuple[Player, Card]:
        for index, card in enumerate(self.cards()):
            if not card.is_trump:
                return self.history[index]
        raise Exception("No non_trump found")

    def first_trump(self) -> Tuple[Player, Card]:
        for index, card in enumerate(self.cards()):
            if card.is_trump:
                return self.history[index]
        raise Exception("No trump found")

    def all_non_trump(self) -> bool:
        return not any(card.is_trump for card in self.cards())

    def points(self) -> int:
        return sum([card.rank.value for card in self.cards()])
