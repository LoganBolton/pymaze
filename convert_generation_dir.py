from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


GENERAL_PROMPT = (
    "You are given an image of a maze where the green square marks the START cell and the red square marks the END cell of the maze. The walls of the maze are solid black lines. Dashed gray lines mark cell boundaries that can be crossed. You are given a proposed sequence of moves to reach the end of the maze starting from the green square and ending at the red square. A vaild path must NOT cross any solid black walls and must end up in the red square cell. A valid path can also move through any of the dashed gray cell lines. Respond with $\boxed{valid}$ if the path is valid or respond with $\boxed{invalid}$ if the path is invalid. Determine if the following proposed path is valid."
)

def convert_generation_dir(generation_dir: Path, output_base: Path | None) -> None:
    if not generation_dir.exists() or not generation_dir.is_dir():
        raise FileNotFoundError(f"Generation directory not found: {generation_dir}")

    if output_base is None:
        output_base = generation_dir

    valid_dir = output_base / "valid_flattened"
    invalid_dir = output_base / "substitution_invalid_flattened"
    valid_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir.mkdir(parents=True, exist_ok=True)

    metadata_files = sorted(generation_dir.glob("path_length_*/maze_*_*/metadata.json"))
    if not metadata_files:
        raise FileNotFoundError("No metadata files found under the provided generation directory.")

    for metadata_path in metadata_files:
        with metadata_path.open("r", encoding="utf-8") as fh:
            metadata = json.load(fh)

        image_name = metadata.get("output_image")
        if not image_name:
            continue

        source_image = metadata_path.parent / image_name
        if not source_image.exists():
            continue

        directions = metadata.get("shortest_path_directions", [])
        path_str = ", ".join(directions) if directions else "(no path available)"

        destination_image_valid = valid_dir / source_image.name
        shutil.copy2(source_image, destination_image_valid)

        text_path_valid = destination_image_valid.with_suffix(".txt")
        lines_valid = [GENERAL_PROMPT, "", f"Proposed path: {path_str}", "", QUESTION]
        text_path_valid.write_text("\n".join(lines_valid), encoding="utf-8")

        substitution = metadata.get("incorrect_paths", {}).get("substitution")
        if substitution:
            destination_image_invalid = invalid_dir / source_image.name
            shutil.copy2(source_image, destination_image_invalid)

            sub_dirs = substitution.get("directions", [])
            sub_path_str = ", ".join(sub_dirs) if sub_dirs else "(no path available)"
            changed_index = substitution.get("modified_index")
            original_dir = substitution.get("original_direction")
            new_dir = substitution.get("new_direction")

            text_path_invalid = destination_image_invalid.with_suffix(".txt")
            if changed_index is not None:
                detail_line = f"Substitution detail: index {changed_index}, {original_dir} -> {new_dir}"
            else:
                detail_line = "Substitution detail: not available"

            lines_invalid = [GENERAL_PROMPT, "", f"Proposed path: {sub_path_str}", detail_line, "", QUESTION]
            text_path_invalid.write_text("\n".join(lines_invalid), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flatten a generation directory into valid and substitution-invalid prompt datasets."
    )
    parser.add_argument(
        "generation_dir",
        type=Path,
        help="Path to the generation directory (e.g. output/generation_YYYYMMDD_HHMMSS)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Base directory for flattened outputs. Defaults to the generation directory itself.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert_generation_dir(args.generation_dir, args.output)


if __name__ == "__main__":
    main()
