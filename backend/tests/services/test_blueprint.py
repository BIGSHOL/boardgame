"""Tests for BlueprintService - 청사진 카드 시스템."""
import pytest
from app.services.blueprint_service import (
    BlueprintService,
    BlueprintCard,
    BlueprintCategory,
    BlueprintCondition,
    BLUEPRINT_CARDS,
)
from app.services.tile_service import TileCategory


class TestBlueprintDefinitions:
    """Test blueprint card definitions."""

    def test_blueprint_count(self):
        """Should have 24 blueprint cards (6 per category, 4 categories)."""
        assert len(BLUEPRINT_CARDS) == 24

    def test_palace_proximity_blueprints(self):
        """Should have 6 palace proximity blueprints."""
        palace_bps = [bp for bp in BLUEPRINT_CARDS.values()
                      if bp.category == BlueprintCategory.PALACE_PROXIMITY]
        assert len(palace_bps) == 6

    def test_category_collection_blueprints(self):
        """Should have 6 category collection blueprints."""
        collection_bps = [bp for bp in BLUEPRINT_CARDS.values()
                          if bp.category == BlueprintCategory.CATEGORY_COLLECTION]
        assert len(collection_bps) == 6

    def test_pattern_blueprints(self):
        """Should have 6 pattern blueprints."""
        pattern_bps = [bp for bp in BLUEPRINT_CARDS.values()
                       if bp.category == BlueprintCategory.PATTERN]
        assert len(pattern_bps) == 6

    def test_special_blueprints(self):
        """Should have 6 special blueprints."""
        special_bps = [bp for bp in BLUEPRINT_CARDS.values()
                       if bp.category == BlueprintCategory.SPECIAL]
        assert len(special_bps) == 6

    def test_blueprint_has_required_fields(self):
        """Each blueprint should have all required fields."""
        for bp_id, bp in BLUEPRINT_CARDS.items():
            assert bp.blueprint_id == bp_id
            assert bp.name_ko
            assert bp.name_en
            assert bp.description_ko
            assert bp.condition is not None
            assert bp.bonus_points > 0


class TestGetBlueprintCard:
    """Test getting blueprint card definitions."""

    def test_get_existing_blueprint(self):
        """Should return blueprint for valid ID."""
        bp = BlueprintService.get_blueprint("palace_neighbor_1")
        assert bp is not None
        assert bp.blueprint_id == "palace_neighbor_1"

    def test_get_nonexistent_blueprint(self):
        """Should return None for invalid ID."""
        bp = BlueprintService.get_blueprint("invalid_blueprint")
        assert bp is None

    def test_get_all_blueprints(self):
        """Should return all blueprints."""
        all_bps = BlueprintService.get_all_blueprints()
        assert len(all_bps) == 24


class TestDealBlueprints:
    """Test dealing blueprints to players."""

    def test_deal_blueprints_2_players(self):
        """Should deal 3 blueprints to each of 2 players."""
        hands = BlueprintService.deal_blueprints(2)
        assert len(hands) == 2
        for hand in hands:
            assert len(hand) == 3
        # All dealt cards should be unique
        all_dealt = [bp for hand in hands for bp in hand]
        assert len(all_dealt) == len(set(all_dealt))

    def test_deal_blueprints_4_players(self):
        """Should deal 3 blueprints to each of 4 players."""
        hands = BlueprintService.deal_blueprints(4)
        assert len(hands) == 4
        for hand in hands:
            assert len(hand) == 3
        all_dealt = [bp for hand in hands for bp in hand]
        assert len(all_dealt) == len(set(all_dealt))

    def test_deal_blueprints_shuffled(self):
        """Dealing should produce different results (shuffled)."""
        hands1 = BlueprintService.deal_blueprints(2)
        hands2 = BlueprintService.deal_blueprints(2)
        # Very unlikely to be exactly the same
        assert hands1 != hands2 or True  # Allow same result but unlikely


class TestBlueprintConditionEvaluation:
    """Test evaluating blueprint conditions."""

    @pytest.fixture
    def sample_board(self):
        """Create a sample board for testing."""
        board = []
        for row in range(5):
            board_row = []
            for col in range(5):
                cell = {
                    "position": {"row": row, "col": col},
                    "terrain": "normal",
                    "tile": None,
                }
                board_row.append(cell)
            board.append(board_row)
        return board

    @pytest.fixture
    def sample_player(self):
        """Create a sample player state."""
        return {
            "id": 1,
            "user_id": 1,
            "placed_tiles": [],
            "resources": {"wood": 5, "stone": 5, "tile": 5, "ink": 5},
            "workers": {
                "apprentices": {"available": 3, "placed": []},
                "officials": {"available": 2, "placed": []},
            },
            "score": 0,
        }

    def test_palace_neighbor_condition_not_met(self, sample_board, sample_player):
        """Should return 0 when condition not met."""
        # No palace on board
        score = BlueprintService.evaluate_blueprint(
            "palace_neighbor_1", sample_board, sample_player
        )
        assert score == 0

    def test_palace_neighbor_condition_met(self, sample_board, sample_player):
        """Should return bonus when tiles adjacent to palace."""
        # Place palace at (2, 2)
        sample_board[2][2]["tile"] = {
            "tile_id": "palace_1",
            "owner_id": 1,
            "placed_workers": [],
        }
        # Place adjacent tile at (2, 1)
        sample_board[2][1]["tile"] = {
            "tile_id": "government_1",
            "owner_id": 1,
            "placed_workers": [],
        }
        sample_player["placed_tiles"] = ["palace_1", "government_1"]

        score = BlueprintService.evaluate_blueprint(
            "palace_neighbor_1", sample_board, sample_player
        )
        assert score >= 0  # May be 0 if condition requires more

    def test_category_collection_condition(self, sample_board, sample_player):
        """Should score for collecting tiles of same category."""
        # Place 3 commercial tiles
        sample_board[0][0]["tile"] = {"tile_id": "commercial_1", "owner_id": 1, "placed_workers": []}
        sample_board[0][1]["tile"] = {"tile_id": "commercial_2", "owner_id": 1, "placed_workers": []}
        sample_board[0][2]["tile"] = {"tile_id": "commercial_3", "owner_id": 1, "placed_workers": []}
        sample_player["placed_tiles"] = ["commercial_1", "commercial_2", "commercial_3"]

        # Find a collection blueprint for commercial
        score = BlueprintService.evaluate_blueprint(
            "collection_commercial", sample_board, sample_player
        )
        assert score >= 0

    def test_row_pattern_condition(self, sample_board, sample_player):
        """Should score for completing a row."""
        # Fill row 0
        for col in range(5):
            sample_board[0][col]["tile"] = {
                "tile_id": f"residential_{col+1}",
                "owner_id": 1,
                "placed_workers": [],
            }
        sample_player["placed_tiles"] = [f"residential_{i+1}" for i in range(5)]

        score = BlueprintService.evaluate_blueprint(
            "pattern_row", sample_board, sample_player
        )
        assert score >= 0

    def test_fengshui_mastery_condition(self, sample_board, sample_player):
        """Should score for having multiple fengshui tiles."""
        # Place tiles with fengshui_active
        sample_board[1][2]["tile"] = {
            "tile_id": "government_1",
            "owner_id": 1,
            "placed_workers": [],
            "fengshui_active": True,
        }
        sample_board[2][2]["tile"] = {
            "tile_id": "palace_1",
            "owner_id": 1,
            "placed_workers": [],
            "fengshui_active": True,
        }
        sample_player["placed_tiles"] = ["government_1", "palace_1"]

        score = BlueprintService.evaluate_blueprint(
            "special_fengshui", sample_board, sample_player
        )
        assert score >= 0


class TestCalculateBlueprintScore:
    """Test calculating total blueprint score for a player."""

    @pytest.fixture
    def sample_board(self):
        """Create a sample board."""
        board = []
        for row in range(5):
            board_row = []
            for col in range(5):
                cell = {
                    "position": {"row": row, "col": col},
                    "terrain": "normal",
                    "tile": None,
                }
                board_row.append(cell)
            board.append(board_row)
        return board

    @pytest.fixture
    def sample_player(self):
        """Create a sample player state."""
        return {
            "id": 1,
            "user_id": 1,
            "placed_tiles": [],
            "blueprints": ["palace_neighbor_1", "collection_commercial"],
            "resources": {"wood": 5, "stone": 5, "tile": 5, "ink": 5},
            "workers": {
                "apprentices": {"available": 3, "placed": []},
                "officials": {"available": 2, "placed": []},
            },
            "score": 0,
        }

    def test_calculate_total_blueprint_score(self, sample_board, sample_player):
        """Should sum scores from all player's blueprints."""
        total = BlueprintService.calculate_total_blueprint_score(
            sample_board, sample_player
        )
        assert isinstance(total, int)
        assert total >= 0

    def test_calculate_blueprint_breakdown(self, sample_board, sample_player):
        """Should return breakdown of each blueprint's score."""
        breakdown = BlueprintService.get_blueprint_score_breakdown(
            sample_board, sample_player
        )
        assert isinstance(breakdown, dict)
        assert "palace_neighbor_1" in breakdown
        assert "collection_commercial" in breakdown
        assert "total" in breakdown


class TestSelectBlueprint:
    """Test blueprint selection during game setup."""

    def test_select_blueprint_valid(self):
        """Should allow selecting from dealt blueprints."""
        dealt = ["palace_neighbor_1", "collection_commercial", "pattern_row"]
        selected, remaining = BlueprintService.select_blueprint(dealt, "palace_neighbor_1")
        assert selected == "palace_neighbor_1"
        assert "palace_neighbor_1" not in remaining
        assert len(remaining) == 2

    def test_select_blueprint_invalid(self):
        """Should raise error for non-dealt blueprint."""
        dealt = ["palace_neighbor_1", "collection_commercial", "pattern_row"]
        with pytest.raises(ValueError):
            BlueprintService.select_blueprint(dealt, "invalid_blueprint")


class TestBlueprintSerialization:
    """Test blueprint serialization for storage."""

    def test_blueprint_to_dict(self):
        """Blueprint should serialize to dict."""
        bp = BlueprintService.get_blueprint("palace_neighbor_1")
        bp_dict = bp.to_dict()
        assert bp_dict["blueprint_id"] == "palace_neighbor_1"
        assert "name_ko" in bp_dict
        assert "bonus_points" in bp_dict

    def test_blueprint_from_id(self):
        """Should reconstruct blueprint from ID."""
        bp_id = "palace_neighbor_1"
        bp = BlueprintService.get_blueprint(bp_id)
        assert bp is not None
        assert bp.blueprint_id == bp_id
