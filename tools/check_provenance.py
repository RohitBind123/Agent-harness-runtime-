#!/usr/bin/env python3
"""Fail if retired external-provenance material reappears in the corpus.

The other two linters (check_handbook.py, check_xrefs.py) only reach
docs/handbook/. Every file this check exists for sits outside that tree, so
this one walks the whole repository, including .docx via zipfile.

Rules live in tools/provenance-denylist.txt — see that file for why.
Exit 1 on any finding, 0 otherwise. Reports; never rewrites.
"""
from __future__ import annotations

import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DENYLIST = Path(__file__).resolve().parent / "provenance-denylist.txt"

TEXT_SUFFIXES = {".md", ".svg", ".txt", ".py", ".yml", ".yaml", ".json"}
DOCX_SUFFIX = ".docx"
SKIP_DIRS = {".git", "__pycache__", "node_modules"}

# The denylist names the strings it forbids; it is the one file exempt from them.
EXEMPT = {DENYLIST.relative_to(ROOT).as_posix()}

RE_LINT_OK = re.compile(r"<!--\s*lint-ok\b")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


@dataclass(frozen=True)
class Rule:
    kind: str
    pattern: re.Pattern
    message: str


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    excerpt: str
    message: str


def load_rules(path: Path) -> list[Rule]:
    rules: list[Rule] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Patterns contain "|" themselves, so take the first field from the
        # left and the message from the right; everything between is the regex.
        if line.count("|") < 2:
            print(f"  FAIL  malformed denylist rule: {raw}", file=sys.stderr)
            raise SystemExit(2)
        kind, rest = line.split("|", 1)
        pattern, message = rest.rsplit("|", 1)
        kind, pattern, message = kind.strip(), pattern.strip(), message.strip()
        rules.append(Rule(kind, re.compile(pattern), message))
    return rules


def docx_lines(path: Path) -> list[str]:
    """Paragraph text from a .docx, so binaries are not a blind spot."""
    try:
        with zipfile.ZipFile(path) as z:
            xml = ET.fromstring(z.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, ET.ParseError):
        return []
    return [
        "".join(t.text or "" for t in para.iter(W + "t"))
        for para in xml.iter(W + "p")
    ]


def file_lines(path: Path) -> list[str]:
    if path.suffix.lower() == DOCX_SUFFIX:
        return docx_lines(path)
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def display_path(path: Path) -> str:
    """Repo-relative where possible; absolute for paths passed from outside it."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def scan(path: Path, rules: list[Rule]) -> list[Finding]:
    rel = display_path(path)
    if rel in EXEMPT:
        return []
    findings: list[Finding] = []
    for number, line in enumerate(file_lines(path), start=1):
        if RE_LINT_OK.search(line):
            continue
        for rule in rules:
            match = rule.pattern.search(line)
            if match:
                findings.append(
                    Finding(rel, number, rule.kind, match.group(0), rule.message)
                )
    return findings


def targets() -> list[Path]:
    found: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.suffix.lower() == DOCX_SUFFIX:
            found.append(path)
    return found


def main(argv: list[str]) -> int:
    rules = load_rules(DENYLIST)
    paths = [Path(a).resolve() for a in argv[1:]] or targets()

    findings: list[Finding] = []
    for path in paths:
        findings.extend(scan(path, rules))

    by_file: dict[str, list[Finding]] = {}
    for finding in findings:
        by_file.setdefault(finding.path, []).append(finding)

    for path in sorted(by_file):
        print(f"  FAIL  {path}")
        for finding in by_file[path]:
            print(f"          {finding.path}:{finding.line}  [{finding.kind}] "
                  f"{finding.excerpt!r}")
            print(f"          {finding.message}")

    print(f"\n{len(paths)} file(s): {len(findings)} provenance finding(s)")
    if findings:
        print("\nRetired external-provenance material must not return. See "
              "docs/project/decisions/ADR-0025-no-external-codebase-is-evidence.md")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
