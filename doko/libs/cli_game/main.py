from typing import List, Tuple
from enum import Enum
from random import shuffle

class Rank(Enum):
    ace = 11
    ten = 10
    king = 4
    queen = 3
    jack = 2


class Suit(Enum):
    clubs = "♣"
    spades = "♠"
    hearts = "♥"
    diamonds = "♦"


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


class Deck:
    cards: List[Card]

    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards
        self.shuffle()

    def shuffle(self) -> None:
        shuffle(self.cards)

    def hand_out(self) -> List[List[Card]]:
        return [self.cards[:10], self.cards[10:20], self.cards[20:30], self.cards[30:]]


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


class Ruleset:
    # depends on the Ruleset
    cards: list[Card]
    trump_rank: dict[Card, int]

    def winner(self, stack: Stack) -> Player:
        """
        All non-trump:
          First card decides colour. Highest of that colour wins
          ace (11) > ten (10) > king (4)

        At least one trump:
          Highest trump wins
        """

        if stack.all_non_trump():
            first_player, first_card = stack.first_non_trump()
            suit = first_card.suit

            highest_card = first_card
            winning_player = first_player
            for player, card in stack.history:
                if card.suit != suit:
                    continue
                if card.rank.value > highest_card.rank.value:
                    highest_card = card
                    winning_player = player

        else:
            winning_player, highest_card = stack.first_trump()
            for player, card in stack.history:
                if not card.is_trump:
                    continue
                if self.trump_rank[card] < self.trump_rank[highest_card]:
                    highest_card = card
                    winning_player = player

        return winning_player


class Normal(Ruleset):
    trump_rank: dict[Card, int] = {
        Card(Suit.hearts, Rank.ten, is_trump=True): 0,
        Card(Suit.clubs, Rank.queen, is_trump=True): 1,
        Card(Suit.spades, Rank.queen, is_trump=True): 2,
        Card(Suit.hearts, Rank.queen, is_trump=True): 3,
        Card(Suit.diamonds, Rank.queen, is_trump=True): 4,
        Card(Suit.clubs, Rank.jack, is_trump=True): 5,
        Card(Suit.spades, Rank.jack, is_trump=True): 6,
        Card(Suit.hearts, Rank.jack, is_trump=True): 7,
        Card(Suit.diamonds, Rank.jack, is_trump=True): 8,
        Card(Suit.diamonds, Rank.ace, is_trump=True): 9,
        Card(Suit.diamonds, Rank.ten, is_trump=True): 10,
        Card(Suit.diamonds, Rank.king, is_trump=True): 11,
    }

    cards: list[Card] = [
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


def set_players() -> List[Player]:
    return [Player("player_0"), Player("player_1"), Player("player_2"), Player("player_3")]


def run_turn(players: List[Player], ruleset: Ruleset) -> None:
    stack: Stack = Stack()
    for player in players:
        cards = {index: str(card) for index, card in enumerate(player.hand.cards)}
        card_index = int(input(f"{player.name}: select from {cards}"))
        player.select_card(card_index)
        stack.add(player, player.play_card())

    winner = ruleset.winner(stack)
    points = stack.points()
    print(f"Played cards: {[str(card) for card in stack.cards()]}")
    print(f"{points} points go to {winner.name}")


if __name__ == "__main__":
    players: List[Player] = set_players()
    ruleset = Normal()
    deck: Deck = Deck(ruleset.cards)

    for player, cards in zip(players, deck.hand_out()):
        player.hand_cards(cards)
    for n_turn in range(0, 10):
        run_turn(players, ruleset)
