#!/usr/bin/env python3
"""
Validate reformatted interview transcripts against their raw originals.

Usage:
    python validate_transcripts.py                  # validate all pairs
    python validate_transcripts.py 01               # single participant
    python validate_transcripts.py --csv PATH       # custom CSV path
"""

import sys
import re
import csv
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ─── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
ORIGINAL_DIR = SCRIPT_DIR / "original"
REFORMATTED_DIR = SCRIPT_DIR / "reformatted"
DEFAULT_CSV = SCRIPT_DIR / "participant_metadata.csv"

# ─── Constants ────────────────────────────────────────────────────────────────

VALID_CHANNELS = {"SPOKEN", "WRITTEN", "LLM", "RESEARCHER"}

# Raw file patterns
SPEAKER_RE = re.compile(r'^(Proband \(schriftlich\)|Proband|LLM|Wissenschaftler):$')
TASK_TRANSITION_RE = re.compile(r'^\[Proband wechselt')
STAGE_LINE_RE = re.compile(r'^\[.+\]$')

# Reformatted file patterns
TURN_HEADER_RE = re.compile(r'^\[(\d{3}) (\w+)\]$')
STATEMENT_ID_RE = re.compile(r'^\[(\d{3})\.(\d+)\](.*)')
TASK_HEADER_RE = re.compile(r'^\[TASK ')
INLINE_HEADER_RE = re.compile(r'\[PARTICIPANT:\s*(\S+)\s*\|\s*UUID:\s*([\w-]+)\s*\|\s*GROUP:\s*(\w+)\]')

# Math notation markers (LaTeX / raw escapes / ASCII exponents that get normalized)
MATH_RE = re.compile(r'\^|overline\{|\\text\{|overrightarrow|\\frac\{|\\\[|\\\\')

SPEAKER_MAP = {
    'Proband': 'SPOKEN',
    'Proband (schriftlich)': 'WRITTEN',
    'LLM': 'LLM',
    'Wissenschaftler': 'RESEARCHER',
}

# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class RawTurn:
    channel: str
    lines: list = field(default_factory=list)


@dataclass
class RawFile:
    turns: list = field(default_factory=list)              # list[RawTurn]
    stage_directions: list = field(default_factory=list)   # list[(line_num, text)]
    task_transitions: list = field(default_factory=list)   # list[(line_num, text)]


@dataclass
class ReformattedTurn:
    number: int
    channel: str
    content_lines: list = field(default_factory=list)


@dataclass
class ReformattedFile:
    header: dict = field(default_factory=dict)
    turns: list = field(default_factory=list)              # list[ReformattedTurn]
    stage_directions: list = field(default_factory=list)   # list[(line_num, text)]
    statement_ids: list = field(default_factory=list)      # list[(line_num, turn_num, sub_idx)]


# ─── Parsing ──────────────────────────────────────────────────────────────────

def parse_raw(path: Path) -> RawFile:
    result = RawFile()
    current_turn: Optional[RawTurn] = None

    with open(path, encoding='utf-8') as f:
        for line_num, raw_line in enumerate(f, 1):
            line = raw_line.rstrip()  # strip trailing whitespace incl. \n

            m = SPEAKER_RE.match(line)
            if m:
                current_turn = RawTurn(channel=SPEAKER_MAP[m.group(1)])
                result.turns.append(current_turn)
                continue

            if TASK_TRANSITION_RE.match(line):
                result.task_transitions.append((line_num, line))
                continue

            if STAGE_LINE_RE.match(line):
                result.stage_directions.append((line_num, line))
                continue

            stripped = line.strip()
            if stripped and current_turn is not None:
                current_turn.lines.append((line_num, stripped))

    return result


def parse_reformatted(path: Path) -> Optional[ReformattedFile]:
    result = ReformattedFile()
    current_turn: Optional[ReformattedTurn] = None
    in_header = False
    header_done = False

    try:
        with open(path, encoding='utf-8') as f:
            lines = list(f)
    except OSError:
        return None

    for line_num, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip()
        stripped = line.strip()

        # ── YAML-style header (--- fences)
        if stripped == '---' and not header_done:
            in_header = not in_header
            if not in_header:
                header_done = True
            continue

        if in_header:
            if ':' in stripped:
                key, _, val = stripped.partition(':')
                result.header[key.strip()] = val.strip()
            continue

        # ── Inline header fallback: [PARTICIPANT: X | UUID: Y | GROUP: Z]
        if not header_done and stripped.startswith('[PARTICIPANT:'):
            m = INLINE_HEADER_RE.search(stripped)
            if m:
                result.header = {
                    'PARTICIPANT': m.group(1),
                    'UUID': m.group(2),
                    'GROUP': m.group(3),
                }
                header_done = True
            continue

        # ── Turn header: [NNN CHANNEL]
        m = TURN_HEADER_RE.match(stripped)
        if m:
            current_turn = ReformattedTurn(number=int(m.group(1)), channel=m.group(2))
            result.turns.append(current_turn)
            continue

        # ── Statement ID line: [NNN.n]<content>
        m = STATEMENT_ID_RE.match(stripped)
        if m:
            turn_num, sub_idx = int(m.group(1)), int(m.group(2))
            content = m.group(3).strip()
            result.statement_ids.append((line_num, turn_num, sub_idx))
            if current_turn is not None:
                current_turn.content_lines.append(content)
            continue

        # ── Task header (not a stage direction)
        if TASK_HEADER_RE.match(stripped):
            continue

        # ── Stage direction: any remaining [bracket line]
        if stripped.startswith('[') and stripped.endswith(']') and stripped:
            result.stage_directions.append((line_num, stripped))
            continue

        # ── Content line under current turn
        if stripped and current_turn is not None:
            current_turn.content_lines.append(stripped)

    return result


def load_csv(path: Path) -> dict:
    """Returns dict keyed by zero-padded 2-digit participant_id → row dict."""
    rows = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            pid = row['participant_id'].strip().zfill(2)
            rows[pid] = {k.strip(): v.strip() for k, v in row.items()}
    return rows


def find_reformatted(participant_id: str) -> Optional[Path]:
    for ext in ('.txt', '.formatted.txt', '.reformatted.txt'):
        p = REFORMATTED_DIR / f"{participant_id}{ext}"
        if p.exists():
            return p
    return None


# ─── Normalization helpers ─────────────────────────────────────────────────────

def expand_escapes(text: str) -> list:
    """Replace literal \\n with real newlines, return non-empty stripped segments."""
    expanded = text.replace('\\n', '\n')
    return [seg.strip() for seg in expanded.split('\n') if seg.strip()]


def collect_raw_content(turns: list, channel: str) -> list:
    """Returns list of (line_num, text) from raw turns for the given channel."""
    result = []
    for turn in turns:
        if turn.channel != channel:
            continue
        for line_num, text in turn.lines:
            for seg in expand_escapes(text):
                result.append((line_num, seg))
    return result


def collect_ref_content(turns: list, channel: str) -> list:
    """Returns list of text strings from reformatted turns for the given channel."""
    result = []
    for turn in turns:
        if turn.channel != channel:
            continue
        for text in turn.content_lines:
            result.extend(expand_escapes(text))
    return result


def has_math(text: str) -> bool:
    return bool(MATH_RE.search(text))


_SUPERSCRIPTS = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')

def normalize_math(text: str) -> str:
    """Collapse whitespace and convert ASCII exponents (^N, ^{N}) to Unicode superscripts."""
    text = re.sub(r'\^\{?(\d+)\}?', lambda m: m.group(1).translate(_SUPERSCRIPTS), text)
    return re.sub(r'\s+', '', text)


# ─── Validation checks ────────────────────────────────────────────────────────

def check_header_metadata(ref: ReformattedFile, csv_row: dict) -> list:
    issues = []
    h = ref.header
    pid = h.get('PARTICIPANT', h.get('participant_id', ''))
    uuid = h.get('UUID', '').lower()
    group = h.get('GROUP', '')

    if pid.lstrip('0') != csv_row['participant_id'].lstrip('0'):
        issues.append(f"FAIL participant ID '{pid}' ≠ CSV '{csv_row['participant_id']}'")
    if uuid != csv_row['UUID'].lower():
        issues.append(f"FAIL UUID '{uuid}' ≠ CSV '{csv_row['UUID']}'")
    if group != csv_row['group']:
        issues.append(f"FAIL group '{group}' ≠ CSV '{csv_row['group']}'")
    return issues


def check_channel_tags(ref: ReformattedFile) -> list:
    return [
        f"FAIL turn {t.number:03d}: invalid channel '{t.channel}'"
        for t in ref.turns
        if t.channel not in VALID_CHANNELS
    ]


def check_turn_sequence(ref: ReformattedFile) -> list:
    issues = []
    nums = [t.number for t in ref.turns]
    if not nums:
        return ["FAIL no turns found"]
    if nums[0] != 1:
        issues.append(f"FAIL first turn is {nums[0]:03d}, expected 001")
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1] + 1:
            issues.append(f"FAIL sequence gap: {nums[i-1]:03d} → {nums[i]:03d}")
    return issues


def check_statement_nesting(ref: ReformattedFile) -> list:
    issues = []
    turn_map = {t.number: t.channel for t in ref.turns}
    seen: set = set()
    for line_num, turn_num, sub_idx in ref.statement_ids:
        if turn_num not in turn_map:
            issues.append(
                f"FAIL [{turn_num:03d}.{sub_idx}] line {line_num}: "
                f"references non-existent turn {turn_num:03d}"
            )
        elif turn_map[turn_num] not in ('SPOKEN', 'WRITTEN'):
            issues.append(
                f"FAIL [{turn_num:03d}.{sub_idx}] line {line_num}: "
                f"under {turn_map[turn_num]} turn (only SPOKEN/WRITTEN allowed)"
            )
        key = (turn_num, sub_idx)
        if key in seen:
            issues.append(f"FAIL [{turn_num:03d}.{sub_idx}]: duplicate statement ID")
        seen.add(key)
    return issues


def check_stage_directions(raw: RawFile, ref: ReformattedFile) -> list:
    ref_stages = {text for _, text in ref.stage_directions}
    return [
        f"WARN stage direction missing/changed (raw line {ln}): {text!r}"
        for ln, text in raw.stage_directions
        if text not in ref_stages
    ]


def check_content_completeness(raw: RawFile, ref: ReformattedFile) -> list:
    issues = []

    # ── SPOKEN, WRITTEN, RESEARCHER: exact match, then math-normalized fallback
    for channel in ('SPOKEN', 'WRITTEN', 'RESEARCHER'):
        raw_items = collect_raw_content(raw.turns, channel)   # [(line_num, text)]
        ref_set = set(collect_ref_content(ref.turns, channel))
        norm_ref_set: set = set()  # built lazily on first mismatch
        for line_num, line in raw_items:
            if line in ref_set:
                continue
            if not norm_ref_set:
                norm_ref_set = {normalize_math(r) for r in ref_set}
            if normalize_math(line) in norm_ref_set:
                continue  # matches after math normalization — OK
            preview = (line[:80] + '…') if len(line) > 80 else line
            level = "WARN" if has_math(line) else "FAIL"
            issues.append(f"{level} [{channel}] raw line {line_num}: {preview!r}")

    # ── LLM: paragraph-level word-overlap check (tolerates math normalization)
    raw_llm_paras: list = []  # [(line_num, para_text)]
    for turn in raw.turns:
        if turn.channel != 'LLM':
            continue
        for line_num, text in turn.lines:
            expanded = text.replace('\\n', '\n')
            for para in re.split(r'\n{2,}', expanded):
                para = para.strip()
                if para:
                    raw_llm_paras.append((line_num, para))

    ref_llm_blob = ' '.join(collect_ref_content(ref.turns, 'LLM'))
    ref_words_cache: set = set()  # computed once

    for line_num, para in raw_llm_paras:
        if len(para) < 30:
            continue
        raw_words = set(re.findall(r'[a-zA-ZÄÖÜäöüß]{4,}', para))
        if not raw_words:
            continue
        if not ref_words_cache:
            ref_words_cache = set(re.findall(r'[a-zA-ZÄÖÜäöüß]{4,}', ref_llm_blob))
        overlap = len(raw_words & ref_words_cache) / len(raw_words)
        if overlap < 0.70:
            level = "WARN" if has_math(para) else "FAIL"
            preview = (para[:80] + '…') if len(para) > 80 else para
            issues.append(f"{level} LLM raw line {line_num}: paragraph low word overlap ({overlap:.0%}): {preview!r}")

    math_count = sum(
        1 for t in raw.turns
        if t.channel == 'LLM' and any(has_math(text) for _, text in t.lines)
    )
    if math_count:
        issues.append(
            f"WARN {math_count} LLM turn(s) contain math notation — "
            f"spot-check reformatted math rendering manually"
        )

    return issues


# ─── Per-file validation runner ───────────────────────────────────────────────

def validate_participant(pid: str, csv_rows: dict) -> tuple:
    """Returns (passed: bool|None, output_lines: list[str]). None = skipped."""
    raw_path = ORIGINAL_DIR / f"{pid}.raw.txt"
    ref_path = find_reformatted(pid)

    if not raw_path.exists():
        return None, [f"  SKIP  raw file not found: {raw_path.name}"]
    if ref_path is None:
        return None, [f"  SKIP  no reformatted file found in {REFORMATTED_DIR.name}/"]

    raw = parse_raw(raw_path)
    ref = parse_reformatted(ref_path)
    if ref is None:
        return False, [f"  FAIL  could not parse: {ref_path.name}"]

    csv_row = csv_rows.get(pid)
    out: list = []
    passed = True

    def emit(label: str, issues: list) -> None:
        nonlocal passed
        fails = [i for i in issues if i.startswith('FAIL')]
        warns = [i for i in issues if i.startswith('WARN')]
        if fails:
            passed = False
            out.append(f"  [FAIL] {label}")
            for msg in fails:
                out.append(f"         {msg}")
        elif warns:
            out.append(f"  [WARN] {label}")
            for msg in warns:
                out.append(f"         {msg}")
        else:
            out.append(f"  [OK  ] {label}")

    if csv_row:
        emit("Header metadata", check_header_metadata(ref, csv_row))
    else:
        out.append(f"  [SKIP] Header metadata — participant {pid} not in CSV")

    emit("Channel tags", check_channel_tags(ref))
    emit("Turn sequence", check_turn_sequence(ref))
    emit("Statement ID nesting", check_statement_nesting(ref))
    emit("Stage directions", check_stage_directions(raw, ref))
    emit("Content completeness", check_content_completeness(raw, ref))

    return passed, out


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate reformatted interview transcripts against raw originals."
    )
    parser.add_argument(
        'participant', nargs='?',
        help="Participant ID, e.g. 01. Omit to validate all."
    )
    parser.add_argument(
        '--csv', default=str(DEFAULT_CSV),
        help="Path to participant_metadata.csv"
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(2)

    csv_rows = load_csv(csv_path)

    if args.participant:
        pids = [args.participant.zfill(2)]
    else:
        pids = sorted(
            p.stem.replace('.raw', '')
            for p in ORIGINAL_DIR.glob('*.raw.txt')
        )

    total = skipped = 0
    failed_pids: list = []

    for pid in pids:
        print(f"\n=== Participant {pid} ===")
        result, lines = validate_participant(pid, csv_rows)
        for line in lines:
            print(line)
        if result is None:
            skipped += 1
        elif result:
            total += 1
        else:
            total += 1
            failed_pids.append(pid)

    passed = total - len(failed_pids)
    print(f"\n{'─' * 40}")
    print(f"Summary: {passed}/{total} files passed", end="")
    if skipped:
        print(f"  ({skipped} skipped — no reformatted file)", end="")
    print()
    if failed_pids:
        print(f"Files with errors: {', '.join(failed_pids)}")

    sys.exit(1 if failed_pids else 0)


if __name__ == '__main__':
    main()
