#!/usr/bin/env python3
"""Cross-reference resolver for the Autonomous Agent Architecture Handbook.

`check_handbook.py` lints one chapter at a time, so it can verify that a
reference names a chapter that exists but not that the *section* it names does.
This tool builds the section index for the whole corpus first, then resolves
every reference against it.

Phase 3 §5, batch 6: "Full cross-reference pass — every `Ch NN §M` reference
resolved against the final text." Doing that by hand across fifty chapters is
the kind of task that is done once and then decays, so it is a tool.

What it resolves:

    Chapter 41 §5.7     Ch 41 §5.7      C41 §5.7        prose forms
    C41 sec 5.7         C41 sec. 5.7                    diagram forms, since
                                                        diagrams are 7-bit ASCII
                                                        and cannot carry §
    §5.7                                                bare: the current chapter
    Appendix A          Interlude II                    existence only

What it deliberately ignores: `[AHE §3.1]`, `[DAR §9.2]` and every other
provenance tag. Those are citations into the sources, not into this book, and
the handbook has no copy of either to resolve against.

Chapters 0-7 use the Phase 1 §15 layout, where the tag sits on a subheading and
the bullets beneath carry bare section numbers:

    ### Supported by the attached Durable Runtime architecture `[DAR]`

    - Domain state and run state as distinct categories (§3.3).

Those `(§3.3)`s are the source's sections, not this chapter's, so a bare
reference inside a tagged block is skipped. Qualified references are still
resolved there, because `Ch 3 §7.3` means this book wherever it appears.

Usage:
    python3 tools/check_xrefs.py
    python3 tools/check_xrefs.py --list-sections 41

Exit code 0 when every reference resolves, 1 otherwise.
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass, field

CHAPTER_GLOB = "docs/handbook/chapters/*.md"
OTHER_GLOBS = (
    "docs/handbook/levels/*.md",
    "docs/handbook/interludes/*.md",
    "docs/handbook/appendices/*.md",
    "docs/handbook/front-matter/*.md",
)

APPENDICES = set("ABCDEFGHIJ")
INTERLUDES = {"I", "II"}

# Provenance tags carry section numbers into AHE and DAR, which are not this
# book. Strip them before anything else or every `[AHE §3.1]` reads as a
# same-chapter reference to §3.1.
RE_PROVENANCE = re.compile(r"\[(?:AHE|DAR|INF|BP|FUT)[^\]]*\]")

RE_SECTION = re.compile(r"^## (\d+)\.\s")
RE_SUBSECTION = re.compile(r"^### (\d+)\.(\d+)\s")
RE_HEADER_CHAPTER = re.compile(r"^\s*Level \d+ . Chapter (\d+)\s*$")

# "Chapter 41 §5.7" | "Ch 41 §5.7" | "C41 §5.7" | "C41 sec 5.7"
RE_CH_SECTION = re.compile(
    r"\b(?:Chapter|Ch|C)\s?(\d{1,2})\s*(?:§|sec\.?\s+)(\d{1,2}(?:\.\d{1,2})?)"
)
# A bare "§5.7" resolves against the chapter it appears in.
RE_BARE_SECTION = re.compile(r"(?<![\w.])§\s?(\d{1,2}(?:\.\d{1,2})?)")

RE_APPENDIX = re.compile(r"\bAppendix ([A-Z])\b")
RE_INTERLUDE = re.compile(r"\bInterlude ([IVX]+)\b")


@dataclass
class Doc:
    path: str
    number: int | None = None          # chapter number, when it is a chapter
    sections: set[str] = field(default_factory=set)
    lines: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.split("/")[-1]


@dataclass
class Finding:
    path: str
    line: int
    reference: str
    message: str


def parse(path: str) -> Doc:
    lines = open(path, encoding="utf-8").read().split("\n")
    doc = Doc(path=path, lines=lines)
    for line in lines:
        match = RE_HEADER_CHAPTER.match(line)
        if match and doc.number is None:
            doc.number = int(match.group(1))
        match = RE_SECTION.match(line)
        if match:
            doc.sections.add(match.group(1))
            continue
        match = RE_SUBSECTION.match(line)
        if match:
            doc.sections.add(f"{match.group(1)}.{match.group(2)}")
            # A subsection implies its parent section exists; the parent is
            # matched above in every real chapter, but appendices and level
            # openers are free-form and this keeps them honest.
            doc.sections.add(match.group(1))
    return doc


def units(doc: Doc) -> list[tuple[str, list[int], bool]]:
    """Scannable units, each with a char-index-to-line map.

    Prose is joined into paragraphs before matching, because the corpus wraps
    at 100 columns and a reference straddles the break often enough to matter:
    `Chapter 20` can end one line and `§12.1` begin the next, and a line-at-a-
    time scan reads the second half as a same-chapter reference. Fenced blocks
    are scanned line by line, since joining a diagram's rows would invent
    adjacencies that are not there.
    """
    out: list[tuple[str, list[int], bool]] = []
    in_fence = False
    in_source_block = False
    buffer: list[str] = []
    buffer_lines: list[int] = []

    def flush() -> None:
        if not buffer:
            return
        text = " ".join(buffer)
        offsets: list[int] = []
        for chunk, line_no in zip(buffer, buffer_lines):
            offsets.extend([line_no] * (len(chunk) + 1))
        out.append((text, offsets[:len(text)] or [buffer_lines[0]], in_source_block))
        buffer.clear()
        buffer_lines.clear()

    for index, raw in enumerate(doc.lines, 1):
        if raw.lstrip().startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            out.append((raw, [index] * max(len(raw), 1), in_source_block))
            continue
        if raw.startswith("## "):
            flush()
            in_source_block = False
        elif raw.startswith("### "):
            flush()
            in_source_block = bool(RE_PROVENANCE.search(raw))
        if not raw.strip():
            flush()
            continue
        buffer.append(raw)
        buffer_lines.append(index)
    flush()
    return out


def blank(match: "re.Match[str]") -> str:
    """Length-preserving removal, so char offsets still map to lines."""
    return " " * len(match.group(0))


def resolve(docs: list[Doc], chapters: dict[int, Doc]) -> list[Finding]:
    out: list[Finding] = []
    for doc in docs:
        for text, offsets, in_source_block in units(doc):

            def line_at(pos: int) -> int:
                return offsets[min(pos, len(offsets) - 1)]

            line = RE_PROVENANCE.sub(blank, text)

            for match in RE_CH_SECTION.finditer(line):
                number, section = match.group(1), match.group(2)
                target = chapters.get(int(number))
                ref = f"Ch {number} \u00a7{section}"
                where = line_at(match.start())
                if target is None:
                    out.append(Finding(doc.path, where, ref,
                                       f"chapter {number} does not exist"))
                elif section not in target.sections:
                    out.append(Finding(doc.path, where, ref,
                                       f"chapter {number} has no \u00a7{section}"
                                       f"{nearest(section, target.sections)}"))

            # Bare section numbers resolve against the chapter they sit in, so
            # the qualified forms are blanked first or "Ch 41 sec 5.7" would
            # also read as a same-chapter reference to 5.7.
            stripped = RE_CH_SECTION.sub(blank, line)
            for match in RE_BARE_SECTION.finditer(stripped):
                if doc.number is None or in_source_block:
                    continue
                section = match.group(1)
                if section not in doc.sections:
                    out.append(Finding(doc.path, line_at(match.start()),
                                       f"\u00a7{section}",
                                       f"this chapter has no \u00a7{section}"
                                       f"{nearest(section, doc.sections)}"))

            for match in RE_APPENDIX.finditer(line):
                if match.group(1) not in APPENDICES:
                    out.append(Finding(doc.path, line_at(match.start()),
                                       f"Appendix {match.group(1)}",
                                       "appendices run A-J"))

            for match in RE_INTERLUDE.finditer(line):
                if match.group(1) not in INTERLUDES:
                    out.append(Finding(doc.path, line_at(match.start()),
                                       f"Interlude {match.group(1)}",
                                       "there are two interludes, I and II"))
    return out


def nearest(section: str, available: set[str]) -> str:
    """A hint, because the common error is an off-by-one subsection."""
    if "." not in section:
        return ""
    parent, _ = section.split(".", 1)
    siblings = sorted(
        (s for s in available if s.startswith(f"{parent}.")),
        key=lambda s: [int(p) for p in s.split(".")],
    )
    return f" (it has {', '.join('§' + s for s in siblings)})" if siblings else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-sections", type=int, metavar="NN",
                        help="print one chapter's section index and exit")
    args = parser.parse_args()

    paths = sorted(glob.glob(CHAPTER_GLOB))
    docs = [parse(p) for p in paths]
    chapters = {d.number: d for d in docs if d.number is not None}

    if args.list_sections is not None:
        target = chapters.get(args.list_sections)
        if target is None:
            print(f"no chapter {args.list_sections}", file=sys.stderr)
            return 1
        for section in sorted(target.sections,
                              key=lambda s: [int(p) for p in s.split(".")]):
            print(f"§{section}")
        return 0

    for pattern in OTHER_GLOBS:
        docs.extend(parse(p) for p in sorted(glob.glob(pattern)))

    findings = resolve(docs, chapters)

    by_file: dict[str, list[Finding]] = {}
    for finding in findings:
        by_file.setdefault(finding.path, []).append(finding)

    for path in sorted(by_file):
        print(f"  FAIL  {path.split('/')[-1]}")
        for finding in by_file[path]:
            print(f"        {path}:{finding.line}  {finding.reference}")
            print(f"                {finding.message}")

    print()
    print(f"{len(docs)} document(s), {len(chapters)} chapter(s): "
          f"{len(findings)} unresolved reference(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
