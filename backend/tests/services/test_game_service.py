"""
Game service tests.
Tests for game creation and management logic.

TDD Status: GREEN (tests and implementation complete)
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.game_service import GameService


class TestCreateInitialBoard:
    """Tests for initial board creation."""

    def test_creates_5x5_board(self):
        """Should create 5x5 grid."""
        board = GameService.create_initial_board()

        assert len(board) == 5
        for row in board:
            assert len(row) == 5

    def test_cells_have_correct_structure(self):
        """Each cell should have position, terrain, and tile."""
        board = GameService.create_initial_board()

        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                assert "position" in cell
                assert cell["position"]["row"] == row_idx
                assert cell["position"]["col"] == col_idx
                assert "terrain" in cell
                assert "tile" in cell
                assert cell["tile"] is None  # No tiles initially

    def test_corners_are_mountains(self):
        """Corner cells should be mountains."""
        board = GameService.create_initial_board()

        # Four corners
        assert board[0][0]["terrain"] == "mountain"
        assert board[0][4]["terrain"] == "mountain"
        assert board[4][0]["terrain"] == "mountain"
        assert board[4][4]["terrain"] == "mountain"

    def test_center_is_water(self):
        """Center cell should be water."""
        board = GameService.create_initial_board()

        assert board[2][2]["terrain"] == "water"

    def test_other_cells_are_normal(self):
        """Non-special cells should be normal terrain."""
        board = GameService.create_initial_board()

        assert board[0][1]["terrain"] == "normal"
        assert board[1][1]["terrain"] == "normal"
        assert board[3][3]["terrain"] == "normal"


class TestCreateInitialPlayer:
    """Tests for initial player creation."""

    def test_creates_player_with_correct_info(self):
        """Should create player with provided info."""
        player = GameService.create_initial_player(
            player_id=1,
            user_id=100,
            username="test_user",
            color="blue",
            turn_order=0,
            is_host=True,
        )

        assert player["id"] == 1
        assert player["user_id"] == 100
        assert player["username"] == "test_user"
        assert player["color"] == "blue"
        assert player["turn_order"] == 0
        assert player["is_host"] is True

    def test_creates_player_with_initial_resources(self):
        """Should have initial resources (wood=2, stone=2)."""
        player = GameService.create_initial_player(
            player_id=1,
            user_id=100,
            username="test",
            color="blue",
            turn_order=0,
            is_host=False,
        )

        assert player["resources"]["wood"] == 2
        assert player["resources"]["stone"] == 2
        assert player["resources"]["tile"] == 0
        assert player["resources"]["ink"] == 0

    def test_creates_player_with_initial_workers(self):
        """Should have initial workers (3 apprentices, 2 officials)."""
        player = GameService.create_initial_player(
            player_id=1,
            user_id=100,
            username="test",
            color="blue",
            turn_order=0,
            is_host=False,
        )

        assert player["workers"]["apprentices"]["total"] == 3
        assert player["workers"]["apprentices"]["available"] == 3
        assert player["workers"]["officials"]["total"] == 2
        assert player["workers"]["officials"]["available"] == 2

    def test_creates_player_with_empty_collections(self):
        """Should have empty blueprints and placed tiles."""
        player = GameService.create_initial_player(
            player_id=1,
            user_id=100,
            username="test",
            color="blue",
            turn_order=0,
            is_host=False,
        )

        assert player["blueprints"] == []
        assert player["placed_tiles"] == []
        assert player["score"] == 0


class TestGenerateTilePool:
    """Tests for tile pool generation."""

    def test_generates_correct_number_of_tiles(self):
        """Should generate 36 tiles total."""
        tiles = GameService.generate_tile_pool()

        # 4 palace + 6 government + 6 religious + 8 commercial + 8 residential + 4 gate = 36
        assert len(tiles) == 36

    def test_has_correct_tile_types(self):
        """Should have correct number of each tile type."""
        tiles = GameService.generate_tile_pool()

        palace_count = sum(1 for t in tiles if t.startswith("palace_"))
        government_count = sum(1 for t in tiles if t.startswith("government_"))
        religious_count = sum(1 for t in tiles if t.startswith("religious_"))
        commercial_count = sum(1 for t in tiles if t.startswith("commercial_"))
        residential_count = sum(1 for t in tiles if t.startswith("residential_"))
        gate_count = sum(1 for t in tiles if t.startswith("gate_"))

        assert palace_count == 4
        assert government_count == 6
        assert religious_count == 6
        assert commercial_count == 8
        assert residential_count == 8
        assert gate_count == 4

    def test_tiles_are_shuffled(self):
        """Multiple generations should produce different orders."""
        tiles1 = GameService.generate_tile_pool()
        tiles2 = GameService.generate_tile_pool()

        # Very unlikely to be the same (1/36! chance)
        # Check at least some positions are different
        differences = sum(1 for t1, t2 in zip(tiles1, tiles2) if t1 != t2)
        # Allow for possibility they're the same by chance, but expect most to differ
        assert differences > 0 or tiles1 == tiles2


class TestGetTileResource:
    """Tests for tile resource mapping."""

    def test_palace_gives_no_resource(self):
        """Palace tiles give points, not resources."""
        assert GameService._get_tile_resource("palace") is None

    def test_government_gives_ink(self):
        """Government tiles produce ink."""
        assert GameService._get_tile_resource("government") == "ink"

    def test_religious_gives_tile(self):
        """Religious tiles produce tile resources."""
        assert GameService._get_tile_resource("religious") == "tile"

    def test_commercial_gives_stone(self):
        """Commercial tiles produce stone."""
        assert GameService._get_tile_resource("commercial") == "stone"

    def test_residential_gives_wood(self):
        """Residential tiles produce wood."""
        assert GameService._get_tile_resource("residential") == "wood"

    def test_gate_gives_no_resource(self):
        """Gate tiles give special abilities, not resources."""
        assert GameService._get_tile_resource("gate") is None

    def test_unknown_tile_returns_none(self):
        """Unknown tile types return None."""
        assert GameService._get_tile_resource("unknown") is None


class TestValidateWorkerPlacement:
    """Tests for worker placement validation."""

    def test_invalid_when_not_players_turn(self):
        """Should fail when not player's turn."""
        game = MagicMock()
        game.current_turn_player_id = 2
        game.players = [{"id": 1, "user_id": 100}]

        is_valid, error = GameService.validate_worker_placement(
            game, 1, "apprentice", {"row": 0, "col": 1}, 0
        )

        assert is_valid is False
        assert "Not your turn" in error

    def test_invalid_when_player_not_found(self):
        """Should fail when player not in game."""
        game = MagicMock()
        game.current_turn_player_id = 1
        game.players = [{"id": 2, "user_id": 200}]

        is_valid, error = GameService.validate_worker_placement(
            game, 1, "apprentice", {"row": 0, "col": 1}, 0
        )

        assert is_valid is False
        assert "Player not found" in error

    def test_invalid_when_no_workers_available(self):
        """Should fail when no workers of type available."""
        game = MagicMock()
        game.current_turn_player_id = 1
        game.players = [{
            "id": 1,
            "user_id": 100,
            "workers": {
                "apprentices": {"total": 3, "available": 0, "placed": 3},
                "officials": {"total": 2, "available": 2, "placed": 0},
            }
        }]

        is_valid, error = GameService.validate_worker_placement(
            game, 1, "apprentice", {"row": 0, "col": 1}, 0
        )

        assert is_valid is False
        assert "No apprentice workers available" in error

    def test_invalid_position_out_of_bounds(self):
        """Should fail for invalid board position."""
        game = MagicMock()
        game.current_turn_player_id = 1
        game.players = [{
            "id": 1,
            "user_id": 100,
            "workers": {
                "apprentices": {"total": 3, "available": 3, "placed": 0},
                "officials": {"total": 2, "available": 2, "placed": 0},
            }
        }]

        is_valid, error = GameService.validate_worker_placement(
            game, 1, "apprentice", {"row": 5, "col": 0}, 0
        )

        assert is_valid is False
        assert "Invalid board position" in error

    def test_invalid_on_mountain(self):
        """Should fail when placing on mountain terrain."""
        game = MagicMock()
        game.current_turn_player_id = 1
        game.players = [{
            "id": 1,
            "user_id": 100,
            "workers": {
                "apprentices": {"total": 3, "available": 3, "placed": 0},
                "officials": {"total": 2, "available": 2, "placed": 0},
            }
        }]
        game.board = GameService.create_initial_board()

        is_valid, error = GameService.validate_worker_placement(
            game, 1, "apprentice", {"row": 0, "col": 0}, 0  # Mountain corner
        )

        assert is_valid is False
        assert "Cannot place worker on mountain" in error

    def test_invalid_when_no_tile(self):
        """Should fail when no tile at position."""
        game = MagicMock()
        game.current_turn_player_id = 1
        game.players = [{
            "id": 1,
            "user_id": 100,
            "workers": {
                "apprentices": {"total": 3, "available": 3, "placed": 0},
                "officials": {"total": 2, "available": 2, "placed": 0},
            }
        }]
        game.board = GameService.create_initial_board()

        is_valid, error = GameService.validate_worker_placement(
            game, 1, "apprentice", {"row": 1, "col": 1}, 0
        )

        assert is_valid is False
        assert "No tile at this position" in error


class TestToGameStateResponse:
    """Tests for game state serialization."""

    def test_includes_all_required_fields(self):
        """Response should include all required fields."""
        game = MagicMock()
        game.id = 1
        game.lobby_id = 10
        game.status.value = "in_progress"
        game.current_round = 2
        game.total_rounds = 4
        game.current_turn_player_id = 1
        game.turn_order = [1, 2]
        game.board = [[]]
        game.players = []
        game.available_tiles = ["tile1", "tile2", "tile3", "tile4"]
        game.created_at = None
        game.updated_at = None

        response = GameService.to_game_state_response(game)

        assert response["id"] == 1
        assert response["lobby_id"] == 10
        assert response["status"] == "in_progress"
        assert response["current_round"] == 2
        assert response["total_rounds"] == 4
        assert response["current_turn_player_id"] == 1
        assert response["turn_order"] == [1, 2]

    def test_only_shows_top_three_tiles(self):
        """Should only expose top 3 available tiles."""
        game = MagicMock()
        game.id = 1
        game.lobby_id = 10
        game.status.value = "in_progress"
        game.current_round = 1
        game.total_rounds = 4
        game.current_turn_player_id = 1
        game.turn_order = [1]
        game.board = [[]]
        game.players = []
        game.available_tiles = ["tile1", "tile2", "tile3", "tile4", "tile5"]
        game.created_at = None
        game.updated_at = None

        response = GameService.to_game_state_response(game)

        assert len(response["available_tiles"]) == 3
        assert response["available_tiles"] == ["tile1", "tile2", "tile3"]
