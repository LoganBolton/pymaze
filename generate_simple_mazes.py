from __future__ import absolute_import
from src.maze_manager import MazeManager

if __name__ == "__main__":
    # Create a maze manager
    manager = MazeManager()

    # Generate a 3x3 maze
    print("Generating 3x3 maze...")
    maze_3x3 = manager.add_maze(3, 3)

    # Save the maze as PNG file without text
    print("Saving 3x3 maze...")
    manager.set_filename("output/maze_3x3")
    manager.show_maze(maze_3x3.id, cell_size=2, show_text=False, display=False)

    print("\nMaze generated and saved to output/maze_3x3_generation.png")
