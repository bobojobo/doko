import pytest

from doko.game.card import Card, Rank, Suit


# Fixtures for commonly used test cards
@pytest.fixture
def ace_spades():
    """Test card: Ace of Spades (non-trump)."""
    return Card(Suit.spades, Rank.ace, False)


@pytest.fixture
def queen_hearts():
    """Test card: Queen of Hearts (trump)."""
    return Card(Suit.hearts, Rank.queen, True)


@pytest.fixture
def ten_diamonds():
    """Test card: Ten of Diamonds (trump)."""
    return Card(Suit.diamonds, Rank.ten, True)


@pytest.fixture
def jack_clubs():
    """Test card: Jack of Clubs (trump)."""
    return Card(Suit.clubs, Rank.jack, True)


# Tests for Rank enum
class TestRank:
    """Test cases for the Rank enum."""

    def test_rank_values(self):
        """Test that rank values match Doppelkopf scoring."""
        assert Rank.ace.value == 11
        assert Rank.ten.value == 10
        assert Rank.king.value == 4
        assert Rank.queen.value == 3
        assert Rank.jack.value == 2

    def test_rank_abbreviation(self):
        """Test rank abbreviation method."""
        assert Rank.ace.abbreviation() == "A"
        assert Rank.ten.abbreviation() == "10"
        assert Rank.king.abbreviation() == "K"
        assert Rank.queen.abbreviation() == "Q"
        assert Rank.jack.abbreviation() == "J"

    def test_abbreviation_from_name(self):
        """Test static method for getting abbreviation from rank name."""
        assert Rank.abbreviation_from_name("ace") == "A"
        assert Rank.abbreviation_from_name("ten") == "10"
        assert Rank.abbreviation_from_name("king") == "K"
        assert Rank.abbreviation_from_name("queen") == "Q"
        assert Rank.abbreviation_from_name("jack") == "J"

    def test_abbreviation_from_name_unknown(self):
        """Test abbreviation_from_name with unknown rank name."""
        assert Rank.abbreviation_from_name("unknown") == "unknown"
        assert Rank.abbreviation_from_name("") == ""


# Tests for Suit enum
class TestSuit:
    """Test cases for the Suit enum."""

    def test_suit_values(self):
        """Test that suit values are correct."""
        assert Suit.clubs.value == "clubs"
        assert Suit.spades.value == "spades"
        assert Suit.hearts.value == "hearts"
        assert Suit.diamonds.value == "diamonds"

    def test_suit_symbol(self):
        """Test suit symbol method."""
        assert Suit.clubs.symbol() == "♣️"
        assert Suit.spades.symbol() == "♠️"
        assert Suit.hearts.symbol() == "♥️"
        assert Suit.diamonds.symbol() == "♦️"

    def test_symbol_from_name(self):
        """Test static method for getting symbol from suit name."""
        assert Suit.symbol_from_name("clubs") == "♣️"
        assert Suit.symbol_from_name("spades") == "♠️"
        assert Suit.symbol_from_name("hearts") == "♥️"
        assert Suit.symbol_from_name("diamonds") == "♦️"

    def test_symbol_from_name_unknown(self):
        """Test symbol_from_name with unknown suit name."""
        assert Suit.symbol_from_name("unknown") == "unknown"
        assert Suit.symbol_from_name("") == ""


# Tests for Card class
class TestCard:
    """Test cases for the Card class."""

    def test_card_initialization(self):
        """Test card initialization with all attributes."""
        card = Card(Suit.hearts, Rank.king, False)
        assert card.suit == Suit.hearts
        assert card.rank == Rank.king
        assert card.is_trump == False

    def test_card_str(self, ace_spades, queen_hearts, ten_diamonds, jack_clubs):
        """Test card string representation."""
        assert str(ace_spades) == "spades ace"
        assert str(queen_hearts) == "hearts queen"
        assert str(ten_diamonds) == "diamonds ten"
        assert str(jack_clubs) == "clubs jack"

    def test_card_display(self, ace_spades, queen_hearts, ten_diamonds, jack_clubs):
        """Test card display method with abbreviations and symbols."""
        assert ace_spades.display() == "A ♠️"
        assert queen_hearts.display() == "Q ♥️"
        assert ten_diamonds.display() == "10 ♦️"
        assert jack_clubs.display() == "J ♣️"

    def test_card_equality(self):
        """Test card equality comparison."""
        # Same cards should be equal
        card1 = Card(Suit.hearts, Rank.ace, False)
        card2 = Card(Suit.hearts, Rank.ace, True)  # trump status doesn't affect equality
        assert card1 == card2

        # Different suits should not be equal
        card3 = Card(Suit.spades, Rank.ace, False)
        assert card1 != card3

        # Different ranks should not be equal
        card4 = Card(Suit.hearts, Rank.king, False)
        assert card1 != card4

        # Different types should not be equal
        assert card1 != "not a card"
        assert card1 != None
        assert card1 != 42

    def test_card_hash(self):
        """Test card hashing for use in sets and dictionaries."""
        card1 = Card(Suit.hearts, Rank.ace, False)
        card2 = Card(Suit.hearts, Rank.ace, True)  # trump status doesn't affect hash
        card3 = Card(Suit.spades, Rank.ace, False)

        # Same cards should have same hash
        assert hash(card1) == hash(card2)

        # Different cards should have different hashes (likely but not guaranteed)
        assert hash(card1) != hash(card3)

        # Test that cards can be used in sets
        card_set = {card1, card2, card3}
        assert len(card_set) == 2  # card1 and card2 are considered equal

    def test_card_repr(self, ace_spades, queen_hearts):
        """Test card repr method."""
        assert repr(ace_spades) == "spades ace"
        assert repr(queen_hearts) == "hearts queen"

    def test_trump_status(self):
        """Test that trump status is preserved correctly."""
        trump_card = Card(Suit.diamonds, Rank.ace, True)
        non_trump_card = Card(Suit.spades, Rank.ace, False)
        
        assert trump_card.is_trump == True
        assert non_trump_card.is_trump == False

    def test_all_rank_suit_combinations(self):
        """Test creating cards with all rank and suit combinations."""
        for suit in Suit:
            for rank in Rank:
                for is_trump in [True, False]:
                    card = Card(suit, rank, is_trump)
                    assert card.suit == suit
                    assert card.rank == rank
                    assert card.is_trump == is_trump
                    
                    # Test that string methods work
                    assert isinstance(str(card), str)
                    assert isinstance(card.display(), str)
                    assert isinstance(repr(card), str)

    def test_card_in_collections(self):
        """Test that cards work properly in collections."""
        cards = [
            Card(Suit.hearts, Rank.ace, False),
            Card(Suit.spades, Rank.king, True),
            Card(Suit.diamonds, Rank.queen, False),
            Card(Suit.clubs, Rank.jack, True)
        ]
        
        # Test in list
        assert len(cards) == 4
        
        # Test in set (should remove duplicates)
        card_set = set(cards)
        assert len(card_set) == 4
        
        # Add duplicate
        cards.append(Card(Suit.hearts, Rank.ace, True))  # Same as first, different trump
        card_set = set(cards)
        assert len(card_set) == 4  # Still 4 because trump doesn't affect equality
        
        # Test in dict as keys
        card_dict = {card: f"Card {i}" for i, card in enumerate(cards)}
        assert len(card_dict) == 4


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("suit", [Suit.clubs, Suit.spades, Suit.hearts, Suit.diamonds])
@pytest.mark.parametrize("rank", [Rank.ace, Rank.ten, Rank.king, Rank.queen, Rank.jack])
@pytest.mark.parametrize("is_trump", [True, False])
def test_card_creation_parametrized(suit, rank, is_trump):
    """Parametrized test for creating cards with all combinations."""
    card = Card(suit, rank, is_trump)
    assert card.suit == suit
    assert card.rank == rank
    assert card.is_trump == is_trump
    assert isinstance(str(card), str)
    assert isinstance(card.display(), str)


@pytest.mark.parametrize("rank_name,expected", [
    ("ace", "A"),
    ("ten", "10"), 
    ("king", "K"),
    ("queen", "Q"),
    ("jack", "J"),
    ("unknown", "unknown"),
    ("", "")
])
def test_rank_abbreviation_from_name_parametrized(rank_name, expected):
    """Parametrized test for rank abbreviation from name."""
    assert Rank.abbreviation_from_name(rank_name) == expected


@pytest.mark.parametrize("suit_name,expected", [
    ("clubs", "♣️"),
    ("spades", "♠️"),
    ("hearts", "♥️"),
    ("diamonds", "♦️"),
    ("unknown", "unknown"),
    ("", "")
])
def test_suit_symbol_from_name_parametrized(suit_name, expected):
    """Parametrized test for suit symbol from name."""
    assert Suit.symbol_from_name(suit_name) == expected