#!/usr/bin/env python3
"""Generate HPNC.md — LLM-optimized context file from documentation sources.

Reads MkDocs English documentation and produces a single markdown file
optimized for AI agent consumption. No navigation artifacts, concise structure.

Usage:
    python scripts/generate_hpnc_md.py [output_path]

Default output: _hpnc/HPNC.md
"""

from __future__ import annotations

import sys
from pathlib import Path


def generate(docs_dir: Path, output: Path) -> None:
    """Generate HPNC.md from documentation sources.

    Args:
        docs_dir: Path to the English docs directory.
        output: Path to write the generated file.
    """
    sections: list[str] = []

    sections.append("# HPNC — Human-Planned Night Crew")
    sections.append("")
    sections.append("LLM-optimized context file. Generated from docs/en/.")
    sections.append("")

    # Read docs in logical order
    order = [
        "index.md",
        "getting-started.md",
        "concepts/night-policy.md",
        "concepts/story-format.md",
        "concepts/state-machine.md",
        "cli/init.md",
        "cli/validate.md",
        "cli/start.md",
        "cli/status.md",
        "cli/queue.md",
        "configuration/config-yaml.md",
        "configuration/frontmatter-schema.md",
        "troubleshooting.md",
    ]

    for filename in order:
        filepath = docs_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8").strip()
            sections.append(content)
            sections.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(sections), encoding="utf-8")
    print(f"Generated: {output} ({len(sections)} sections)")


def main() -> None:
    """Entry point."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs" / "en"
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else project_root / "_hpnc" / "HPNC.md"
    generate(docs_dir, output)


if __name__ == "__main__":
    main()
