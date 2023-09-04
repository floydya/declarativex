import re
import sys
from typing import TextIO


def annotate_pylint_output(file_path: str) -> None:
    with open(file_path, "r") as f:
        process_output(f)


def process_output(f: TextIO) -> None:
    pylint_regex = re.compile(r"^(.+):(\d+):(\d+): (\w+): (.+)$")
    exit_code = 0

    for line in f.readlines():
        match = pylint_regex.match(line)
        if match:
            file_path, line_num, _, issue_type, description = match.groups()
            issue_type = issue_type.lower()
            annotation_level = (
                "warning" if issue_type == "warning" else "error"
            )

            print(
                f"::{annotation_level} file={file_path},"
                f"line={line_num}::{description}"
            )

            if annotation_level == "error":
                exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: annotate_pylint.py <pylint_output_file>")
        sys.exit(1)

    annotate_pylint_output(sys.argv[1])
