#!/usr/bin/env python3
"""Generate Appendices D, E, G, H, I, and J from the chapters.

Phase 3 §7.3: six of the ten appendices are assembled from material the
chapters already carry, "not hand-maintained -- that is the only way they stay
true across fifty chapters." Appendix A has worked that way since batch 0; this
is the same idea applied to the rest.

    D  Reference Schema                  the data structures of every §9
    E  Port Signatures                   the Protocol definitions of every §8
    G  Failure Mode Catalogue            the failure table of every §11
    H  Anti-Pattern Index                every anti-pattern named, with its
                                         diagnosing chapter
    I  Bibliography and Source Map       every [AHE] and [DAR] citation,
                                         reverse-indexed
    J  Chapter Prerequisites and Unlocks the dependency spine as a flat table

B, C, and F stay hand-written: two are consolidations of the authoring
conventions and one needs a test recipe per invariant, none of which is latent
in the chapters.

Appendix H is the one that is only *semi*-generated. An anti-pattern is named in
prose rather than in a structured block, so the extractor collects the sentences
that name one and the result is a curated index over a mechanical sweep -- which
is honest about what it is, and better than a hand-maintained list that misses
the chapter written last week.

Usage:
    python3 tools/build_appendices.py
    python3 tools/build_appendices.py --check
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass, field

CHAPTER_GLOB = "docs/handbook/chapters/*.md"
OUT_DIR = "docs/handbook/appendices"

RE_HEADER_CHAPTER = re.compile(r"^\s*Level (\d+) . Chapter (\d+)\s*$")
RE_HEADER_REQUIRES = re.compile(r"^\s*Requires\s+(.*)$")
RE_HEADER_UNLOCKS = re.compile(r"^\s*Unlocks\s+(.*)$")
RE_HEADER_DIAGRAMS = re.compile(r"^\s*Diagrams\s+(Light|Core|Full) \((\d+)\)\s*$")
RE_TITLE = re.compile(r"^# Chapter (\d+) — (.+?)\s*$")
RE_SECTION = re.compile(r"^## (\d+)\. (.+?)\s*$")
RE_CHAPTER_REF = re.compile(r"\bC(\d+)\b")

RE_CLASS = re.compile(r"^class\s+(\w+)\s*\(([^)]*)\)\s*:")
RE_DEF = re.compile(r"^\s{4}(async\s+)?def\s+(\w+)\s*\(")
RE_DATACLASS = re.compile(r"^@dataclass")
RE_DOCSTRING = re.compile(r'^\s*"""(.*)')

RE_CITATION = re.compile(r"\[(AHE|DAR)([^\]]*)\]")
RE_ANTIPATTERN = re.compile(r"anti-pattern", re.IGNORECASE)

PREAMBLE = """
> **Generated file. Do not edit by hand.**
>
> Assembled from the chapters by `tools/build_appendices.py`. To change an
> entry, edit the chapter it comes from and regenerate.
"""


@dataclass
class Chapter:
    path: str
    number: int = 0
    level: int = 0
    title: str = ""
    tier: str = ""
    requires: list[int] = field(default_factory=list)
    unlocks: list[int] = field(default_factory=list)
    requires_text: str = ""
    unlocks_text: str = ""
    # section number -> list of (line_no, text)
    sections: dict[int, list[str]] = field(default_factory=dict)
    lines: list[str] = field(default_factory=list)

    @property
    def ref(self) -> str:
        return f"Ch {self.number}"

    @property
    def link(self) -> str:
        return f"[Ch {self.number}](../chapters/{self.path.split('/')[-1]})"


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------


def header_fields(lines: list[str]) -> dict[str, str]:
    """Key/value pairs from the opening header block, continuations joined.

    The header is itself a fenced block, so it has to be read before the
    fence-aware walk below or every `Level 0 . Chapter 7` line is skipped as
    diagram content. Requires and Unlocks wrap across lines in most chapters,
    and the wrapped half carries no keyword.
    """
    fields: dict[str, list[str]] = {}
    key: str | None = None
    seen_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            if seen_fence:
                break
            seen_fence = True
            continue
        if not seen_fence:
            continue
        match = re.match(r"^\s{2,}(Requires|Unlocks|Diagrams|Variant)\s+(.*)$", line)
        if match:
            key = match.group(1)
            fields.setdefault(key, []).append(match.group(2).strip())
        elif key and line.strip():
            fields[key].append(line.strip())
    return {k: " ".join(v) for k, v in fields.items()}


def parse(path: str) -> Chapter:
    lines = open(path, encoding="utf-8").read().split("\n")
    ch = Chapter(path=path, lines=lines)

    for line in lines[:14]:
        match = RE_HEADER_CHAPTER.match(line)
        if match:
            ch.level, ch.number = int(match.group(1)), int(match.group(2))
            break

    fields = header_fields(lines)
    ch.requires_text = fields.get("Requires", "")
    ch.unlocks_text = fields.get("Unlocks", "")
    ch.requires = [int(n) for n in RE_CHAPTER_REF.findall(ch.requires_text)]
    ch.unlocks = [int(n) for n in RE_CHAPTER_REF.findall(ch.unlocks_text)]
    match = re.match(r"(Light|Core|Full)\b", fields.get("Diagrams", ""))
    if match:
        ch.tier = match.group(1)

    in_fence = False
    current = 0
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            ch.sections.setdefault(current, []).append(line)
            continue
        if not in_fence:
            match = RE_TITLE.match(line)
            if match:
                ch.title = match.group(2)
            match = RE_SECTION.match(line)
            if match:
                current = int(match.group(1))
                continue
        ch.sections.setdefault(current, []).append(line)
    return ch


def code_blocks(ch: Chapter, section: int, language: str = "python") -> list[list[str]]:
    """Fenced blocks of one language inside one section."""
    out: list[list[str]] = []
    body: list[str] = []
    open_lang: str | None = None
    for line in ch.sections.get(section, []):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            if open_lang is None:
                open_lang = stripped[3:].strip()
                body = []
            else:
                if open_lang == language:
                    out.append(body)
                open_lang = None
            continue
        if open_lang is not None:
            body.append(line)
    return out


def tables(ch: Chapter, section: int) -> list[list[list[str]]]:
    """Markdown tables inside one section, as lists of cell-rows."""
    out: list[list[list[str]]] = []
    current: list[list[str]] = []
    in_fence = False
    for line in ch.sections.get(section, []):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue                      # the separator row
            current.append(cells)
        elif current:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def first_docstring(body: list[str], start: int) -> str:
    """The first sentence of a class or method docstring.

    Docstrings wrap at 72 columns, so the first *line* routinely ends mid-
    clause. The first sentence is what the index wants, and it is worth the
    extra few lines of gathering.
    """
    text = ""
    for offset, line in enumerate(body[start:start + 8]):
        match = RE_DOCSTRING.match(line)
        if not match:
            if text:
                break
            continue
        text = match.group(1).strip()
        for follow in body[start + offset + 1:start + offset + 6]:
            if "." in text or not follow.strip() or '"""' in follow:
                break
            text += " " + follow.strip()
        break
    text = text.split('"""')[0].strip()
    sentence = text.split(". ")[0].rstrip(".").strip()
    return sentence


# --------------------------------------------------------------------------
# Appendix D -- Reference Schema
# --------------------------------------------------------------------------


def build_d(chapters: list[Chapter]) -> str:
    rows: list[str] = []
    detail: list[str] = []
    for ch in chapters:
        found: list[tuple[str, str, str]] = []
        for body in code_blocks(ch, 9):
            for index, line in enumerate(body):
                match = RE_CLASS.match(line)
                if not match:
                    continue
                name, bases = match.group(1), match.group(2)
                if "Protocol" in bases:
                    continue                  # those are Appendix E's
                kind = "enum" if "Enum" in bases else "dataclass"
                if index and RE_DATACLASS.match(body[index - 1].strip()):
                    kind = "dataclass"
                found.append((name, kind, first_docstring(body, index + 1)))
        if not found:
            continue
        for name, kind, gist in found:
            rows.append(f"| `{name}` | {kind} | {ch.link} | {gist or '—'} |")
        detail.append(f"### Chapter {ch.number} — {ch.title}\n")
        for body in code_blocks(ch, 9):
            detail.append("```python\n" + "\n".join(body).strip("\n") + "\n```\n")

    parts = [
        "# Appendix D — Reference Schema\n",
        PREAMBLE,
        "\nEvery data structure the handbook defines, from the *Data Structures* "
        "section of each chapter. Frozen dataclasses are the handbook's data "
        "carriers; enums are the closed vocabularies. Ports live in "
        "[Appendix E](e-port-signatures.md).\n",
        f"\n{len(rows)} structures across {len(detail)} chapters.\n",
        "\n---\n\n## Index\n",
        "\n| Structure | Kind | Chapter | Purpose |",
        "\n|---|---|---|---|\n",
        "\n".join(rows),
        "\n\n---\n\n## Definitions\n\n",
        "\n".join(detail),
    ]
    return "".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------
# Appendix E -- Port Signatures
# --------------------------------------------------------------------------


def build_e(chapters: list[Chapter]) -> str:
    rows: list[str] = []
    detail: list[str] = []
    total = 0
    for ch in chapters:
        found = False
        for body in code_blocks(ch, 8):
            for index, line in enumerate(body):
                match = RE_CLASS.match(line)
                if not match or "Protocol" not in match.group(2):
                    continue
                found = True
                total += 1
                methods = []
                for follow in body[index + 1:]:
                    if RE_CLASS.match(follow):
                        break
                    hit = RE_DEF.match(follow)
                    if hit:
                        methods.append(("async " if hit.group(1) else "") + hit.group(2))
                rows.append(
                    f"| `{match.group(1)}` | {ch.link} | "
                    f"{', '.join(f'`{m}`' for m in methods) or '—'} | "
                    f"{first_docstring(body, index + 1) or '—'} |"
                )
        if found:
            detail.append(f"### Chapter {ch.number} — {ch.title}\n")
            for body in code_blocks(ch, 8):
                detail.append("```python\n" + "\n".join(body).strip("\n") + "\n```\n")

    parts = [
        "# Appendix E — Port Signatures\n",
        PREAMBLE,
        "\nEvery `Protocol` the handbook defines, from the *Internal APIs* section "
        "of each chapter. A port is an extension point you implement; the "
        "handbook uses `typing.Protocol` rather than ABCs throughout, and a "
        "signature without type hints is not a contract.\n",
        "\nThe docstrings are load-bearing. Several ports carry their design "
        "argument there — why a method raises rather than warns, why an update "
        "method is absent — and those are reproduced in full below.\n",
        f"\n{total} ports across {len(detail)} chapters.\n",
        "\n---\n\n## Index\n",
        "\n| Port | Chapter | Methods | Purpose |",
        "\n|---|---|---|---|\n",
        "\n".join(rows),
        "\n\n---\n\n## Definitions\n\n",
        "\n".join(detail),
    ]
    return "".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------
# Appendix G -- Failure Mode Catalogue
# --------------------------------------------------------------------------

# Five header shapes across the corpus; all reduce to these four columns.
G_COLUMNS = ("Failure", "Trigger", "Detector", "Recovery")
G_ALIASES = {
    "failure": "Failure",
    "failure mode": "Failure",
    "category error": "Failure",
    "trigger": "Trigger",
    "symptom": "Detector",
    "detected by": "Detector",
    "detection": "Detector",
    "detector": "Detector",
    "recovery": "Recovery",
}


def build_g(chapters: list[Chapter]) -> str:
    rows: list[str] = []
    for ch in chapters:
        for table in tables(ch, 11):
            if len(table) < 2:
                continue
            header = [G_ALIASES.get(c.lower().strip("* "), "") for c in table[0]]
            if "Recovery" not in header and "Detector" not in header:
                continue
            for cells in table[1:]:
                mapped = {name: "" for name in G_COLUMNS}
                for name, value in zip(header, cells):
                    if name:
                        mapped[name] = value
                if not any(mapped.values()):
                    continue
                # A three-column table leads with the trigger; the failure is
                # then the trigger, which is how those chapters read it.
                if not mapped["Failure"]:
                    mapped["Failure"] = mapped["Trigger"]
                    mapped["Trigger"] = ""
                rows.append(
                    f"| {ch.link} | {mapped['Failure']} | {mapped['Trigger'] or '—'} "
                    f"| {mapped['Detector'] or '—'} | {mapped['Recovery'] or '—'} |"
                )

    nothing = sum(1 for r in rows if re.search(r"\|\s*(?:Nothing|None)\b", r, re.I))
    parts = [
        "# Appendix G — Failure Mode Catalogue\n",
        PREAMBLE,
        "\nEvery entry from the *Failure Modes* section of every chapter, in one "
        "table. The handbook treats the failure table as a design artefact "
        "rather than a postscript (Chapter 27 §14), so this is the closest "
        "thing the book has to a single specification of what can go wrong.\n",
        f"\n{len(rows)} failure modes across {len(chapters)} chapters. "
        f"**{nothing} of them have no detector** — the recurring shape of "
        "Levels 3 through 5, where the failure produces no error and often no "
        "signal at all.\n",
        "\n---\n\n",
        "| Chapter | Failure | Trigger | Detector | Recovery |\n",
        "|---|---|---|---|---|\n",
        "\n".join(rows),
    ]
    return "".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------
# Appendix H -- Anti-Pattern Index
# --------------------------------------------------------------------------


def paragraphs(ch: Chapter, section: int) -> list[str]:
    """Prose paragraphs of one section, wrapping joined, fences dropped."""
    out: list[str] = []
    buffer: list[str] = []
    in_fence = False
    for line in ch.sections.get(section, []):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            if buffer:
                out.append(" ".join(buffer))
                buffer = []
            continue
        if in_fence or not line.strip() or line.startswith("|"):
            if buffer:
                out.append(" ".join(buffer))
                buffer = []
            continue
        buffer.append(line.strip())
    if buffer:
        out.append(" ".join(buffer))
    return out


# "App. B.2" and "Alg. 1" end in a period that is not a sentence boundary, and
# citations like `[AHE App. B.2]` sit mid-sentence throughout the book.
ABBREVIATIONS = ("App.", "Alg.", "Fig.", "sec.", "Ch.", "vs.", "e.g.", "i.e.")


def sentences(text: str) -> list[str]:
    """Split on sentence boundaries, without splitting inside a citation."""
    guarded = text
    for abbreviation in ABBREVIATIONS:
        guarded = guarded.replace(abbreviation + " ", abbreviation + "\x00")
    parts = re.split(r"(?<=[.:])\s+(?=[A-Z`*])", guarded)
    return [p.replace("\x00", " ") for p in parts]


def build_h(chapters: list[Chapter]) -> str:
    named: list[str] = []       # from the explicit tables a few chapters carry
    mentions: list[str] = []

    for ch in chapters:
        for section in sorted(ch.sections):
            for table in tables(ch, section):
                if not table or "anti-pattern" not in table[0][0].lower():
                    continue
                for cells in table[1:]:
                    padded = cells + [""] * (3 - len(cells))
                    named.append(
                        f"| {padded[0]} | {padded[1]} | {padded[2] or '—'} | "
                        f"{ch.link} |"
                    )

            for para in paragraphs(ch, section):
                if not RE_ANTIPATTERN.search(para):
                    continue
                # The sentence, not the wrapped line: prose wraps at 100
                # columns and a line-at-a-time sweep quotes half a clause.
                for sentence in sentences(para):
                    if RE_ANTIPATTERN.search(sentence):
                        text = re.sub(r"\s+", " ", sentence).strip("-*# ")
                        mentions.append(f"| {ch.link} | §{section} | {text} |")

    parts = [
        "# Appendix H — Anti-Pattern Index\n",
        PREAMBLE,
        "\n**Semi-generated, and the only appendix that is.** An anti-pattern is "
        "named in prose rather than in a structured block, so this is a "
        "mechanical sweep for every place the book names one, plus the explicit "
        "tables a few chapters carry. It is a curated index over a complete "
        "sweep rather than a hand-maintained list, which is the trade that keeps "
        "it true as chapters are added.\n",
        "\n---\n\n## Named in a table\n\n",
        "Chapters 0 through 2 close with an explicit anti-pattern table, which is "
        "where the book's named failures were first collected.\n\n",
        "| Anti-pattern | Why it fails | Fixed in | Named in |\n",
        "|---|---|---|---|\n",
        "\n".join(named),
        f"\n\n---\n\n## Every mention, in order\n\n{len(mentions)} passages "
        "across the book name an anti-pattern. The sweep is complete; the "
        "phrasing is the chapter's.\n\n",
        "| Chapter | Section | Passage |\n",
        "|---|---|---|\n",
        "\n".join(mentions),
    ]
    return "".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------
# Appendix I -- Bibliography and Source Map
# --------------------------------------------------------------------------


def normalise_citation(piece: str) -> str:
    """`[AHE 3.1]` and `[AHE \u00a73.1]` are the same reference.

    Diagrams are 7-bit ASCII (Appendix C), so a citation inside one drops the
    section mark. Without this they index as two entries and the reverse map
    understates both.
    """
    piece = piece.strip().strip(".")
    if re.match(r"^\u00a7?\d", piece):
        return "\u00a7" + piece.lstrip("\u00a7 ")
    return piece


def build_i(chapters: list[Chapter]) -> str:
    index: dict[tuple[str, str], set[int]] = {}
    per_chapter: dict[int, dict[str, int]] = {}

    for ch in chapters:
        counts = {"AHE": 0, "DAR": 0}
        for section in sorted(ch.sections):
            for line in ch.sections[section]:
                for tag, rest in RE_CITATION.findall(line):
                    counts[tag] += 1
                    body = re.sub(r"\s+", " ", rest).strip()
                    if not body:
                        index.setdefault((tag, "(untargeted)"), set()).add(ch.number)
                        continue
                    for piece in body.split(","):
                        piece = normalise_citation(piece)
                        if piece:
                            index.setdefault((tag, piece), set()).add(ch.number)
        per_chapter[ch.number] = counts

    def sort_key(item: tuple[str, str]) -> tuple[str, int, list[float], str]:
        tag, ref = item
        group = 0 if ref.startswith("\u00a7") else 1 if ref.startswith("App.") else 2
        digits = [float(d) for d in re.findall(r"\d+", ref)] or [999.0]
        return (tag, group, digits, ref)

    lines: list[str] = []
    for tag, ref in sorted(index, key=sort_key):
        chapters_citing = ", ".join(f"Ch {n}" for n in sorted(index[(tag, ref)]))
        lines.append(f"| `[{tag}]` | {ref} | {len(index[(tag, ref)])} | {chapters_citing} |")

    density = [
        f"| Ch {n} | {c['AHE']} | {c['DAR']} | {c['AHE'] + c['DAR']} |"
        for n, c in sorted(per_chapter.items())
    ]

    total = sum(len(v) for v in index.values())
    parts = [
        "# Appendix I — Bibliography and Source Map\n",
        PREAMBLE,
        "\nThe two primary sources, reverse-indexed: for each cited section, "
        "which chapters draw on it. `[AHE]` is the Agentic Harness Engineering "
        "paper and `[DAR]` the durable agent runtime specification; they are "
        "co-primary, and where they overlap the handbook cites both and names "
        "the difference rather than merging them.\n",
        "\nClaims tagged `[INF]`, `[BP]`, and `[FUT]` are not indexed here. They "
        "are the handbook's own inference, established practice, and "
        "speculation respectively, and none of them resolves to a source "
        "section.\n",
        f"\n{len(index)} distinct citations, {total} chapter-citations in total.\n",
        "\n---\n\n## By source section\n\n",
        "| Source | Section | Chapters | Cited in |\n",
        "|---|---|---:|---|\n",
        "\n".join(lines),
        "\n\n---\n\n## Citation density, by chapter\n\n",
        "A chapter with no `[AHE]` or `[DAR]` citation is a chapter the handbook "
        "derived on its own, which the linter warns about so that it is a "
        "decision rather than an oversight.\n\n",
        "| Chapter | `[AHE]` | `[DAR]` | Total |\n",
        "|---|---:|---:|---:|\n",
        "\n".join(density),
    ]
    return "".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------
# Appendix J -- Chapter Prerequisites and Unlocks
# --------------------------------------------------------------------------


LEVEL_NAMES = {
    0: "Foundations",
    1: "High-Level Runtime",
    2: "Core Components",
    3: "Advanced Runtime",
    4: "Production Engineering",
    5: "Self-Evolving Systems",
}


def build_j(chapters: list[Chapter]) -> str:
    by_number = {ch.number: ch for ch in chapters}
    required_by: dict[int, set[int]] = {ch.number: set() for ch in chapters}
    for ch in chapters:
        for req in ch.requires:
            if req in required_by:
                required_by[req].add(ch.number)

    rows = []
    for ch in chapters:
        req = ch.requires_text or "—"
        unl = ch.unlocks_text or "—"
        rows.append(
            f"| {ch.link} | {ch.title} | {ch.level} | {ch.tier} | {req} | {unl} |"
        )

    load = sorted(
        ((len(v), k) for k, v in required_by.items()), reverse=True
    )[:12]
    load_rows = [
        f"| Ch {n} | {by_number[n].title} | {count} | "
        f"{', '.join(f'Ch {m}' for m in sorted(required_by[n]))} |"
        for count, n in load if count
    ]

    orphans = [f"Ch {ch.number} — {ch.title}"
               for ch in chapters if not ch.requires and ch.number != 0]

    parts = [
        "# Appendix J — Chapter Prerequisites and Unlocks\n",
        PREAMBLE,
        "\nThe dependency spine as a flat table, taken from the header block of "
        "every chapter. `Requires` names chapters that must precede; `Unlocks` "
        "names chapters that build on this one. The linter enforces the "
        "direction of both, so a cycle is not expressible.\n",
        f"\n{len(chapters)} chapters across {len(LEVEL_NAMES)} levels.\n",
        "\n---\n\n## The spine\n\n",
        "| Chapter | Title | Level | Tier | Requires | Unlocks |\n",
        "|---|---|---:|---|---|---|\n",
        "\n".join(rows),
        "\n\n---\n\n## Load-bearing chapters\n\n",
        "Ranked by how many later chapters declare them a prerequisite. These "
        "are the chapters a reader cannot skip, and the ones an edit is most "
        "expensive in.\n\n",
        "| Chapter | Title | Required by | Which |\n",
        "|---|---|---:|---|\n",
        "\n".join(load_rows),
        "\n\n---\n\n## Entry points\n\n",
        "Chapters that declare no prerequisite, and can therefore be read "
        "first:\n\n",
        "\n".join(f"- {o}" for o in orphans) or "- (none)",
    ]
    return "".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


BUILDERS = {
    "d-reference-schema.md": build_d,
    "e-port-signatures.md": build_e,
    "g-failure-mode-catalogue.md": build_g,
    "h-anti-pattern-index.md": build_h,
    "i-bibliography-and-source-map.md": build_i,
    "j-chapter-prerequisites-and-unlocks.md": build_j,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify the appendices are current; write nothing")
    args = parser.parse_args()

    paths = sorted(glob.glob(CHAPTER_GLOB))
    if not paths:
        print("no chapters found", file=sys.stderr)
        return 1
    chapters = [parse(p) for p in paths]

    stale = []
    for name, builder in BUILDERS.items():
        content = builder(chapters)
        target = f"{OUT_DIR}/{name}"
        try:
            existing = open(target, encoding="utf-8").read()
        except FileNotFoundError:
            existing = None
        if args.check:
            if existing != content:
                stale.append(target)
            continue
        open(target, "w", encoding="utf-8").write(content)
        print(f"wrote {target}: {len(content.splitlines())} lines")

    if args.check:
        if stale:
            for target in stale:
                print(f"{target} is out of date; run tools/build_appendices.py",
                      file=sys.stderr)
            return 1
        print(f"{len(BUILDERS)} appendices are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
