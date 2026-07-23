#!/usr/bin/env python3
"""Convert working-patterns.txt into pastable codebook relabel commands.

The input format is expected to be a simple outline:

  "target pattern label"

      "source canonical label"

Each quoted item under a heading becomes part of one command that relabels
all exact source labels to the current heading using the codebook relabel
helper.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import sys


def unquote(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]
    return text


def parse_outline(path: Path):
    heading = None
    sections = []
    errors = []

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue

        indent = len(raw) - len(raw.lstrip(" \t"))
        stripped = raw.strip()

        if indent == 0 and stripped.startswith('"') and stripped.endswith('"'):
            # heading = unquote(stripped)
            heading = stripped
            sections.append([heading, []])
            continue

        if indent > 0 and stripped.startswith('"') and stripped.endswith('"'):
            if heading is None or not sections:
                errors.append(f"{path}:{lineno}: item found before any heading")
                continue
            # source_label = unquote(stripped)
            source_label = stripped
            sections[-1][1].append(source_label)
            continue

        errors.append(f"{path}:{lineno}: unrecognized line shape: {raw.rstrip()!r}")

    return sections, errors


def format_command(
    codebook: str, source_labels: list[str], target_label: str, apply: bool
) -> str:
    parts = [
        "python",
        "./codebook.py",
        "relabel",
        codebook,
        "--select-labels",
    ]
    parts.extend(source_labels)
    parts.extend(["--to", target_label])
    if apply:
        parts.append("--apply")
    return " ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Turn a working-patterns outline into pastable relabel commands."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="working-patterns.txt",
        help="outline file to read (default: working-patterns.txt)",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="-",
        help="output txt file or '-' for stdout (default: stdout)",
    )
    parser.add_argument(
        "--codebook",
        default="./codebooks/codebook_v2.csv",
        help="codebook CSV path used in emitted commands",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="include --apply in emitted commands",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    sections, errors = parse_outline(input_path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise SystemExit(1)

    lines = []
    for heading, source_labels in sections:
        if not source_labels:
            continue
        if lines:
            lines.append("")
        lines.append(f"# {heading}")
        lines.append(format_command(args.codebook, source_labels, heading, args.apply))

    output = "\n".join(lines) + ("\n" if lines else "")
    if args.out == "-":
        sys.stdout.write(output)
    else:
        Path(args.out).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
