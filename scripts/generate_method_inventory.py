#!/usr/bin/env python3
"""Generate or check a simple method inventory."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

from _bootstrap import PROJECT_ROOT


def collect_entries() -> list[dict[str, str | int]]:
    entries = []
    for path in sorted((PROJECT_ROOT / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                entries.append(
                    {
                        "path": str(path.relative_to(PROJECT_ROOT)),
                        "line": node.lineno,
                        "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                        "name": node.name,
                        "summary": (ast.get_docstring(node) or "No docstring.").splitlines()[0],
                    }
                )
    return sorted(entries, key=lambda row: (str(row["path"]), int(row["line"])))


def render(entries: list[dict[str, str | int]]) -> str:
    lines = [
        "# Method Inventory",
        "",
        "| Path | Line | Kind | Name | Summary |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in entries:
        lines.append(f"| {row['path']} | {row['line']} | {row['kind']} | `{row['name']}` | {row['summary']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = PROJECT_ROOT / "docs" / "method-inventory.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    text = render(collect_entries())
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != text:
            print("method inventory is stale")
            return 1
        print("Method inventory is current.")
        return 0
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

