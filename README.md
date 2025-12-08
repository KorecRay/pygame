# Pygame Tiled Project

This is a project demonstrating how to use Tiled Map Editor with Pygame.

## Features

*   Loads TMX maps created with the Tiled Map Editor.
*   Renders tile layers.
*   Handles collision detection based on object layers in Tiled.

## How to Run

1.  **Install dependencies:**

    ```bash
    pip install pygame pytmx
    ```

2.  **Run the game:**

    ```bash
    python main.py
    ```

## Project Structure

*   `main.py`: The main entry point of the game.
*   `settings.py`: Contains all the game settings and constants.
*   `core/maploader.py`: Handles loading and rendering the Tiled map.
*   `assets/`: Contains all game assets like maps and tilesets.
*   `sprites/`: Contains game sprites like the player and enemies.
