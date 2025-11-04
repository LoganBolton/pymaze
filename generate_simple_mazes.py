from __future__ import absolute_import

import os

from src.maze_manager import MazeManager


OUTPUT_DIR = "output"


def ensure_output_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


if __name__ == "__main__":
    ensure_output_dir(OUTPUT_DIR)

    manager = MazeManager()

    for idx in range(1, 6):
        print(f"Generating 3x3 maze {idx}...")
        maze = manager.add_maze(3, 3)

        filename = os.path.join(OUTPUT_DIR, f"maze_3x3_{idx}")
        print(f"Saving 3x3 maze {idx} to {filename}_generation.png")
        manager.set_filename(filename)
        manager.show_maze(maze.id, cell_size=20, show_text=False, display=False)

    for idx in range(1, 6):
        print(f"Generating 4x4 maze {idx}...")
        maze = manager.add_maze(4, 4)

        filename = os.path.join(OUTPUT_DIR, f"maze_4x4_{idx}")
        print(f"Saving 4x4 maze {idx} to {filename}_generation.png")
        manager.set_filename(filename)
        manager.show_maze(maze.id, cell_size=18, show_text=False, display=False)

    print("\nAll 3x3 and 4x4 mazes generated and saved to the output directory.")
