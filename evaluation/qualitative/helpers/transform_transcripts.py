#!/usr/bin/env python3
"""
reformat_transcript.py

Applies three mechanical transformations to a raw participant transcript
(the "NN_raw.txt" format used in this thesis project):

  1. Insertion of turn IDs  ([NNN CHANNEL])  and statement/clause IDs
     ([NNN.n]) for SPOKEN and WRITTEN turns.
  2. Insertion of a YAML-style metadata header ("---\\nPARTICIPANT: ...").
     Fields are left blank unless supplied via CLI flags.
  3. Math notation normalization (LaTeX escapes and/or Unicode math
     symbols -> a single consistent style). Defaults to ASCII
     (e.g. "x^2", "sqrt(9)", "pi"), with an optional Unicode mode
     (e.g. "x²", "√9", "π") for parity with earlier manual work.

WHAT THIS SCRIPT DOES *NOT* DO (by design, out of scope for this pass):
  - It does not insert [TASK <task-id> | DIFFICULTY <medium/hard>]
    placeholders at task-transition stage directions.
  - It does not wrap LLM <think>...</think> segments -- LLM/RESEARCHER
    turns are emitted as a single uncoded block, exactly as the raw
    file's line order gives them.
  - It does not attempt to resolve ambiguous turn boundaries, e.g. a
    line of clearly-spoken content that follows a stage direction with
    no new speaker header (this occurred a handful of times across the
    12 transcripts we did by hand, and needed human judgment). The
    script will silently continue the previous turn in that case, so
    spot-check the output around stage directions.

INPUT FORMAT ASSUMPTIONS (matches every NN_raw.txt seen so far):
  - Turn headers ("Wissenschaftler:", "Proband:", "Proband (schriftlich):",
    "LLM:") start at column 0, optionally without the trailing colon,
    and are tolerated with a few observed typos (Wissernschaftler,
    Wissendschaftler, ...).
  - Content lines belonging to a turn are indented with exactly four
    leading spaces.
  - Stage directions are bracket-wrapped lines ("[Proband liest ...]")
    that also start at column 0. They receive no ID, do not advance the
    turn counter, and are passed through unchanged (no math/text
    normalization applied to them).
  - LLM output may contain literal "\\n" / "\\n\\n" escape sequences and
    literal `\"` escaped quotes; these are unescaped for readability.

USAGE
  python reformat_transcript.py 12_raw.txt
  python reformat_transcript.py 12_raw.txt -o 12_reformatted.txt \\
      --participant 12 --uuid 473ee59a-2809-485a-a7ca-5d2f8f776bca --group B
  python reformat_transcript.py 12_raw.txt --math unicode
  python reformat_transcript.py 12_raw.txt --math none -o 12_ids_only.txt
"""

import argparse
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Turn-header detection
# --------------------------------------------------------------------------

# Tolerant of the typos observed across transcripts (Wissernschaftler,
# Wissendschaftler, ...) and of an omitted trailing colon.
RESEARCHER_RE = re.compile(r"^Wiss.*chaftler\s*:?\s*$", re.IGNORECASE)
WRITTEN_RE = re.compile(r"^Proband\s*\(schriftlich\)\s*:?\s*$", re.IGNORECASE)
SPOKEN_RE = re.compile(r"^Proband\s*:?\s*$", re.IGNORECASE)
LLM_RE = re.compile(r"^LLM\s*:?\s*$", re.IGNORECASE)

HEADER_PATTERNS = [
    (WRITTEN_RE, "WRITTEN"),
    (SPOKEN_RE, "SPOKEN"),
    (RESEARCHER_RE, "RESEARCHER"),
    (LLM_RE, "LLM"),
]

CLAUSE_CHANNELS = {"SPOKEN", "WRITTEN"}  # get [NNN.n] sub-IDs
BLOCK_CHANNELS = {"RESEARCHER", "LLM"}  # single uncoded block


def detect_channel(line: str):
    """Return the canonical channel name if `line` is a turn header, else None."""
    stripped = line.strip()
    for pattern, channel in HEADER_PATTERNS:
        if pattern.match(stripped):
            return channel
    return None


def is_stage_direction(line: str) -> bool:
    """A stage direction is an unindented, bracket-wrapped line."""
    stripped = line.strip()
    return stripped.startswith("[") and stripped.endswith("]")


# --------------------------------------------------------------------------
# Generic text cleanup (independent of math mode)
# --------------------------------------------------------------------------

def unescape_common(text: str) -> str:
    """Turn literal escape sequences from the raw export into real characters.

    Newlines are consistently stored as the two-character sequence "\\n"
    (one real backslash + n) across every raw file checked. Quotes are
    inconsistent: some files escape them as \\" and some don't escape
    them at all (a bare " appears in running text). A strict JSON-string
    decode breaks on the latter, so we handle each escape independently
    with plain substitution instead -- a bare " is simply left alone,
    which is a no-op rather than a parse error.

    LaTeX backslashes are NOT touched here: some files store LaTeX
    commands with a doubled backslash ("\\\\frac") and some with a
    single one ("\\frac"). That inconsistency is handled downstream in
    the math-normalization regexes, which tolerate either count, rather
    than here.
    """
    text = text.replace(r"\n", "\n")
    text = text.replace(r"\"", '"')
    return text


# --------------------------------------------------------------------------
# Math normalization
# --------------------------------------------------------------------------

# Unicode superscript/subscript digit tables, used in both directions.
_SUPERSCRIPT = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUBSCRIPT = "₀₁₂₃₄₅₆₇₈₉"
_SUP_TO_ASCII = {ch: f"^{i}" for i, ch in enumerate(_SUPERSCRIPT)}
_SUB_TO_ASCII = {ch: f"_{i}" for i, ch in enumerate(_SUBSCRIPT)}


def _strip_latex_delimiters(text: str) -> str:
    """Remove \\( \\) and \\[ \\] inline/display math delimiters, keep contents.

    Also strips \\left / \\right (LaTeX auto-sizing markers, e.g.
    "\\left(\\frac{AB}{2}\\right)^2"), keeping the bracket character
    that follows them.

    Tolerant of both a single and a doubled backslash before each
    delimiter, since raw files are inconsistent about this (see
    unescape_common's docstring).
    """
    text = re.sub(r"\\{1,2}left", "", text)
    text = re.sub(r"\\{1,2}right", "", text)
    text = re.sub(r"\\{1,2}\(", "", text)
    text = re.sub(r"\\{1,2}\)", "", text)
    text = re.sub(r"\\{1,2}\[", "", text)
    text = re.sub(r"\\{1,2}\]", "", text)
    return text


def _convert_latex_commands(text: str, target: str) -> str:
    """Convert the handful of LaTeX math commands seen in these transcripts.

    target is "ascii" or "unicode".

    Every command pattern below tolerates 1 or 2 leading backslashes
    ("\\{1,2}"), since raw files are inconsistent about doubling them
    (see unescape_common's docstring).

    Order matters here too: \\frac{a}{b} arguments can themselves
    contain a nested \\sqrt{...} (e.g. \\frac{x}{\\sqrt{A^2+B^2}}),
    which breaks a naive non-nesting-brace regex for \\frac. So \\text
    and \\sqrt are resolved first (removing their inner braces), and
    \\frac is then applied repeatedly until stable so multiple/nested
    fracs all clear.
    """
    # \text{word} -> word (no nesting expected)
    text = re.sub(r"\\{1,2}text\{([^{}]*)\}", r"\1", text)

    # \sqrt{...} and \frac{a}{b} can nest inside each other in either
    # direction (sqrt-in-frac, frac-in-sqrt, frac-in-frac, ...), and a
    # single non-nesting-brace regex only ever resolves the innermost
    # level in one pass. So resolve both together, repeatedly, until
    # nothing changes -- each pass peels off whatever is currently
    # brace-balanced (i.e. has no further nested command inside it),
    # and outer layers become resolvable on the next pass.
    sqrt_repl = r"sqrt(\1)" if target == "ascii" else r"√(\1)"
    sqrt_re = re.compile(r"\\{1,2}sqrt\{([^{}]*)\}")
    frac_re = re.compile(r"\\{1,2}frac\{([^{}]*)\}\{([^{}]*)\}")
    prev = None
    while prev != text:
        prev = text
        text = sqrt_re.sub(sqrt_repl, text)
        text = frac_re.sub(r"(\1)/(\2)", text)

    if target == "ascii":
        text = re.sub(r"\\{1,2}times", "*", text)
        text = re.sub(r"\\{1,2}cdot", "*", text)
        text = re.sub(r"\\{1,2}pi\b", "pi", text)
        text = re.sub(r"\\{1,2}theta\b", "theta", text)
        # 32^\circ -> 32 deg ; standalone \circ -> deg
        text = re.sub(r"\^\\{1,2}circ", " deg", text)
        text = re.sub(r"\\{1,2}circ", "deg", text)
        # LaTeX writes "3\sqrt{5}" for 3*sqrt(5) (implicit multiplication);
        # make the operator explicit once it's plain ASCII "3sqrt(5)".
        text = re.sub(r"(\d)sqrt\(", r"\1*sqrt(", text)
    else:  # unicode
        text = re.sub(r"\\{1,2}times", "·", text)
        text = re.sub(r"\\{1,2}cdot", "·", text)
        text = re.sub(r"\\{1,2}pi\b", "π", text)
        text = re.sub(r"\\{1,2}theta\b", "θ", text)
        text = re.sub(r"\^\\{1,2}circ", "°", text)
        text = re.sub(r"\\{1,2}circ", "°", text)

    return text


_KNOWN_LATEX_COMMANDS = (
    "frac", "sqrt", "pi", "theta", "times", "cdot", "text", "circ",
)


def _check_residual_latex(text: str) -> str:
    """Return a short description if a backslash command wasn't recognized
    and converted (so it can be flagged for manual review), else None.
    """
    for m in re.finditer(r"\\{1,2}([A-Za-z]+)", text):
        if m.group(1) not in _KNOWN_LATEX_COMMANDS:
            return m.group(0)
    return None


def _convert_existing_unicode_to_ascii(text: str) -> str:
    """Convert math symbols that were already typed as literal Unicode
    (not LaTeX escapes) into ASCII equivalents."""
    for ch, repl in _SUP_TO_ASCII.items():
        text = text.replace(ch, repl)
    for ch, repl in _SUB_TO_ASCII.items():
        text = text.replace(ch, repl)

    # √(...) and √token -> sqrt(...) / sqrt(token)
    text = text.replace("√(", "sqrt(")
    text = re.sub(r"√\s*([A-Za-z0-9]+)", r"sqrt(\1)", text)

    text = text.replace("π", "pi")
    text = text.replace("θ", "theta")
    text = text.replace("·", "*")
    text = text.replace("×", "*")
    text = text.replace("°", " deg")
    return text


def _convert_existing_ascii_to_unicode(text: str) -> str:
    """Convert ASCII-style math (a^2, sqrt(9), pi, ...) into Unicode symbols.

    Only handles the simple, single-digit exponent case reliably
    (a^2 -> a²); anything more complex (a^(n+1)) is left as-is since a
    faithful Unicode rendering isn't always possible.
    """
    digit_to_sup = {str(i): ch for i, ch in enumerate(_SUPERSCRIPT)}
    text = re.sub(
        r"\^([0-9])",
        lambda m: digit_to_sup[m.group(1)],
        text,
    )
    text = re.sub(r"\bsqrt\(([^()]*)\)", r"√(\1)", text)
    text = re.sub(r"\bpi\b", "π", text, flags=re.IGNORECASE)
    text = re.sub(r"\btheta\b", "θ", text, flags=re.IGNORECASE)
    return text


def normalize_math(text: str, mode: str, warnings: list = None, lineno: int = None) -> str:
    """Normalize math notation in `text` to the requested style.

    mode: "ascii" | "unicode" | "none"
    """
    if mode == "none":
        return text

    text = _strip_latex_delimiters(text)
    text = _convert_latex_commands(text, target=mode)

    if mode == "ascii":
        text = _convert_existing_unicode_to_ascii(text)
    else:
        text = _convert_existing_ascii_to_unicode(text)

    if warnings is not None:
        residual = _check_residual_latex(text)
        if residual:
            warnings.append(
                f"line {lineno}: unrecognized LaTeX command {residual!r} "
                f"left as-is -- check this line's math by hand"
            )

    return text


# --------------------------------------------------------------------------
# Core transformation
# --------------------------------------------------------------------------

def reformat(
    raw_lines,
    math_mode: str = "ascii",
    participant: str = "",
    uuid: str = "",
    group: str = "",
):
    """Return (output_lines, warnings)."""
    output = [
        "---",
        f"PARTICIPANT: {participant}",
        f"UUID: {uuid}",
        f"GROUP: {group}",
        "---",
    ]
    warnings = []

    turn_counter = 0
    clause_counter = 0
    current_channel = None

    for lineno, raw_line in enumerate(raw_lines, start=1):
        line = raw_line.rstrip("\n")
        if line.strip() == "":
            continue  # skip genuinely blank lines

        is_indented = line.startswith("    ") or line.startswith("\t")

        if not is_indented:
            channel = detect_channel(line)
            if channel is not None:
                turn_counter += 1
                clause_counter = 0
                current_channel = channel
                output.append(f"[{turn_counter:03d} {channel}]")
                continue

            if is_stage_direction(line):
                # Pass through unchanged; no ID, no counter movement,
                # no text normalization.
                output.append(line.strip())
                continue

            # Unrecognized unindented line: don't guess, flag it and
            # pass it through so nothing is silently dropped.
            warnings.append(
                f"line {lineno}: unrecognized header/stage-direction "
                f"format, passed through unchanged: {line!r}"
            )
            output.append(line.strip())
            continue

        # --- indented content line ---
        content = line.strip()
        content = unescape_common(content)

        if current_channel is None:
            warnings.append(
                f"line {lineno}: content line found before any turn header; "
                f"skipped: {line!r}"
            )
            continue

        if current_channel in CLAUSE_CHANNELS:
            # Collapse any embedded newlines (e.g. from \n unescaping in a
            # written message) so the 1 raw-line = 1 clause invariant holds.
            content = normalize_math(content, math_mode, warnings, lineno)
            content = " ".join(content.splitlines())
            clause_counter += 1
            output.append(f"[{turn_counter:03d}.{clause_counter}]    {content}")
        else:  # BLOCK_CHANNELS
            content = normalize_math(content, math_mode, warnings, lineno)
            for subline in content.split("\n"):
                subline = subline.rstrip()
                # Preserve relative indentation (e.g. nested "   - " bullets
                # under a numbered step) rather than flattening it away;
                # only fully-blank lines collapse to a true blank line.
                output.append(f"    {subline}" if subline.strip() else "")

    return output, warnings


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Insert turn/statement IDs, a metadata header, and "
        "normalize math notation in a raw participant transcript.",
    )
    parser.add_argument("input", type=Path, help="Path to NN_raw.txt")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output path (default: print to stdout)",
    )
    parser.add_argument("--participant", default="", help="PARTICIPANT header field")
    parser.add_argument("--uuid", default="", help="UUID header field")
    parser.add_argument("--group", default="", help="GROUP header field")
    parser.add_argument(
        "--math", choices=["ascii", "unicode", "none"], default="ascii",
        help="Math normalization style (default: ascii)",
    )
    args = parser.parse_args()

    raw_lines = args.input.read_text(encoding="utf-8").splitlines(keepends=True)

    output_lines, warnings = reformat(
        raw_lines,
        math_mode=args.math,
        participant=args.participant,
        uuid=args.uuid,
        group=args.group,
    )

    result = "\n".join(output_lines) + "\n"

    if args.output:
        args.output.write_text(result, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(result)

    if warnings:
        print("\n--- WARNINGS (review these manually) ---", file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)


if __name__ == "__main__":
    main()
