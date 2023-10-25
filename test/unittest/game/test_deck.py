import pytest
from unittest.mock import patch

from doko.game.deck import Deck
from doko.game.card import Card, Rank, Suit


@pytest.fixture
def sample_cards():
    """Create a sample set of 20 cards for testing."""
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


@pytest.fixture
def doppelkopf_deck():
    """Create a full Doppelkopf deck with 40 cards (20 unique cards x 2)."""
    cards = []
    # Create two copies of each card for Doppelkopf
    for _ in range(2):
        cards.extend([
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
        ])
    return cards


@pytest.fixture
def four_cards():
    """Create exactly 4 cards for minimal hand out testing."""
    return [
        Card(Suit.spades, Rank.ace, False),
        Card(Suit.hearts, Rank.king, False),
        Card(Suit.diamonds, Rank.queen, True),
        Card(Suit.clubs, Rank.jack, True),
    ]


class TestDeck:
    """Test cases for the Deck class."""

    def test_deck_initialization(self, sample_cards):
        """Test that deck initializes with provided cards."""
        deck = Deck(sample_cards)
        assert len(deck.cards) == 20
        # Verify all cards are present (though order may be different due to shuffle)
        assert len([c for c in deck.cards if c.suit == Suit.spades]) == 5
        assert len([c for c in deck.cards if c.suit == Suit.hearts]) == 5
        assert len([c for c in deck.cards if c.suit == Suit.diamonds]) == 5
        assert len([c for c in deck.cards if c.suit == Suit.clubs]) == 5

    def test_deck_initialization_with_empty_list(self):
        """Test that deck can be initialized with empty card list."""
        deck = Deck([])
        assert len(deck.cards) == 0

    @patch('doko.game.deck.shuffle')
    def test_deck_initialization_calls_shuffle(self, mock_shuffle, sample_cards):
        """Test that deck initialization calls shuffle."""
        Deck(sample_cards)
        mock_shuffle.assert_called_once()

    @patch('doko.game.deck.shuffle')
    def test_shuffle_method(self, mock_shuffle, sample_cards):
        """Test that shuffle method calls the random.shuffle function."""
        deck = Deck(sample_cards)
        mock_shuffle.reset_mock()  # Reset the call from initialization
        
        deck.shuffle()
        mock_shuffle.assert_called_once_with(deck.cards)

    def test_shuffle_changes_card_order(self, sample_cards):
        """Test that shuffle actually changes the order of cards."""
        # Create original order
        original_cards = sample_cards.copy()
        
        # Create multiple decks and check if any have different order
        order_changed = False
        for _ in range(10):  # Try multiple times since shuffle is random
            deck = Deck(original_cards.copy())
            if [str(c) for c in deck.cards] != [str(c) for c in original_cards]:
                order_changed = True
                break
        
        assert order_changed, "Shuffle should change card order"

    def test_hand_out_with_four_cards(self, four_cards):
        """Test hand_out with exactly 4 cards (1 per player)."""
        deck = Deck(four_cards)
        hands = deck.hand_out()
        
        assert len(hands) == 4  # Four players
        assert all(len(hand) == 1 for hand in hands)  # One card per player
        
        # Verify all cards are distributed
        all_dealt_cards = [card for hand in hands for card in hand]
        assert len(all_dealt_cards) == 4

    def test_hand_out_with_twenty_cards(self, sample_cards):
        """Test hand_out with 20 cards (5 per player)."""
        deck = Deck(sample_cards)
        hands = deck.hand_out()
        
        assert len(hands) == 4  # Four players
        assert all(len(hand) == 5 for hand in hands)  # Five cards per player
        
        # Verify all cards are distributed
        all_dealt_cards = [card for hand in hands for card in hand]
        assert len(all_dealt_cards) == 20

    def test_hand_out_with_doppelkopf_deck(self, doppelkopf_deck):
        """Test hand_out with full 40-card Doppelkopf deck (10 per player)."""
        deck = Deck(doppelkopf_deck)
        hands = deck.hand_out()
        
        assert len(hands) == 4  # Four players
        assert all(len(hand) == 10 for hand in hands)  # Ten cards per player
        
        # Verify all cards are distributed
        all_dealt_cards = [card for hand in hands for card in hand]
        assert len(all_dealt_cards) == 40

    def test_hand_out_distribution_is_sequential(self, four_cards):
        """Test that hand_out distributes cards sequentially from the deck."""
        deck = Deck(four_cards)
        # Don't shuffle to test exact distribution
        deck.cards = four_cards  # Override the shuffled cards
        
        hands = deck.hand_out()
        
        # First player gets first card, second gets second, etc.
        assert hands[0][0] == four_cards[0]
        assert hands[1][0] == four_cards[1]
        assert hands[2][0] == four_cards[2]
        assert hands[3][0] == four_cards[3]

    def test_hand_out_with_non_divisible_by_four_cards(self):
        """Test that hand_out raises assertion error when cards not divisible by 4."""
        # Test with 3 cards (not divisible by 4)
        cards = [
            Card(Suit.spades, Rank.ace, False),
            Card(Suit.hearts, Rank.king, False),
            Card(Suit.diamonds, Rank.queen, True),
        ]
        deck = Deck(cards)
        
        with pytest.raises(AssertionError, match="This deck is not evenly divisible by the four players"):
            deck.hand_out()

    def test_hand_out_with_five_cards_raises_error(self):
        """Test that hand_out raises assertion error with 5 cards."""
        cards = [
            Card(Suit.spades, Rank.ace, False),
            Card(Suit.hearts, Rank.king, False),
            Card(Suit.diamonds, Rank.queen, True),
            Card(Suit.clubs, Rank.jack, True),
            Card(Suit.spades, Rank.ten, False),
        ]
        deck = Deck(cards)
        
        with pytest.raises(AssertionError, match="This deck is not evenly divisible by the four players"):
            deck.hand_out()

    def test_hand_out_with_zero_cards(self):
        """Test hand_out with empty deck."""
        deck = Deck([])
        hands = deck.hand_out()
        
        assert len(hands) == 4  # Four players
        assert all(len(hand) == 0 for hand in hands)  # No cards per player

    def test_hand_out_preserves_card_properties(self, sample_cards):
        """Test that hand_out preserves card properties (suit, rank, is_trump)."""
        deck = Deck(sample_cards)
        hands = deck.hand_out()
        
        # Collect all dealt cards
        all_dealt_cards = [card for hand in hands for card in hand]
        
        # Check that we have the expected number of trump cards
        original_trump_count = sum(1 for card in sample_cards if card.is_trump)
        dealt_trump_count = sum(1 for card in all_dealt_cards if card.is_trump)
        assert dealt_trump_count == original_trump_count
        
        # Check that we have the expected number of each suit
        for suit in Suit:
            original_count = sum(1 for card in sample_cards if card.suit == suit)
            dealt_count = sum(1 for card in all_dealt_cards if card.suit == suit)
            assert dealt_count == original_count

    def test_multiple_hand_outs_give_same_result(self, four_cards):
        """Test that calling hand_out multiple times gives the same result."""
        deck = Deck(four_cards)
        deck.cards = four_cards  # Override shuffled cards for predictable test
        
        hands1 = deck.hand_out()
        hands2 = deck.hand_out()
        
        # Both should have same structure
        assert len(hands1) == len(hands2) == 4
        for i in range(4):
            assert len(hands1[i]) == len(hands2[i])
            for j in range(len(hands1[i])):
                assert str(hands1[i][j]) == str(hands2[i][j])

    def test_deck_cards_remain_unchanged_after_hand_out(self, sample_cards):
        """Test that the original deck.cards list is not modified by hand_out."""
        deck = Deck(sample_cards)
        original_deck_size = len(deck.cards)
        
        deck.hand_out()
        
        # Deck should still have all its cards
        assert len(deck.cards) == original_deck_size