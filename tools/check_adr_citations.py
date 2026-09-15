#!/usr/bin/env python3
"""Fail if an ADR's ## Source field cites a section that does not exist.

Architecture Gate 01 (2026-09-15) found ADR-0012 citing "§13.1, §13.2" of a
document whose sections run §0-§10. A citation to an ABSENT document is
honestly unverifiable; a citation to a READABLE document that does not contain
the cited section looks checkable and silently is not. Only the second kind is
catchable mechanically, so this catches it.

Scope: the ## Source field only. The `Date / context` field is ATTRIBUTION --
when and in what setting a decision was taken -- and is not required to resolve
to a file. Conflating the two is what produced the overstated finding that
ADR-0032 supersedes. See docs/project/19-recovered-architecture-evidence.md
section 1.2.

Blockquote lines inside ## Source are commentary about a citation (for example,
a correction note quoting the citation it replaces) and are not themselves
citations, so they are excluded.

Exit 1 on any unresolved citation, 0 otherwise. Reports; never rewrites.

Known limitation, and it matters: this script's own first version reported five
failures, four of which were its bug -- the .docx heading parser required
"15 Title" where the source writes "15. Title". A provenance checker is itself
an artifact with a provenance problem. Verify a finding by hand before acting
on it.
"""
from __future__ import annotations

import os
import re
import sys
import glob
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECISIONS = os.path.join(ROOT, "docs", "project", "decisions")

# "## 5. Design principles" -> 5 ; "### 5.1 The two..." -> 5.1 ; "## 7a. ..." -> 7a
MD_HEADING = re.compile(r"^#+\s+([0-9]+[0-9a-z.]*?)\.?\s")
# "17.3 Per-table specification" and "15. Memory Write Architecture"
DOCX_HEADING = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)*)[.]?\s+\S")
SOURCE_FIELD = re.compile(r"^## Source\s*\n(.*?)(?=^## |\Z)", re.S | re.M)
CITED_PATH = re.compile(r"`([^`]+\.(?:md|docx))`([^`]*)")
SECTION_REF = re.compile(r"§([0-9]+(?:\.[0-9]+)*)")


def sections_of_md(path: str) -> set[str]:
    out = set()
    with open(path, encoding="utf8", errors="replace") as fh:
        for line in fh:
            m = MD_HEADING.match(line)
            if m:
                out.add(m.group(1).rstrip("."))
    return out


def sections_of_docx(path: str) -> set[str] | None:
    try:
        xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf8", "replace")
    except Exception:
        return None
    text = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    return {m.group(1) for m in (DOCX_HEADING.match(l) for l in text.split("\n")) if m}


def resolve(target: str) -> str | None:
    for base in (DECISIONS, ROOT, os.path.join(ROOT, "docs", "project")):
        candidate = os.path.normpath(os.path.join(base, target))
        if os.path.exists(candidate):
            return candidate
    return None


def main() -> int:
    findings, checked = [], 0

    for path in sorted(glob.glob(os.path.join(DECISIONS, "ADR-*.md"))):
        adr = os.path.basename(path)[:8]
        body = open(path, encoding="utf8").read()
        field = SOURCE_FIELD.search(body)
        if not field:
            findings.append((adr, "-", "no ## Source field"))
            continue

        # Commentary, not citation.
        src = "\n".join(
            line for line in field.group(1).split("\n")
            if not line.lstrip().startswith(">")
        )

        for match in CITED_PATH.finditer(src):
            target, tail = match.group(1), match.group(2)
            cited = SECTION_REF.findall(tail)
            if not cited:
                continue
            checked += 1

            real = resolve(target)
            if real is None:
                findings.append((adr, target, "file not found"))
                continue

            sections = (sections_of_docx(real) if real.endswith(".docx")
                        else sections_of_md(real))
            if sections is None:
                findings.append((adr, target, "unreadable"))
                continue

            missing = [c for c in cited if c not in sections]
            if missing:
                findings.append(
                    (adr, os.path.basename(target),
                     "unresolved: " + ", ".join("§" + m for m in missing))
                )

    for adr, target, why in findings:
        print(f"{adr}  {target}\n    {why}")

    print(f"\n{checked} citation group(s) checked, {len(findings)} unresolved")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
