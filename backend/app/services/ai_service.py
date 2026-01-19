"""
AI Service for single player mode.
Provides AI opponents for solo play testing.
"""
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.services.resource_service import Resources, ResourceService, ResourceType
from app.services.worker_service import (
    WorkerService,
    WorkerType,
    PlayerWorkers,
    PlacedWorker,
)
from app.services.tile_service import TileService, TileCategory, TileDefinition
from app.services.blueprint_service import BlueprintService


class AIDifficulty(str, Enum):
    """AI difficulty levels."""
    EASY = "easy"      # Random decisions
    MEDIUM = "medium"  # Basic strategy
    HARD = "hard"      # Optimized strategy


@dataclass
class AIDecision:
    """Represents an AI decision."""
    action_type: str
    params: dict


class AIService:
    """Service for AI opponent logic."""

    @staticmethod
    def make_decision(
        game_state: dict,
        player_state: dict,
        difficulty: AIDifficulty = AIDifficulty.MEDIUM,
    ) -> AIDecision:
        """
        Make a decision for the AI player.

        Args:
            game_state: Current game state
            player_state: AI player's state
            difficulty: AI difficulty level

        Returns:
            AIDecision with action type and parameters
        """
        if difficulty == AIDifficulty.EASY:
            return AIService._make_easy_decision(game_state, player_state)
        elif difficulty == AIDifficulty.MEDIUM:
            return AIService._make_medium_decision(game_state, player_state)
        else:
            return AIService._make_hard_decision(game_state, player_state)

    @staticmethod
    def _make_easy_decision(game_state: dict, player_state: dict) -> AIDecision:
        """
        Easy AI: Makes random valid decisions.
        Good for beginners to practice.
        """
        actions = AIService._get_valid_actions(game_state, player_state)

        if not actions:
            return AIDecision("end_turn", {})

        # Randomly select an action
        action = random.choice(actions)
        return action

    @staticmethod
    def _make_medium_decision(game_state: dict, player_state: dict) -> AIDecision:
        """
        Medium AI: Uses basic strategy.
        - Prioritizes high-point tiles if affordable
        - Places workers for resource generation
        - Considers feng shui bonuses
        """
        # Check if there are dealt blueprints to select (only if no blueprint selected yet)
        dealt_blueprints = player_state.get("dealt_blueprints", [])
        selected_blueprints = player_state.get("blueprints", [])
        if dealt_blueprints and len(selected_blueprints) == 0:
            # Select the blueprint with highest bonus points
            best_bp = AIService._select_best_blueprint(dealt_blueprints)
            if best_bp:
                return AIDecision("select_blueprint", {"blueprint_id": best_bp})

        # Try to place a tile
        tile_decision = AIService._decide_tile_placement(game_state, player_state, optimized=False)
        if tile_decision:
            return tile_decision

        # Try to place a worker
        worker_decision = AIService._decide_worker_placement(game_state, player_state, optimized=False)
        if worker_decision:
            return worker_decision

        # End turn
        return AIDecision("end_turn", {})

    @staticmethod
    def _make_hard_decision(game_state: dict, player_state: dict) -> AIDecision:
        """
        Hard AI: Uses optimized strategy.
        - Maximizes points per resource spent
        - Plans for blueprint completion
        - Blocks opponents when possible
        """
        # Check if there are dealt blueprints to select (only if no blueprint selected yet)
        dealt_blueprints = player_state.get("dealt_blueprints", [])
        selected_blueprints = player_state.get("blueprints", [])
        if dealt_blueprints and len(selected_blueprints) == 0:
            # Select blueprint that aligns with current board state
            best_bp = AIService._select_strategic_blueprint(dealt_blueprints, game_state, player_state)
            if best_bp:
                return AIDecision("select_blueprint", {"blueprint_id": best_bp})

        # Evaluate all possible tile placements
        tile_decision = AIService._decide_tile_placement(game_state, player_state, optimized=True)
        if tile_decision:
            return tile_decision

        # Strategic worker placement
        worker_decision = AIService._decide_worker_placement(game_state, player_state, optimized=True)
        if worker_decision:
            return worker_decision

        return AIDecision("end_turn", {})

    @staticmethod
    def _get_valid_actions(game_state: dict, player_state: dict) -> list[AIDecision]:
        """Get all valid actions for the AI."""
        actions = []

        # Blueprint selection (only if no blueprint selected yet)
        dealt_blueprints = player_state.get("dealt_blueprints", [])
        selected_blueprints = player_state.get("blueprints", [])
        if len(selected_blueprints) == 0:
            for bp_id in dealt_blueprints:
                actions.append(AIDecision("select_blueprint", {"blueprint_id": bp_id}))

        # Tile placement
        resources = Resources.from_dict(player_state.get("resources", {}))
        available_tiles = game_state.get("available_tiles", [])[:3]
        board = game_state.get("board", [])

        for tile_id in available_tiles:
            if TileService.can_afford_tile(resources, tile_id):
                valid_positions = AIService._get_valid_tile_positions(board)
                for pos in valid_positions:
                    actions.append(AIDecision("place_tile", {
                        "tile_id": tile_id,
                        "position": pos,
                    }))

        # Worker placement
        workers = PlayerWorkers.from_dict(player_state.get("workers", {}))

        if workers.apprentices.available > 0:
            slots = AIService._get_worker_slots(board, "apprentice")
            for slot in slots:
                actions.append(AIDecision("place_worker", {
                    "worker_type": "apprentice",
                    "target_position": slot["position"],
                    "slot_index": slot["slot_index"],
                }))

        if workers.officials.available > 0:
            slots = AIService._get_worker_slots(board, "official")
            for slot in slots:
                actions.append(AIDecision("place_worker", {
                    "worker_type": "official",
                    "target_position": slot["position"],
                    "slot_index": slot["slot_index"],
                }))

        return actions

    @staticmethod
    def _get_valid_tile_positions(board: list[list[dict]]) -> list[dict]:
        """Get valid positions for tile placement."""
        positions = []
        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell.get("terrain") == "mountain":
                    continue
                if cell.get("tile") is not None:
                    continue
                positions.append({"row": row_idx, "col": col_idx})
        return positions

    @staticmethod
    def _get_worker_slots(board: list[list[dict]], worker_type: str) -> list[dict]:
        """Get available worker slots on the board."""
        slots = []
        w_type = WorkerType(worker_type)

        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell.get("terrain") == "mountain":
                    continue
                if cell.get("tile") is None:
                    continue

                tile = cell["tile"]
                placed_workers = [
                    PlacedWorker.from_dict(w)
                    for w in tile.get("placed_workers", [])
                ]

                max_slots = 2 if worker_type == "apprentice" else 1
                for slot_idx in range(max_slots):
                    if WorkerService.can_place_on_tile(placed_workers, w_type, slot_idx):
                        slots.append({
                            "position": {"row": row_idx, "col": col_idx},
                            "slot_index": slot_idx,
                        })

        return slots

    @staticmethod
    def _select_best_blueprint(dealt_blueprints: list[str]) -> str | None:
        """Select the blueprint with highest potential points."""
        if not dealt_blueprints:
            return None

        best_bp = None
        best_points = 0

        for bp_id in dealt_blueprints:
            bp = BlueprintService.get_blueprint(bp_id)
            if bp and bp.bonus_points > best_points:
                best_points = bp.bonus_points
                best_bp = bp_id

        return best_bp

    @staticmethod
    def _select_strategic_blueprint(
        dealt_blueprints: list[str],
        game_state: dict,
        player_state: dict,
    ) -> str | None:
        """Select blueprint based on current game state and achievability."""
        if not dealt_blueprints:
            return None

        board = game_state.get("board", [])
        # Use user_id since tiles store owner_id as user_id
        player_id = player_state.get("user_id")

        # Count player's tiles by category
        category_counts = {}
        player_positions = []

        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell.get("tile") and cell["tile"].get("owner_id") == player_id:
                    tile_id = cell["tile"].get("tile_id", "")
                    category = tile_id.split("_")[0]
                    category_counts[category] = category_counts.get(category, 0) + 1
                    player_positions.append((row_idx, col_idx))

        # Score each blueprint
        best_bp = None
        best_score = -1

        for bp_id in dealt_blueprints:
            bp = BlueprintService.get_blueprint(bp_id)
            if not bp:
                continue

            # Calculate achievability score
            score = AIService._calculate_blueprint_achievability(
                bp, category_counts, player_positions, board
            )

            # Weight by bonus points
            weighted_score = score * bp.bonus_points

            if weighted_score > best_score:
                best_score = weighted_score
                best_bp = bp_id

        return best_bp

    @staticmethod
    def _calculate_blueprint_achievability(
        blueprint,
        category_counts: dict,
        player_positions: list,
        board: list,
    ) -> float:
        """Calculate how achievable a blueprint is (0.0 to 1.0)."""
        condition = blueprint.condition

        if condition.condition_type == "category_count":
            category = condition.params.get("category", "")
            min_count = condition.params.get("min_count", 1)
            current = category_counts.get(category, 0)
            return min(1.0, current / min_count)

        elif condition.condition_type == "diverse_categories":
            min_types = condition.params.get("min_types", 1)
            current_types = len(category_counts)
            return min(1.0, current_types / min_types)

        elif condition.condition_type == "tile_count":
            min_count = condition.params.get("min_count", 1)
            current = len(player_positions)
            return min(1.0, current / min_count)

        # Default: moderate achievability
        return 0.5

    @staticmethod
    def _decide_tile_placement(
        game_state: dict,
        player_state: dict,
        optimized: bool = False,
    ) -> AIDecision | None:
        """Decide which tile to place and where."""
        resources = Resources.from_dict(player_state.get("resources", {}))
        available_tiles = game_state.get("available_tiles", [])[:3]
        board = game_state.get("board", [])
        # Use user_id since tiles store owner_id as user_id
        player_id = player_state.get("user_id")

        if not available_tiles:
            return None

        # Get affordable tiles
        affordable_tiles = [
            tile_id for tile_id in available_tiles
            if TileService.can_afford_tile(resources, tile_id)
        ]

        if not affordable_tiles:
            return None

        valid_positions = AIService._get_valid_tile_positions(board)
        if not valid_positions:
            return None

        if optimized:
            # Evaluate all combinations and pick best
            best_tile = None
            best_pos = None
            best_score = -float("inf")

            for tile_id in affordable_tiles:
                tile_def = TileService.get_tile_definition(tile_id)
                if not tile_def:
                    continue

                for pos in valid_positions:
                    score_breakdown = TileService.calculate_placement_score(board, pos, tile_id)
                    total_score = score_breakdown["total"]

                    # Calculate efficiency (points per resource spent)
                    cost = tile_def.cost
                    total_cost = cost.wood + cost.stone + cost.tile + cost.ink
                    efficiency = total_score / max(1, total_cost)

                    # Factor in remaining resources after purchase
                    remaining = (
                        resources.wood - cost.wood +
                        resources.stone - cost.stone +
                        resources.tile - cost.tile +
                        resources.ink - cost.ink
                    )

                    # Weighted score
                    weighted_score = total_score * 2 + efficiency + remaining * 0.1

                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_tile = tile_id
                        best_pos = pos

            if best_tile and best_pos:
                return AIDecision("place_tile", {
                    "tile_id": best_tile,
                    "position": best_pos,
                })
        else:
            # Medium difficulty: prefer high-point tiles with feng shui
            best_tile = None
            best_pos = None
            best_score = 0

            for tile_id in affordable_tiles:
                for pos in valid_positions:
                    score_breakdown = TileService.calculate_placement_score(board, pos, tile_id)
                    total_score = score_breakdown["total"]

                    if total_score > best_score:
                        best_score = total_score
                        best_tile = tile_id
                        best_pos = pos

            if best_tile and best_pos:
                return AIDecision("place_tile", {
                    "tile_id": best_tile,
                    "position": best_pos,
                })

        # Fallback: random affordable tile in random position
        tile_id = random.choice(affordable_tiles)
        pos = random.choice(valid_positions)
        return AIDecision("place_tile", {"tile_id": tile_id, "position": pos})

    @staticmethod
    def _decide_worker_placement(
        game_state: dict,
        player_state: dict,
        optimized: bool = False,
    ) -> AIDecision | None:
        """Decide where to place a worker."""
        workers = PlayerWorkers.from_dict(player_state.get("workers", {}))
        board = game_state.get("board", [])
        # Use user_id since tiles store owner_id as user_id
        player_id = player_state.get("user_id")

        # Prefer officials for higher production
        worker_type = None
        if workers.officials.available > 0:
            worker_type = "official"
        elif workers.apprentices.available > 0:
            worker_type = "apprentice"
        else:
            return None

        slots = AIService._get_worker_slots(board, worker_type)
        if not slots:
            # Try the other worker type
            if worker_type == "official" and workers.apprentices.available > 0:
                worker_type = "apprentice"
                slots = AIService._get_worker_slots(board, worker_type)
            elif worker_type == "apprentice" and workers.officials.available > 0:
                worker_type = "official"
                slots = AIService._get_worker_slots(board, worker_type)

        if not slots:
            return None

        if optimized:
            # Prefer tiles that produce resources we need
            resources = Resources.from_dict(player_state.get("resources", {}))

            # Determine which resource is most needed
            resource_priority = AIService._get_resource_priority(resources, game_state)

            best_slot = None
            best_priority = -1

            for slot in slots:
                pos = slot["position"]
                cell = board[pos["row"]][pos["col"]]
                tile = cell.get("tile", {})
                tile_id = tile.get("tile_id", "")
                category = tile_id.split("_")[0]

                # Check if this tile produces a needed resource
                resource_produced = AIService._get_tile_resource_type(category)
                if resource_produced and resource_produced in resource_priority:
                    priority = resource_priority[resource_produced]

                    # Prefer own tiles
                    if tile.get("owner_id") == player_id:
                        priority += 10

                    if priority > best_priority:
                        best_priority = priority
                        best_slot = slot

            if best_slot:
                return AIDecision("place_worker", {
                    "worker_type": worker_type,
                    "target_position": best_slot["position"],
                    "slot_index": best_slot["slot_index"],
                })

        # Default: pick a random slot
        slot = random.choice(slots)
        return AIDecision("place_worker", {
            "worker_type": worker_type,
            "target_position": slot["position"],
            "slot_index": slot["slot_index"],
        })

    @staticmethod
    def _get_resource_priority(resources: Resources, game_state: dict) -> dict[str, int]:
        """Calculate priority for each resource type based on current state."""
        # Lower amounts = higher priority
        priority = {}

        # Base priority on scarcity
        priority["wood"] = max(0, 5 - resources.wood)
        priority["stone"] = max(0, 5 - resources.stone)
        priority["tile"] = max(0, 4 - resources.tile)
        priority["ink"] = max(0, 3 - resources.ink)

        # Adjust based on available tiles
        available_tiles = game_state.get("available_tiles", [])[:3]

        for tile_id in available_tiles:
            tile_def = TileService.get_tile_definition(tile_id)
            if tile_def:
                cost = tile_def.cost
                if cost.wood > resources.wood:
                    priority["wood"] += 2
                if cost.stone > resources.stone:
                    priority["stone"] += 2
                if cost.tile > resources.tile:
                    priority["tile"] += 2
                if cost.ink > resources.ink:
                    priority["ink"] += 2

        return priority

    @staticmethod
    def _get_tile_resource_type(category: str) -> str | None:
        """Get the resource type produced by a tile category."""
        resource_map = {
            "government": "ink",
            "religious": "tile",
            "commercial": "stone",
            "residential": "wood",
        }
        return resource_map.get(category)


class AIPlayer:
    """
    Represents an AI-controlled player.
    Wraps AIService with player-specific state.
    """

    def __init__(
        self,
        player_id: int,
        user_id: int,
        username: str,
        color: str,
        difficulty: AIDifficulty = AIDifficulty.MEDIUM,
    ):
        self.player_id = player_id
        self.user_id = user_id
        self.username = username
        self.color = color
        self.difficulty = difficulty
        self.is_ai = True

    def get_decision(self, game_state: dict, player_state: dict) -> AIDecision:
        """Get the AI's next decision."""
        return AIService.make_decision(game_state, player_state, self.difficulty)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "player_id": self.player_id,
            "user_id": self.user_id,
            "username": self.username,
            "color": self.color,
            "difficulty": self.difficulty.value,
            "is_ai": True,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AIPlayer":
        """Create AIPlayer from dictionary."""
        return cls(
            player_id=data["player_id"],
            user_id=data["user_id"],
            username=data["username"],
            color=data["color"],
            difficulty=AIDifficulty(data.get("difficulty", "medium")),
        )


# Pre-defined AI personalities for more variety
AI_PERSONALITIES = {
    "aggressive_builder": {
        "name": "공격적 건축가",
        "name_en": "Aggressive Builder",
        "difficulty": AIDifficulty.HARD,
        "strategy": "Focuses on placing as many tiles as possible",
    },
    "resource_hoarder": {
        "name": "자원 수집가",
        "name_en": "Resource Hoarder",
        "difficulty": AIDifficulty.MEDIUM,
        "strategy": "Prioritizes resource generation",
    },
    "feng_shui_master": {
        "name": "풍수 대가",
        "name_en": "Feng Shui Master",
        "difficulty": AIDifficulty.HARD,
        "strategy": "Maximizes feng shui bonuses",
    },
    "beginner": {
        "name": "초보 도전자",
        "name_en": "Beginner Challenger",
        "difficulty": AIDifficulty.EASY,
        "strategy": "Makes random decisions, good for practice",
    },
}


def create_ai_opponent(
    player_id: int,
    personality: str = "resource_hoarder",
) -> AIPlayer:
    """
    Create an AI opponent with a specific personality.

    Args:
        player_id: Unique player ID
        personality: AI personality from AI_PERSONALITIES

    Returns:
        Configured AIPlayer instance
    """
    personality_data = AI_PERSONALITIES.get(personality, AI_PERSONALITIES["resource_hoarder"])

    return AIPlayer(
        player_id=player_id,
        user_id=-player_id,  # Negative user_id for AI players
        username=f"AI - {personality_data['name']}",
        color="gray",
        difficulty=personality_data["difficulty"],
    )
