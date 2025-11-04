from __future__ import absolute_import

import json
import os
import uuid
from collections import deque
from datetime import datetime

from src.maze_manager import MazeManager


OUTPUT_DIR = "output"


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def save_metadata(path, data):
    with open(path, "w", encoding="utf-8") as metadata_file:
        json.dump(data, metadata_file, indent=2)


def compute_shortest_path(maze):
    start = maze.entry_coor
    goal = maze.exit_coor

    queue = deque([start])
    parents = {start: None}

    def get_neighbors(r, c):
        cell = maze.grid[r][c]
        neighbors = []
        if not cell.walls["top"] and r > 0:
            neighbors.append((r - 1, c))
        if not cell.walls["right"] and c < maze.num_cols - 1:
            neighbors.append((r, c + 1))
        if not cell.walls["bottom"] and r < maze.num_rows - 1:
            neighbors.append((r + 1, c))
        if not cell.walls["left"] and c > 0:
            neighbors.append((r, c - 1))
        return neighbors

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for neighbor in get_neighbors(*current):
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)

    if goal not in parents:
        return {
            "coordinates": [],
            "directions": [],
            "directions_numeric": [],
        }

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parents[node]
    path.reverse()

    direction_map = {
        (-1, 0): ("down", 0),   # visually downward on plot
        (1, 0): ("up", 1),      # visually upward on plot
        (0, -1): ("left", 2),
        (0, 1): ("right", 3),
    }

    directions = []
    numeric = []
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        dr = r2 - r1
        dc = c2 - c1
        dir_label, dir_code = direction_map[(dr, dc)]
        directions.append(dir_label)
        numeric.append(dir_code)

    return {
        "coordinates": [list(coord) for coord in path],
        "directions": directions,
        "directions_numeric": numeric,
    }


def run_generation():
    ensure_dir(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(OUTPUT_DIR, f"generation_{timestamp}")
    ensure_dir(run_dir)

    manager = MazeManager()

    maze_specs = [
        {"rows": 3, "cols": 3, "cell_size": 20, "count": 5},
        {"rows": 4, "cols": 4, "cell_size": 18, "count": 5},
    ]

    maze_index = 1

    for spec in maze_specs:
        rows = spec["rows"]
        cols = spec["cols"]
        cell_size = spec["cell_size"]
        count = spec["count"]

        for _ in range(count):
            print(f"Generating {rows}x{cols} maze {maze_index}...")
            maze = manager.add_maze(rows, cols)

            maze_dir = os.path.join(run_dir, f"maze_{maze_index}")
            ensure_dir(maze_dir)

            short_uuid = uuid.uuid4().hex[:8]
            file_stem = f"maze_{short_uuid}_{maze_index}"
            base_filename = os.path.join(maze_dir, file_stem)
            manager.set_filename(base_filename)

            print(f"Saving maze {maze_index} to {base_filename}_generation.png")
            manager.show_maze(maze.id, cell_size=cell_size, show_text=False, display=False)

            generated_path = f"{base_filename}_generation.png"
            final_png_name = f"{file_stem}.png"
            final_png_path = os.path.join(maze_dir, final_png_name)
            os.replace(generated_path, final_png_path)

            shortest_path = compute_shortest_path(maze)

            path_image_name = None
            path_coords = [tuple(coord) for coord in shortest_path["coordinates"]]
            if len(path_coords) >= 2:
                path_base_filename = os.path.join(maze_dir, f"{file_stem}_path")
                manager.set_filename(path_base_filename)
                manager.show_maze(
                    maze.id,
                    cell_size=cell_size,
                    show_text=False,
                    display=False,
                    path_coords=path_coords,
                    path_color="red",
                    path_linewidth=1.5,
                )
                generated_path_image = f"{path_base_filename}_generation.png"
                path_image_name = f"{file_stem}_path.png"
                os.replace(generated_path_image, os.path.join(maze_dir, path_image_name))

            metadata = {
                "maze_index": maze_index,
                "generated_at": timestamp,
                "unique_id": short_uuid,
                "rows": rows,
                "cols": cols,
                "cell_size": cell_size,
                "maze_id": maze.id,
                "entry_coordinate": list(maze.entry_coor),
                "exit_coordinate": list(maze.exit_coor),
                "generation_algorithm": "depth_first_recursive_backtracker",
                "generation_path_length": len(maze.generation_path),
                "shortest_path_directions": shortest_path["directions"],
                "shortest_path_length": len(shortest_path["coordinates"]),
                "shortest_path_coordinates": shortest_path["coordinates"],
                "shortest_path_directions_numeric": shortest_path["directions_numeric"],
                "output_image": final_png_name,
                "output_image_with_path": path_image_name,
                "generation_path": [list(step) for step in maze.generation_path],
            }

            metadata_path = os.path.join(maze_dir, "metadata.json")
            save_metadata(metadata_path, metadata)

            maze_index += 1

    print("\nAll 3x3 and 4x4 mazes generated with metadata saved.")


if __name__ == "__main__":
    run_generation()
