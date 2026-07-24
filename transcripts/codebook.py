#!/usr/bin/env python3
"""
codebook.py — code mapping + pattern coding tooling.

Three commands:
  build   : parse *_codes.txt first-cycle files -> long-format codebook CSV (v0).
  view    : regenerate the aggregated codebook view from a long-format CSV.
  relabel : bulk-set a column for a selected group of rows (code mapping
            merges, or pattern-coding pattern_code assignment).

Long-format schema (one row per code application, the source of truth):
  id, group, raw_label, canonical_label, in_vivo, [pattern_code, ...]
    id : NN.NNN.n  (participant . turn . subline)  -- unique application key
    canonical_label : seeded == raw_label in v0; code mapping overwrites in place.
    pattern_code (or any --column you choose): created on first relabel call
      targeting it, seeded == canonical_label, then overwritten per selection.
      Keeping this as its own column (not overwriting canonical_label again)
      preserves the 1st-order/2nd-order mapping a Gioia data structure needs.

Versioning is `cp codebook_v1.csv codebook_v2.csv` before a NEW coding
iteration (e.g. code mapping -> pattern coding); within one iteration, edit
the file in place. Frequency / spread / group coverage are NEVER stored;
`view` derives them so they cannot drift from the rows.

pandas is assumed available.
"""

import argparse
import glob
import os
import re
import sys
import pandas as pd

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

# Lead-verb extraction for `view --group-by-verb`: strip grammatical
# modifiers only (re-/self- prefix, a leading manner adverb), never verb
# synonyms -- synonym-level grouping is a meaning judgment (pattern coding),
# out of scope for this purely orthographic organizing aid. Validated at
# 100% gerund coverage (0 exceptions) against the full v1 codebook.
_VERB_PREFIX_RE = re.compile(r"^(re|self)-", re.I)
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
        all_rows, columns=["id", "group", "raw_label", "canonical_label", "in_vivo"]
    )

    # --- validation ---
    errors = []
    dups = df[df["id"].duplicated(keep=False)].sort_values("id")
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
    df.to_csv(args.out, index=False)
    print(f"  written: {args.out}")


def cmd_view(args):
    df = pd.read_csv(args.codebook, dtype=str).fillna("")
    if args.column not in df.columns:
        sys.exit(
            f"view: column {args.column!r} not found in {args.codebook} "
            f"(columns present: {list(df.columns)}). If this is a "
            f"pattern-coding column, it's only created once `relabel "
            f"--column {args.column}` has run at least once."
        )
    df["participant"] = df["id"].str.split(".").str[0]
    col = args.column

    def agg(g):
        gc = g["group"].value_counts()
        out = {
            "frequency": len(g),
            "n_participants": g["participant"].nunique(),
            "group_coverage": f"E:{gc.get('E', 0)} / B:{gc.get('B', 0)}",
        }
        if args.quotes:
            ex = g["in_vivo"].dropna().unique().tolist()[: args.quotes]
            out["examples"] = " || ".join(ex)
        return pd.Series(out)

    view = (
        df.groupby(col, sort=False)
        .apply(agg, include_groups=False)
        .reset_index()
        .sort_values(["frequency", col], ascending=[False, True])
    )

    verb_note = ""
    if args.group_by_verb:
        # Lead verb is extracted from whatever column we're viewing -- for
        # canonical_label that's the 1st-order verb; for pattern_code it's
        # the same for still-unmerged rows (seeded == canonical_label), and
        # the pattern label's own lead verb for already-merged ones (which
        # doubles as a rough progress signal: merged clusters show up as a
        # single high-frequency row instead of a many-row family).
        view["lead_verb"] = view[col].apply(lead_verb)

        if args.filter_verb:
            view = view[view["lead_verb"] == args.filter_verb.lower()]

        unmatched = view[view["lead_verb"].isna()]
        if not unmatched.empty:
            print(f"  WARNING: {len(unmatched)} value(s) had no extractable "
                  f"lead verb, left ungrouped:")
            for lbl in unmatched[col]:
                print(f"    - {lbl!r}")
        view["n_in_cluster"] = view.groupby("lead_verb")[col].transform("count")
        view = view.sort_values(
            ["n_in_cluster", "lead_verb", "frequency", col],
            ascending=[False, True, False, True],
        )
        n_verbs = view["lead_verb"].nunique()
        verb_note = f" | grouped by lead verb: {n_verbs} families"

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
        view.to_csv(args.out, index=False)
        print(f"written: {args.out}")
    else:
        with pd.option_context(
            "display.max_rows", None, "display.max_colwidth", 60, "display.width", 200
        ):
            if args.group_by_verb:
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

    print(
        "\n"
        "view summary: "
        f"{col} values: {len(view)} | "
        f"applications: {len(df)} | "
        f"funnel: {len(df)} -> {len(view)}",
        sep="\n",
    )


def cmd_relabel(args):
    df = pd.read_csv(args.codebook, dtype=str).fillna("")

    required_cols = {"id", "group", "raw_label", "canonical_label", "in_vivo"}
    missing = required_cols - set(df.columns)
    if missing:
        sys.exit(
            f"relabel: {args.codebook} doesn't look like a long-format "
            f"codebook (missing columns: {sorted(missing)}). Did you point "
            f"this at an aggregated view file by mistake?"
        )

    created_column = args.column not in df.columns
    if created_column:
        df[args.column] = df["canonical_label"]  # seed, same convention as v0->v1

    if bool(args.select_verb) == bool(args.select_labels):
        sys.exit("relabel: specify exactly one of --select-verb or --select-labels")

    if args.select_verb:
        mask = df["canonical_label"].apply(lead_verb) == args.select_verb.lower()
    else:
        mask = df["canonical_label"].isin(args.select_labels)

    if args.exclude:
        mask &= ~df["canonical_label"].isin(args.exclude)

    selected = df[mask]
    if selected.empty:
        sys.exit("relabel: selection matched 0 rows -- check spelling/casing")

    print(f"=== relabel === column: {args.column}{' (new)' if created_column else ''}")
    n_participants = selected["id"].str.split(".").str[0].nunique()
    gc = selected["group"].value_counts()
    print(
        f"selection matched {len(selected)} row(s), {n_participants} "
        f"participant(s), E:{gc.get('E', 0)} / B:{gc.get('B', 0)}"
    )
    print()
    for _, r in selected.sort_values("id").iterrows():
        print(f"  {r['id']:12} [{r['group']}] {r[args.column]!r} -> {args.to!r}")

    if not args.apply:
        print(f"\nDRY RUN -- no changes written. Re-run with --apply to commit.")
        return

    df.loc[mask, args.column] = args.to
    df.to_csv(args.codebook, index=False)
    print(f"\nwritten: {args.codebook}")
    print(
        f"\nsuggested log entry:\n"
        f"  - merged {len(selected)} `{args.select_verb or 'selected'}` "
        f'code(s) -> "{args.to}" ({args.column})'
    )


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
            "--column pattern_code once that column exists, to view "
            "progress on a pattern-coding pass."
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
    v.add_argument("--filter-verb", help="only show rows whose lead verb matches this")
    v.set_defaults(func=cmd_view)

    r = sub.add_parser(
        "relabel", help="bulk-set a column for a selected group of codes"
    )
    r.add_argument("codebook", help="long-format codebook CSV, edited in place")
    r.add_argument(
        "--column",
        default="pattern_code",
        help=(
            "column to write into. Defaults to pattern_code. For pattern coding, use e.g. "
            "created and seeded from canonical_label "
            "on first use, so 1st-order granularity stays intact underneath."
        ),
    )
    r.add_argument(
        "--select-verb",
        help="select all rows whose canonical_label lead verb matches this",
    )
    r.add_argument(
        "--select-labels",
        nargs="+",
        help="select rows by exact canonical_label match",
    )
    r.add_argument(
        "--exclude",
        nargs="+",
        default=None,
        help="exclude these exact canonical_label values from the selection",
    )
    r.add_argument("--to", required=True, help="new value to assign to selected rows")
    r.add_argument(
        "--apply",
        action="store_true",
        help="actually write changes (default: dry-run preview only)",
    )
    r.set_defaults(func=cmd_relabel)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
