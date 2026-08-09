#!/usr/bin/env python3
"""Assemble Appendix A (Glossary) from the chapters' N4 term tables.

Phase 3 section 7.3: appendices D, E, G, H, I, and J are generated or
semi-generated from the chapters rather than hand-maintained, because across
fifty chapters a hand-written index goes stale silently. Appendix A is the
first of them.

Each chapter ends section 16 with:

    **Terms introduced in this chapter**

    | Term | In one sentence | Tag | Next needed in |
    |------|-----------------|-----|----------------|
    | **Run** | One goal under execution... | `[DAR]` | Ch 6, Ch 17 |

This reads those tables, sorts the union alphabetically, records which chapter
defined each term, and writes docs/handbook/appendices/a-glossary.md.

Usage:
    python3 tools/build_glossary.py
    python3 tools/build_glossary.py --check      # fail if out of date
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass

CHAPTERS = "docs/handbook/chapters/*.md"
OUTPUT = "docs/handbook/appendices/a-glossary.md"

RE_MARKER = re.compile(r"^\*\*Terms introduced in this chapter\*\*\s*$")
RE_ROW = re.compile(r"^\|\s*\*\*(?P<term>[^*]+)\*\*\s*\|(?P<rest>.*)\|\s*$")
RE_TITLE = re.compile(r"^# Chapter (\d+) — (.+?)\s*$")


@dataclass(frozen=True)
class Entry:
    term: str
    definition: str
    tag: str
    next_needed: str
    chapter: int
    chapter_title: str

    @property
    def sort_key(self) -> str:
        return self.term.lower().lstrip("<([")


def parse_chapter(path: str) -> list[Entry]:
    lines = open(path, encoding="utf-8").read().split("\n")

    number, title = -1, ""
    for line in lines:
        match = RE_TITLE.match(line)
        if match:
            number, title = int(match.group(1)), match.group(2)
            break

    entries: list[Entry] = []
    collecting = False
    for line in lines:
        if RE_MARKER.match(line):
            collecting = True
            continue
        if not collecting:
            continue
        if line.startswith("---") or (line.strip() and not line.startswith("|")):
            break
        match = RE_ROW.match(line)
        if not match:
            continue
        cells = [c.strip() for c in match.group("rest").split("|")]
        if len(cells) < 3:
            continue
        entries.append(Entry(
            term=match.group("term").strip(),
            definition=cells[0],
            tag=cells[1],
            next_needed=cells[2],
            chapter=number,
            chapter_title=title,
        ))
    return entries


def render(entries: list[Entry], chapters_seen: int) -> str:
    # A term may appear in more than one chapter -- typically forward-declared
    # in plain language, then defined properly later. Keep the fullest
    # definition and record every chapter that carries it.
    merged: dict[str, Entry] = {}
    homes: dict[str, list[int]] = {}
    for entry in sorted(entries, key=lambda e: (e.sort_key, e.chapter)):
        key = entry.sort_key
        homes.setdefault(key, []).append(entry.chapter)
        if key not in merged or len(entry.definition) > len(merged[key].definition):
            merged[key] = entry

    by_letter: dict[str, list[Entry]] = {}
    for key in sorted(merged):
        by_letter.setdefault(key[0].upper(), []).append(merged[key])

    out: list[str] = []
    out.append("# Appendix A — Glossary")
    out.append("")
    out.append("> **Generated file. Do not edit by hand.**")
    out.append(">")
    out.append("> Assembled from the *Terms introduced in this chapter* table at the end of every")
    out.append("> chapter by `tools/build_glossary.py`. To change an entry, edit the defining")
    out.append("> chapter's table and regenerate.")
    out.append("")
    out.append(f"Covering {chapters_seen} chapters and {len(merged)} terms.")
    out.append("")
    out.append("Provenance tags: `[AHE]` the Agentic Harness Engineering paper · `[DAR]` the durable")
    out.append("runtime specification · `[INF]` handbook inference · `[BP]` industry practice ·")
    out.append("`[FUT]` speculative proposal.")
    out.append("")
    out.append("**Jump to:** " + " · ".join(f"[{k}](#{k.lower()})" for k in sorted(by_letter)))
    out.append("")
    out.append("---")
    out.append("")

    for letter in sorted(by_letter):
        out.append(f"## {letter}")
        out.append("")
        out.append("| Term | Definition | Tag | Defined in |")
        out.append("|------|------------|-----|------------|")
        for entry in by_letter[letter]:
            chapters = sorted(set(homes[entry.sort_key]))
            where = ", ".join(f"Ch {c}" for c in chapters)
            out.append(
                f"| **{entry.term}** | {entry.definition} | {entry.tag} | {where} |"
            )
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Terms by chapter")
    out.append("")
    by_chapter: dict[int, list[Entry]] = {}
    for entry in entries:
        by_chapter.setdefault(entry.chapter, []).append(entry)
    out.append("| Chapter | Terms introduced |")
    out.append("|---------|------------------|")
    for number in sorted(by_chapter):
        names = ", ".join(e.term for e in by_chapter[number])
        out.append(f"| Ch {number} | {names} |")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the generated file is out of date")
    args = parser.parse_args()

    paths = sorted(glob.glob(CHAPTERS))
    entries: list[Entry] = []
    for path in paths:
        entries.extend(parse_chapter(path))

    if not entries:
        print("no term tables found", file=sys.stderr)
        return 1

    content = render(entries, len(paths))

    try:
        existing = open(OUTPUT, encoding="utf-8").read()
    except FileNotFoundError:
        existing = None

    unique = len({e.sort_key for e in entries})

    if args.check:
        if existing != content:
            print(f"{OUTPUT} is out of date; run tools/build_glossary.py",
                  file=sys.stderr)
            return 1
        print(f"{OUTPUT} is up to date ({unique} terms)")
        return 0

    open(OUTPUT, "w", encoding="utf-8").write(content)
    print(f"wrote {OUTPUT}: {unique} terms ({len(entries)} rows) "
          f"from {len(paths)} chapters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
