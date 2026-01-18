"""
Tile service for managing building tiles.
Handles tile definitions, placement, and scoring.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.services.resource_service import Resources, ResourceType


class TileCategory(str, Enum):
    """Building tile categories."""
    PALACE = "palace"
    GOVERNMENT = "government"
    RELIGIOUS = "religious"
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    GATE = "gate"


@dataclass
class TileCost:
    """Cost to build a tile."""
    wood: int = 0
    stone: int = 0
    tile: int = 0
    ink: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "wood": self.wood,
            "stone": self.stone,
            "tile": self.tile,
            "ink": self.ink,
        }

    def to_resource_dict(self) -> dict[ResourceType, int]:
        """Convert to ResourceType dict for payment."""
        cost = {}
        if self.wood > 0:
            cost[ResourceType.WOOD] = self.wood
        if self.stone > 0:
            cost[ResourceType.STONE] = self.stone
        if self.tile > 0:
            cost[ResourceType.TILE] = self.tile
        if self.ink > 0:
            cost[ResourceType.INK] = self.ink
        return cost


@dataclass
class TileDefinition:
    """Definition of a building tile."""
    tile_id: str
    category: TileCategory
    name_ko: str
    name_en: str
    cost: TileCost
    base_points: int
    fengshui_bonus: int  # Bonus when placed with good feng shui
    adjacency_bonus: dict[TileCategory, int]  # Bonus for adjacent tiles
    special_effect: str | None = None
    worker_slots: int = 2  # Apprentice slots (official slot is always 1)

    def to_dict(self) -> dict:
        return {
            "tile_id": self.tile_id,
            "category": self.category.value,
            "name_ko": self.name_ko,
            "name_en": self.name_en,
            "cost": self.cost.to_dict(),
            "base_points": self.base_points,
            "fengshui_bonus": self.fengshui_bonus,
            "adjacency_bonus": {k.value: v for k, v in self.adjacency_bonus.items()},
            "special_effect": self.special_effect,
            "worker_slots": self.worker_slots,
        }


# Tile Definitions - Core Game Tiles
TILE_DEFINITIONS: dict[str, TileDefinition] = {
    # Palace tiles (4) - High points, high cost
    "palace_1": TileDefinition(
        tile_id="palace_1",
        category=TileCategory.PALACE,
        name_ko="경복궁",
        name_en="Gyeongbokgung Palace",
        cost=TileCost(wood=3, stone=3, tile=2, ink=1),
        base_points=8,
        fengshui_bonus=4,
        adjacency_bonus={TileCategory.GOVERNMENT: 2},
        special_effect="royal_blessing",
    ),
    "palace_2": TileDefinition(
        tile_id="palace_2",
        category=TileCategory.PALACE,
        name_ko="창덕궁",
        name_en="Changdeokgung Palace",
        cost=TileCost(wood=3, stone=2, tile=2, ink=1),
        base_points=7,
        fengshui_bonus=4,
        adjacency_bonus={TileCategory.RELIGIOUS: 2},
        special_effect="secret_garden",
    ),
    "palace_3": TileDefinition(
        tile_id="palace_3",
        category=TileCategory.PALACE,
        name_ko="경희궁",
        name_en="Gyeonghuigung Palace",
        cost=TileCost(wood=2, stone=3, tile=2, ink=1),
        base_points=6,
        fengshui_bonus=3,
        adjacency_bonus={TileCategory.PALACE: 3},
    ),
    "palace_4": TileDefinition(
        tile_id="palace_4",
        category=TileCategory.PALACE,
        name_ko="덕수궁",
        name_en="Deoksugung Palace",
        cost=TileCost(wood=2, stone=2, tile=2, ink=1),
        base_points=5,
        fengshui_bonus=3,
        adjacency_bonus={TileCategory.COMMERCIAL: 2},
    ),

    # Government tiles (6) - Moderate points, produce ink
    "government_1": TileDefinition(
        tile_id="government_1",
        category=TileCategory.GOVERNMENT,
        name_ko="의정부",
        name_en="State Council",
        cost=TileCost(wood=2, stone=2, ink=1),
        base_points=4,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.PALACE: 2},
        special_effect="policy_maker",
    ),
    "government_2": TileDefinition(
        tile_id="government_2",
        category=TileCategory.GOVERNMENT,
        name_ko="육조거리",
        name_en="Six Ministries Street",
        cost=TileCost(wood=2, stone=1, ink=1),
        base_points=3,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.GOVERNMENT: 1},
    ),
    "government_3": TileDefinition(
        tile_id="government_3",
        category=TileCategory.GOVERNMENT,
        name_ko="사헌부",
        name_en="Office of Inspector General",
        cost=TileCost(wood=1, stone=2, ink=1),
        base_points=3,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.PALACE: 1},
    ),
    "government_4": TileDefinition(
        tile_id="government_4",
        category=TileCategory.GOVERNMENT,
        name_ko="성균관",
        name_en="Royal Academy",
        cost=TileCost(wood=2, stone=1, tile=1),
        base_points=4,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.RELIGIOUS: 1},
        special_effect="scholar_training",
    ),
    "government_5": TileDefinition(
        tile_id="government_5",
        category=TileCategory.GOVERNMENT,
        name_ko="한성부",
        name_en="Capital Administration",
        cost=TileCost(wood=1, stone=1, ink=1),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.RESIDENTIAL: 1},
    ),
    "government_6": TileDefinition(
        tile_id="government_6",
        category=TileCategory.GOVERNMENT,
        name_ko="승정원",
        name_en="Royal Secretariat",
        cost=TileCost(wood=1, stone=2),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.PALACE: 1},
    ),

    # Religious tiles (6) - Moderate points, produce tiles
    "religious_1": TileDefinition(
        tile_id="religious_1",
        category=TileCategory.RELIGIOUS,
        name_ko="종묘",
        name_en="Jongmyo Shrine",
        cost=TileCost(wood=2, stone=2, tile=1),
        base_points=5,
        fengshui_bonus=3,
        adjacency_bonus={TileCategory.PALACE: 2},
        special_effect="ancestral_blessing",
    ),
    "religious_2": TileDefinition(
        tile_id="religious_2",
        category=TileCategory.RELIGIOUS,
        name_ko="사직단",
        name_en="Sajik Altar",
        cost=TileCost(wood=1, stone=2, tile=1),
        base_points=4,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.GOVERNMENT: 1},
    ),
    "religious_3": TileDefinition(
        tile_id="religious_3",
        category=TileCategory.RELIGIOUS,
        name_ko="원각사",
        name_en="Wongaksa Temple",
        cost=TileCost(wood=2, stone=1, tile=1),
        base_points=3,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.RELIGIOUS: 1},
    ),
    "religious_4": TileDefinition(
        tile_id="religious_4",
        category=TileCategory.RELIGIOUS,
        name_ko="흥천사",
        name_en="Heungcheonsa Temple",
        cost=TileCost(wood=2, stone=1),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.RESIDENTIAL: 1},
    ),
    "religious_5": TileDefinition(
        tile_id="religious_5",
        category=TileCategory.RELIGIOUS,
        name_ko="봉은사",
        name_en="Bongeunsa Temple",
        cost=TileCost(wood=1, stone=1, tile=1),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
    ),
    "religious_6": TileDefinition(
        tile_id="religious_6",
        category=TileCategory.RELIGIOUS,
        name_ko="문묘",
        name_en="Confucian Shrine",
        cost=TileCost(wood=1, stone=2),
        base_points=3,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.GOVERNMENT: 1},
    ),

    # Commercial tiles (8) - Low points, produce stone
    "commercial_1": TileDefinition(
        tile_id="commercial_1",
        category=TileCategory.COMMERCIAL,
        name_ko="시전",
        name_en="Market Street",
        cost=TileCost(wood=1, stone=1),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
        special_effect="trade_route",
    ),
    "commercial_2": TileDefinition(
        tile_id="commercial_2",
        category=TileCategory.COMMERCIAL,
        name_ko="이현",
        name_en="Ihyeon Market",
        cost=TileCost(wood=1, stone=1),
        base_points=1,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.RESIDENTIAL: 1},
    ),
    "commercial_3": TileDefinition(
        tile_id="commercial_3",
        category=TileCategory.COMMERCIAL,
        name_ko="칠패",
        name_en="Chilpae Market",
        cost=TileCost(wood=2, stone=1),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.GATE: 1},
    ),
    "commercial_4": TileDefinition(
        tile_id="commercial_4",
        category=TileCategory.COMMERCIAL,
        name_ko="종로",
        name_en="Jongno Street",
        cost=TileCost(wood=1, stone=2),
        base_points=3,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.GOVERNMENT: 1},
    ),
    "commercial_5": TileDefinition(
        tile_id="commercial_5",
        category=TileCategory.COMMERCIAL,
        name_ko="운종가",
        name_en="Unjongga",
        cost=TileCost(wood=1, stone=1),
        base_points=1,
        fengshui_bonus=0,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
    ),
    "commercial_6": TileDefinition(
        tile_id="commercial_6",
        category=TileCategory.COMMERCIAL,
        name_ko="배오개",
        name_en="Baeogae",
        cost=TileCost(wood=1, stone=1),
        base_points=1,
        fengshui_bonus=0,
        adjacency_bonus={TileCategory.RESIDENTIAL: 1},
    ),
    "commercial_7": TileDefinition(
        tile_id="commercial_7",
        category=TileCategory.COMMERCIAL,
        name_ko="광통교",
        name_en="Gwangtong Bridge",
        cost=TileCost(wood=2),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={},
        special_effect="bridge_crossing",
    ),
    "commercial_8": TileDefinition(
        tile_id="commercial_8",
        category=TileCategory.COMMERCIAL,
        name_ko="저자거리",
        name_en="Jeoja Street",
        cost=TileCost(stone=2),
        base_points=1,
        fengshui_bonus=0,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
    ),

    # Residential tiles (8) - Lowest points, produce wood
    "residential_1": TileDefinition(
        tile_id="residential_1",
        category=TileCategory.RESIDENTIAL,
        name_ko="북촌",
        name_en="Bukchon",
        cost=TileCost(wood=2),
        base_points=2,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.PALACE: 1},
        special_effect="noble_district",
    ),
    "residential_2": TileDefinition(
        tile_id="residential_2",
        category=TileCategory.RESIDENTIAL,
        name_ko="남촌",
        name_en="Namchon",
        cost=TileCost(wood=2),
        base_points=2,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.GOVERNMENT: 1},
    ),
    "residential_3": TileDefinition(
        tile_id="residential_3",
        category=TileCategory.RESIDENTIAL,
        name_ko="서촌",
        name_en="Seochon",
        cost=TileCost(wood=1, stone=1),
        base_points=1,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.RELIGIOUS: 1},
    ),
    "residential_4": TileDefinition(
        tile_id="residential_4",
        category=TileCategory.RESIDENTIAL,
        name_ko="중촌",
        name_en="Jungchon",
        cost=TileCost(wood=1),
        base_points=1,
        fengshui_bonus=0,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
    ),
    "residential_5": TileDefinition(
        tile_id="residential_5",
        category=TileCategory.RESIDENTIAL,
        name_ko="피맛골",
        name_en="Pimatgol",
        cost=TileCost(wood=1),
        base_points=0,
        fengshui_bonus=0,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
    ),
    "residential_6": TileDefinition(
        tile_id="residential_6",
        category=TileCategory.RESIDENTIAL,
        name_ko="청계천변",
        name_en="Cheonggyecheon Side",
        cost=TileCost(wood=1, stone=1),
        base_points=1,
        fengshui_bonus=1,
        adjacency_bonus={},
        special_effect="waterfront",
    ),
    "residential_7": TileDefinition(
        tile_id="residential_7",
        category=TileCategory.RESIDENTIAL,
        name_ko="가회동",
        name_en="Gahoe-dong",
        cost=TileCost(wood=2),
        base_points=1,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.RESIDENTIAL: 1},
    ),
    "residential_8": TileDefinition(
        tile_id="residential_8",
        category=TileCategory.RESIDENTIAL,
        name_ko="인사동",
        name_en="Insa-dong",
        cost=TileCost(wood=1),
        base_points=1,
        fengshui_bonus=0,
        adjacency_bonus={TileCategory.COMMERCIAL: 1},
    ),

    # Gate tiles (4) - Special tiles for city walls
    "gate_1": TileDefinition(
        tile_id="gate_1",
        category=TileCategory.GATE,
        name_ko="숭례문",
        name_en="Sungnyemun Gate",
        cost=TileCost(wood=1, stone=3),
        base_points=4,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.COMMERCIAL: 2},
        special_effect="south_gate",
        worker_slots=1,
    ),
    "gate_2": TileDefinition(
        tile_id="gate_2",
        category=TileCategory.GATE,
        name_ko="흥인지문",
        name_en="Heunginjimun Gate",
        cost=TileCost(wood=1, stone=3),
        base_points=4,
        fengshui_bonus=2,
        adjacency_bonus={TileCategory.COMMERCIAL: 2},
        special_effect="east_gate",
        worker_slots=1,
    ),
    "gate_3": TileDefinition(
        tile_id="gate_3",
        category=TileCategory.GATE,
        name_ko="돈의문",
        name_en="Donuimun Gate",
        cost=TileCost(wood=1, stone=2),
        base_points=3,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.RESIDENTIAL: 1},
        special_effect="west_gate",
        worker_slots=1,
    ),
    "gate_4": TileDefinition(
        tile_id="gate_4",
        category=TileCategory.GATE,
        name_ko="숙정문",
        name_en="Sukjeongmun Gate",
        cost=TileCost(wood=1, stone=2),
        base_points=3,
        fengshui_bonus=1,
        adjacency_bonus={TileCategory.PALACE: 1},
        special_effect="north_gate",
        worker_slots=1,
    ),
}


class TileService:
    """Service for managing building tiles."""

    @staticmethod
    def get_tile_definition(tile_id: str) -> TileDefinition | None:
        """Get tile definition by ID."""
        return TILE_DEFINITIONS.get(tile_id)

    @staticmethod
    def get_all_tiles() -> list[TileDefinition]:
        """Get all tile definitions."""
        return list(TILE_DEFINITIONS.values())

    @staticmethod
    def get_tiles_by_category(category: TileCategory) -> list[TileDefinition]:
        """Get all tiles of a specific category."""
        return [t for t in TILE_DEFINITIONS.values() if t.category == category]

    @staticmethod
    def can_afford_tile(resources: Resources, tile_id: str) -> bool:
        """Check if player can afford to build a tile."""
        tile = TileService.get_tile_definition(tile_id)
        if not tile:
            return False

        return (
            resources.wood >= tile.cost.wood
            and resources.stone >= tile.cost.stone
            and resources.tile >= tile.cost.tile
            and resources.ink >= tile.cost.ink
        )

    @staticmethod
    def validate_placement(
        board: list[list[dict]],
        position: dict,
        tile_id: str,
    ) -> tuple[bool, str]:
        """
        Validate tile placement on board.

        Args:
            board: Current game board
            position: Target position {row, col}
            tile_id: Tile to place

        Returns:
            Tuple of (is_valid, error_message)
        """
        row, col = position["row"], position["col"]

        # Check bounds
        if not (0 <= row < 5 and 0 <= col < 5):
            return False, "Position out of bounds"

        cell = board[row][col]

        # Check terrain
        if cell["terrain"] == "mountain":
            return False, "Cannot build on mountain"

        # Check if cell is already occupied
        if cell["tile"] is not None:
            return False, "Cell already has a tile"

        # Check tile exists
        tile = TileService.get_tile_definition(tile_id)
        if not tile:
            return False, "Invalid tile ID"

        return True, ""

    @staticmethod
    def calculate_placement_score(
        board: list[list[dict]],
        position: dict,
        tile_id: str,
    ) -> dict:
        """
        Calculate score for placing a tile.

        Args:
            board: Current game board
            position: Target position
            tile_id: Tile being placed

        Returns:
            Score breakdown dictionary
        """
        tile = TileService.get_tile_definition(tile_id)
        if not tile:
            return {"base": 0, "fengshui": 0, "adjacency": 0, "total": 0}

        row, col = position["row"], position["col"]
        base_points = tile.base_points

        # Calculate feng shui bonus (배산임수 - mountain behind, water in front)
        fengshui_bonus = TileService._calculate_fengshui(board, row, col, tile)

        # Calculate adjacency bonus
        adjacency_bonus = TileService._calculate_adjacency(board, row, col, tile)

        total = base_points + fengshui_bonus + adjacency_bonus

        return {
            "base": base_points,
            "fengshui": fengshui_bonus,
            "adjacency": adjacency_bonus,
            "total": total,
        }

    @staticmethod
    def _calculate_fengshui(
        board: list[list[dict]],
        row: int,
        col: int,
        tile: TileDefinition,
    ) -> int:
        """Calculate feng shui bonus for placement."""
        # 배산임수: Mountain to the north (lower row), water to the south (higher row)
        has_mountain_north = row > 0 and board[row - 1][col]["terrain"] == "mountain"
        has_water_south = row < 4 and board[row + 1][col]["terrain"] == "water"

        # Also check for water in center
        is_near_water = False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < 5 and 0 <= nc < 5:
                    if board[nr][nc]["terrain"] == "water":
                        is_near_water = True
                        break

        if has_mountain_north and (has_water_south or is_near_water):
            return tile.fengshui_bonus
        elif has_mountain_north or is_near_water:
            return tile.fengshui_bonus // 2

        return 0

    @staticmethod
    def _calculate_adjacency(
        board: list[list[dict]],
        row: int,
        col: int,
        tile: TileDefinition,
    ) -> int:
        """Calculate adjacency bonus for placement."""
        bonus = 0

        # Check 4 adjacent cells (orthogonal only)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                adjacent_cell = board[nr][nc]
                if adjacent_cell["tile"] is not None:
                    adjacent_tile_id = adjacent_cell["tile"]["tile_id"]
                    adjacent_tile = TileService.get_tile_definition(adjacent_tile_id)
                    if adjacent_tile and adjacent_tile.category in tile.adjacency_bonus:
                        bonus += tile.adjacency_bonus[adjacent_tile.category]

        return bonus

    @staticmethod
    def create_placed_tile(
        tile_id: str,
        owner_id: int,
    ) -> dict:
        """Create a placed tile data structure."""
        tile = TileService.get_tile_definition(tile_id)
        if not tile:
            raise ValueError(f"Invalid tile ID: {tile_id}")

        return {
            "tile_id": tile_id,
            "owner_id": owner_id,
            "placed_workers": [],
            "fengshui_active": False,
        }

    @staticmethod
    def get_resource_production(tile_id: str) -> ResourceType | None:
        """Get the resource type produced by a tile."""
        tile = TileService.get_tile_definition(tile_id)
        if not tile:
            return None

        production_map = {
            TileCategory.PALACE: None,
            TileCategory.GOVERNMENT: ResourceType.INK,
            TileCategory.RELIGIOUS: ResourceType.TILE,
            TileCategory.COMMERCIAL: ResourceType.STONE,
            TileCategory.RESIDENTIAL: ResourceType.WOOD,
            TileCategory.GATE: None,
        }
        return production_map.get(tile.category)
