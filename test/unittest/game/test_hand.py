import pytest

from doko.game.hand import Hand
from doko.game.card import Card, Rank, Suit


@pytest.fixture
def sample_hand_cards():
    """Create a sample set of 10 cards for testing hands."""
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
def valid_hand(sample_hand_cards):
    """Create a valid hand with 10 cards."""
    return Hand(sample_hand_cards.copy())


@pytest.fixture
def ace_spades():
    """Test card: Ace of Spades (non-trump)."""
    return Card(Suit.spades, Rank.ace, False)


@pytest.fixture
def queen_hearts():
    """Test card: Queen of Hearts (trump)."""
    return Card(Suit.hearts, Rank.queen, True)


@pytest.fixture
def king_clubs():
    """Test card: King of Clubs (non-trump) - not in sample hand."""
    return Card(Suit.clubs, Rank.king, False)


class TestHandInitialization:
    """Test cases for Hand initialization."""

    def test_valid_hand_creation(self, sample_hand_cards):
        """Test creating a hand with exactly 10 cards."""
        hand = Hand(sample_hand_cards)
        assert len(hand.cards) == 10
        assert hand.selected == 0
        assert hand.cards == sample_hand_cards

    def test_hand_creation_with_fewer_cards(self):
        """Test that creating a hand with fewer than 10 cards raises AssertionError."""
        cards = [
            Card(Suit.spades, Rank.ace, False),
            Card(Suit.spades, Rank.ten, False),
            Card(Suit.spades, Rank.king, False),
        ]
        with pytest.raises(AssertionError, match="A hand starts with 10 cards, not 3"):
            Hand(cards)

    def test_hand_creation_with_more_cards(self):
        """Test that creating a hand with more than 10 cards raises AssertionError."""
        cards = [Card(Suit.spades, Rank.ace, False) for _ in range(12)]
        with pytest.raises(AssertionError, match="A hand starts with 10 cards, not 12"):
            Hand(cards)

    def test_hand_creation_with_empty_list(self):
        """Test that creating a hand with no cards raises AssertionError."""
        with pytest.raises(AssertionError, match="A hand starts with 10 cards, not 0"):
            Hand([])

    def test_hand_creation_with_duplicate_cards(self):
        """Test creating a hand with duplicate cards is allowed."""
        cards = [Card(Suit.spades, Rank.ace, False) for _ in range(10)]
        hand = Hand(cards)
        assert len(hand.cards) == 10
        assert all(card.suit == Suit.spades and card.rank == Rank.ace for card in hand.cards)


class TestHandContains:
    """Test cases for the __contains__ method."""

    def test_contains_existing_card(self, valid_hand, ace_spades):
        """Test that a card in the hand is found."""
        assert ace_spades in valid_hand

    def test_contains_existing_trump_card(self, valid_hand, queen_hearts):
        """Test that a trump card in the hand is found."""
        assert queen_hearts in valid_hand

    def test_contains_non_existing_card(self, valid_hand, king_clubs):
        """Test that a card not in the hand is not found."""
        assert king_clubs not in valid_hand

    def test_contains_similar_card_different_trump_status(self, valid_hand):
        """Test that a card with same suit/rank but different trump status is found (Card equality ignores trump status)."""
        # Create a card similar to one in hand but with different trump status
        non_trump_queen_hearts = Card(Suit.hearts, Rank.queen, False)
        # The sample hand has Queen of Hearts as trump (True)
        # Card equality only considers suit and rank, not trump status
        assert non_trump_queen_hearts in valid_hand


class TestHandSelect:
    """Test cases for the select method."""

    def test_select_valid_index(self, valid_hand):
        """Test selecting a card with a valid index."""
        valid_hand.select(5)
        assert valid_hand.selected == 5

    def test_select_first_card(self, valid_hand):
        """Test selecting the first card (index 0)."""
        valid_hand.select(0)
        assert valid_hand.selected == 0

    def test_select_last_card(self, valid_hand):
        """Test selecting the last card (index 9)."""
        valid_hand.select(9)
        assert valid_hand.selected == 9

    def test_select_index_equal_to_hand_size(self, valid_hand):
        """Test selecting an index equal to hand size (should be valid)."""
        valid_hand.select(10)
        assert valid_hand.selected == 10

    def test_select_index_too_high(self, valid_hand):
        """Test that selecting an index beyond hand size raises AssertionError."""
        with pytest.raises(AssertionError, match="Card 11 is not selectable from 10 available cards"):
            valid_hand.select(11)

    def test_select_negative_index(self, valid_hand):
        """Test that selecting a negative index is allowed (Python negative indexing)."""
        # The select method only checks upper bound, negative indices are allowed
        valid_hand.select(-1)
        assert valid_hand.selected == -1

    def test_select_updates_selected_index(self, valid_hand):
        """Test that multiple selections update the selected index."""
        valid_hand.select(3)
        assert valid_hand.selected == 3
        
        valid_hand.select(7)
        assert valid_hand.selected == 7


class TestHandPlaySelected:
    """Test cases for the play_selected method."""

    def test_play_selected_default_index(self, valid_hand, sample_hand_cards):
        """Test playing the selected card with default selection (index 0)."""
        expected_card = sample_hand_cards[0]
        played_card = valid_hand.play_selected()
        
        assert played_card == expected_card
        assert len(valid_hand.cards) == 9
        assert played_card not in valid_hand.cards

    def test_play_selected_after_selection(self, valid_hand, sample_hand_cards):
        """Test playing a card after selecting a specific index."""
        valid_hand.select(5)
        expected_card = sample_hand_cards[5]
        
        played_card = valid_hand.play_selected()
        
        assert played_card == expected_card
        assert len(valid_hand.cards) == 9
        assert played_card not in valid_hand.cards

    def test_play_selected_last_card(self, valid_hand, sample_hand_cards):
        """Test playing the last card in the hand."""
        valid_hand.select(9)
        expected_card = sample_hand_cards[9]
        
        played_card = valid_hand.play_selected()
        
        assert played_card == expected_card
        assert len(valid_hand.cards) == 9
        assert played_card not in valid_hand.cards

    def test_play_selected_updates_hand_order(self, valid_hand, sample_hand_cards):
        """Test that playing a card from the middle updates the hand correctly."""
        valid_hand.select(3)
        expected_card = sample_hand_cards[3]
        remaining_cards = sample_hand_cards[:3] + sample_hand_cards[4:]
        
        played_card = valid_hand.play_selected()
        
        assert played_card == expected_card
        assert valid_hand.cards == remaining_cards

    def test_play_multiple_cards_sequentially(self, valid_hand, sample_hand_cards):
        """Test playing multiple cards in sequence."""
        # Play first card (index 0)
        first_played = valid_hand.play_selected()
        assert first_played == sample_hand_cards[0]
        assert len(valid_hand.cards) == 9
        
        # Play another card (now index 1 from remaining cards)
        valid_hand.select(1)  # This is now the original index 2 card (index 1 after removal)
        second_played = valid_hand.play_selected()
        assert second_played == sample_hand_cards[2]  # Original index 2 card
        assert len(valid_hand.cards) == 8

    def test_play_selected_with_selection_out_of_bounds_after_cards_played(self, valid_hand):
        """Test playing cards when selection index becomes invalid."""
        # Play some cards to reduce hand size
        valid_hand.play_selected()  # Remove card at index 0
        valid_hand.play_selected()  # Remove another card at index 0
        
        # Now hand has 8 cards, but selected is still 0
        assert len(valid_hand.cards) == 8
        
        # Should be able to play normally
        played_card = valid_hand.play_selected()
        assert played_card is not None
        assert len(valid_hand.cards) == 7


class TestHandOrder:
    """Test cases for the order method."""

    def test_order_not_implemented(self, valid_hand):
        """Test that the order method raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            valid_hand.order()


class TestHandIntegration:
    """Integration tests for Hand class methods working together."""

    def test_complete_hand_workflow(self, sample_hand_cards):
        """Test a complete workflow: create hand, select cards, play cards."""
        hand = Hand(sample_hand_cards.copy())
        
        # Initially 10 cards
        assert len(hand.cards) == 10
        
        # Select and play a card
        hand.select(3)
        played_card1 = hand.play_selected()
        assert len(hand.cards) == 9
        assert played_card1 not in hand.cards
        
        # Select and play another card
        hand.select(5)
        played_card2 = hand.play_selected()
        assert len(hand.cards) == 8
        assert played_card2 not in hand.cards
        assert played_card1 != played_card2
        
        # Verify remaining cards are still valid
        for card in hand.cards:
            assert isinstance(card, Card)

    def test_hand_with_edge_case_selections(self, sample_hand_cards):
        """Test edge cases with card selection and playing."""
        hand = Hand(sample_hand_cards.copy())
        
        # Play all cards one by one from the beginning
        played_cards = []
        original_length = len(hand.cards)
        
        for i in range(original_length):
            # Always select index 0 (first remaining card)
            hand.select(0)
            played_card = hand.play_selected()
            played_cards.append(played_card)
            assert len(hand.cards) == original_length - i - 1
        
        # Verify all cards were played
        assert len(hand.cards) == 0
        assert len(played_cards) == 10
        assert len(set(played_cards)) == len(played_cards)  # All cards should be unique

    def test_hand_cards_immutability_after_initialization(self, sample_hand_cards):
        """Test that the original cards list is not affected by hand operations."""
        original_cards = sample_hand_cards.copy()
        hand = Hand(sample_hand_cards.copy())  # Pass a copy to avoid modifying original
        
        # Play a card
        hand.play_selected()
        
        # Original list should be unchanged
        assert len(original_cards) == 10
        assert original_cards == sample_hand_cards