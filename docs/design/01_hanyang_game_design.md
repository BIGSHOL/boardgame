# Hanyang: The Foundation (한양: 도읍의 설계자들) - Game Design Document

## 1. Game Overview
- **Theme**: Early Joseon Dynasty (1394). Construction of the new capital, Hanyang.
- **Role**: Chief Architects designing the palace, walls, gates, and markets.
- **Goal**: Build the most prestigious city by managing resources, dispatching workers, and utilizing Feng Shui (Baesanimsu).

## 2. Visual Style & Color Palette
- **Architecture (Gray #373d41)**: Walls, Tiles, Stone.
- **Scholars/Night (Navy #081429)**: Officials (Meeples), Rivers, Ink.
- **Wealth/Prosperity (Yellow #fdb813)**: Brassware, Coins, Crops, Bonus Points.

## 3. Core Mechanics

### 3.1. Hybrid Board System
The game utilizes two distinct types of boards:
1.  **Main Board (The Capital Map)**
    -   Represents the shared construction site of Hanyang.
    -   Contains the geography (Mountain to North, Water to South) for Feng Shui bonuses.
    -   Start with limited spaces; highly competitive area control.
    -   **Action**: Placement of Building Tiles.
2.  **Player Board (The Architect's Desk)**
    -   Represents the player's personal office/workshop.
    -   **Action**: Resource gathering, engine building, worker management.
    -   **Components**: Slots for Tuckable cards, Resource tracks, Worker holding area.

### 3.2. Worker System: 'Dispatch & Settle'
-   **Apprentice (Personal Board)**: Workers start on the player board to gather resources or upgrade tech. They return to the pool after use (standard placement).
-   **Official (Main Board)**: To build on the Main Board, a worker must be **Dispatched**.
    -   **Permanent Assignment**: Dispatched workers stay on the building tile placed on the Main Board. They do **not** return.
    -   **Trade-off**: Increases influence/scoring on the map but reduces the number of available actions per turn on the Personal Board.

### 3.3. Multi-use Cards (The Blueprint System)
Every card represents a blueprint and has two sections:
-   **Top (Construction Mode)**: Detailed building.
    -   *Cost*: High resources.
    -   *Effect*: Place tile on Main Board + Score Points + Influence.
-   **Bottom (Resource/Support Mode)**: Foundation/Logistics.
    -   *Action*: Tuck under Player Board.
    -   *Effect*: Passive income (e.g., +1 Stone per turn), Ability upgrade, or one-time resource burst.

### 3.4. Landscape & Feng Shui (Baesanimsu)
-   **Grid System**: The Main Board is a grid.
-   **Feng Shui Bonus**:
    -   *Criteria*: Back to Mountain (North), Face to Water (South).
    -   *Reward*: Yellow Marker (Bonus Points/Currency).
-   **Adjacency Synergy**: Placing specific building types next to others triggers combos (e.g., Market next to Residential).

## 4. Game Loop (Turn Structure)
On a turn, a player chooses **ONE** main action:

1.  **Drafting (Design)**: Take a Blueprint Card from the central market.
2.  **Resource Gathering (Logistics)**: Place a worker on the Personal Board (Quarry, Logging, Kiln) to get materials.
3.  **Construction (Build)**:
    -   Pay resources.
    -   **Dispatch** a worker to the Main Board.
    -   Place a Building Tile and the Worker on the map.
    -   Trigger 'On Build' effects and check Adjacency/Feng Shui.
4.  **Registration (Engine Building)**:
    -   Tuck a card under the Personal Board.
    -   Gain its passive benefit immediately or from next turn (Engine buildup).

## 5. End Game Condition
-   **The Four Great Gates (Sadämum)**: The game ends when all 4 Gates are constructed.
-   **Scoring**:
    -   Building Points (on tiles).
    -   Feng Shui Bonuses (Yellow markers).
    -   Adjacency Synergies.
    -   Contribution to the Great Gates.

## 6. Components (Digital/Physical)
-   **Meeples**: Gat-wearing Scholars (Navy).
-   **Tokens**: Wood (Log), Stone (Hex), Coin (Circle), Ink (Drop).
-   **Tiles**: Polyomino or Square tiles for buildings.
