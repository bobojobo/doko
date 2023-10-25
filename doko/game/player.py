from doko.game.hand import Hand
from doko.game.card import Card


class Player:
    name: str
    hand: Hand
    is_re: bool
    points: int

    def __init__(self, name: str) -> None:
        self.name = name

    def hand_cards(self, cards: list[Card]) -> None:
        self.hand = Hand(cards)

    def select_card(self, index: int) -> None:
        self.hand.select(index)

    def play_card(self) -> Card:
        return self.hand.play_selected()

    def belongs_to_re(self) -> None:
        self.is_re = True

    def add_points(self, points: int) -> None:
        self.points += points


if __name__ == "__main__":
    player1 = Player("Anon")
    print(player1.name)
