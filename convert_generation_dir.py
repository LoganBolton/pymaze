from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


GENERAL_PROMPT = (
    "You are given an image of a maze where the green square marks the START cell and the red square marks the END cell of the maze. "
    "The walls of the maze are solid black lines. Dashed gray lines mark cell boundaries that can be crossed. "
    "You are given a proposed sequence of moves to reach the end of the maze starting from the green square and ending at the red square. "
    "A valid path must NOT cross any solid black walls and must end up in the red square cell. A valid path can also move through any of the dashed gray cell lines. "
    "Respond with $\\boxed{valid}$ if the path is valid or respond with $\\boxed{invalid}$ if the path is invalid. Determine if the following proposed path is valid."
)

SKETCH_PROMPT = "Please sketch out the proposed path before responding with your final answer."


def write_prompt_file(destination: Path, proposed_path: str, *, sketch: bool = False) -> None:
    lines: list[str] = [GENERAL_PROMPT]
    if sketch:
        lines.append(SKETCH_PROMPT)
    lines.extend(["", f"Proposed path: {proposed_path}"])
    destination.write_text("\n".join(lines), encoding="utf-8")


def convert_generation_dir(generation_dir: Path, output_base: Path | None) -> None:
    if not generation_dir.exists() or not generation_dir.is_dir():
        raise FileNotFoundError(f"Generation directory not found: {generation_dir}")

    if output_base is None:
        output_base = generation_dir

    valid_dir = output_base / "valid_flattened"
    sketch_valid_dir = output_base / "sketch_valid_flattened"
    invalid_dir = output_base / "substitution_invalid_flattened"
    sketch_invalid_dir = output_base / "substitution_sketch_invalid_flattened"
    for directory in (valid_dir, sketch_valid_dir, invalid_dir, sketch_invalid_dir):
        directory.mkdir(parents=True, exist_ok=True)

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

        dest_valid = valid_dir / source_image.name
        shutil.copy2(source_image, dest_valid)
        write_prompt_file(dest_valid.with_suffix(".txt"), path_str)

        dest_sketch_valid = sketch_valid_dir / source_image.name
        shutil.copy2(source_image, dest_sketch_valid)
        write_prompt_file(dest_sketch_valid.with_suffix(".txt"), path_str, sketch=True)

        substitution = metadata.get("incorrect_paths", {}).get("substitution")
        if substitution:
            sub_dirs = substitution.get("directions", [])
            sub_path_str = ", ".join(sub_dirs) if sub_dirs else "(no path available)"

            dest_invalid = invalid_dir / source_image.name
            shutil.copy2(source_image, dest_invalid)
            write_prompt_file(dest_invalid.with_suffix(".txt"), sub_path_str)

            dest_sketch_invalid = sketch_invalid_dir / source_image.name
            shutil.copy2(source_image, dest_sketch_invalid)
            write_prompt_file(dest_sketch_invalid.with_suffix(".txt"), sub_path_str, sketch=True)


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
