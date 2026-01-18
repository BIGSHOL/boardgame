"""
Tile service tests.
Tests for building tile definitions and placement logic.

TDD Status: GREEN (tests and implementation complete)
"""
import pytest

from app.services.tile_service import (
    TileService,
    TileCategory,
    TileCost,
    TileDefinition,
    TILE_DEFINITIONS,
)
from app.services.resource_service import Resources, ResourceType


class TestTileDefinitions:
    """Tests for tile definition data."""

    def test_all_tiles_have_definitions(self):
        """Should have 36 total tiles."""
        assert len(TILE_DEFINITIONS) == 36

    def test_palace_tiles_count(self):
        """Should have 4 palace tiles."""
        palaces = TileService.get_tiles_by_category(TileCategory.PALACE)
        assert len(palaces) == 4

    def test_government_tiles_count(self):
        """Should have 6 government tiles."""
        gov = TileService.get_tiles_by_category(TileCategory.GOVERNMENT)
        assert len(gov) == 6

    def test_religious_tiles_count(self):
        """Should have 6 religious tiles."""
        religious = TileService.get_tiles_by_category(TileCategory.RELIGIOUS)
        assert len(religious) == 6

    def test_commercial_tiles_count(self):
        """Should have 8 commercial tiles."""
        commercial = TileService.get_tiles_by_category(TileCategory.COMMERCIAL)
        assert len(commercial) == 8

    def test_residential_tiles_count(self):
        """Should have 8 residential tiles."""
        residential = TileService.get_tiles_by_category(TileCategory.RESIDENTIAL)
        assert len(residential) == 8

    def test_gate_tiles_count(self):
        """Should have 4 gate tiles."""
        gates = TileService.get_tiles_by_category(TileCategory.GATE)
        assert len(gates) == 4

    def test_tile_has_required_fields(self):
        """Each tile should have all required fields."""
        for tile_id, tile in TILE_DEFINITIONS.items():
            assert tile.tile_id == tile_id
            assert tile.category is not None
            assert tile.name_ko is not None
            assert tile.name_en is not None
            assert tile.cost is not None
            assert tile.base_points >= 0
            assert tile.fengshui_bonus >= 0
            assert tile.adjacency_bonus is not None
            assert tile.worker_slots >= 1


class TestGetTileDefinition:
    """Tests for getting tile definitions."""

    def test_get_existing_tile(self):
        """Should return tile definition for valid ID."""
        tile = TileService.get_tile_definition("palace_1")

        assert tile is not None
        assert tile.tile_id == "palace_1"
        assert tile.name_ko == "경복궁"
        assert tile.category == TileCategory.PALACE

    def test_get_nonexistent_tile(self):
        """Should return None for invalid ID."""
        tile = TileService.get_tile_definition("invalid_tile")
        assert tile is None

    def test_get_all_tiles(self):
        """Should return all tile definitions."""
        tiles = TileService.get_all_tiles()
        assert len(tiles) == 36


class TestTileCost:
    """Tests for tile cost handling."""

    def test_tile_cost_to_dict(self):
        """Should serialize cost to dictionary."""
        cost = TileCost(wood=2, stone=1, tile=1, ink=0)
        data = cost.to_dict()

        assert data == {"wood": 2, "stone": 1, "tile": 1, "ink": 0}

    def test_tile_cost_to_resource_dict(self):
        """Should convert to ResourceType dictionary."""
        cost = TileCost(wood=2, stone=1, tile=0, ink=1)
        resource_dict = cost.to_resource_dict()

        assert resource_dict == {
            ResourceType.WOOD: 2,
            ResourceType.STONE: 1,
            ResourceType.INK: 1,
        }
        # Should not include zero-cost resources
        assert ResourceType.TILE not in resource_dict

    def test_palace_is_expensive(self):
        """Palace tiles should be the most expensive."""
        palace = TileService.get_tile_definition("palace_1")
        residential = TileService.get_tile_definition("residential_4")

        palace_total = (
            palace.cost.wood + palace.cost.stone + palace.cost.tile + palace.cost.ink
        )
        residential_total = (
            residential.cost.wood
            + residential.cost.stone
            + residential.cost.tile
            + residential.cost.ink
        )

        assert palace_total > residential_total


class TestCanAffordTile:
    """Tests for checking if player can afford a tile."""

    def test_can_afford_with_exact_resources(self):
        """Should return True with exact resources."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)
        can_afford = TileService.can_afford_tile(resources, "residential_7")

        assert can_afford is True  # residential_7 costs wood=2

    def test_can_afford_with_excess_resources(self):
        """Should return True with more than enough resources."""
        resources = Resources(wood=5, stone=5, tile=5, ink=5)
        can_afford = TileService.can_afford_tile(resources, "palace_1")

        assert can_afford is True

    def test_cannot_afford_insufficient_resources(self):
        """Should return False with insufficient resources."""
        resources = Resources(wood=1, stone=1, tile=0, ink=0)
        can_afford = TileService.can_afford_tile(resources, "palace_1")

        assert can_afford is False

    def test_cannot_afford_invalid_tile(self):
        """Should return False for invalid tile ID."""
        resources = Resources(wood=10, stone=10, tile=10, ink=10)
        can_afford = TileService.can_afford_tile(resources, "invalid_tile")

        assert can_afford is False

    def test_initial_resources_can_afford_basic_tiles(self):
        """Initial resources (wood=2, stone=2) should afford some tiles."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        # Can afford residential tiles
        assert TileService.can_afford_tile(resources, "residential_4") is True
        assert TileService.can_afford_tile(resources, "residential_5") is True

        # Cannot afford palace
        assert TileService.can_afford_tile(resources, "palace_1") is False


class TestValidatePlacement:
    """Tests for tile placement validation."""

    def _create_empty_board(self) -> list[list[dict]]:
        """Create empty 5x5 board for testing."""
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

    def test_valid_placement_on_empty_cell(self):
        """Should allow placement on empty normal cell."""
        board = self._create_empty_board()

        is_valid, error = TileService.validate_placement(
            board, {"row": 2, "col": 2}, "residential_1"
        )

        assert is_valid is True
        assert error == ""

    def test_invalid_placement_on_mountain(self):
        """Should not allow placement on mountain."""
        board = self._create_empty_board()
        board[0][0]["terrain"] = "mountain"

        is_valid, error = TileService.validate_placement(
            board, {"row": 0, "col": 0}, "residential_1"
        )

        assert is_valid is False
        assert "mountain" in error.lower()

    def test_invalid_placement_on_occupied_cell(self):
        """Should not allow placement on cell with existing tile."""
        board = self._create_empty_board()
        board[2][2]["tile"] = {"tile_id": "residential_1", "owner_id": 1}

        is_valid, error = TileService.validate_placement(
            board, {"row": 2, "col": 2}, "residential_2"
        )

        assert is_valid is False
        assert "already" in error.lower()

    def test_invalid_placement_out_of_bounds(self):
        """Should not allow placement outside board."""
        board = self._create_empty_board()

        is_valid, error = TileService.validate_placement(
            board, {"row": 5, "col": 0}, "residential_1"
        )

        assert is_valid is False
        assert "bounds" in error.lower()

    def test_invalid_tile_id(self):
        """Should not allow invalid tile ID."""
        board = self._create_empty_board()

        is_valid, error = TileService.validate_placement(
            board, {"row": 2, "col": 2}, "invalid_tile"
        )

        assert is_valid is False
        assert "invalid" in error.lower()


class TestCalculatePlacementScore:
    """Tests for placement score calculation."""

    def _create_empty_board(self) -> list[list[dict]]:
        """Create empty 5x5 board for testing."""
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

    def test_base_points_only(self):
        """Should return base points with no bonuses."""
        board = self._create_empty_board()

        score = TileService.calculate_placement_score(
            board, {"row": 2, "col": 2}, "residential_4"
        )

        # residential_4 has base_points=1
        assert score["base"] == 1
        assert score["fengshui"] == 0
        assert score["adjacency"] == 0
        assert score["total"] == 1

    def test_fengshui_bonus_full(self):
        """Should give full feng shui bonus with mountain north and water south."""
        board = self._create_empty_board()
        board[0][2]["terrain"] = "mountain"  # Mountain to north
        board[2][2]["terrain"] = "water"  # Water in center

        score = TileService.calculate_placement_score(
            board, {"row": 1, "col": 2}, "palace_1"
        )

        # palace_1 has fengshui_bonus=4
        assert score["fengshui"] == 4

    def test_fengshui_bonus_partial(self):
        """Should give partial feng shui bonus with only mountain or water."""
        board = self._create_empty_board()
        board[0][2]["terrain"] = "mountain"  # Only mountain, no water

        score = TileService.calculate_placement_score(
            board, {"row": 1, "col": 2}, "palace_1"
        )

        # Should get half the bonus
        assert score["fengshui"] == 2  # 4 // 2

    def test_adjacency_bonus(self):
        """Should calculate adjacency bonus correctly."""
        board = self._create_empty_board()
        # Place a palace tile
        board[2][2]["tile"] = {"tile_id": "palace_1", "owner_id": 1}

        # Place government tile adjacent (government gets +2 from palace)
        score = TileService.calculate_placement_score(
            board, {"row": 2, "col": 3}, "government_1"
        )

        assert score["adjacency"] == 2

    def test_multiple_adjacency_bonuses(self):
        """Should sum multiple adjacency bonuses."""
        board = self._create_empty_board()
        # Place two government tiles
        board[2][1]["tile"] = {"tile_id": "government_1", "owner_id": 1}
        board[2][3]["tile"] = {"tile_id": "government_2", "owner_id": 1}

        # government_2 gets +1 from each adjacent government
        score = TileService.calculate_placement_score(
            board, {"row": 2, "col": 2}, "government_2"
        )

        # government_2 has adjacency_bonus={GOVERNMENT: 1}
        assert score["adjacency"] == 2

    def test_invalid_tile_returns_zero(self):
        """Should return zero score for invalid tile."""
        board = self._create_empty_board()

        score = TileService.calculate_placement_score(
            board, {"row": 2, "col": 2}, "invalid_tile"
        )

        assert score["total"] == 0


class TestCreatePlacedTile:
    """Tests for creating placed tile data."""

    def test_create_placed_tile(self):
        """Should create correct placed tile structure."""
        placed = TileService.create_placed_tile("palace_1", owner_id=1)

        assert placed["tile_id"] == "palace_1"
        assert placed["owner_id"] == 1
        assert placed["placed_workers"] == []
        assert placed["fengshui_active"] is False

    def test_create_placed_tile_invalid_id(self):
        """Should raise error for invalid tile ID."""
        with pytest.raises(ValueError) as exc_info:
            TileService.create_placed_tile("invalid_tile", owner_id=1)

        assert "Invalid tile ID" in str(exc_info.value)


class TestGetResourceProduction:
    """Tests for tile resource production."""

    def test_government_produces_ink(self):
        """Government tiles should produce ink."""
        resource = TileService.get_resource_production("government_1")
        assert resource == ResourceType.INK

    def test_religious_produces_tile(self):
        """Religious tiles should produce tile."""
        resource = TileService.get_resource_production("religious_1")
        assert resource == ResourceType.TILE

    def test_commercial_produces_stone(self):
        """Commercial tiles should produce stone."""
        resource = TileService.get_resource_production("commercial_1")
        assert resource == ResourceType.STONE

    def test_residential_produces_wood(self):
        """Residential tiles should produce wood."""
        resource = TileService.get_resource_production("residential_1")
        assert resource == ResourceType.WOOD

    def test_palace_produces_nothing(self):
        """Palace tiles should not produce resources."""
        resource = TileService.get_resource_production("palace_1")
        assert resource is None

    def test_gate_produces_nothing(self):
        """Gate tiles should not produce resources."""
        resource = TileService.get_resource_production("gate_1")
        assert resource is None

    def test_invalid_tile_produces_nothing(self):
        """Invalid tile should return None."""
        resource = TileService.get_resource_production("invalid_tile")
        assert resource is None


class TestTileDefinitionSerialization:
    """Tests for tile definition serialization."""

    def test_tile_to_dict(self):
        """Should serialize tile definition correctly."""
        tile = TileService.get_tile_definition("palace_1")
        data = tile.to_dict()

        assert data["tile_id"] == "palace_1"
        assert data["category"] == "palace"
        assert data["name_ko"] == "경복궁"
        assert data["name_en"] == "Gyeongbokgung Palace"
        assert data["cost"]["wood"] == 3
        assert data["cost"]["stone"] == 3
        assert data["base_points"] == 8
        assert data["fengshui_bonus"] == 4
        assert "government" in data["adjacency_bonus"]
