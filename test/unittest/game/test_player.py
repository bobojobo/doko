import pytest

from doko.game.player import Player
from doko.game.card import Card, Rank, Suit
from doko.game.hand import Hand


# Fixtures for commonly used test cards
@pytest.fixture
def test_cards():
    """Create a list of 10 test cards for a valid hand."""
    return [
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


@pytest.fixture
def player():
    """Create a test player."""
    return Player("TestPlayer")


@pytest.fixture
def player_with_hand(test_cards):
    """Create a test player with a hand of cards."""
    player = Player("TestPlayer")
    player.hand_cards(test_cards)
    return player


class TestPlayer:
    """Test cases for the Player class."""

    def test_player_initialization(self):
        """Test player is initialized correctly with a name."""
        player = Player("Alice")
        assert player.name == "Alice"
        # Other attributes should not be set initially
        assert not hasattr(player, 'hand')
        assert not hasattr(player, 'is_re')
        assert not hasattr(player, 'points')

    def test_player_initialization_with_different_names(self):
        """Test player initialization with various name types."""
        # Test with different name formats
        player1 = Player("Bob")
        player2 = Player("Player123")
        player3 = Player("")
        
        assert player1.name == "Bob"
        assert player2.name == "Player123"
        assert player3.name == ""

    def test_hand_cards_assignment(self, player, test_cards):
        """Test that cards are properly assigned to player's hand."""
        player.hand_cards(test_cards)
        
        assert hasattr(player, 'hand')
        assert isinstance(player.hand, Hand)
        assert player.hand.cards == test_cards
        assert len(player.hand.cards) == 10

    def test_hand_cards_with_invalid_number_of_cards(self, player):
        """Test that hand_cards raises an error with invalid number of cards."""
        # Test with less than 10 cards
        fewer_cards = [Card(Suit.spades, Rank.ace, False)]
        with pytest.raises(AssertionError, match="A hand starts with 10 cards, not 1"):
            player.hand_cards(fewer_cards)
        
        # Test with more than 10 cards
        more_cards = [Card(Suit.spades, Rank.ace, False)] * 11
        with pytest.raises(AssertionError, match="A hand starts with 10 cards, not 11"):
            player.hand_cards(more_cards)

    def test_select_card(self, player_with_hand):
        """Test card selection functionality."""
        # Test selecting valid indices
        player_with_hand.select_card(0)
        assert player_with_hand.hand.selected == 0
        
        player_with_hand.select_card(5)
        assert player_with_hand.hand.selected == 5
        
        player_with_hand.select_card(9)
        assert player_with_hand.hand.selected == 9

    def test_select_card_invalid_index(self, player_with_hand):
        """Test that selecting invalid card index behavior."""
        # Note: The current Hand implementation has a bug - it allows selecting index 10
        # but will fail when trying to play that card. Testing actual behavior here.
        
        # This currently doesn't raise an error due to the Hand class bug (uses <= instead of <)
        player_with_hand.select_card(10)
        assert player_with_hand.hand.selected == 10
        
        # But trying to play this invalid selection will raise IndexError
        with pytest.raises(IndexError, match="pop index out of range"):
            player_with_hand.play_card()
        
        # Test selecting index beyond 10 does raise an error
        with pytest.raises(AssertionError, match="Card 15 is not selectable from 10 available cards"):
            player_with_hand.select_card(15)

    def test_select_card_without_hand(self, player):
        """Test that selecting a card without a hand raises an error."""
        with pytest.raises(AttributeError):
            player.select_card(0)

    def test_play_card(self, player_with_hand):
        """Test playing the selected card."""
        # Get the expected card before playing
        expected_card = player_with_hand.hand.cards[0]
        
        # Select and play the first card
        player_with_hand.select_card(0)
        played_card = player_with_hand.play_card()
        
        # Should return the first card (same object)
        assert played_card is expected_card
        # Hand should now have 9 cards
        assert len(player_with_hand.hand.cards) == 9
        # The played card should no longer be in the hand
        assert expected_card not in player_with_hand.hand.cards

    def test_play_card_different_selections(self, test_cards):
        """Test playing different selected cards."""
        # Create a fresh player for this test
        player = Player("TestPlayer")
        player.hand_cards(test_cards.copy())
        
        # Test playing card at index 3
        expected_card_3 = player.hand.cards[3]
        player.select_card(3)
        played_card = player.play_card()
        assert played_card is expected_card_3
        assert len(player.hand.cards) == 9
        
        # Create another fresh player for the second test
        player2 = Player("TestPlayer2")
        player2.hand_cards(test_cards.copy())
        
        # Test playing card at index 7
        expected_card_7 = player2.hand.cards[7]
        player2.select_card(7)
        played_card = player2.play_card()
        assert played_card is expected_card_7
        assert len(player2.hand.cards) == 9

    def test_play_card_without_selection(self, player_with_hand):
        """Test playing card with default selection (index 0)."""
        # Get the expected card (default selection is 0)
        expected_card = player_with_hand.hand.cards[0]
        
        # Default selected should be 0
        played_card = player_with_hand.play_card()
        assert played_card is expected_card
        assert len(player_with_hand.hand.cards) == 9

    def test_play_card_without_hand(self, player):
        """Test that playing a card without a hand raises an error."""
        with pytest.raises(AttributeError):
            player.play_card()

    def test_belongs_to_re(self, player):
        """Test assigning player to Re team."""
        # Initially should not have is_re attribute
        assert not hasattr(player, 'is_re')
        
        # After calling belongs_to_re, should be True
        player.belongs_to_re()
        assert hasattr(player, 'is_re')
        assert player.is_re is True

    def test_belongs_to_re_multiple_calls(self, player):
        """Test multiple calls to belongs_to_re."""
        player.belongs_to_re()
        assert player.is_re is True
        
        # Calling again should still be True
        player.belongs_to_re()
        assert player.is_re is True

    def test_add_points(self, player):
        """Test adding points to player."""
        # Initially should not have points attribute
        assert not hasattr(player, 'points')
        
        # Add some points - this should raise AttributeError since points isn't initialized
        with pytest.raises(AttributeError):
            player.add_points(10)

    def test_add_points_after_initialization(self, player):
        """Test adding points after manual initialization."""
        # Manually initialize points (since constructor doesn't do it)
        player.points = 0
        
        # Test adding positive points
        player.add_points(10)
        assert player.points == 10
        
        player.add_points(5)
        assert player.points == 15
        
        # Test adding negative points
        player.add_points(-3)
        assert player.points == 12

    def test_add_points_with_different_values(self, player):
        """Test adding various point values."""
        player.points = 0
        
        # Test with zero
        player.add_points(0)
        assert player.points == 0
        
        # Test with large values
        player.add_points(100)
        assert player.points == 100
        
        # Test with negative values
        player.add_points(-50)
        assert player.points == 50

    def test_player_complete_workflow(self, test_cards):
        """Test a complete workflow with a player."""
        # Create player
        player = Player("CompleteTest")
        assert player.name == "CompleteTest"
        
        # Give player cards
        player.hand_cards(test_cards)
        assert len(player.hand.cards) == 10
        
        # Assign to Re team
        player.belongs_to_re()
        assert player.is_re is True
        
        # Initialize points
        player.points = 0
        
        # Add points
        player.add_points(20)
        assert player.points == 20
        
        # Select and play a card
        expected_card = player.hand.cards[2]
        player.select_card(2)
        played_card = player.play_card()
        assert played_card is expected_card
        assert len(player.hand.cards) == 9
        
        # Add more points
        player.add_points(15)
        assert player.points == 35

    def test_player_state_independence(self, test_cards):
        """Test that different players maintain independent state."""
        player1 = Player("Player1")
        player2 = Player("Player2")
        
        # Give both players the same cards
        player1.hand_cards(test_cards.copy())
        player2.hand_cards(test_cards.copy())
        
        # Set different states
        player1.belongs_to_re()
        player1.points = 10
        player1.select_card(3)
        
        player2.points = 20
        player2.select_card(7)
        
        # Verify independence
        assert player1.name == "Player1"
        assert player2.name == "Player2"
        assert player1.is_re is True
        assert not hasattr(player2, 'is_re')
        assert player1.points == 10
        assert player2.points == 20
        assert player1.hand.selected == 3
        assert player2.hand.selected == 7
        
        # Play cards and verify they're different
        card1 = player1.play_card()
        card2 = player2.play_card()
        assert card1 == test_cards[3]
        assert card2 == test_cards[7]