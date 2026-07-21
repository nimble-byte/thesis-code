#!/usr/bin/env python3
"""
codebook.py — first->second cycle transition tooling (Pass A: code mapping).

Two commands:
  build : parse *_codes.txt first-cycle files -> long-format codebook CSV (v0).
  view  : regenerate the aggregated codebook view from a long-format CSV.

Long-format schema (one row per code application, the source of truth):
  id, group, raw_label, canonical_label, in_vivo
    id : NN.NNN.n  (participant . turn . subline)  -- unique application key
    canonical_label : seeded == raw_label in v0; Pass A overwrites on merge.

Versioning is `cp codebook_v0.csv codebook_v1.csv` then edit canonical_label.
Frequency / spread / group coverage are NEVER stored; `view` derives them so
they cannot drift from the rows.

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
    r'^\[(?P<turn>\d{3})\.(?P<sub>[0-9a-z]+)\]\s+'
    r'PROCESS:\s+(?P<label>.+?)\s+\|\s+IV:\s+(?P<iv>.+)$'
)
# IV field is quote-wrapped: IV: "verbatim text"
IV_RE = re.compile(r'^"(?P<quote>.*)"\s*$')
# A line that opens like a coded statement but isn't a PROCESS line
# (e.g. filler "[011.15] — (no code: ...)"). Used only to classify skips.
STMT_LIKE_RE = re.compile(r'^\[\d{3}\.[0-9a-z]+\]')
HEADER_KEY_RE = re.compile(r'^(?P<key>[A-Z]+):\s*(?P<val>.+?)\s*$')


def parse_file(path):
    """Return (rows, skipped_filler, warnings) for one _codes.txt file."""
    participant = None
    group = None
    rows = []
    skipped_filler = 0
    warnings = []

    with open(path, encoding='utf-8') as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip('\n')
            stripped = line.strip()
            if not stripped:
                continue

            # Header fields (participant / group) — read from file, not filename.
            hk = HEADER_KEY_RE.match(stripped)
            if hk and hk.group('key') in ('PARTICIPANT', 'GROUP'):
                if hk.group('key') == 'PARTICIPANT':
                    participant = hk.group('val').strip()
                else:
                    group = hk.group('val').strip()
                continue

            if stripped.startswith('[TASK'):
                continue

            m = CODE_RE.match(stripped)
            if m:
                if participant is None or group is None:
                    warnings.append(
                        f"{path}:{lineno}: code line before PARTICIPANT/GROUP header")
                pid = f"{int(participant):02d}" if participant and participant.isdigit() \
                    else str(participant)
                app_id = f"{pid}.{m.group('turn')}.{m.group('sub')}"

                iv_raw = m.group('iv').strip()
                iv_m = IV_RE.match(iv_raw)
                if iv_m:
                    iv_clean = iv_m.group('quote').strip()
                else:
                    # Didn't match the expected quoted-string shape at all;
                    # fall back to the raw text but flag it for a look.
                    iv_clean = iv_raw
                    warnings.append(
                        f"{path}:{lineno}: IV field not in expected \"...\" "
                        f"shape, kept as-is: {iv_raw[:80]!r}")

                rows.append({
                    'id': app_id,
                    'group': group,
                    'raw_label': m.group('label').strip(),
                    'canonical_label': m.group('label').strip(),  # seed == raw
                    'in_vivo': iv_clean,
                })
                continue

            # Not a code line. Classify: known filler vs. unexpected.
            if STMT_LIKE_RE.match(stripped):
                if '(no code' in stripped:
                    skipped_filler += 1
                else:
                    warnings.append(
                        f"{path}:{lineno}: statement-like line did not parse "
                        f"as PROCESS|IV: {stripped[:80]!r}")
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

    df = pd.DataFrame(all_rows, columns=[
        'id', 'group', 'raw_label', 'canonical_label', 'in_vivo'])

    # --- validation ---
    errors = []
    dups = df[df['id'].duplicated(keep=False)].sort_values('id')
    if not dups.empty:
        errors.append(f"duplicate id(s) — {dups['id'].nunique()} value(s):\n"
                      + dups[['id', 'raw_label']].to_string(index=False))
    bad_group = df[~df['group'].isin(['E', 'B'])]
    if not bad_group.empty:
        errors.append("unexpected group value(s): "
                      + ", ".join(sorted(bad_group['group'].dropna().unique())))
    empty_lab = df[df['raw_label'].str.strip() == '']
    if not empty_lab.empty:
        errors.append(f"{len(empty_lab)} row(s) with empty raw_label")
    stray_quote = df[df['in_vivo'].str.contains('"', regex=False)]
    if not stray_quote.empty:
        errors.append(f"{len(stray_quote)} row(s) with a leftover \" in in_vivo "
                      f"— IV_RE extraction likely didn't match, check warnings:\n"
                      + stray_quote[['id', 'in_vivo']].to_string(index=False))

    print("=== build report ===")
    for fn, n in per_file.items():
        print(f"  {fn}: {n} codes")
    print(f"  total code applications : {len(df)}")
    print(f"  filler lines skipped    : {total_filler}")
    print(f"  unique ids              : {df['id'].nunique()}")
    print(f"  groups                  : "
          + ", ".join(f"{g}={c}" for g, c in df['group'].value_counts().items()))
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
            f"reconstruct.")
    df.to_csv(args.out, index=False)
    print(f"  written: {args.out}")


def cmd_view(args):
    df = pd.read_csv(args.codebook, dtype=str).fillna('')
    df['participant'] = df['id'].str.split('.').str[0]

    def agg(g):
        gc = g['group'].value_counts()
        out = {
            'frequency': len(g),
            'n_participants': g['participant'].nunique(),
            'group_coverage': f"E:{gc.get('E', 0)} / B:{gc.get('B', 0)}",
        }
        if args.quotes:
            ex = g['in_vivo'].dropna().unique().tolist()[:args.quotes]
            out['examples'] = ' || '.join(ex)
        return pd.Series(out)

    view = (df.groupby('canonical_label', sort=False)
              .apply(agg, include_groups=False)
              .reset_index()
              .sort_values(['frequency', 'canonical_label'],
                           ascending=[False, True]))

    print(f"=== view === canonical labels: {len(view)} | "
          f"applications: {len(df)} | "
          f"funnel: {len(df)} -> {len(view)}")
    if args.out:
        out_abs = os.path.abspath(args.out)
        in_abs = os.path.abspath(args.codebook)
        if out_abs == in_abs:
            sys.exit(
                f"view: refusing to write output over the input codebook "
                f"({args.out}). The view has a different schema (aggregated) "
                f"and would destroy the long-format source, including any "
                f"canonical_label merge decisions it holds. Choose a "
                f"different --out path.")
        if os.path.exists(args.out) and not args.force:
            sys.exit(
                f"view: {args.out} already exists. Refusing to overwrite "
                f"without --force (protects prior view snapshots and, more "
                f"importantly, any other file you might have pointed at by "
                f"mistake).")
        view.to_csv(args.out, index=False)
        print(f"written: {args.out}")
    else:
        with pd.option_context('display.max_rows', None,
                               'display.max_colwidth', 60,
                               'display.width', 200):
            print(view.to_string(index=False))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('build', help='parse *_codes.txt -> long codebook CSV')
    b.add_argument('inputs', nargs='+', help='files or globs, e.g. "*_codes.txt"')
    b.add_argument('-o', '--out', default='codebook_v0.csv')
    b.add_argument('--force', action='store_true',
                   help='allow overwriting an existing --out file')
    b.set_defaults(func=cmd_build)

    v = sub.add_parser('view', help='aggregate a long codebook into a view')
    v.add_argument('codebook', help='long-format codebook CSV')
    v.add_argument('-o', '--out', default=None,
                   help='write view CSV (default: print to stdout)')
    v.add_argument('-q', '--quotes', type=int, default=0, metavar='N',
                   help='include up to N in_vivo examples per canonical label')
    v.add_argument('--force', action='store_true',
                   help='allow overwriting an existing --out file')
    v.set_defaults(func=cmd_view)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
