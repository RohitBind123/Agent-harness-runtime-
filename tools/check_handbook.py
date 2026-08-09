#!/usr/bin/env python3
"""Convention linter for the Autonomous Agent Architecture Handbook.

Enforces the mechanical parts of the authoring conventions so that they do not
drift across fifty chapters. Specification: docs/handbook/CONVENTIONS.md, which
consolidates Phase 1 sections 6-7, Phase 2 section 7, and Phase 3 section 3.1.

The linter reports; it never rewrites. Diagram authoring stays a human judgement.

Usage:
    python3 tools/check_handbook.py
    python3 tools/check_handbook.py docs/handbook/chapters/08-*.md
    python3 tools/check_handbook.py --warnings-as-errors

Exit code 0 when no errors were found, 1 otherwise.
"""

from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Conventions, encoded
# --------------------------------------------------------------------------

DIAGRAM_MAX_COLUMNS = 78
# Phase 2 section 7.2 estimated "under 150 words" before any chapter existed. The
# eight shipped chapters land at 154-264, so the band is set from the measured
# corpus rather than the estimate. See CONVENTIONS.md, "Revisions".
COLD_OPEN_MAX_WORDS = 250
LAST_CHAPTER = 49

TIER_FIGURE_COUNT = {"Light": None, "Core": 5, "Full": 9}

# Prose-word bands, including the on-ramp blocks (Phase 3 section 0, decision 6)
# and excluding diagrams, tables, and code. Baselined against the nine written
# chapters, whose prose measures 5,176-6,352.
TIER_WORD_BAND = {
    "Light": (4_500, 7_000),
    "Core": (4_500, 7_000),
    "Full": (4_500, 7_500),
}

# CONCEPTUAL VIEW is the Light-tier axis: foundational chapters draw models, not
# components, so they have no layer, time, or state axis to declare.
AXIS_LABELS = ("LAYER VIEW", "TIME VIEW", "STATE VIEW", "CONCEPTUAL VIEW")

KNOWN_FENCE_LANGUAGES = {"python", "sql", "yaml", "json", "text", "bash", "diff"}

PROVENANCE_TAGS = {"AHE", "DAR", "INF", "BP", "FUT"}

# Scripts that have no place in an English handbook. Latin-1 accents,
# em dashes, and the section mark are deliberately NOT here: prose uses
# them. See check_prose_script.
FOREIGN_SCRIPT_RANGES = (
    (0x0400, 0x04FF),   # Cyrillic
    (0x0590, 0x05FF),   # Hebrew
    (0x0600, 0x06FF),   # Arabic
    (0x0900, 0x097F),   # Devanagari
    (0x3040, 0x30FF),   # Hiragana, Katakana
    (0x3400, 0x4DBF),   # CJK extension A
    (0x4E00, 0x9FFF),   # CJK unified ideographs
    (0xAC00, 0xD7AF),   # Hangul
)

# Section 5 and 7 are chapter-specific by design; the rest carry a fixed stem.
SECTION_STEMS: dict[int, tuple[str, ...]] = {
    1: ("Motivation",),
    2: ("High-Level Mental Model",),
    3: ("High-Level Architecture",),
    4: ("Low-Level",),
    6: ("Runtime Sequence",),
    8: ("Interfaces", "Internal APIs"),
    9: ("Data Structures",),
    10: ("Communication",),
    11: ("Failure Modes",),
    12: ("Scalability",),
    13: ("Production Engineering",),
    14: ("Relation to AHE", "Relation to the Base Runtime"),
    15: ("Industry Perspective",),
    16: ("Key Takeaways",),
}

# Phase 1 section 7.6. "the agent" is checked separately: it is legitimate inside
# quotation marks, where chapters diagnose the phrase rather than use it.
PROHIBITED_WORDS = {
    "just": 'signals a skipped explanation; delete it or explain the step',
    "simply": 'signals a skipped explanation; delete it or explain the step',
    "orchestrator": 'use "run driver"',
    "workflow": 'use "plan" or "task graph"',
    "prompt engineering": 'use "context engineering" or "harness engineering"',
}

ONRAMP_BLOCKS = (
    ("N1", re.compile(r"^### 1\.2 In plain language\s*$"),
     "### 1.2 In plain language"),
    ("N2", re.compile(r"^### 2\.1 .*\banalog(y|ies)\b", re.IGNORECASE),
     "### 2.1 The analogy, and where it breaks"),
    ("N3", re.compile(r"^### 2\.2 Why\b", re.IGNORECASE),
     "### 2.2 Why this component must exist"),
    ("N4", re.compile(r"^\*\*Terms introduced in this chapter\*\*\s*$"),
     "**Terms introduced in this chapter** (tail of section 16)"),
)

RE_HEADER_LEVEL = re.compile(r"^\s*Level (\d+) . Chapter (\d+)\s*$")
RE_HEADER_DIAGRAMS = re.compile(r"^\s*Diagrams\s+(Light|Core|Full) \((\d+)\)\s*$")
RE_HEADER_REQUIRES = re.compile(r"^\s*Requires\s+(.*)$")
RE_HEADER_UNLOCKS = re.compile(r"^\s*Unlocks\s+(.*)$")
RE_HEADER_VARIANT = re.compile(r"^\s*Variant\s+(.*)$")
RE_CHAPTER_REF = re.compile(r"\bC(\d+)\b")
RE_SECTION = re.compile(r"^## (\d+)\. (.+?)\s*$")
RE_SUBSECTION = re.compile(r"^### (\d+)\.(\d+) (.+?)\s*$")
RE_FIGURE = re.compile(r"^\s*Figure (\d+)\.(\d+) -- (.+?)\s*$")
RE_FIGURE_TYPE = re.compile(r"\((?:D[1-9]\b[^)]*|conceptual)\)\s*$")
RE_TAG = re.compile(r"\[([A-Z]{2,4})\]")
RE_XREF_CHAPTER = re.compile(r"\b(?:Ch|Chapter) (\d+)\b")
RE_XREF_APPENDIX = re.compile(r"\bAppendix ([A-Z])\b")
RE_XREF_INTERLUDE = re.compile(r"\bInterlude ([IVX]+)\b")
RE_NEXT_LINE = re.compile(r"^\*\*Next:\*\*\s+Chapter (\d+)\b")
RE_LINT_OK = re.compile(r"<!--\s*lint-ok\b")

# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------


@dataclass
class Fence:
    start: int          # 1-indexed line of the opening fence
    end: int            # 1-indexed line of the closing fence
    language: str
    lines: list[str]

    @property
    def figures(self) -> list[tuple[int, str]]:
        """Figure captions, each joined with its continuation lines.

        A caption may wrap; Chapters 0, 1, and 4 all carry the diagram type on a
        second, indented line. Continuation stops at a blank line or the next
        caption.
        """
        found: list[tuple[int, str]] = []
        for offset, line in enumerate(self.lines):
            if not RE_FIGURE.match(line):
                continue
            parts = [line.strip()]
            for follow in self.lines[offset + 1:]:
                if not follow.strip() or RE_FIGURE.match(follow):
                    break
                parts.append(follow.strip())
            found.append((self.start + 1 + offset, " ".join(parts)))
        return found


@dataclass
class Finding:
    level: str          # "error" or "warning"
    line: int
    check: str
    message: str


@dataclass
class Chapter:
    path: str
    lines: list[str]
    fences: list[Fence] = field(default_factory=list)
    sections: list[tuple[int, int, str]] = field(default_factory=list)
    subsections: list[tuple[int, int, int, str]] = field(default_factory=list)
    number: int | None = None
    level: int | None = None
    tier: str | None = None
    declared_figures: int | None = None
    variant: str | None = None
    requires: list[int] = field(default_factory=list)
    unlocks: list[int] = field(default_factory=list)

    @property
    def is_foundational(self) -> bool:
        """Phase 1 section 1.3: in Ch 0-3, sections 4-9 describe models, not
        components, so their titles are chapter-specific by design."""
        return bool(self.variant and "foundational" in self.variant.lower())

    @property
    def header(self) -> Fence | None:
        return self.fences[0] if self.fences else None

    @property
    def prose_lines(self) -> list[tuple[int, str]]:
        """Lines outside every fenced block, 1-indexed."""
        inside = set()
        for fence in self.fences:
            inside.update(range(fence.start, fence.end + 1))
        return [(i, l) for i, l in enumerate(self.lines, 1) if i not in inside]

    @property
    def diagram_fences(self) -> list[Fence]:
        """Unlabelled fences carrying a Figure caption, excluding the header."""
        return [f for f in self.fences[1:] if f.language == "" and f.figures]

    @property
    def illustrative_fences(self) -> list[Fence]:
        return [f for f in self.fences[1:] if f.language == "" and not f.figures]


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------


def parse(path: str) -> Chapter:
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    chapter = Chapter(path=path, lines=lines)

    open_at: int | None = None
    language = ""
    body: list[str] = []

    for index, line in enumerate(lines, 1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        is_fence = stripped.startswith("```") and indent <= 3

        if is_fence:
            if open_at is None:
                open_at = index
                language = stripped[3:].strip()
                body = []
            else:
                chapter.fences.append(Fence(open_at, index, language, body))
                open_at = None
            continue

        if open_at is not None:
            body.append(line)
            continue

        section = RE_SECTION.match(line)
        if section:
            chapter.sections.append((index, int(section.group(1)), section.group(2)))
            continue

        subsection = RE_SUBSECTION.match(line)
        if subsection:
            chapter.subsections.append(
                (index, int(subsection.group(1)), int(subsection.group(2)),
                 subsection.group(3))
            )

    if open_at is not None:
        chapter.fences.append(Fence(open_at, len(lines), language, body))

    header = chapter.header
    if header:
        for line in header.lines:
            match = RE_HEADER_LEVEL.match(line)
            if match:
                chapter.level = int(match.group(1))
                chapter.number = int(match.group(2))
            match = RE_HEADER_DIAGRAMS.match(line)
            if match:
                chapter.tier = match.group(1)
                chapter.declared_figures = int(match.group(2))
            match = RE_HEADER_REQUIRES.match(line)
            if match:
                chapter.requires += [int(n) for n in RE_CHAPTER_REF.findall(match.group(1))]
            match = RE_HEADER_UNLOCKS.match(line)
            if match:
                chapter.unlocks += [int(n) for n in RE_CHAPTER_REF.findall(match.group(1))]
            match = RE_HEADER_VARIANT.match(line)
            if match:
                chapter.variant = match.group(1).strip()

    return chapter


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def check_fences_balanced(ch: Chapter) -> list[Finding]:
    opens = sum(
        1 for l in ch.lines
        if l.lstrip().startswith("```") and (len(l) - len(l.lstrip())) <= 3
    )
    if opens % 2:
        return [Finding("error", 0, "fences",
                        f"odd number of fence markers ({opens}); a block is unclosed")]
    return []


def check_header(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    header = ch.header
    if header is None or header.start != 1:
        return [Finding("error", 1, "header",
                        "chapter must open with an unlabelled header block on line 1")]
    if ch.number is None:
        out.append(Finding("error", header.start, "header",
                           "header is missing a 'Level N . Chapter NN' line"))
    if ch.tier is None:
        out.append(Finding("error", header.start, "header",
                           "header is missing a 'Diagrams Tier (N)' line"))

    stem = ch.path.split("/")[-1].split("-")[0]
    if ch.number is not None and stem.isdigit() and int(stem) != ch.number:
        out.append(Finding("error", header.start, "header",
                           f"filename says chapter {int(stem)}, header says {ch.number}"))

    if ch.number is not None:
        for req in ch.requires:
            if req >= ch.number:
                out.append(Finding("error", header.start, "spine",
                                   f"Requires C{req}, which does not precede "
                                   f"C{ch.number}"))
        for unlock in ch.unlocks:
            if unlock <= ch.number:
                out.append(Finding("error", header.start, "spine",
                                   f"Unlocks C{unlock}, which does not follow "
                                   f"C{ch.number}"))
        for ref in ch.requires + ch.unlocks:
            if ref > LAST_CHAPTER:
                out.append(Finding("error", header.start, "spine",
                                   f"header references C{ref}; the book ends at "
                                   f"C{LAST_CHAPTER}"))
    return out


def check_sections(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    numbers = [n for _, n, _ in ch.sections]
    if numbers != list(range(1, 17)):
        out.append(Finding("error", 0, "template",
                           f"expected 16 top-level sections numbered 1-16, found "
                           f"{numbers or 'none'}"))
        return out
    for line_no, number, title in ch.sections:
        if ch.is_foundational and 4 <= number <= 9:
            continue
        stems = SECTION_STEMS.get(number)
        if stems and not any(title.startswith(s) for s in stems):
            out.append(Finding("error", line_no, "template",
                               f"section {number} is '{title}'; expected it to start "
                               f"with one of {list(stems)}"))
    return out


def check_onramp(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    prose = "\n".join(l for _, l in ch.prose_lines)
    for name, pattern, expected in ONRAMP_BLOCKS:
        if not any(pattern.match(line) for line in prose.split("\n")):
            out.append(Finding("error", 0, "on-ramp",
                               f"missing on-ramp block {name}: expected '{expected}'"))
    return out


def check_figures(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    figures = [(line_no, text) for f in ch.diagram_fences for line_no, text in f.figures]

    if ch.declared_figures is not None and len(figures) != ch.declared_figures:
        out.append(Finding("error", 1, "figures",
                           f"header declares {ch.declared_figures} diagrams, found "
                           f"{len(figures)} Figure captions"))

    if ch.tier and ch.tier in TIER_FIGURE_COUNT:
        required = TIER_FIGURE_COUNT[ch.tier]
        if required is not None and ch.declared_figures != required:
            out.append(Finding("error", 1, "figures",
                               f"tier {ch.tier} requires exactly {required} diagrams, "
                               f"header declares {ch.declared_figures}"))

    seen: set[tuple[int, int]] = set()
    for line_no, text in figures:
        match = RE_FIGURE.match(text)
        assert match
        chapter_no, figure_no = int(match.group(1)), int(match.group(2))
        if ch.number is not None and chapter_no != ch.number:
            out.append(Finding("error", line_no, "figures",
                               f"caption reads 'Figure {chapter_no}.{figure_no}' in "
                               f"chapter {ch.number}"))
        if (chapter_no, figure_no) in seen:
            out.append(Finding("error", line_no, "figures",
                               f"duplicate caption number {chapter_no}.{figure_no}"))
        seen.add((chapter_no, figure_no))
        if not RE_FIGURE_TYPE.search(text):
            out.append(Finding("error", line_no, "figures",
                               "caption must end with a diagram type, e.g. "
                               "'(D1 High-Level Architecture)'"))

    for fence in ch.diagram_fences:
        if not any(any(axis in line for axis in AXIS_LABELS) for line in fence.lines):
            out.append(Finding("error", fence.start, "figures",
                               "diagram has no axis label; add LAYER VIEW, TIME VIEW, "
                               "or STATE VIEW"))
    return out


def check_diagram_rendering(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    for fence in ch.diagram_fences + ch.illustrative_fences:
        for offset, line in enumerate(fence.lines):
            line_no = fence.start + 1 + offset
            if len(line) > DIAGRAM_MAX_COLUMNS:
                out.append(Finding("error", line_no, "diagram",
                                   f"line is {len(line)} columns; the limit is "
                                   f"{DIAGRAM_MAX_COLUMNS}"))
            if any(ord(c) > 127 for c in line):
                bad = sorted({c for c in line if ord(c) > 127})
                out.append(Finding("error", line_no, "diagram",
                                   f"non-ASCII character(s) {bad} in a diagram; "
                                   f"Appendix C requires 7-bit ASCII"))
    return out


def check_fence_languages(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    for fence in ch.fences[1:]:
        if fence.language and fence.language not in KNOWN_FENCE_LANGUAGES:
            out.append(Finding("error", fence.start, "fences",
                               f"unknown fence language '{fence.language}'; expected "
                               f"one of {sorted(KNOWN_FENCE_LANGUAGES)}"))
    return out


def check_prose_script(ch: Chapter) -> list[Finding]:
    """Catch non-Latin script in prose.

    Prose legitimately contains em dashes, section marks, and accented
    Latin, so a blanket ASCII rule (which diagrams do get) is wrong here.
    But CJK, Cyrillic, Arabic, and similar have no place in an English
    handbook, and they arrive as generation artifacts that read as
    plausible until someone greps. Found in Ch 17 after it was written.
    """
    out: list[Finding] = []
    for line_no, line in ch.prose_lines:
        stray = sorted({c for c in line if any(
            start <= ord(c) <= end for start, end in FOREIGN_SCRIPT_RANGES
        )})
        if stray:
            out.append(Finding("error", line_no, "script",
                               f"non-Latin script character(s) {stray} in prose"))
    return out


def check_prohibited_words(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    for line_no, line in ch.prose_lines:
        if RE_LINT_OK.search(line) or line.lstrip().startswith(">"):
            continue
        # Quoted or code-spanned text is diagnosis, not use.
        scrubbed = re.sub(r'"[^"]*"', "", line)
        scrubbed = re.sub(r"`[^`]*`", "", scrubbed)
        scrubbed = re.sub(r"\*[^*]+\*", "", scrubbed)
        lowered = scrubbed.lower()
        for word, advice in PROHIBITED_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", lowered):
                out.append(Finding("error", line_no, "vocabulary",
                                   f"prohibited word '{word}': {advice}"))
        # Phase 1 section 7.6 bans "the agent" only when it names a system
        # component. Narrative history, quoted user speech, and named
        # misconceptions are legitimate, so this needs a human and is a warning.
        if re.search(r"\bthe agents?\b", lowered):
            out.append(Finding("warning", line_no, "vocabulary",
                               '"the agent": confirm this is not naming a system '
                               "component (use Run, Episode, Planner, Activity Runner)"))
    return out


def check_provenance(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    found: set[str] = set()
    for line_no, line in ch.prose_lines:
        for tag in RE_TAG.findall(line):
            if tag in PROVENANCE_TAGS:
                found.add(tag)
            elif tag.isupper() and len(tag) <= 4 and tag not in {"TODO", "NOTE"}:
                out.append(Finding("error", line_no, "provenance",
                                   f"unknown provenance tag [{tag}]; valid tags are "
                                   f"{sorted(PROVENANCE_TAGS)}"))
    for required in ("AHE", "DAR", "INF"):
        if required not in found:
            out.append(Finding("warning", 0, "provenance",
                               f"no [{required}] claim in this chapter; check that "
                               f"provenance is being recorded"))
    return out


def check_cross_references(ch: Chapter) -> list[Finding]:
    out: list[Finding] = []
    for line_no, line in ch.prose_lines:
        for number in RE_XREF_CHAPTER.findall(line):
            if int(number) > LAST_CHAPTER:
                out.append(Finding("error", line_no, "xref",
                                   f"reference to Chapter {number}; the book ends at "
                                   f"{LAST_CHAPTER}"))
        for letter in RE_XREF_APPENDIX.findall(line):
            if letter > "J":
                out.append(Finding("error", line_no, "xref",
                                   f"reference to Appendix {letter}; appendices run A-J"))
        for numeral in RE_XREF_INTERLUDE.findall(line):
            if numeral not in {"I", "II"}:
                out.append(Finding("error", line_no, "xref",
                                   f"reference to Interlude {numeral}; there are two"))
    return out


def check_handoff(ch: Chapter) -> list[Finding]:
    tail = [l for _, l in ch.prose_lines if l.strip()]
    for line in reversed(tail):
        match = RE_NEXT_LINE.match(line)
        if match:
            if ch.number is not None and ch.number < LAST_CHAPTER:
                nxt = int(match.group(1))
                if nxt != ch.number + 1:
                    return [Finding("error", 0, "handoff",
                                    f"hand-off names Chapter {nxt}; expected "
                                    f"{ch.number + 1}")]
            return []
        if line.startswith("**Next:**") or line.startswith("**Level"):
            return []
    if ch.number == LAST_CHAPTER:
        return []
    return [Finding("error", 0, "handoff",
                    "chapter does not end with a '**Next:** Chapter NN' hand-off")]


def check_cold_open(ch: Chapter) -> list[Finding]:
    start = None
    end = len(ch.lines)
    for line_no, section, sub, title in ch.subsections:
        if (section, sub) == (1, 1):
            if "cold open" not in title.lower():
                return [Finding("error", line_no, "cold-open",
                                f"section 1.1 is '{title}'; expected 'Cold open'")]
            start = line_no
        elif start is not None and line_no > start:
            end = line_no
            break
    if start is None:
        return [Finding("error", 0, "cold-open", "no '### 1.1 Cold open' subsection")]
    words = len(" ".join(ch.lines[start:end - 1]).split())
    if words > COLD_OPEN_MAX_WORDS:
        return [Finding("warning", start, "cold-open",
                        f"cold open is {words} words; the convention is under "
                        f"{COLD_OPEN_MAX_WORDS}")]
    return []


def check_word_count(ch: Chapter) -> list[Finding]:
    # Prose only. Counting diagrams, tables, and code would penalise a chapter
    # for carrying more of them, which is the opposite of the intent: the band
    # exists to stop the PROSE becoming an essay.
    words = len(" ".join(l for _, l in ch.prose_lines).split())
    band = TIER_WORD_BAND.get(ch.tier or "")
    if not band:
        return []
    low, high = band
    if not low <= words <= high:
        return [Finding("warning", 0, "length",
                        f"{words} words; the {ch.tier} band is {low}-{high}")]
    return []


CHECKS = (
    check_fences_balanced,
    check_header,
    check_sections,
    check_onramp,
    check_figures,
    check_diagram_rendering,
    check_fence_languages,
    check_prose_script,
    check_prohibited_words,
    check_provenance,
    check_cross_references,
    check_handoff,
    check_cold_open,
    check_word_count,
)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def lint(path: str) -> list[Finding]:
    chapter = parse(path)
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(chapter))
    return sorted(findings, key=lambda f: (f.line, f.check))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*",
                        default=sorted(glob.glob("docs/handbook/chapters/*.md")))
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args()

    paths = args.paths or sorted(glob.glob("docs/handbook/chapters/*.md"))
    if not paths:
        print("no chapters found", file=sys.stderr)
        return 1

    total_errors = 0
    total_warnings = 0

    for path in paths:
        findings = lint(path)
        errors = [f for f in findings if f.level == "error"]
        warnings = [f for f in findings if f.level == "warning"]
        total_errors += len(errors)
        total_warnings += len(warnings)

        name = path.split("/")[-1]
        if not findings:
            print(f"  ok    {name}")
            continue
        print(f"  {'FAIL ' if errors else 'warn '} {name}")
        for finding in findings:
            where = f"{path}:{finding.line}" if finding.line else path
            print(f"        {finding.level:<7} {finding.check:<12} {where}")
            print(f"                {finding.message}")

    print()
    print(f"{len(paths)} chapter(s): {total_errors} error(s), "
          f"{total_warnings} warning(s)")

    if total_errors or (args.warnings_as_errors and total_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
