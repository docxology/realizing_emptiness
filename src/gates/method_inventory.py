"""Method inventory over ``src/`` built from AST scanning."""

from __future__ import annotations

import ast
from pathlib import Path


def collect_entries(project_root: Path) -> list[dict[str, str | int]]:
    entries = []
    for path in sorted((project_root / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                entries.append(
                    {
                        "path": str(path.relative_to(project_root)),
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
