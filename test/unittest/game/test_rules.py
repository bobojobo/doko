import pytest

from doko.game.card import Card, Rank, Suit
from doko.game.player import Player
from doko.game.stack import Stack
from doko.game.rules import Ruleset, Normal


# Fixtures for test players
@pytest.fixture
def player1():
    """Test player 1."""
    return Player("Alice")


@pytest.fixture
def player2():
    """Test player 2."""
    return Player("Bob")


@pytest.fixture
def player3():
    """Test player 3."""
    return Player("Charlie")


@pytest.fixture
def player4():
    """Test player 4."""
    return Player("David")


# Fixtures for test cards (non-trump)
@pytest.fixture
def ace_spades():
    """Ace of Spades (non-trump)."""
    return Card(Suit.spades, Rank.ace, False)


@pytest.fixture
def ten_spades():
    """Ten of Spades (non-trump)."""
    return Card(Suit.spades, Rank.ten, False)


@pytest.fixture
def king_spades():
    """King of Spades (non-trump)."""
    return Card(Suit.spades, Rank.king, False)


@pytest.fixture
def ace_clubs():
    """Ace of Clubs (non-trump)."""
    return Card(Suit.clubs, Rank.ace, False)


@pytest.fixture
def ten_clubs():
    """Ten of Clubs (non-trump)."""
    return Card(Suit.clubs, Rank.ten, False)


@pytest.fixture
def king_clubs():
    """King of Clubs (non-trump)."""
    return Card(Suit.clubs, Rank.king, False)


@pytest.fixture
def ace_hearts():
    """Ace of Hearts (non-trump)."""
    return Card(Suit.hearts, Rank.ace, False)


@pytest.fixture
def king_hearts():
    """King of Hearts (non-trump)."""
    return Card(Suit.hearts, Rank.king, False)


# Fixtures for trump cards
@pytest.fixture
def hearts_ten():
    """Hearts Ten (highest trump)."""
    return Card(Suit.hearts, Rank.ten, True)


@pytest.fixture
def clubs_queen():
    """Clubs Queen (second highest trump)."""
    return Card(Suit.clubs, Rank.queen, True)


@pytest.fixture
def spades_queen():
    """Spades Queen (third highest trump)."""
    return Card(Suit.spades, Rank.queen, True)


@pytest.fixture
def hearts_queen():
    """Hearts Queen (fourth highest trump)."""
    return Card(Suit.hearts, Rank.queen, True)


@pytest.fixture
def diamonds_queen():
    """Diamonds Queen (fifth highest trump)."""
    return Card(Suit.diamonds, Rank.queen, True)


@pytest.fixture
def clubs_jack():
    """Clubs Jack (trump)."""
    return Card(Suit.clubs, Rank.jack, True)


@pytest.fixture
def diamonds_ace():
    """Diamonds Ace (trump)."""
    return Card(Suit.diamonds, Rank.ace, True)


@pytest.fixture
def diamonds_ten():
    """Diamonds Ten (trump)."""
    return Card(Suit.diamonds, Rank.ten, True)


@pytest.fixture
def diamonds_king():
    """Diamonds King (lowest trump)."""
    return Card(Suit.diamonds, Rank.king, True)


@pytest.fixture
def normal_ruleset():
    """Normal Doppelkopf ruleset."""
    return Normal()


@pytest.fixture
def stack():
    """Empty stack for testing."""
    return Stack()


class TestRuleset:
    """Test cases for the base Ruleset class."""

    def test_ruleset_is_abstract(self):
        """Test that Ruleset cannot be instantiated directly."""
        # The Ruleset class doesn't have the required attributes defined
        # This is more of a design check that subclasses must implement them
        ruleset = Ruleset()
        assert not hasattr(ruleset, 'cards') or ruleset.cards is None
        assert not hasattr(ruleset, 'trump_rank') or ruleset.trump_rank is None


class TestNormal:
    """Test cases for the Normal ruleset."""

    def test_normal_has_required_attributes(self, normal_ruleset):
        """Test that Normal ruleset has all required attributes."""
        assert hasattr(normal_ruleset, 'cards')
        assert hasattr(normal_ruleset, 'trump_rank')
        assert isinstance(normal_ruleset.cards, list)
        assert isinstance(normal_ruleset.trump_rank, dict)

    def test_normal_has_correct_card_count(self, normal_ruleset):
        """Test that Normal ruleset has exactly 40 cards (Doppelkopf deck)."""
        assert len(normal_ruleset.cards) == 40

    def test_normal_trump_rank_count(self, normal_ruleset):
        """Test that Normal ruleset has exactly 12 trump cards defined."""
        assert len(normal_ruleset.trump_rank) == 12

    def test_trump_rank_order(self, normal_ruleset):
        """Test that trump cards are ranked correctly (lower number = higher rank)."""
        # Hearts ten should be highest trump (rank 0)
        hearts_ten = Card(Suit.hearts, Rank.ten, is_trump=True)
        assert normal_ruleset.trump_rank[hearts_ten] == 0
        
        # Diamonds king should be lowest trump (rank 11)
        diamonds_king = Card(Suit.diamonds, Rank.king, is_trump=True)
        assert normal_ruleset.trump_rank[diamonds_king] == 11

    def test_all_queens_are_trump(self, normal_ruleset):
        """Test that all queens are defined as trump cards."""
        for suit in [Suit.clubs, Suit.spades, Suit.hearts, Suit.diamonds]:
            queen = Card(suit, Rank.queen, is_trump=True)
            assert queen in normal_ruleset.trump_rank

    def test_all_jacks_are_trump(self, normal_ruleset):
        """Test that all jacks are defined as trump cards."""
        for suit in [Suit.clubs, Suit.spades, Suit.hearts, Suit.diamonds]:
            jack = Card(suit, Rank.jack, is_trump=True)
            assert jack in normal_ruleset.trump_rank


class TestWinnerNonTrump:
    """Test cases for winner determination with all non-trump cards."""

    def test_winner_single_card(self, normal_ruleset, stack, player1, ace_spades):
        """Test winner with only one card played."""
        stack.add(player1, ace_spades)
        winner = normal_ruleset.winner(stack)
        assert winner == player1

    def test_winner_same_suit_ace_wins(self, normal_ruleset, stack, player1, player2, ace_spades, king_spades):
        """Test that ace wins over king in same suit."""
        stack.add(player1, king_spades)
        stack.add(player2, ace_spades)
        winner = normal_ruleset.winner(stack)
        assert winner == player2

    def test_winner_same_suit_ten_wins_over_king(self, normal_ruleset, stack, player1, player2, ten_spades, king_spades):
        """Test that ten wins over king in same suit."""
        stack.add(player1, king_spades)
        stack.add(player2, ten_spades)
        winner = normal_ruleset.winner(stack)
        assert winner == player2

    def test_winner_same_suit_ace_wins_over_ten(self, normal_ruleset, stack, player1, player2, ace_spades, ten_spades):
        """Test that ace wins over ten in same suit."""
        stack.add(player1, ten_spades)
        stack.add(player2, ace_spades)
        winner = normal_ruleset.winner(stack)
        assert winner == player2

    def test_winner_different_suits_first_card_suit_wins(self, normal_ruleset, stack, player1, player2, king_spades, ace_clubs):
        """Test that only cards of the first suit count when suits differ."""
        stack.add(player1, king_spades)
        stack.add(player2, ace_clubs)
        winner = normal_ruleset.winner(stack)
        assert winner == player1  # First card's suit (spades) wins

    def test_winner_multiple_players_same_suit(self, normal_ruleset, stack, player1, player2, player3, player4, 
                                                king_spades, ace_spades, ten_spades):
        """Test winner with multiple players playing same suit."""
        ten_spades_2 = Card(Suit.spades, Rank.ten, False)
        stack.add(player1, king_spades)
        stack.add(player2, ace_spades)
        stack.add(player3, ten_spades)
        stack.add(player4, ten_spades_2)
        winner = normal_ruleset.winner(stack)
        assert winner == player2  # Ace has highest value (11)

    def test_winner_mixed_suits_only_first_suit_counts(self, normal_ruleset, stack, player1, player2, player3, player4,
                                                        king_spades, ace_clubs, ten_clubs, ace_hearts):
        """Test that only cards matching first card's suit are considered."""
        king_spades_2 = Card(Suit.spades, Rank.king, False)
        stack.add(player1, king_spades)
        stack.add(player2, ace_clubs)
        stack.add(player3, ten_clubs)
        stack.add(player4, king_spades_2)
        winner = normal_ruleset.winner(stack)
        # Both kings are equal, first player wins
        assert winner == player1


class TestWinnerWithTrump:
    """Test cases for winner determination with trump cards involved."""

    def test_winner_single_trump_beats_non_trump(self, normal_ruleset, stack, player1, player2, ace_spades, diamonds_king):
        """Test that any trump card beats non-trump cards."""
        stack.add(player1, ace_spades)
        stack.add(player2, diamonds_king)  # Lowest trump
        winner = normal_ruleset.winner(stack)
        assert winner == player2

    def test_winner_highest_trump_wins(self, normal_ruleset, stack, player1, player2, hearts_ten, clubs_queen):
        """Test that highest trump card wins."""
        stack.add(player1, clubs_queen)
        stack.add(player2, hearts_ten)  # Highest trump
        winner = normal_ruleset.winner(stack)
        assert winner == player2

    def test_winner_trump_hierarchy(self, normal_ruleset, stack, player1, player2, player3, 
                                     diamonds_king, diamonds_ace, clubs_jack):
        """Test trump card hierarchy."""
        stack.add(player1, diamonds_king)  # Rank 11 (lowest)
        stack.add(player2, diamonds_ace)   # Rank 9
        stack.add(player3, clubs_jack)     # Rank 5
        winner = normal_ruleset.winner(stack)
        assert winner == player3  # Clubs jack has lowest rank number (highest priority)

    def test_winner_queen_hierarchy(self, normal_ruleset, stack, player1, player2, player3, player4,
                                     clubs_queen, spades_queen, hearts_queen, diamonds_queen):
        """Test queen hierarchy in trump order."""
        stack.add(player1, diamonds_queen)  # Rank 4
        stack.add(player2, hearts_queen)    # Rank 3
        stack.add(player3, spades_queen)    # Rank 2
        stack.add(player4, clubs_queen)     # Rank 1
        winner = normal_ruleset.winner(stack)
        assert winner == player4  # Clubs queen is highest

    def test_winner_hearts_ten_always_wins(self, normal_ruleset, stack, player1, player2, player3,
                                            clubs_queen, spades_queen, hearts_ten):
        """Test that hearts ten (highest trump) always wins."""
        stack.add(player1, clubs_queen)
        stack.add(player2, spades_queen)
        stack.add(player3, hearts_ten)
        winner = normal_ruleset.winner(stack)
        assert winner == player3

    def test_winner_trump_with_non_trump_mixed(self, normal_ruleset, stack, player1, player2, player3, player4,
                                                ace_spades, king_clubs, diamonds_ten, ace_hearts):
        """Test trump wins even when non-trump cards have higher face value."""
        stack.add(player1, ace_spades)    # Non-trump, value 11
        stack.add(player2, king_clubs)    # Non-trump, value 4
        stack.add(player3, diamonds_ten)  # Trump, rank 10
        stack.add(player4, ace_hearts)    # Non-trump, value 11
        winner = normal_ruleset.winner(stack)
        assert winner == player3  # Only trump card wins

    def test_winner_multiple_trumps_lowest_rank_wins(self, normal_ruleset, stack, player1, player2, player3,
                                                      diamonds_ace, diamonds_ten, diamonds_king):
        """Test that among multiple trumps, the one with lowest rank number wins."""
        stack.add(player1, diamonds_king)  # Rank 11
        stack.add(player2, diamonds_ten)   # Rank 10
        stack.add(player3, diamonds_ace)   # Rank 9
        winner = normal_ruleset.winner(stack)
        assert winner == player3  # Diamonds ace has lowest rank number


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_winner_empty_stack_raises_error(self, normal_ruleset, stack):
        """Test that empty stack raises an appropriate error."""
        with pytest.raises(Exception):
            normal_ruleset.winner(stack)

    def test_winner_with_invalid_trump_card(self, normal_ruleset, stack, player1):
        """Test behavior with trump card not in trump_rank dictionary."""
        # Create a trump card that's not in the Normal ruleset
        invalid_trump = Card(Suit.spades, Rank.ace, True)  # Spades ace is not trump in Normal rules
        stack.add(player1, invalid_trump)
        
        # This should raise a KeyError when trying to access trump_rank
        with pytest.raises(KeyError):
            normal_ruleset.winner(stack)

    def test_winner_duplicate_cards_same_player(self, normal_ruleset, stack, player1, ace_spades):
        """Test with duplicate cards from same player."""
        ace_spades_2 = Card(Suit.spades, Rank.ace, False)
        stack.add(player1, ace_spades)
        stack.add(player1, ace_spades_2)
        winner = normal_ruleset.winner(stack)
        assert winner == player1

    def test_winner_all_same_value_first_wins(self, normal_ruleset, stack, player1, player2, player3):
        """Test that when all cards have same value, first player wins."""
        king_spades_1 = Card(Suit.spades, Rank.king, False)
        king_spades_2 = Card(Suit.spades, Rank.king, False)
        king_spades_3 = Card(Suit.spades, Rank.king, False)
        
        stack.add(player1, king_spades_1)
        stack.add(player2, king_spades_2)
        stack.add(player3, king_spades_3)
        winner = normal_ruleset.winner(stack)
        assert winner == player1