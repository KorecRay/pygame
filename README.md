# Ink Ninja - Remastered

A Pygame-based platformer game featuring Tiled map integration, dynamic lighting, and level management.

## Features

*   **Tiled Map Integration:** Loads `.tmx` maps with support for tile layers and object layers (collisions, hazards, etc.).
*   **Dynamic Lighting:** Implements a light manager for visibility effects.
*   **Level System:** Includes a level selector and JSON-based level data management.
*   **Game Entities:**
    *   **Player:** Controllable character with movement and physics.
    *   **Enemies:** AI-controlled entities with patrol logic.
    *   **Props:** Interactive items like shields, torches, and anti-explosion power-ups.
*   **Debug Mode:** Visualizes hitboxes and collision rectangles for development.

## How to Run

1.  **Install dependencies:**

    ```bash
    pip install pygame pytmx
    ```

2.  **Run the game:**

    ```bash
    python main.py
    ```

## Controls

*   **Arrow Keys:** Move
*   **Space:** Jump
*   **R:** Restart Level
*   **M:** Toggle Debug Mode
*   **ESC:** Pause Game

## Project Structure

*   `main.py`: Game entry point and main loop.
*   `settings.py`: Global configuration and constants.
*   `core/`: Core systems (Map loader, Light manager, Level selector, etc.).
*   `sprites/`: Game entity classes (Player, Enemy, Prop, Destination).
*   `assets/`: Game assets (Maps, Images, JSON data).

## Development

*   **Map Editing:** Use [Tiled Map Editor](https://www.mapeditor.org/) to modify `.tmx` files in `assets/map/`.
*   **Level Data:** Configure spawn points and enemy data in `assets/data/level_data.json`.
