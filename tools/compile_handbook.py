#!/usr/bin/env python3
"""Compile the handbook into a single DOCX reading edition.

Phase 3 §5, batch 6: "Compiled DOCX v1.0 -- regenerated from Markdown, replacing
the v0.8 draft." The v0.8 draft carried the two blueprints plus Chapters 0-7,
which was the right shape when that was all there was. v1.0 is the book.

Assembly order is the reading order, not the file order:

    front matter F.1-F.4
    level opener, then its chapters, for each of the six levels
    interludes at their designated positions (after Ch 20 and Ch 41)
    appendices A-J

The Markdown stays canonical. This produces a reading artefact and nothing
depends on it, which is deliberate -- a compiled edition that something imports
is a compiled edition that has to be correct rather than merely current.

Requires pandoc. Usage:

    python3 tools/compile_handbook.py
    python3 tools/compile_handbook.py --markdown-only   # emit the merged .md
"""

from __future__ import annotations

import argparse
import glob
import re
import shutil
import subprocess
import sys
import tempfile

OUTPUT = ("docs/handbook/compiled/"
          "next-generation-autonomous-ai-agent-architecture-handbook.docx")
VERSION = "1.0"

FRONT_MATTER = sorted(glob.glob("docs/handbook/front-matter/*.md"))
APPENDICES = sorted(glob.glob("docs/handbook/appendices/*.md"))
INTERLUDES = {
    20: "docs/handbook/interludes/interlude-1-assembling-a-minimal-runtime.md",
    41: "docs/handbook/interludes/interlude-2-anatomy-of-a-bad-week.md",
}
LEVEL_OPENERS = {
    0: "docs/handbook/levels/level-0-foundations.md",
    1: "docs/handbook/levels/level-1-high-level-runtime.md",
    2: "docs/handbook/levels/level-2-core-components.md",
    3: "docs/handbook/levels/level-3-advanced-runtime.md",
    4: "docs/handbook/levels/level-4-production.md",
    5: "docs/handbook/levels/level-5-self-evolving.md",
}

RE_HEADER_CHAPTER = re.compile(r"^\s*Level (\d+) . Chapter (\d+)\s*$")

TITLE_BLOCK = f"""---
title: "Next-Generation Autonomous AI Agent Architecture"
subtitle: "A handbook for building, operating, and evolving agent runtimes"
version: "{VERSION}"
---

"""


def chapter_level(path: str) -> tuple[int, int]:
    for line in open(path, encoding="utf-8").read().split("\n")[:14]:
        match = RE_HEADER_CHAPTER.match(line)
        if match:
            return int(match.group(1)), int(match.group(2))
    return (9, 99)


def read(path: str) -> str:
    text = open(path, encoding="utf-8").read().rstrip()
    # Relative links resolve inside the repository and mean nothing in a DOCX.
    # Strip the target, keep the text: a printed cross-reference is prose.
    text = re.sub(r"\[([^\]]+)\]\((?!http)[^)]+\)", r"\1", text)
    return text


def assemble() -> str:
    parts: list[str] = [TITLE_BLOCK]

    parts.append("# Front Matter\n")
    parts.extend(read(p) for p in FRONT_MATTER)

    chapters = sorted(
        ((chapter_level(p), p) for p in glob.glob("docs/handbook/chapters/*.md")),
        key=lambda item: item[0][1],
    )
    by_level: dict[int, list[str]] = {}
    for (level, _number), path in chapters:
        by_level.setdefault(level, []).append(path)

    for level in sorted(by_level):
        opener = LEVEL_OPENERS.get(level)
        if opener:
            parts.append(read(opener))
        for path in by_level[level]:
            parts.append(read(path))
            _, number = chapter_level(path)
            if number in INTERLUDES:
                parts.append(read(INTERLUDES[number]))

    parts.append("# Appendices\n")
    parts.extend(read(p) for p in APPENDICES)

    return "\n\n\\newpage\n\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown-only", action="store_true",
                        help="write the merged Markdown beside the DOCX and stop")
    args = parser.parse_args()

    merged = assemble()

    if args.markdown_only:
        target = OUTPUT.replace(".docx", ".md")
        open(target, "w", encoding="utf-8").write(merged)
        print(f"wrote {target}: {len(merged.splitlines())} lines")
        return 0

    if not shutil.which("pandoc"):
        print("pandoc not found; install it or use --markdown-only",
              file=sys.stderr)
        return 1

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as handle:
        handle.write(merged)
        source = handle.name

    result = subprocess.run(
        ["pandoc", source, "-o", OUTPUT,
         "--from", "markdown+pipe_tables+backtick_code_blocks",
         "--toc", "--toc-depth=2", "--standalone"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(f"wrote {OUTPUT} (v{VERSION}): "
          f"{len(merged.splitlines())} source lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
