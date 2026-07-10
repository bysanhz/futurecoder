"""Usage:
    python scripts/zh_cn/check_po_placeholders.py translations/locales/zh/LC_MESSAGES/futurecoder.po

Check the Simplified Chinese gettext PO file for high-risk placeholder mistakes.

This script is intentionally lightweight and does not require project startup. It uses
`polib`, which is already listed as a development dependency in pyproject.toml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import polib

SPECIAL_RE = re.compile(r"__\w+__")
BRACE_RE = re.compile(r"\{[^{}]+\}")
INLINE_CODE_RE = re.compile(r"`[^`]+`")


def tokens(text: str, pattern: re.Pattern[str]) -> list[str]:
    """Return sorted tokens matched by pattern.

    Details:
        Duplicate tokens are preserved because repeated placeholders can matter.

    Args:
        text: Text to inspect.
        pattern: Compiled regular expression.

    Returns:
        A sorted list of matched token strings.
    """
    return sorted(pattern.findall(text or ""))


def check_entry(entry: polib.POEntry) -> list[str]:
    """Check one PO entry for placeholder mismatches.

    Details:
        The checks focus on placeholders that commonly break futurecoder runtime
        translation checks: __special__ strings and Python/format placeholders.
        Inline-code mismatches are reported as warnings because Chinese sentences may
        legitimately move or add inline explanations, but they should still be reviewed.

    Args:
        entry: A polib POEntry.

    Returns:
        A list of human-readable issue messages.
    """
    if entry.obsolete or not entry.msgstr:
        return []

    issues: list[str] = []
    pairs = [
        ("special", SPECIAL_RE, True),
        ("brace", BRACE_RE, True),
        ("inline-code", INLINE_CODE_RE, False),
    ]
    for name, pattern, strict in pairs:
        src = tokens(entry.msgid, pattern)
        dst = tokens(entry.msgstr, pattern)
        if src != dst:
            level = "ERROR" if strict else "WARN"
            issues.append(
                f"{level} {name} mismatch at {entry.linenum}:\n"
                f"  msgid tokens : {src}\n"
                f"  msgstr tokens: {dst}\n"
                f"  msgid       : {entry.msgid[:120]!r}"
            )
    return issues


def main() -> int:
    """Run the checker.

    Returns:
        Process exit code. 0 means no strict errors; 1 means at least one strict
        placeholder error was found.
    """
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2

    po_path = Path(sys.argv[1])
    po = polib.pofile(str(po_path))
    all_issues: list[str] = []
    strict_error = False

    for entry in po:
        issues = check_entry(entry)
        all_issues.extend(issues)
        if any(issue.startswith("ERROR") for issue in issues):
            strict_error = True

    if all_issues:
        print("\n\n".join(all_issues))
    else:
        print(f"OK: no placeholder issues found in {po_path}")

    return 1 if strict_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
