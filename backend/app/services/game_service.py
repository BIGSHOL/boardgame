"""
Game service for managing game state and actions.
"""
import json
import random
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game, GameAction, GameStatus
from app.models.lobby import Lobby, LobbyPlayer
from app.services.resource_service import ResourceService, Resources, ResourceType
from app.services.worker_service import WorkerService, PlayerWorkers, WorkerState
from app.services.tile_service import TileService
from app.services.blueprint_service import BlueprintService


class GameService:
    """Service for managing games."""

    TOTAL_ROUNDS = 4
    BOARD_SIZE = 5

    @staticmethod
    def create_initial_board() -> list[list[dict]]:
        """Create initial 5x5 game board."""
        board = []
        for row in range(GameService.BOARD_SIZE):
            board_row = []
            for col in range(GameService.BOARD_SIZE):
                cell = {
                    "position": {"row": row, "col": col},
                    "terrain": "normal",
                    "tile": None,
                }
                # Add some terrain variation (mountains/water at edges)
                if (row == 0 or row == 4) and (col == 0 or col == 4):
                    cell["terrain"] = "mountain"
                elif (row == 2 and col == 2):
                    cell["terrain"] = "water"
                board_row.append(cell)
            board.append(board_row)
        return board

    @staticmethod
    def create_initial_player(
        player_id: int,
        user_id: int,
        username: str,
        color: str,
        turn_order: int,
        is_host: bool,
    ) -> dict:
        """Create initial player state."""
        resources = ResourceService.get_initial_resources()
        workers = WorkerService.get_initial_workers()

        return {
            "id": player_id,
            "user_id": user_id,
            "username": username,
            "color": color,
            "turn_order": turn_order,
            "is_host": is_host,
            "is_ready": True,
            "resources": resources.to_dict(),
            "workers": workers.to_dict(),
            "blueprints": [],
            "score": 0,
            "placed_tiles": [],
        }

    @staticmethod
    def generate_tile_pool() -> list[str]:
        """Generate shuffled tile pool."""
        # Building tiles by category
        tiles = []

        # Palace tiles (4)
        tiles.extend([f"palace_{i}" for i in range(1, 5)])
        # Government tiles (6)
        tiles.extend([f"government_{i}" for i in range(1, 7)])
        # Religious tiles (6)
        tiles.extend([f"religious_{i}" for i in range(1, 7)])
        # Commercial tiles (8)
        tiles.extend([f"commercial_{i}" for i in range(1, 9)])
        # Residential tiles (8)
        tiles.extend([f"residential_{i}" for i in range(1, 9)])
        # Gate tiles (4)
        tiles.extend([f"gate_{i}" for i in range(1, 5)])

        random.shuffle(tiles)
        return tiles

    @staticmethod
    async def create_game(
        db: AsyncSession,
        lobby: Lobby,
    ) -> Game:
        """Create a new game from lobby."""
        # Create initial board
        board = GameService.create_initial_board()

        # Deal blueprint cards to players
        num_players = len(lobby.players)
        blueprint_hands = BlueprintService.deal_blueprints(num_players, cards_per_player=3)

        # Create player states
        players = []
        turn_order_list = []

        for idx, lobby_player in enumerate(sorted(lobby.players, key=lambda p: p.turn_order)):
            player_state = GameService.create_initial_player(
                player_id=lobby_player.id,
                user_id=lobby_player.user_id,
                username=lobby_player.user.username,
                color=lobby_player.color.value,
                turn_order=lobby_player.turn_order,
                is_host=lobby_player.user_id == lobby.host_id,
            )
            # Assign dealt blueprint cards
            player_state["dealt_blueprints"] = blueprint_hands[idx]
            player_state["blueprints"] = []  # Selected blueprints will be stored here
            players.append(player_state)
            turn_order_list.append(lobby_player.user_id)  # Use user_id, not lobby_player.id

        # Generate tile pool
        available_tiles = GameService.generate_tile_pool()

        # Create game
        game = Game(
            lobby_id=lobby.id,
            status=GameStatus.IN_PROGRESS,
            current_round=1,
            total_rounds=GameService.TOTAL_ROUNDS,
            current_turn_player_id=turn_order_list[0],
            turn_order_json=json.dumps(turn_order_list),
            board_json=json.dumps(board),
            players_json=json.dumps(players),
            available_tiles_json=json.dumps(available_tiles),
            discarded_tiles_json=json.dumps([]),
        )

        db.add(game)
        await db.flush()
        await db.refresh(game)

        return game

    @staticmethod
    async def get_game(
        db: AsyncSession,
        game_id: int,
    ) -> Game | None:
        """Get game by ID."""
        result = await db.execute(select(Game).where(Game.id == game_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_game_by_lobby(
        db: AsyncSession,
        lobby_id: int,
    ) -> Game | None:
        """Get game by lobby ID."""
        result = await db.execute(select(Game).where(Game.lobby_id == lobby_id))
        return result.scalar_one_or_none()

    @staticmethod
    def get_player_state(game: Game, player_id: int) -> dict | None:
        """Get player state from game by user_id.

        Note: player_id here refers to user_id, not player["id"].
        This matches how current_turn_player_id stores user_id values.
        """
        players = game.players
        for player in players:
            if player["user_id"] == player_id:
                return player
        return None

    @staticmethod
    def update_player_state(game: Game, player_id: int, updates: dict) -> None:
        """Update player state in game by user_id.

        Note: player_id here refers to user_id, not player["id"].
        """
        players = game.players
        for i, player in enumerate(players):
            if player["user_id"] == player_id:
                players[i].update(updates)
                game.players = players
                return

    @staticmethod
    def get_current_player(game: Game) -> dict | None:
        """Get current turn player."""
        return GameService.get_player_state(game, game.current_turn_player_id)

    @staticmethod
    def advance_turn(game: Game) -> None:
        """Advance to next player's turn."""
        turn_order = game.turn_order
        current_index = turn_order.index(game.current_turn_player_id)
        next_index = (current_index + 1) % len(turn_order)

        # Check if round is complete
        if next_index == 0:
            game.current_round += 1
            # Check if game is over (all rounds complete)
            if game.current_round > game.total_rounds:
                GameService._finalize_game(game)
                return

        # Check if tiles are exhausted
        if len(game.available_tiles) == 0:
            GameService._finalize_game(game)
            return

        game.current_turn_player_id = turn_order[next_index]

    @staticmethod
    def _finalize_game(game: Game) -> None:
        """Finalize game and calculate final scores."""
        game.status = GameStatus.FINISHED

        # Calculate final scores for all players
        final_scores = GameService.calculate_final_scores(game)

        # Update each player's final score
        for score_data in final_scores:
            GameService.update_player_state(game, score_data["player_id"], {
                "final_score": score_data["total_score"],
                "score_breakdown": {
                    "base_score": score_data["base_score"],
                    "blueprint_score": score_data["blueprint_score"],
                    "worker_score": score_data["worker_score"],
                    "resource_penalty": score_data["resource_penalty"],
                },
            })

    @staticmethod
    async def record_action(
        db: AsyncSession,
        game: Game,
        player_id: int,
        action_type: str,
        payload: dict,
    ) -> GameAction:
        """Record a game action."""
        action = GameAction(
            game_id=game.id,
            player_id=player_id,
            action_type=action_type,
            payload_json=json.dumps(payload),
        )
        db.add(action)
        await db.flush()
        await db.refresh(action)
        return action

    @staticmethod
    def validate_worker_placement(
        game: Game,
        player_id: int,
        worker_type: str,
        position: dict,
        slot_index: int,
    ) -> tuple[bool, str]:
        """
        Validate worker placement.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's player's turn
        if game.current_turn_player_id != player_id:
            return False, "Not your turn"

        # Get player state
        player = GameService.get_player_state(game, player_id)
        if not player:
            return False, "Player not found"

        # Check worker availability
        workers = PlayerWorkers.from_dict(player["workers"])
        from app.services.worker_service import WorkerType

        w_type = WorkerType(worker_type)
        if not WorkerService.can_place_worker(workers, w_type):
            return False, f"No {worker_type} workers available"

        # Check board position
        row, col = position["row"], position["col"]
        if not (0 <= row < GameService.BOARD_SIZE and 0 <= col < GameService.BOARD_SIZE):
            return False, "Invalid board position"

        board = game.board
        cell = board[row][col]

        # Check terrain
        if cell["terrain"] == "mountain":
            return False, "Cannot place worker on mountain"

        # Check if tile exists at position
        if cell["tile"] is None:
            return False, "No tile at this position"

        # Check slot availability
        from app.services.worker_service import PlacedWorker

        placed_workers = [
            PlacedWorker.from_dict(w) for w in cell["tile"].get("placed_workers", [])
        ]
        if not WorkerService.can_place_on_tile(placed_workers, w_type, slot_index):
            return False, "Slot not available"

        return True, ""

    @staticmethod
    async def place_worker(
        db: AsyncSession,
        game: Game,
        player_id: int,
        worker_type: str,
        position: dict,
        slot_index: int,
    ) -> dict:
        """
        Place a worker on the board.

        Returns:
            Action result with updated state
        """
        from app.services.worker_service import WorkerType, PlacedWorker

        # Validate
        is_valid, error = GameService.validate_worker_placement(
            game, player_id, worker_type, position, slot_index
        )
        if not is_valid:
            raise ValueError(error)

        # Get player and update workers
        player = GameService.get_player_state(game, player_id)
        workers = PlayerWorkers.from_dict(player["workers"])
        w_type = WorkerType(worker_type)

        new_workers = WorkerService.place_worker(workers, w_type)

        # Update board
        row, col = position["row"], position["col"]
        board = game.board
        cell = board[row][col]

        placed_worker = PlacedWorker(
            player_id=player_id,
            worker_type=w_type,
            slot_index=slot_index,
        )
        cell["tile"]["placed_workers"].append(placed_worker.to_dict())

        # Update game state
        game.board = board
        GameService.update_player_state(game, player_id, {"workers": new_workers.to_dict()})

        # Record action
        action = await GameService.record_action(
            db,
            game,
            player_id,
            "place_worker",
            {
                "worker_type": worker_type,
                "target_position": position,
                "slot_index": slot_index,
            },
        )

        await db.flush()

        return {
            "action_id": action.id,
            "worker_type": worker_type,
            "position": position,
            "slot_index": slot_index,
        }

    @staticmethod
    def validate_tile_placement(
        game: Game,
        player_id: int,
        tile_id: str,
        position: dict,
    ) -> tuple[bool, str]:
        """
        Validate tile placement.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's player's turn
        if game.current_turn_player_id != player_id:
            return False, "Not your turn"

        # Get player state
        player = GameService.get_player_state(game, player_id)
        if not player:
            return False, "Player not found"

        # Check if tile is available
        available_tiles = game.available_tiles
        if tile_id not in available_tiles[:3]:  # Only top 3 are selectable
            return False, "Tile not available for selection"

        # Check if player can afford
        resources = Resources.from_dict(player["resources"])
        if not TileService.can_afford_tile(resources, tile_id):
            return False, "Cannot afford this tile"

        # Validate board placement
        board = game.board
        is_valid, error = TileService.validate_placement(board, position, tile_id)
        if not is_valid:
            return False, error

        return True, ""

    @staticmethod
    async def place_tile(
        db: AsyncSession,
        game: Game,
        player_id: int,
        tile_id: str,
        position: dict,
    ) -> dict:
        """
        Place a tile on the board.

        Returns:
            Action result with score breakdown
        """
        # Validate
        is_valid, error = GameService.validate_tile_placement(
            game, player_id, tile_id, position
        )
        if not is_valid:
            raise ValueError(error)

        # Get player and deduct cost
        player = GameService.get_player_state(game, player_id)
        resources = Resources.from_dict(player["resources"])
        tile_def = TileService.get_tile_definition(tile_id)
        cost = tile_def.cost.to_resource_dict()

        new_resources = ResourceService.pay_cost(resources, cost)

        # Calculate score
        board = game.board
        score_breakdown = TileService.calculate_placement_score(board, position, tile_id)

        # Place tile on board
        row, col = position["row"], position["col"]
        placed_tile = TileService.create_placed_tile(tile_id, player_id)

        # Check feng shui
        if score_breakdown["fengshui"] > 0:
            placed_tile["fengshui_active"] = True

        board[row][col]["tile"] = placed_tile

        # Remove tile from available pool
        available_tiles = game.available_tiles
        available_tiles.remove(tile_id)

        # Update player state
        new_score = player.get("score", 0) + score_breakdown["total"]
        placed_tiles = player.get("placed_tiles", [])
        placed_tiles.append(tile_id)

        GameService.update_player_state(game, player_id, {
            "resources": new_resources.to_dict(),
            "score": new_score,
            "placed_tiles": placed_tiles,
        })

        # Update game state
        game.board = board
        game.available_tiles = available_tiles

        # Record action
        action = await GameService.record_action(
            db,
            game,
            player_id,
            "place_tile",
            {
                "tile_id": tile_id,
                "position": position,
                "score_breakdown": score_breakdown,
            },
        )

        await db.flush()

        return {
            "action_id": action.id,
            "tile_id": tile_id,
            "position": position,
            "score_breakdown": score_breakdown,
            "new_score": new_score,
        }

    @staticmethod
    async def end_turn(
        db: AsyncSession,
        game: Game,
        player_id: int,
    ) -> dict:
        """End current player's turn."""
        if game.current_turn_player_id != player_id:
            raise ValueError("Not your turn")

        # Collect resources from placed workers
        player = GameService.get_player_state(game, player_id)
        resources = Resources.from_dict(player["resources"])

        # Calculate production from all tiles with player's workers
        board = game.board
        for row in board:
            for cell in row:
                if cell["tile"] is not None:
                    tile = cell["tile"]
                    for placed_worker in tile.get("placed_workers", []):
                        if placed_worker["player_id"] == player_id:
                            # Add resource based on tile type
                            tile_type = tile["tile_id"].split("_")[0]
                            resource_type = GameService._get_tile_resource(tile_type)
                            if resource_type:
                                from app.services.resource_service import ResourceType

                                production = 1
                                if placed_worker["worker_type"] == "official":
                                    production = 2
                                resources = ResourceService.add_resource(
                                    resources,
                                    ResourceType(resource_type),
                                    production,
                                )

        # Update player state
        GameService.update_player_state(game, player_id, {"resources": resources.to_dict()})

        # Advance turn
        GameService.advance_turn(game)

        # Record action
        action = await GameService.record_action(
            db, game, player_id, "end_turn", {}
        )

        await db.flush()

        return {
            "action_id": action.id,
            "next_player_id": game.current_turn_player_id,
            "current_round": game.current_round,
            "game_status": game.status.value,
        }

    @staticmethod
    def _get_tile_resource(tile_type: str) -> str | None:
        """Get resource produced by tile type."""
        resource_map = {
            "palace": None,  # Palace gives points, not resources
            "government": "ink",
            "religious": "tile",
            "commercial": "stone",
            "residential": "wood",
            "gate": None,  # Gate gives special abilities
        }
        return resource_map.get(tile_type)

    @staticmethod
    async def select_blueprint(
        db: AsyncSession,
        game: Game,
        player_id: int,
        blueprint_id: str,
    ) -> dict:
        """
        Select a blueprint card from dealt cards.

        Returns:
            Result with selected blueprint and remaining cards
        """
        player = GameService.get_player_state(game, player_id)
        if not player:
            raise ValueError("Player not found")

        dealt = player.get("dealt_blueprints", [])
        if not dealt:
            raise ValueError("No blueprints to select from")

        if blueprint_id not in dealt:
            raise ValueError("Blueprint not in dealt cards")

        # Select the blueprint
        selected, remaining = BlueprintService.select_blueprint(dealt, blueprint_id)

        # Update player state
        blueprints = player.get("blueprints", [])
        blueprints.append(selected)

        GameService.update_player_state(game, player_id, {
            "blueprints": blueprints,
            "dealt_blueprints": remaining,
        })

        # Record action
        action = await GameService.record_action(
            db, game, player_id, "select_blueprint",
            {"blueprint_id": blueprint_id}
        )

        await db.flush()

        return {
            "action_id": action.id,
            "selected_blueprint": selected,
            "remaining_blueprints": remaining,
        }

    @staticmethod
    def calculate_final_scores(game: Game) -> list[dict]:
        """
        Calculate final scores including blueprint bonuses.

        Returns:
            List of player score breakdowns
        """
        board = game.board
        results = []

        for player in game.players:
            base_score = player.get("score", 0)

            # Calculate blueprint scores
            blueprint_breakdown = BlueprintService.get_blueprint_score_breakdown(
                board, player
            )
            blueprint_total = blueprint_breakdown.get("total", 0)

            # Calculate worker scores (each placed worker gives 1 point)
            # Note: placed_workers store player_id as user_id
            worker_score = 0
            for row in board:
                for cell in row:
                    if cell.get("tile"):
                        for pw in cell["tile"].get("placed_workers", []):
                            if pw["player_id"] == player["user_id"]:
                                worker_score += 1

            # Calculate remaining resource penalty (-1 per 3 resources)
            resources = player.get("resources", {})
            total_resources = sum(resources.values())
            resource_penalty = -(total_resources // 3)

            total_score = base_score + blueprint_total + worker_score + resource_penalty

            results.append({
                "player_id": player["id"],
                "user_id": player["user_id"],
                "username": player.get("username", "Unknown"),
                "base_score": base_score,
                "blueprint_score": blueprint_total,
                "blueprint_breakdown": blueprint_breakdown,
                "worker_score": worker_score,
                "resource_penalty": resource_penalty,
                "total_score": total_score,
            })

        # Sort by total score descending
        results.sort(key=lambda x: x["total_score"], reverse=True)

        # Add rankings
        for i, result in enumerate(results):
            result["rank"] = i + 1

        return results

    @staticmethod
    def to_game_state_response(game: Game) -> dict:
        """Convert game to API response format."""
        return {
            "id": game.id,
            "lobby_id": game.lobby_id,
            "status": game.status.value,
            "current_round": game.current_round,
            "total_rounds": game.total_rounds,
            "current_turn_player_id": game.current_turn_player_id,
            "turn_order": game.turn_order,
            "board": game.board,
            "players": game.players,
            "available_tiles": game.available_tiles[:3] if game.available_tiles else [],  # Only show top 3
            "discarded_tiles": [],  # Don't expose full discard pile
            "created_at": game.created_at.isoformat() if game.created_at else None,
            "updated_at": game.updated_at.isoformat() if game.updated_at else None,
        }
