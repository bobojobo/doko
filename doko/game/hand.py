from doko.game.card import Card


class Hand:
    cards: list[Card]
    selected: int

    def __init__(self, cards: list[Card]) -> None:
        assert (n_cards := len(cards)) == 10, f"A hand starts with 10 cards, not {n_cards}."
        self.cards = cards
        self.selected = 0

    def __contains__(self, card: Card) -> bool:
        return card in self.cards

    def order(self) -> None:
        raise NotImplementedError

    def select(self, index: int) -> None:
        assert index <= len(self.cards), f"Card {index} is not selectable from {len(self.cards)} available cards."
        self.selected = index

    def play_selected(self) -> Card:
        return self.cards.pop(self.selected)


if __name__ == "__main__":
    from doko.game.card import Rank, Suit, Card

    hand1 = Hand(
        [
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
        ]
    )

    print([(card.rank.name, card.suit.value) for card in hand1.cards])
