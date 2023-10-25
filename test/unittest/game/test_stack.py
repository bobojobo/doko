import pytest

from doko.game.card import Card, Rank, Suit
from doko.game.player import Player
from doko.game.stack import Stack


# Fixtures for commonly used test cards
@pytest.fixture
def ace_spades():
    """Test card: Ace of Spades (non-trump)."""
    return Card(Suit.spades, Rank.ace, False)


@pytest.fixture
def ten_clubs():
    """Test card: Ten of Clubs (non-trump)."""
    return Card(Suit.clubs, Rank.ten, False)


@pytest.fixture
def queen_hearts():
    """Test card: Queen of Hearts (trump)."""
    return Card(Suit.hearts, Rank.queen, True)


@pytest.fixture
def jack_diamonds():
    """Test card: Jack of Diamonds (trump)."""
    return Card(Suit.diamonds, Rank.jack, True)


@pytest.fixture
def king_hearts():
    """Test card: King of Hearts (non-trump)."""
    return Card(Suit.hearts, Rank.king, False)


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
    return Player("Diana")


class TestStack:
    """Test class for Stack functionality."""

    def test_init(self):
        """Test Stack initialization."""
        stack = Stack()
        assert stack.history == []

    def test_add_single_card(self, player1, ace_spades):
        """Test adding a single card to the stack."""
        stack = Stack()
        stack.add(player1, ace_spades)
        
        assert len(stack.history) == 1
        assert stack.history[0] == (player1, ace_spades)

    def test_add_multiple_cards(self, player1, player2, ace_spades, queen_hearts):
        """Test adding multiple cards to the stack."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, queen_hearts)
        
        assert len(stack.history) == 2
        assert stack.history[0] == (player1, ace_spades)
        assert stack.history[1] == (player2, queen_hearts)

    def test_cards_empty_stack(self):
        """Test cards() method with empty stack."""
        stack = Stack()
        assert stack.cards() == []

    def test_cards_single_card(self, player1, ace_spades):
        """Test cards() method with single card."""
        stack = Stack()
        stack.add(player1, ace_spades)
        
        cards = stack.cards()
        assert len(cards) == 1
        assert cards[0] == ace_spades

    def test_cards_multiple_cards(self, player1, player2, player3, ace_spades, queen_hearts, jack_diamonds):
        """Test cards() method with multiple cards."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, queen_hearts)
        stack.add(player3, jack_diamonds)
        
        cards = stack.cards()
        assert len(cards) == 3
        assert cards[0] == ace_spades
        assert cards[1] == queen_hearts
        assert cards[2] == jack_diamonds

    def test_first_non_trump_first_card(self, player1, ace_spades):
        """Test first_non_trump() when first card is non-trump."""
        stack = Stack()
        stack.add(player1, ace_spades)
        
        player, card = stack.first_non_trump()
        assert player == player1
        assert card == ace_spades

    def test_first_non_trump_second_card(self, player1, player2, queen_hearts, ten_clubs):
        """Test first_non_trump() when second card is first non-trump."""
        stack = Stack()
        stack.add(player1, queen_hearts)  # trump
        stack.add(player2, ten_clubs)     # non-trump
        
        player, card = stack.first_non_trump()
        assert player == player2
        assert card == ten_clubs

    def test_first_non_trump_mixed_cards(self, player1, player2, player3, queen_hearts, jack_diamonds, king_hearts):
        """Test first_non_trump() with mixed trump and non-trump cards."""
        stack = Stack()
        stack.add(player1, queen_hearts)    # trump
        stack.add(player2, jack_diamonds)   # trump
        stack.add(player3, king_hearts)     # non-trump
        
        player, card = stack.first_non_trump()
        assert player == player3
        assert card == king_hearts

    def test_first_non_trump_no_non_trump_raises_exception(self, player1, player2, queen_hearts, jack_diamonds):
        """Test first_non_trump() raises exception when no non-trump cards."""
        stack = Stack()
        stack.add(player1, queen_hearts)
        stack.add(player2, jack_diamonds)
        
        with pytest.raises(Exception, match="No non_trump found"):
            stack.first_non_trump()

    def test_first_trump_first_card(self, player1, queen_hearts):
        """Test first_trump() when first card is trump."""
        stack = Stack()
        stack.add(player1, queen_hearts)
        
        player, card = stack.first_trump()
        assert player == player1
        assert card == queen_hearts

    def test_first_trump_second_card(self, player1, player2, ace_spades, jack_diamonds):
        """Test first_trump() when second card is first trump."""
        stack = Stack()
        stack.add(player1, ace_spades)      # non-trump
        stack.add(player2, jack_diamonds)   # trump
        
        player, card = stack.first_trump()
        assert player == player2
        assert card == jack_diamonds

    def test_first_trump_mixed_cards(self, player1, player2, player3, ace_spades, ten_clubs, queen_hearts):
        """Test first_trump() with mixed non-trump and trump cards."""
        stack = Stack()
        stack.add(player1, ace_spades)    # non-trump
        stack.add(player2, ten_clubs)     # non-trump
        stack.add(player3, queen_hearts)  # trump
        
        player, card = stack.first_trump()
        assert player == player3
        assert card == queen_hearts

    def test_first_trump_no_trump_raises_exception(self, player1, player2, ace_spades, ten_clubs):
        """Test first_trump() raises exception when no trump cards."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, ten_clubs)
        
        with pytest.raises(Exception, match="No trump found"):
            stack.first_trump()

    def test_all_non_trump_empty_stack(self):
        """Test all_non_trump() with empty stack."""
        stack = Stack()
        assert stack.all_non_trump() is True

    def test_all_non_trump_only_non_trump_cards(self, player1, player2, ace_spades, ten_clubs):
        """Test all_non_trump() when all cards are non-trump."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, ten_clubs)
        
        assert stack.all_non_trump() is True

    def test_all_non_trump_only_trump_cards(self, player1, player2, queen_hearts, jack_diamonds):
        """Test all_non_trump() when all cards are trump."""
        stack = Stack()
        stack.add(player1, queen_hearts)
        stack.add(player2, jack_diamonds)
        
        assert stack.all_non_trump() is False

    def test_all_non_trump_mixed_cards(self, player1, player2, ace_spades, queen_hearts):
        """Test all_non_trump() with mixed trump and non-trump cards."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, queen_hearts)
        
        assert stack.all_non_trump() is False

    def test_points_empty_stack(self):
        """Test points() calculation with empty stack."""
        stack = Stack()
        assert stack.points() == 0

    def test_points_single_card(self, player1, ace_spades):
        """Test points() calculation with single card."""
        stack = Stack()
        stack.add(player1, ace_spades)
        
        assert stack.points() == 11  # Ace value

    def test_points_multiple_cards(self, player1, player2, player3, ace_spades, queen_hearts, jack_diamonds):
        """Test points() calculation with multiple cards."""
        stack = Stack()
        stack.add(player1, ace_spades)    # 11 points
        stack.add(player2, queen_hearts)  # 3 points
        stack.add(player3, jack_diamonds) # 2 points
        
        assert stack.points() == 16  # 11 + 3 + 2

    def test_points_full_trick(self, player1, player2, player3, player4):
        """Test points() calculation with a full 4-card trick."""
        # Create cards with known point values
        ace_spades = Card(Suit.spades, Rank.ace, False)      # 11 points
        ten_hearts = Card(Suit.hearts, Rank.ten, True)       # 10 points
        king_clubs = Card(Suit.clubs, Rank.king, False)      # 4 points
        queen_diamonds = Card(Suit.diamonds, Rank.queen, True) # 3 points
        
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, ten_hearts)
        stack.add(player3, king_clubs)
        stack.add(player4, queen_diamonds)
        
        assert stack.points() == 28  # 11 + 10 + 4 + 3

    def test_stack_order_preservation(self, player1, player2, player3, ace_spades, queen_hearts, jack_diamonds):
        """Test that stack preserves the order of cards added."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, queen_hearts)
        stack.add(player3, jack_diamonds)
        
        # Check history order
        assert stack.history[0] == (player1, ace_spades)
        assert stack.history[1] == (player2, queen_hearts)
        assert stack.history[2] == (player3, jack_diamonds)
        
        # Check cards order
        cards = stack.cards()
        assert cards[0] == ace_spades
        assert cards[1] == queen_hearts
        assert cards[2] == jack_diamonds

    def test_add_same_player_multiple_times(self, player1, ace_spades, queen_hearts):
        """Test adding multiple cards from the same player (edge case)."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player1, queen_hearts)
        
        assert len(stack.history) == 2
        assert stack.history[0] == (player1, ace_spades)
        assert stack.history[1] == (player1, queen_hearts)

    def test_add_same_card_multiple_times(self, player1, player2, ace_spades):
        """Test adding the same card multiple times (edge case)."""
        stack = Stack()
        stack.add(player1, ace_spades)
        stack.add(player2, ace_spades)
        
        assert len(stack.history) == 2
        assert stack.history[0] == (player1, ace_spades)
        assert stack.history[1] == (player2, ace_spades)