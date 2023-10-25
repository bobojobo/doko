from doko.game.card import Card, Suit, Rank
from doko.game.stack import Stack
from doko.game.player import Player


# https://de.wikipedia.org/wiki/Doppelkopf#Spielregeln_nach_den_Turnierspielregeln_des_DDV


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
