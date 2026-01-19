"""Blueprint Card Service - 청사진 카드 시스템.

청사진 카드는 게임 시작 시 플레이어에게 배분되며,
게임 종료 시 조건 충족에 따라 추가 점수를 제공합니다.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import random

from app.services.tile_service import TileCategory


class BlueprintCategory(str, Enum):
    """Blueprint card categories."""
    PALACE_PROXIMITY = "palace_proximity"  # 궁궐 인접 관련
    CATEGORY_COLLECTION = "category_collection"  # 건물 유형 수집
    PATTERN = "pattern"  # 패턴 완성
    SPECIAL = "special"  # 특수 조건


@dataclass
class BlueprintCondition:
    """Blueprint completion condition."""
    condition_type: str
    params: dict = field(default_factory=dict)


@dataclass
class BlueprintCard:
    """Blueprint card definition."""
    blueprint_id: str
    category: BlueprintCategory
    name_ko: str
    name_en: str
    description_ko: str
    condition: BlueprintCondition
    bonus_points: int

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "blueprint_id": self.blueprint_id,
            "category": self.category.value,
            "name_ko": self.name_ko,
            "name_en": self.name_en,
            "description_ko": self.description_ko,
            "condition": {
                "type": self.condition.condition_type,
                "params": self.condition.params,
            },
            "bonus_points": self.bonus_points,
        }


# Blueprint Card Definitions
BLUEPRINT_CARDS: dict[str, BlueprintCard] = {}


def _init_blueprints():
    """Initialize all blueprint cards."""
    global BLUEPRINT_CARDS

    # === PALACE PROXIMITY (궁궐 인접) - 6 cards ===
    BLUEPRINT_CARDS["palace_neighbor_1"] = BlueprintCard(
        blueprint_id="palace_neighbor_1",
        category=BlueprintCategory.PALACE_PROXIMITY,
        name_ko="궁궐의 벗",
        name_en="Palace Companion",
        description_ko="궁궐에 인접한 내 건물 2개 이상",
        condition=BlueprintCondition("palace_adjacent", {"min_count": 2}),
        bonus_points=4,
    )
    BLUEPRINT_CARDS["palace_neighbor_2"] = BlueprintCard(
        blueprint_id="palace_neighbor_2",
        category=BlueprintCategory.PALACE_PROXIMITY,
        name_ko="궁성 수호자",
        name_en="Palace Guardian",
        description_ko="궁궐에 인접한 내 건물 3개 이상",
        condition=BlueprintCondition("palace_adjacent", {"min_count": 3}),
        bonus_points=6,
    )
    BLUEPRINT_CARDS["palace_neighbor_3"] = BlueprintCard(
        blueprint_id="palace_neighbor_3",
        category=BlueprintCategory.PALACE_PROXIMITY,
        name_ko="어전 담당관",
        name_en="Royal Steward",
        description_ko="궁궐 4방향 모두에 내 건물 배치",
        condition=BlueprintCondition("palace_surround", {"directions": 4}),
        bonus_points=10,
    )
    BLUEPRINT_CARDS["palace_neighbor_4"] = BlueprintCard(
        blueprint_id="palace_neighbor_4",
        category=BlueprintCategory.PALACE_PROXIMITY,
        name_ko="내전 설계사",
        name_en="Inner Palace Designer",
        description_ko="궁궐 인접 관아 건물 2개 이상",
        condition=BlueprintCondition("palace_adjacent_category", {"category": "government", "min_count": 2}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["palace_neighbor_5"] = BlueprintCard(
        blueprint_id="palace_neighbor_5",
        category=BlueprintCategory.PALACE_PROXIMITY,
        name_ko="왕실 상인",
        name_en="Royal Merchant",
        description_ko="궁궐 인접 시전 건물 2개 이상",
        condition=BlueprintCondition("palace_adjacent_category", {"category": "commercial", "min_count": 2}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["palace_neighbor_6"] = BlueprintCard(
        blueprint_id="palace_neighbor_6",
        category=BlueprintCategory.PALACE_PROXIMITY,
        name_ko="사찰 후원자",
        name_en="Temple Patron",
        description_ko="궁궐 인접 사찰 건물 1개 이상",
        condition=BlueprintCondition("palace_adjacent_category", {"category": "religious", "min_count": 1}),
        bonus_points=3,
    )

    # === CATEGORY COLLECTION (건물 수집) - 6 cards ===
    BLUEPRINT_CARDS["collection_commercial"] = BlueprintCard(
        blueprint_id="collection_commercial",
        category=BlueprintCategory.CATEGORY_COLLECTION,
        name_ko="상업 거물",
        name_en="Commerce Tycoon",
        description_ko="시전 건물 4개 이상 건설",
        condition=BlueprintCondition("category_count", {"category": "commercial", "min_count": 4}),
        bonus_points=6,
    )
    BLUEPRINT_CARDS["collection_residential"] = BlueprintCard(
        blueprint_id="collection_residential",
        category=BlueprintCategory.CATEGORY_COLLECTION,
        name_ko="민생 도감",
        name_en="Residential Developer",
        description_ko="민가 건물 4개 이상 건설",
        condition=BlueprintCondition("category_count", {"category": "residential", "min_count": 4}),
        bonus_points=6,
    )
    BLUEPRINT_CARDS["collection_government"] = BlueprintCard(
        blueprint_id="collection_government",
        category=BlueprintCategory.CATEGORY_COLLECTION,
        name_ko="관료의 길",
        name_en="Path of Officials",
        description_ko="관아 건물 3개 이상 건설",
        condition=BlueprintCondition("category_count", {"category": "government", "min_count": 3}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["collection_religious"] = BlueprintCard(
        blueprint_id="collection_religious",
        category=BlueprintCategory.CATEGORY_COLLECTION,
        name_ko="신앙의 수호자",
        name_en="Faith Guardian",
        description_ko="사찰 건물 3개 이상 건설",
        condition=BlueprintCondition("category_count", {"category": "religious", "min_count": 3}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["collection_diverse"] = BlueprintCard(
        blueprint_id="collection_diverse",
        category=BlueprintCategory.CATEGORY_COLLECTION,
        name_ko="만물상",
        name_en="Jack of All Trades",
        description_ko="서로 다른 5개 건물 유형 보유",
        condition=BlueprintCondition("diverse_categories", {"min_types": 5}),
        bonus_points=7,
    )
    BLUEPRINT_CARDS["collection_gate"] = BlueprintCard(
        blueprint_id="collection_gate",
        category=BlueprintCategory.CATEGORY_COLLECTION,
        name_ko="성문 관리관",
        name_en="Gate Master",
        description_ko="성문 건물 2개 이상 건설",
        condition=BlueprintCondition("category_count", {"category": "gate", "min_count": 2}),
        bonus_points=4,
    )

    # === PATTERN (패턴) - 6 cards ===
    BLUEPRINT_CARDS["pattern_row"] = BlueprintCard(
        blueprint_id="pattern_row",
        category=BlueprintCategory.PATTERN,
        name_ko="가로 완성",
        name_en="Row Completion",
        description_ko="한 가로줄에 내 건물 4개 이상",
        condition=BlueprintCondition("row_count", {"min_count": 4}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["pattern_column"] = BlueprintCard(
        blueprint_id="pattern_column",
        category=BlueprintCategory.PATTERN,
        name_ko="세로 완성",
        name_en="Column Completion",
        description_ko="한 세로줄에 내 건물 4개 이상",
        condition=BlueprintCondition("column_count", {"min_count": 4}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["pattern_diagonal"] = BlueprintCard(
        blueprint_id="pattern_diagonal",
        category=BlueprintCategory.PATTERN,
        name_ko="대각 연결",
        name_en="Diagonal Line",
        description_ko="대각선으로 내 건물 3개 연속",
        condition=BlueprintCondition("diagonal_count", {"min_count": 3}),
        bonus_points=4,
    )
    BLUEPRINT_CARDS["pattern_cluster"] = BlueprintCard(
        blueprint_id="pattern_cluster",
        category=BlueprintCategory.PATTERN,
        name_ko="밀집 지구",
        name_en="Dense District",
        description_ko="2x2 영역에 내 건물 4개",
        condition=BlueprintCondition("cluster_2x2", {}),
        bonus_points=6,
    )
    BLUEPRINT_CARDS["pattern_corner"] = BlueprintCard(
        blueprint_id="pattern_corner",
        category=BlueprintCategory.PATTERN,
        name_ko="모서리 장악",
        name_en="Corner Control",
        description_ko="보드 모서리 4곳 중 3곳에 내 건물",
        condition=BlueprintCondition("corner_count", {"min_count": 3}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["pattern_center"] = BlueprintCard(
        blueprint_id="pattern_center",
        category=BlueprintCategory.PATTERN,
        name_ko="중심 장악",
        name_en="Center Control",
        description_ko="보드 중앙 3x3 영역에 내 건물 5개 이상",
        condition=BlueprintCondition("center_count", {"min_count": 5}),
        bonus_points=7,
    )

    # === SPECIAL (특수) - 6 cards ===
    BLUEPRINT_CARDS["special_fengshui"] = BlueprintCard(
        blueprint_id="special_fengshui",
        category=BlueprintCategory.SPECIAL,
        name_ko="풍수 달인",
        name_en="Feng Shui Master",
        description_ko="풍수 보너스를 받는 건물 3개 이상",
        condition=BlueprintCondition("fengshui_count", {"min_count": 3}),
        bonus_points=6,
    )
    BLUEPRINT_CARDS["special_workers"] = BlueprintCard(
        blueprint_id="special_workers",
        category=BlueprintCategory.SPECIAL,
        name_ko="인력 동원",
        name_en="Workforce Mobilization",
        description_ko="모든 일꾼을 배치",
        condition=BlueprintCondition("all_workers_placed", {}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["special_efficiency"] = BlueprintCard(
        blueprint_id="special_efficiency",
        category=BlueprintCategory.SPECIAL,
        name_ko="자원 효율",
        name_en="Resource Efficiency",
        description_ko="게임 종료 시 자원 합계 3 이하",
        condition=BlueprintCondition("resources_under", {"max_total": 3}),
        bonus_points=4,
    )
    BLUEPRINT_CARDS["special_adjacent"] = BlueprintCard(
        blueprint_id="special_adjacent",
        category=BlueprintCategory.SPECIAL,
        name_ko="연결 제국",
        name_en="Connected Empire",
        description_ko="모든 내 건물이 서로 인접 연결",
        condition=BlueprintCondition("all_connected", {}),
        bonus_points=8,
    )
    BLUEPRINT_CARDS["special_first_builder"] = BlueprintCard(
        blueprint_id="special_first_builder",
        category=BlueprintCategory.SPECIAL,
        name_ko="선구자",
        name_en="Pioneer",
        description_ko="6개 이상의 건물 건설",
        condition=BlueprintCondition("tile_count", {"min_count": 6}),
        bonus_points=5,
    )
    BLUEPRINT_CARDS["special_balance"] = BlueprintCard(
        blueprint_id="special_balance",
        category=BlueprintCategory.SPECIAL,
        name_ko="균형 잡힌 도시",
        name_en="Balanced City",
        description_ko="관아, 시전, 민가 각 2개 이상",
        condition=BlueprintCondition("balanced_categories", {
            "categories": ["government", "commercial", "residential"],
            "min_each": 2,
        }),
        bonus_points=6,
    )


# Initialize blueprints on module load
_init_blueprints()


class BlueprintService:
    """Service for managing blueprint cards."""

    @staticmethod
    def get_blueprint(blueprint_id: str) -> BlueprintCard | None:
        """Get a blueprint card by ID."""
        return BLUEPRINT_CARDS.get(blueprint_id)

    @staticmethod
    def get_all_blueprints() -> list[BlueprintCard]:
        """Get all blueprint cards."""
        return list(BLUEPRINT_CARDS.values())

    @staticmethod
    def deal_blueprints(num_players: int, cards_per_player: int = 3) -> list[list[str]]:
        """
        Deal blueprint cards to players.

        Args:
            num_players: Number of players
            cards_per_player: Cards to deal to each player (default 3)

        Returns:
            List of blueprint ID lists, one per player
        """
        all_ids = list(BLUEPRINT_CARDS.keys())
        random.shuffle(all_ids)

        hands = []
        for i in range(num_players):
            start = i * cards_per_player
            end = start + cards_per_player
            hands.append(all_ids[start:end])

        return hands

    @staticmethod
    def select_blueprint(dealt_cards: list[str], selected_id: str) -> tuple[str, list[str]]:
        """
        Select a blueprint from dealt cards.

        Args:
            dealt_cards: List of dealt blueprint IDs
            selected_id: ID of selected blueprint

        Returns:
            Tuple of (selected_id, remaining_cards)

        Raises:
            ValueError: If selected_id not in dealt_cards
        """
        if selected_id not in dealt_cards:
            raise ValueError(f"Blueprint {selected_id} not in dealt cards")

        remaining = [card for card in dealt_cards if card != selected_id]
        return selected_id, remaining

    @staticmethod
    def evaluate_blueprint(
        blueprint_id: str,
        board: list[list[dict]],
        player: dict,
    ) -> int:
        """
        Evaluate a blueprint's condition and return bonus points.

        Args:
            blueprint_id: Blueprint card ID
            board: Current game board state
            player: Player state

        Returns:
            Bonus points if condition met, 0 otherwise
        """
        bp = BLUEPRINT_CARDS.get(blueprint_id)
        if not bp:
            return 0

        condition = bp.condition
        # Use user_id since tiles store owner_id as user_id
        player_id = player["user_id"]

        # Get player's tiles on board
        player_tiles = []
        for row in board:
            for cell in row:
                if cell.get("tile") and cell["tile"].get("owner_id") == player_id:
                    player_tiles.append({
                        "position": cell["position"],
                        "tile": cell["tile"],
                    })

        # Evaluate based on condition type
        if condition.condition_type == "palace_adjacent":
            return _evaluate_palace_adjacent(board, player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "palace_surround":
            return _evaluate_palace_surround(board, player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "palace_adjacent_category":
            return _evaluate_palace_adjacent_category(board, player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "category_count":
            return _evaluate_category_count(player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "diverse_categories":
            return _evaluate_diverse_categories(player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "row_count":
            return _evaluate_row_count(board, player_id, condition.params, bp.bonus_points)
        elif condition.condition_type == "column_count":
            return _evaluate_column_count(board, player_id, condition.params, bp.bonus_points)
        elif condition.condition_type == "diagonal_count":
            return _evaluate_diagonal_count(board, player_id, condition.params, bp.bonus_points)
        elif condition.condition_type == "cluster_2x2":
            return _evaluate_cluster_2x2(board, player_id, bp.bonus_points)
        elif condition.condition_type == "corner_count":
            return _evaluate_corner_count(board, player_id, condition.params, bp.bonus_points)
        elif condition.condition_type == "center_count":
            return _evaluate_center_count(board, player_id, condition.params, bp.bonus_points)
        elif condition.condition_type == "fengshui_count":
            return _evaluate_fengshui_count(player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "all_workers_placed":
            return _evaluate_all_workers_placed(player, bp.bonus_points)
        elif condition.condition_type == "resources_under":
            return _evaluate_resources_under(player, condition.params, bp.bonus_points)
        elif condition.condition_type == "all_connected":
            return _evaluate_all_connected(board, player_id, bp.bonus_points)
        elif condition.condition_type == "tile_count":
            return _evaluate_tile_count(player_tiles, condition.params, bp.bonus_points)
        elif condition.condition_type == "balanced_categories":
            return _evaluate_balanced_categories(player_tiles, condition.params, bp.bonus_points)

        return 0

    @staticmethod
    def calculate_total_blueprint_score(board: list[list[dict]], player: dict) -> int:
        """Calculate total score from all player's blueprints."""
        blueprints = player.get("blueprints", [])
        total = 0
        for bp_id in blueprints:
            total += BlueprintService.evaluate_blueprint(bp_id, board, player)
        return total

    @staticmethod
    def get_blueprint_score_breakdown(
        board: list[list[dict]],
        player: dict,
    ) -> dict[str, int]:
        """Get breakdown of scores for each blueprint."""
        blueprints = player.get("blueprints", [])
        breakdown = {}
        total = 0

        for bp_id in blueprints:
            score = BlueprintService.evaluate_blueprint(bp_id, board, player)
            breakdown[bp_id] = score
            total += score

        breakdown["total"] = total
        return breakdown


# === Condition Evaluation Functions ===

def _get_palace_positions(board: list[list[dict]]) -> list[dict]:
    """Find all palace positions on the board."""
    positions = []
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            tile = cell.get("tile")
            if tile and tile.get("tile_id", "").startswith("palace"):
                positions.append({"row": row_idx, "col": col_idx})
    return positions


def _get_adjacent_positions(pos: dict, board_size: int = 5) -> list[dict]:
    """Get adjacent positions (4-directional)."""
    row, col = pos["row"], pos["col"]
    adjacent = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            adjacent.append({"row": nr, "col": nc})
    return adjacent


def _get_tile_category(tile_id: str) -> str:
    """Extract category from tile ID."""
    return tile_id.split("_")[0]


def _evaluate_palace_adjacent(
    board: list[list[dict]],
    player_tiles: list[dict],
    params: dict,
    bonus: int,
) -> int:
    """Count player tiles adjacent to any palace."""
    palace_positions = _get_palace_positions(board)
    if not palace_positions:
        return 0

    adjacent_to_palace = set()
    for palace_pos in palace_positions:
        for adj_pos in _get_adjacent_positions(palace_pos):
            adjacent_to_palace.add((adj_pos["row"], adj_pos["col"]))

    count = 0
    for pt in player_tiles:
        pos = pt["position"]
        if (pos["row"], pos["col"]) in adjacent_to_palace:
            count += 1

    min_count = params.get("min_count", 1)
    return bonus if count >= min_count else 0


def _evaluate_palace_surround(
    board: list[list[dict]],
    player_tiles: list[dict],
    params: dict,
    bonus: int,
) -> int:
    """Check if player surrounds a palace on all 4 sides."""
    palace_positions = _get_palace_positions(board)
    if not palace_positions:
        return 0

    player_positions = {(pt["position"]["row"], pt["position"]["col"]) for pt in player_tiles}
    required_directions = params.get("directions", 4)

    for palace_pos in palace_positions:
        adjacent = _get_adjacent_positions(palace_pos)
        count = sum(1 for adj in adjacent if (adj["row"], adj["col"]) in player_positions)
        if count >= required_directions:
            return bonus

    return 0


def _evaluate_palace_adjacent_category(
    board: list[list[dict]],
    player_tiles: list[dict],
    params: dict,
    bonus: int,
) -> int:
    """Count player tiles of specific category adjacent to palace."""
    palace_positions = _get_palace_positions(board)
    if not palace_positions:
        return 0

    adjacent_to_palace = set()
    for palace_pos in palace_positions:
        for adj_pos in _get_adjacent_positions(palace_pos):
            adjacent_to_palace.add((adj_pos["row"], adj_pos["col"]))

    target_category = params.get("category", "")
    min_count = params.get("min_count", 1)

    count = 0
    for pt in player_tiles:
        pos = pt["position"]
        tile_id = pt["tile"].get("tile_id", "")
        category = _get_tile_category(tile_id)
        if (pos["row"], pos["col"]) in adjacent_to_palace and category == target_category:
            count += 1

    return bonus if count >= min_count else 0


def _evaluate_category_count(player_tiles: list[dict], params: dict, bonus: int) -> int:
    """Count tiles of specific category."""
    target_category = params.get("category", "")
    min_count = params.get("min_count", 1)

    count = sum(
        1 for pt in player_tiles
        if _get_tile_category(pt["tile"].get("tile_id", "")) == target_category
    )
    return bonus if count >= min_count else 0


def _evaluate_diverse_categories(player_tiles: list[dict], params: dict, bonus: int) -> int:
    """Count unique tile categories."""
    categories = {_get_tile_category(pt["tile"].get("tile_id", "")) for pt in player_tiles}
    min_types = params.get("min_types", 1)
    return bonus if len(categories) >= min_types else 0


def _evaluate_row_count(
    board: list[list[dict]],
    player_id: int,
    params: dict,
    bonus: int,
) -> int:
    """Check if player has enough tiles in any row."""
    min_count = params.get("min_count", 1)

    for row in board:
        count = sum(
            1 for cell in row
            if cell.get("tile") and cell["tile"].get("owner_id") == player_id
        )
        if count >= min_count:
            return bonus
    return 0


def _evaluate_column_count(
    board: list[list[dict]],
    player_id: int,
    params: dict,
    bonus: int,
) -> int:
    """Check if player has enough tiles in any column."""
    min_count = params.get("min_count", 1)
    board_size = len(board)

    for col in range(board_size):
        count = sum(
            1 for row in range(board_size)
            if board[row][col].get("tile") and board[row][col]["tile"].get("owner_id") == player_id
        )
        if count >= min_count:
            return bonus
    return 0


def _evaluate_diagonal_count(
    board: list[list[dict]],
    player_id: int,
    params: dict,
    bonus: int,
) -> int:
    """Check for diagonal line of player tiles."""
    min_count = params.get("min_count", 3)
    board_size = len(board)

    def check_diagonal(start_row: int, start_col: int, dr: int, dc: int) -> int:
        count = 0
        max_count = 0
        r, c = start_row, start_col
        while 0 <= r < board_size and 0 <= c < board_size:
            cell = board[r][c]
            if cell.get("tile") and cell["tile"].get("owner_id") == player_id:
                count += 1
                max_count = max(max_count, count)
            else:
                count = 0
            r += dr
            c += dc
        return max_count

    # Check all diagonals
    for i in range(board_size):
        # Top-left to bottom-right
        if check_diagonal(0, i, 1, 1) >= min_count:
            return bonus
        if check_diagonal(i, 0, 1, 1) >= min_count:
            return bonus
        # Top-right to bottom-left
        if check_diagonal(0, i, 1, -1) >= min_count:
            return bonus
        if check_diagonal(i, board_size - 1, 1, -1) >= min_count:
            return bonus

    return 0


def _evaluate_cluster_2x2(board: list[list[dict]], player_id: int, bonus: int) -> int:
    """Check for 2x2 cluster of player tiles."""
    board_size = len(board)

    for r in range(board_size - 1):
        for c in range(board_size - 1):
            cells = [
                board[r][c], board[r][c+1],
                board[r+1][c], board[r+1][c+1]
            ]
            if all(
                cell.get("tile") and cell["tile"].get("owner_id") == player_id
                for cell in cells
            ):
                return bonus
    return 0


def _evaluate_corner_count(
    board: list[list[dict]],
    player_id: int,
    params: dict,
    bonus: int,
) -> int:
    """Count player tiles in corners."""
    board_size = len(board)
    corners = [
        (0, 0), (0, board_size - 1),
        (board_size - 1, 0), (board_size - 1, board_size - 1)
    ]

    count = sum(
        1 for r, c in corners
        if board[r][c].get("tile") and board[r][c]["tile"].get("owner_id") == player_id
    )

    min_count = params.get("min_count", 1)
    return bonus if count >= min_count else 0


def _evaluate_center_count(
    board: list[list[dict]],
    player_id: int,
    params: dict,
    bonus: int,
) -> int:
    """Count player tiles in center 3x3 area."""
    board_size = len(board)
    center_start = (board_size - 3) // 2
    center_end = center_start + 3

    count = 0
    for r in range(center_start, center_end):
        for c in range(center_start, center_end):
            cell = board[r][c]
            if cell.get("tile") and cell["tile"].get("owner_id") == player_id:
                count += 1

    min_count = params.get("min_count", 1)
    return bonus if count >= min_count else 0


def _evaluate_fengshui_count(player_tiles: list[dict], params: dict, bonus: int) -> int:
    """Count tiles with fengshui bonus active."""
    count = sum(
        1 for pt in player_tiles
        if pt["tile"].get("fengshui_active", False)
    )
    min_count = params.get("min_count", 1)
    return bonus if count >= min_count else 0


def _evaluate_all_workers_placed(player: dict, bonus: int) -> int:
    """Check if all workers are placed."""
    workers = player.get("workers", {})
    apprentices = workers.get("apprentices", {})
    officials = workers.get("officials", {})

    if apprentices.get("available", 0) == 0 and officials.get("available", 0) == 0:
        return bonus
    return 0


def _evaluate_resources_under(player: dict, params: dict, bonus: int) -> int:
    """Check if total resources are under threshold."""
    resources = player.get("resources", {})
    total = sum(resources.values())
    max_total = params.get("max_total", 0)
    return bonus if total <= max_total else 0


def _evaluate_all_connected(board: list[list[dict]], player_id: int, bonus: int) -> int:
    """Check if all player tiles are connected."""
    player_positions = []
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell.get("tile") and cell["tile"].get("owner_id") == player_id:
                player_positions.append((row_idx, col_idx))

    if len(player_positions) <= 1:
        return bonus  # 0 or 1 tile is trivially connected

    # BFS to check connectivity
    visited = {player_positions[0]}
    queue = [player_positions[0]]
    position_set = set(player_positions)

    while queue:
        r, c = queue.pop(0)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in position_set and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))

    return bonus if len(visited) == len(player_positions) else 0


def _evaluate_tile_count(player_tiles: list[dict], params: dict, bonus: int) -> int:
    """Check total tile count."""
    min_count = params.get("min_count", 1)
    return bonus if len(player_tiles) >= min_count else 0


def _evaluate_balanced_categories(player_tiles: list[dict], params: dict, bonus: int) -> int:
    """Check if player has minimum tiles in each specified category."""
    categories = params.get("categories", [])
    min_each = params.get("min_each", 1)

    category_counts = {}
    for pt in player_tiles:
        cat = _get_tile_category(pt["tile"].get("tile_id", ""))
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat in categories:
        if category_counts.get(cat, 0) < min_each:
            return 0

    return bonus
