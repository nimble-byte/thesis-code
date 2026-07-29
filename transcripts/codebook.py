#!/usr/bin/env python3
"""
codebook.py — code mapping + pattern coding tooling.

Four commands:
  build   : parse *_codes.txt first-cycle files -> long-format codebook CSV (v0).
  view    : regenerate the aggregated codebook view from a long-format CSV.
  relabel : bulk-set a column for a selected group of rows (code mapping
            merges, or pattern-coding pattern_code/cluster_code assignment).
  check   : read-only structural/quality checks on a long-format CSV.

Long-format schema (one row per code application, the source of truth):
  id, group, raw_label, in_vivo, canonical_label, [pattern_code, [cluster_code]]
    id : NN.NNN.n  (participant . turn . subline)  -- unique application key
    canonical_label : seeded == raw_label in v0; code mapping overwrites in place.
    pattern_code, cluster_code (or any --column you choose): created on first
      relabel call targeting it, seeded from --seed-from (default
      canonical_label), then overwritten per selection. Keeping each as its
      own column (not overwriting the previous one in place) preserves the
      1st-order/2nd-order/3rd-order mapping a Gioia data structure needs.
    Columns are only ever emitted in the order above, and only if present.

Versioning is `cp codebook_v1.csv codebook_v2.csv` before a NEW coding
iteration (e.g. code mapping -> pattern coding -> cluster coding); within one
iteration, edit the file in place. Frequency / spread / group coverage are
NEVER stored; `view` derives them so they cannot drift from the rows.

pandas is assumed available.
"""

import argparse
import glob
import os
import re
import sys
import termios
import pandas as pd
import tty

# [NNN.n] PROCESS: <label> | IV: <verbatim...>
CODE_RE = re.compile(
    r"^\[(?P<turn>\d{3})\.(?P<sub>[0-9a-z]+)\]\s+"
    r"PROCESS:\s+(?P<label>.+?)\s+\|\s+IV:\s+(?P<iv>.+)$"
)
# IV field is quote-wrapped: IV: "verbatim text"
IV_RE = re.compile(r'^"(?P<quote>.*)"\s*$')
# A line that opens like a coded statement but isn't a PROCESS line
# (e.g. filler "[011.15] — (no code: ...)"). Used only to classify skips.
STMT_LIKE_RE = re.compile(r"^\[\d{3}\.[0-9a-z]+\]")
HEADER_KEY_RE = re.compile(r"^(?P<key>[A-Z]+):\s*(?P<val>.+?)\s*$")

# id column: NN.NNN.n with an optional single trailing letter (e.g. 13.023.1b)
ID_RE = re.compile(r"^\d{2}\.\d{3}\.\d+[a-z]?$")

# Canonical long-format column order. Emitted subset-and-in-order on every
# write, so a partially-coded file (no pattern_code/cluster_code yet) doesn't
# get empty columns invented, and a future rebuild can't silently revert it.
COLUMN_ORDER = [
    "id",
    "group",
    "raw_label",
    "in_vivo",
    "canonical_label",
    "pattern_code",
    "cluster_code",
]

REQUIRED_LONG_FORMAT_COLS = {"id", "group", "raw_label", "canonical_label", "in_vivo"}

# Lead-verb extraction for `view --group-by-verb`: strip grammatical
# modifiers only (re-/self- prefix, a leading manner adverb), never verb
# synonyms -- synonym-level grouping is a meaning judgment (pattern coding),
# out of scope for this purely orthographic organizing aid. Validated at
# 100% gerund coverage (0 exceptions) against the full v1 codebook.
_VERB_PREFIX_RE = re.compile(r"^(re|self)-", re.I)
# NB: strips ANY leading "...ly " token, not just adverbs -- would misfire on
# a verb that happened to end in "ly" (e.g. a hypothetical "Bullying ..."
# label). No current label triggers this; flagged here rather than tightened
# because a stricter adverb allowlist is more maintenance than it's worth.
_VERB_ADVERB_RE = re.compile(r"^\w+ly\s+", re.I)
_VERB_LEAD_RE = re.compile(r"^([A-Za-z]+)")


def lead_verb(label):
    """Extract the base process verb from a canonical_label, stripping
    grammatical (not semantic) modifiers. Returns None if no leading
    alphabetic token is found."""
    s = _VERB_PREFIX_RE.sub("", label)
    s = _VERB_ADVERB_RE.sub("", s)
    m = _VERB_LEAD_RE.match(s)
    return m.group(1).lower() if m else None


def order_columns(df):
    """Reindex df to COLUMN_ORDER, dropping absent columns and appending any
    unrecognized ones (defensive) at the end."""
    ordered = [c for c in COLUMN_ORDER if c in df.columns]
    extra = [c for c in df.columns if c not in COLUMN_ORDER]
    return df[ordered + extra]


def read_codebook(path):
    return pd.read_csv(path, dtype=str).fillna("")


def validate_long_format(df, path, context):
    missing = REQUIRED_LONG_FORMAT_COLS - set(df.columns)
    if missing:
        sys.exit(
            f"{context}: {path} doesn't look like a long-format codebook "
            f"(missing columns: {sorted(missing)}). Did you point this at "
            f"an aggregated view file by mistake?"
        )


def require_column(df, name, path, context, label="column", hint=""):
    if name not in df.columns:
        sys.exit(
            f"{context}: {label} {name!r} not found in {path} "
            f"(columns present: {list(df.columns)}){hint}"
        )


def find_duplicate_ids(df):
    return df[df["id"].duplicated(keep=False)].sort_values("id")


def nonempty_values(df, column):
    return [v for v in df[column] if v]


# nargs="+" args that should also accept a comma-separated list (or a mix of
# both), so `--select-labels a,b` and `--select-labels a b` behave the same.
LIST_ARGS = ["select_labels", "exclude", "filter_verb", "exclude_verb", "skip_column"]


def split_list_arg(values):
    return [v.strip() for group in values for v in group.split(",") if v.strip()]


def levenshtein_le(a, b, cutoff):
    """Levenshtein edit distance, capped: returns cutoff + 1 if the true
    distance exceeds cutoff (exact value not needed past that point)."""
    if abs(len(a) - len(b)) > cutoff:
        return cutoff + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
        if min(prev) > cutoff:
            return cutoff + 1
    return prev[-1]


def normalize_for_dupe(s):
    s = re.sub(r"[^\w\s]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def find_near_duplicates(df, column):
    """Report near-identical values within one column: case-insensitive
    equality, equality after whitespace/punctuation normalization, and (for
    values >10 chars) Levenshtein distance <=2. Returns [(ids, message), ...]."""
    values = sorted(set(nonempty_values(df, column)))
    if len(values) < 2:
        return []
    ids_by_value = df.groupby(column)["id"].apply(list)

    findings = []
    seen_pairs = set()

    def bucket_pairs(keyfunc):
        buckets = {}
        for v in values:
            buckets.setdefault(keyfunc(v), []).append(v)
        for bucket in buckets.values():
            for i in range(len(bucket)):
                for j in range(i + 1, len(bucket)):
                    yield bucket[i], bucket[j]

    def add(a, b, reason):
        seen_pairs.add((a, b))
        findings.append(
            (ids_by_value[a] + ids_by_value[b], f"{column}: {a!r} ~ {b!r} ({reason})")
        )

    for a, b in bucket_pairs(str.lower):
        add(a, b, "case-insensitive equal")
    for a, b in bucket_pairs(normalize_for_dupe):
        if (a, b) not in seen_pairs:
            add(a, b, "equal after whitespace/punctuation normalization")

    # Edit-distance pass: cutoff is 2, so a length gap >2 can never qualify --
    # that bound doubles as the prune, no separate threshold to justify.
    long_values = [v for v in values if len(v) > 10]
    for i, a in enumerate(long_values):
        for b in long_values[i + 1 :]:
            if (a, b) in seen_pairs or abs(len(a) - len(b)) > 2:
                continue
            d = levenshtein_le(a, b, 2)
            if d <= 2:
                add(a, b, f"edit distance {d}")

    return findings


def confirm_apply_relabel(prompt):
    """Return True only when the user presses a literal y key."""
    if not sys.stdin.isatty():
        return False

    sys.stdout.write(prompt)
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        response = sys.stdin.read(1)
    except (OSError, ValueError, KeyboardInterrupt):
        response = ""
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    sys.stdout.write("\n")
    sys.stdout.flush()
    return response == "y"


def parse_file(path):
    """Return (rows, skipped_filler, warnings) for one _codes.txt file."""
    participant = None
    group = None
    rows = []
    skipped_filler = 0
    warnings = []

    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                continue

            # Header fields (participant / group) — read from file, not filename.
            hk = HEADER_KEY_RE.match(stripped)
            if hk and hk.group("key") in ("PARTICIPANT", "GROUP"):
                if hk.group("key") == "PARTICIPANT":
                    participant = hk.group("val").strip()
                else:
                    group = hk.group("val").strip()
                continue

            if stripped.startswith("[TASK"):
                continue

            m = CODE_RE.match(stripped)
            if m:
                if participant is None or group is None:
                    warnings.append(
                        f"{path}:{lineno}: code line before PARTICIPANT/GROUP header"
                    )
                pid = (
                    f"{int(participant):02d}"
                    if participant and participant.isdigit()
                    else str(participant)
                )
                app_id = f"{pid}.{m.group('turn')}.{m.group('sub')}"

                iv_raw = m.group("iv").strip()
                iv_m = IV_RE.match(iv_raw)
                if iv_m:
                    iv_clean = iv_m.group("quote").strip()
                else:
                    # Didn't match the expected quoted-string shape at all;
                    # fall back to the raw text but flag it for a look.
                    iv_clean = iv_raw
                    warnings.append(
                        f'{path}:{lineno}: IV field not in expected "..." '
                        f"shape, kept as-is: {iv_raw[:80]!r}"
                    )

                rows.append(
                    {
                        "id": app_id,
                        "group": group,
                        "raw_label": m.group("label").strip(),
                        "canonical_label": m.group("label").strip(),  # seed == raw
                        "in_vivo": iv_clean,
                    }
                )
                continue

            # Not a code line. Classify: known filler vs. unexpected.
            if STMT_LIKE_RE.match(stripped):
                if "(no code" in stripped:
                    skipped_filler += 1
                else:
                    warnings.append(
                        f"{path}:{lineno}: statement-like line did not parse "
                        f"as PROCESS|IV: {stripped[:80]!r}"
                    )
            # anything else (UUID, CODING, SCOPE, ---, etc.) silently ignored
    return rows, skipped_filler, warnings


def cmd_build(args):
    files = []
    for pat in args.inputs:
        files.extend(sorted(glob.glob(pat)))
    if not files:
        sys.exit(f"build: no files matched {args.inputs}")

    all_rows, total_filler, all_warn = [], 0, []
    per_file = {}
    for path in files:
        rows, filler, warn = parse_file(path)
        all_rows.extend(rows)
        total_filler += filler
        all_warn.extend(warn)
        per_file[os.path.basename(path)] = len(rows)

    df = pd.DataFrame(
        all_rows, columns=["id", "group", "raw_label", "in_vivo", "canonical_label"]
    )

    # --- validation ---
    errors = []
    dups = find_duplicate_ids(df)
    if not dups.empty:
        errors.append(
            f"duplicate id(s) — {dups['id'].nunique()} value(s):\n"
            + dups[["id", "raw_label"]].to_string(index=False)
        )
    bad_group = df[~df["group"].isin(["E", "B"])]
    if not bad_group.empty:
        errors.append(
            "unexpected group value(s): "
            + ", ".join(sorted(bad_group["group"].dropna().unique()))
        )
    empty_lab = df[df["raw_label"].str.strip() == ""]
    if not empty_lab.empty:
        errors.append(f"{len(empty_lab)} row(s) with empty raw_label")
    stray_quote = df[df["in_vivo"].str.contains('"', regex=False)]
    if not stray_quote.empty:
        errors.append(
            f'{len(stray_quote)} row(s) with a leftover " in in_vivo '
            f"— IV_RE extraction likely didn't match, check warnings:\n"
            + stray_quote[["id", "in_vivo"]].to_string(index=False)
        )

    print("=== build report ===")
    for fn, n in per_file.items():
        print(f"  {fn}: {n} codes")
    print(f"  total code applications : {len(df)}")
    print(f"  filler lines skipped    : {total_filler}")
    print(f"  unique ids              : {df['id'].nunique()}")
    print(
        f"  groups                  : "
        + ", ".join(f"{g}={c}" for g, c in df["group"].value_counts().items())
    )
    if all_warn:
        print("  WARNINGS:")
        for w in all_warn:
            print(f"    - {w}")
    if errors:
        print("  VALIDATION FAILED:")
        for e in errors:
            print("    - " + e.replace("\n", "\n      "))
        sys.exit(1)
    print("  validation: OK")

    if os.path.exists(args.out) and not args.force:
        sys.exit(
            f"build: {args.out} already exists. Refusing to overwrite "
            f"without --force — if this is a v1/v2 file, it likely holds "
            f"manual canonical_label merge decisions that `build` cannot "
            f"reconstruct."
        )
    order_columns(df).to_csv(args.out, index=False)
    print(f"  written: {args.out}")


def cmd_view(args):
    df = read_codebook(args.codebook)
    validate_long_format(df, args.codebook, "view")
    require_column(
        df,
        args.column,
        args.codebook,
        "view",
        hint=(
            ". If this is a pattern-coding column, it's only created once "
            f"`relabel --column {args.column}` has run at least once."
        ),
    )
    if args.untouched_vs and args.changed_vs:
        sys.exit("view: specify at most one of --untouched-vs or --changed-vs")

    col = args.column

    baseline_note = ""
    if args.untouched_vs or args.changed_vs:
        baseline_col = args.untouched_vs or args.changed_vs
        require_column(df, baseline_col, args.codebook, "view", label="baseline column")
        eq_mask = df[col] == df[baseline_col]
        n_untouched, n_changed = int(eq_mask.sum()), int((~eq_mask).sum())
        v_untouched = df.loc[eq_mask, col].nunique()
        v_changed = df.loc[~eq_mask, col].nunique()
        baseline_note = (
            f"baseline ({col} vs {baseline_col}): "
            f"untouched {n_untouched} row(s) / {v_untouched} distinct value(s) | "
            f"changed {n_changed} row(s) / {v_changed} distinct value(s)"
        )
        df = df[eq_mask] if args.untouched_vs else df[~eq_mask]

    df["participant"] = df["id"].str.split(".").str[0]

    def agg(g):
        gc = g["group"].value_counts()
        out = {
            "frequency": len(g),
            "n_participants": g["participant"].nunique(),
            "group_coverage": f"E:{gc.get('E', 0)} / B:{gc.get('B', 0)}",
        }
        if args.quotes:
            seen = {}
            for _, row in g.iterrows():
                q = row["in_vivo"]
                if not q or q in seen:
                    continue
                seen[q] = row["id"]
                if len(seen) >= args.quotes:
                    break
            out["examples"] = sorted(seen.items(), key=lambda p: p[1])
        return pd.Series(out)

    view = (
        df.groupby(col, sort=False)
        .apply(agg, include_groups=False)
        .reset_index()
        .sort_values(["frequency", col], ascending=[False, True])
    )

    # Lead-verb is needed for grouping AND/OR verb filtering; compute it once,
    # independent of which of those was actually requested.
    need_lead_verb = bool(args.group_by_verb or args.filter_verb or args.exclude_verb)
    if need_lead_verb:
        view["lead_verb"] = view[col].apply(lead_verb)
        unmatched = view[view["lead_verb"].isna()]
        if not unmatched.empty:
            print(
                f"  WARNING: {len(unmatched)} value(s) had no extractable "
                f"lead verb, left ungrouped:"
            )
            for lbl in unmatched[col]:
                print(f"    - {lbl!r}")

    if args.filter_verb:
        view = view[view["lead_verb"].isin([v.lower() for v in args.filter_verb])]
    if args.exclude_verb:
        view = view[~view["lead_verb"].isin([v.lower() for v in args.exclude_verb])]
    if args.filter_regex:
        view = view[view[col].astype(str).str.contains(args.filter_regex, case=False, regex=True)]

    verb_note = ""
    if args.group_by_verb:
        # Lead verb is extracted from whatever column we're viewing -- for
        # canonical_label that's the 1st-order verb; for pattern_code/
        # cluster_code it's the same for still-unmerged rows (seeded ==
        # source column), and the merged label's own lead verb for
        # already-merged ones (which doubles as a rough progress signal:
        # merged clusters show up as a single high-frequency row instead of
        # a many-row family).
        view["n_in_cluster"] = view.groupby("lead_verb")[col].transform("count")
        view = view.sort_values(
            ["n_in_cluster", "lead_verb", "frequency", col],
            ascending=[False, True, False, True],
        )
        n_verbs = view["lead_verb"].nunique()
        verb_note = f" | grouped by lead verb: {n_verbs} families"
    elif need_lead_verb:
        view = view.drop(columns=["lead_verb"])

    print(f"=== view === column: {col}{verb_note}")

    if args.out:
        out_abs = os.path.abspath(args.out)
        in_abs = os.path.abspath(args.codebook)
        if out_abs == in_abs:
            sys.exit(
                f"view: refusing to write output over the input codebook "
                f"({args.out}). The view has a different schema (aggregated) "
                f"and would destroy the long-format source, including any "
                f"merge decisions it holds. Choose a different --out path."
            )
        if os.path.exists(args.out) and not args.force:
            sys.exit(
                f"view: {args.out} already exists. Refusing to overwrite "
                f"without --force (protects prior view snapshots and, more "
                f"importantly, any other file you might have pointed at by "
                f"mistake)."
            )
        view_out = view.copy()
        if "examples" in view_out.columns:
            view_out["examples"] = view_out["examples"].apply(
                lambda ex: " || ".join(q for q, _ in ex)
            )
        view_out.to_csv(args.out, index=False)
        print(f"written: {args.out}")
    else:
        with pd.option_context(
            "display.max_rows", None, "display.max_colwidth", 60, "display.width", 200
        ):
            if args.quotes:
                # examples is rendered as nested per-quote sub-rows below its
                # code's summary row, not as a table cell; n_participants /
                # n_in_cluster are dropped here to make room for that.
                display_cols = [
                    c
                    for c in view.columns
                    if c not in ("n_participants", "n_in_cluster", "examples")
                ]
                body_lines = view[display_cols].to_string(index=False).split("\n")
                print(body_lines[0])
                prev_verb = None
                for row_line, (_, row) in zip(body_lines[1:], view.iterrows()):
                    if (
                        args.group_by_verb
                        and prev_verb is not None
                        and row["lead_verb"] != prev_verb
                    ):
                        print()
                    print(row_line)
                    for quote, qid in row["examples"]:
                        print(f"    {qid:12} \"{quote}\"")
                    if args.group_by_verb:
                        prev_verb = row["lead_verb"]
            elif args.group_by_verb:
                # Render the whole table at once so column widths stay
                # consistent, then insert blank lines at cluster boundaries
                # -- the point of this mode is batching related codes for
                # manual review, not just sorting them.
                lines = view.to_string(index=False).split("\n")
                print(lines[0])
                prev_verb = None
                for row_line, verb in zip(lines[1:], view["lead_verb"]):
                    if prev_verb is not None and verb != prev_verb:
                        print()
                    print(row_line)
                    prev_verb = verb
            else:
                print(view.to_string(index=False))

    summary = (
        "\n"
        "view summary: "
        f"{col} values: {len(view)} | "
        f"applications: {len(df)} | "
        f"funnel: {len(df)} -> {len(view)}"
    )
    if baseline_note:
        summary += "\n" + baseline_note
    print(summary)


def cmd_relabel(args):
    df = read_codebook(args.codebook)
    validate_long_format(df, args.codebook, "relabel")

    require_column(df, args.select_column, args.codebook, "relabel", label="--select-column")
    require_column(df, args.seed_from, args.codebook, "relabel", label="--seed-from")
    if bool(args.select_verb) == bool(args.select_labels):
        sys.exit("relabel: specify exactly one of --select-verb or --select-labels")

    created_column = args.column not in df.columns
    if created_column:
        df[args.column] = df[args.seed_from]
        print(
            f"=== COLUMN CREATED ===\n"
            f"  '{args.column}' did not exist -- seeded from "
            f"'{args.seed_from}' for all {len(df)} row(s).\n"
        )

    sel_col = df[args.select_column]

    if args.select_verb:
        mask = sel_col.apply(lead_verb) == args.select_verb.lower()
    else:
        available = set(sel_col)
        missing = [lbl for lbl in args.select_labels if lbl not in available]
        if missing:
            sys.exit(
                "relabel: --select-labels value(s) matched 0 rows in "
                f"{args.select_column!r}, aborting without writing: {missing}"
            )
        mask = sel_col.isin(args.select_labels)

    if args.exclude:
        mask &= ~sel_col.isin(args.exclude)

    selected = df[mask]
    if selected.empty:
        sys.exit("relabel: selection matched 0 rows -- check spelling/casing")

    print(
        f"=== relabel === select: {args.select_column} -> write: {args.column}"
        f"{' (new)' if created_column else ''}"
    )
    n_participants = selected["id"].str.split(".").str[0].nunique()
    gc = selected["group"].value_counts()
    print(
        f"selection matched {len(selected)} row(s), {n_participants} "
        f"participant(s), E:{gc.get('E', 0)} / B:{gc.get('B', 0)}"
    )
    print()
    for _, r in selected.sort_values("id").iterrows():
        if args.select_column == args.column:
            detail = f"{r[args.column]!r}"
        else:
            detail = (
                f"matched {args.select_column}={r[args.select_column]!r} | "
                f"{args.column} {r[args.column]!r}"
            )
        print(f"  {r['id']:12} [{r['group']}] {detail} -> {args.to!r}")

    if not args.apply:
        if not confirm_apply_relabel(
            "\nApply changes? Press y to commit, any other key for dry run: "
        ):
            print("DRY RUN -- no changes written.")
            return

    df.loc[mask, args.column] = args.to
    order_columns(df).to_csv(args.codebook, index=False)
    print(f"\nwritten: {args.codebook}")

    if args.select_verb:
        selector_desc = f'--select-verb "{args.select_verb}"'
    else:
        selector_desc = f"--select-labels ({len(args.select_labels)} value(s))"
    print(
        f"\nsuggested log entry:\n"
        f"  - merged {len(selected)} code(s) via {selector_desc} on "
        f'{args.select_column} -> "{args.to}" ({args.column})'
    )


def cmd_check(args):
    df = read_codebook(args.codebook)
    validate_long_format(df, args.codebook, "check")

    ignore_ids = set()
    if args.ignore:
        with open(args.ignore, encoding="utf-8") as fh:
            ignore_ids = {line.strip() for line in fh if line.strip()}

    # Each finding is (columns, ids, message); `columns` is a tuple naming
    # every column the finding is about, so --skip-column can suppress it.

    # --- 1. Missing values ---
    missing = []
    for c in df.columns:
        bad = df[df[c].str.strip() == ""]
        if not bad.empty:
            missing.append(((c,), bad["id"].tolist(), f"empty '{c}'"))

    # --- 2. Field transposition ---
    transposition = []
    no_verb = df[df["canonical_label"].apply(lambda s: lead_verb(s) is None)]
    if not no_verb.empty:
        transposition.append(
            (
                ("canonical_label",),
                no_verb["id"].tolist(),
                "canonical_label has no extractable lead verb",
            )
        )
    canon_vals = set(nonempty_values(df, "canonical_label"))
    swapped = df[(df["in_vivo"] != "") & df["in_vivo"].isin(canon_vals)]
    if not swapped.empty:
        transposition.append(
            (
                ("canonical_label", "in_vivo"),
                swapped["id"].tolist(),
                "in_vivo exactly matches a canonical_label value used elsewhere "
                "-- looks like canonical_label/in_vivo were swapped",
            )
        )

    # --- 3. Near-duplicate values (advisory) ---
    near_dupes = []
    for c in ("canonical_label", "pattern_code", "cluster_code"):
        if c in df.columns:
            near_dupes.extend(
                ((c,), ids, message) for ids, message in find_near_duplicates(df, c)
            )

    # --- 4. Unsplit compounds (advisory) ---
    compound_mask = df["raw_label"].str.contains(r",|[a-z][A-Z]", regex=True)
    compounds = df[compound_mask & ~df["id"].isin(ignore_ids)]
    unsplit = [
        (("raw_label",), [cid], f"raw_label looks like an unsplit compound: {label!r}")
        for cid, label in zip(compounds["id"], compounds["raw_label"])
    ]

    # --- 5. ID integrity ---
    id_integrity = []
    dup_ids = find_duplicate_ids(df)
    if not dup_ids.empty:
        id_integrity.append((("id",), dup_ids["id"].unique().tolist(), "duplicate id"))
    bad_id_fmt = df[~df["id"].str.match(ID_RE)]
    if not bad_id_fmt.empty:
        id_integrity.append(
            (("id",), bad_id_fmt["id"].tolist(), "id does not match NN.NNN.n[a-z]?")
        )

    checks = [
        ("1. Missing values", "hard fail", missing),
        ("2. Field transposition", "hard fail", transposition),
        ("3. Near-duplicate values", "advisory -- requires human judgement", near_dupes),
        ("4. Unsplit compounds", "advisory -- requires human judgement", unsplit),
        ("5. ID integrity", "hard fail", id_integrity),
    ]

    skip_columns = set(args.skip_column or [])

    print(f"=== check === {args.codebook}")
    if skip_columns:
        print(f"  suppressing findings for column(s): {', '.join(sorted(skip_columns))}")
    n_hard = n_advisory = 0
    for title, severity, findings in checks:
        kept = [f for f in findings if not skip_columns & set(f[0])]
        dropped = [f for f in findings if f not in kept]
        n = sum(len(ids) for _, ids, _ in kept)
        n_suppressed = sum(len(ids) for _, ids, _ in dropped)
        if severity == "hard fail":
            n_hard += n
        else:
            n_advisory += n
        suffix = f" ({n_suppressed} suppressed)" if n_suppressed else ""
        print(f"\n[{severity}] {title}: {n} finding(s){suffix}")
        for _, ids, message in kept:
            print(f"  - {message}")
            print(f"      ids: {ids}")

    print(f"\ncheck: {n_hard} hard-fail issue(s), {n_advisory} advisory issue(s)")
    if n_hard or n_advisory:
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="parse *_codes.txt -> long codebook CSV")
    b.add_argument("inputs", nargs="+", help='files or globs, e.g. "*_codes.txt"')
    b.add_argument("-o", "--out", default="codebook_v0.csv")
    b.add_argument(
        "--force", action="store_true", help="allow overwriting an existing --out file"
    )
    b.set_defaults(func=cmd_build)

    v = sub.add_parser("view", help="aggregate a long codebook into a view")
    v.add_argument("codebook", help="long-format codebook CSV")
    v.add_argument(
        "--column",
        default="canonical_label",
        help=(
            "column to aggregate on (default: canonical_label). Use e.g. "
            "--column pattern_code or --column cluster_code once that "
            "column exists, to view progress on a later coding pass."
        ),
    )
    v.add_argument(
        "-o", "--out", default=None, help="write view CSV (default: print to stdout)"
    )
    v.add_argument(
        "-q",
        "--quotes",
        type=int,
        default=0,
        metavar="N",
        help="include up to N in_vivo examples per canonical label",
    )
    v.add_argument(
        "--force", action="store_true", help="allow overwriting an existing --out file"
    )
    v.add_argument(
        "--group-by-verb",
        action="store_true",
        dest="group_by_verb",
        help=(
            "sort/cluster by lead process verb (grammatical normalization "
            "only -- re-/self- prefix and leading manner adverb stripped; "
            "no synonym grouping). Organizing aid for manual review, not "
            "an analytic grouping."
        ),
    )
    v.add_argument(
        "--filter-verb",
        nargs="+",
        dest="filter_verb",
        help=(
            "only show rows whose lead verb matches this (works with or "
            "without --group-by-verb); space- or comma-separated"
        ),
    )
    v.add_argument(
        "--exclude-verb",
        nargs="+",
        dest="exclude_verb",
        help=(
            "exclude rows whose lead verb matches this (composes with "
            "--filter-verb); space- or comma-separated"
        ),
    )
    v.add_argument(
        "--filter-regex",
        dest="filter_regex",
        help="only show rows where --column matches this regex, case-insensitive",
    )
    v.add_argument(
        "--untouched-vs",
        dest="untouched_vs",
        metavar="COLUMN",
        help="restrict to rows where --column equals COLUMN (not yet reviewed)",
    )
    v.add_argument(
        "--changed-vs",
        dest="changed_vs",
        metavar="COLUMN",
        help="restrict to rows where --column differs from COLUMN (already reviewed)",
    )
    v.set_defaults(func=cmd_view)

    r = sub.add_parser(
        "relabel", help="bulk-set a column for a selected group of codes"
    )
    r.add_argument("codebook", help="long-format codebook CSV, edited in place")
    r.add_argument(
        "--column",
        default="pattern_code",
        help=(
            "column to write into. Defaults to pattern_code. Created and "
            "seeded from --seed-from on first use, so prior-order "
            "granularity stays intact underneath."
        ),
    )
    r.add_argument(
        "--seed-from",
        dest="seed_from",
        default="canonical_label",
        help=(
            "column to seed --column from, the first time --column is "
            "created (default: canonical_label; use e.g. pattern_code when "
            "starting a cluster_code pass)"
        ),
    )
    r.add_argument(
        "--select-column",
        dest="select_column",
        default="canonical_label",
        help=(
            "column to match --select-verb / --select-labels / --exclude "
            "against (default: canonical_label; use e.g. pattern_code to "
            "route whole clusters without enumerating their labels)"
        ),
    )
    r.add_argument(
        "--select-verb",
        help="select all rows whose --select-column lead verb matches this",
    )
    r.add_argument(
        "--select-labels",
        nargs="+",
        help="select rows by exact --select-column match; space- or comma-separated",
    )
    r.add_argument(
        "--exclude",
        nargs="+",
        default=None,
        help=(
            "exclude these exact --select-column values from the selection; "
            "space- or comma-separated"
        ),
    )
    r.add_argument("--to", required=True, help="new value to assign to selected rows")
    r.add_argument(
        "--apply",
        action="store_true",
        help="actually write changes (default: dry-run preview only)",
    )
    r.set_defaults(func=cmd_relabel)

    c = sub.add_parser(
        "check", help="read-only structural/quality checks on a long codebook"
    )
    c.add_argument("codebook", help="long-format codebook CSV")
    c.add_argument(
        "--ignore",
        help=(
            "path to a plain-text file of ids (one per line) exempt from "
            "the unsplit-compounds check"
        ),
    )
    c.add_argument(
        "--skip-column",
        dest="skip_column",
        nargs="+",
        help=(
            "suppress findings tied to these column(s), e.g. raw_label to "
            "silence unsplit-compound warnings; space- or comma-separated"
        ),
    )
    c.set_defaults(func=cmd_check)

    args = p.parse_args()
    for name in LIST_ARGS:
        values = getattr(args, name, None)
        if values:
            setattr(args, name, split_list_arg(values))
    args.func(args)


if __name__ == "__main__":
    main()
