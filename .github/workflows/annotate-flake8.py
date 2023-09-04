import re
import sys
from typing import TextIO


def annotate_flake8_output(file_path: str) -> None:
    with open(file_path, "r") as f:
        process_output(f)


def process_output(f: TextIO) -> None:
    flake8_regex = re.compile(r"^(.+):(\d+):(\d+): (\w+) (.+)$")
    exit_code = 0

    for line in f.readlines():
        match = flake8_regex.match(line.strip())
        if match:
            file_path, line_num, _, issue_type, description = match.groups()
            annotation_level = (
                "warning" if issue_type.startswith("W") else "error"
            )

            # GitHub Annotation Format
            print(
                f"::{annotation_level} file={file_path},line={line_num}"
                f"::[{issue_type}] {description}"
            )

            if annotation_level == "error":
                exit_code = 1

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: annotate_flake8.py <flake8_output_file>")
        sys.exit(1)

    annotate_flake8_output(sys.argv[1])
