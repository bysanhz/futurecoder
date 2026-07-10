"""Usage:
    python scripts/zh_cn/check_po_placeholders.py translations/locales/zh/LC_MESSAGES/futurecoder.po
    python scripts/zh_cn/check_po_placeholders.py translations/locales/zh/LC_MESSAGES/futurecoder.po --compile

Check the Simplified Chinese gettext PO file for high-risk translation mistakes.

Details:
    futurecoder uses key-based msgids such as
    `pages.AddingStrings.steps.final_text.text`, not English source text.
    Therefore this script must NOT compare placeholders in `msgid` against
    placeholders in `msgstr`. Doing so produces false positives because the
    placeholders live in the translated text and in generated code-block metadata.

    This script instead performs lightweight checks that are valid for this
    repository:

    - the PO file can be parsed by polib;
    - translations can optionally be compiled to a `.mo` file;
    - translation coverage is summarized;
    - suspicious special tokens such as misspelled `__program__` markers are
      reported;
    - Markdown inline-code backticks are balanced;
    - intentional fill-in-the-blank underscores such as `____________` are
      allowed and are not treated as futurecoder placeholders.

    The full runtime placeholder validation is still done by futurecoder itself
    when `core.translation.get(...)` receives both the default source text and
    the translated result.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import polib

# Match futurecoder-style special placeholders only when the token starts with
# a letter after the leading double underscore. This avoids false positives for
# exercise blanks such as `____________`.
SPECIAL_RE = re.compile(r"__[A-Za-z][A-Za-z0-9_]*__")
CODE_RE = re.compile(r"__code\d+__")

ALLOWED_SPECIAL_EXACT = {
    "__program__",
    "__program_indented__",
    "__copyable__",
    "__no_auto_translate__",
}

# A long underscore run can be a deliberate fill-in-the-blank marker. Keep this
# as a warning-only heuristic and ignore pure blank strings.
SUSPICIOUS_UNDERSCORE_RE = re.compile(r"_{3,}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Details:
        The default mode only checks the PO file. Use `--compile` to also write
        a `.mo` file next to the PO file.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Check futurecoder Chinese PO file.")
    parser.add_argument("po_file", type=Path, help="Path to futurecoder.po")
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile the PO file to futurecoder.mo after checks.",
    )
    return parser.parse_args()


def is_allowed_special(token: str) -> bool:
    """Return whether a special token is allowed in futurecoder translations.

    Args:
        token: Token matched by SPECIAL_RE, for example `__code0__`.

    Returns:
        True when the token is a known futurecoder placeholder.
    """

    return token in ALLOWED_SPECIAL_EXACT or bool(CODE_RE.fullmatch(token))


def is_blank_underscore_run(token: str) -> bool:
    """Return whether an underscore run is only a pedagogical blank.

    Args:
        token: Underscore run matched by SUSPICIOUS_UNDERSCORE_RE.

    Returns:
        True when the token contains only underscores and should be ignored.
    """

    return bool(token) and set(token) == {"_"}


def line_of_entry(entry: polib.POEntry) -> int:
    """Return a stable source line number for a PO entry.

    Args:
        entry: PO entry to inspect.

    Returns:
        The entry line number when available, otherwise 0.
    """

    return int(getattr(entry, "linenum", 0) or 0)


def check_entry(entry: polib.POEntry) -> list[str]:
    """Check one PO entry for local translation issues.

    Details:
        This intentionally does not compare msgid tokens with msgstr tokens,
        because futurecoder msgids are keys, not source strings.

    Args:
        entry: PO entry to inspect.

    Returns:
        A list of human-readable warning/error lines for this entry.
    """

    messages: list[str] = []
    text = entry.msgstr or ""
    line = line_of_entry(entry)
    label = f"line {line}: {entry.msgid}"

    if not text:
        return messages

    for token in sorted(set(SPECIAL_RE.findall(text))):
        if not is_allowed_special(token):
            messages.append(
                f"ERROR unknown special token at {label}\n"
                f"  token : {token}\n"
                f"  msgstr: {text[:180]!r}"
            )

    # Long underscore runs are often intentional fill-in-the-blank markers.
    # Warn only if the context suggests something more complex than a pure blank.
    for match in SUSPICIOUS_UNDERSCORE_RE.finditer(text):
        token = match.group(0)
        if is_blank_underscore_run(token):
            continue
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        context = text[start:end]
        if token.startswith("__") and token.endswith("__"):
            continue
        if "__no_auto_translate__" in context:
            continue
        messages.append(
            f"WARN suspicious underscore run at {label}\n"
            f"  context: {context!r}"
        )

    if text.count("`") % 2 != 0:
        messages.append(
            f"ERROR unbalanced markdown backticks at {label}\n"
            f"  msgstr: {text[:180]!r}"
        )

    return messages


def summarize(po: polib.POFile) -> str:
    """Return a translation coverage summary.

    Args:
        po: Parsed PO file.

    Returns:
        Multi-line human-readable summary text.
    """

    entries = [entry for entry in po if not entry.obsolete]
    translated = [entry for entry in entries if entry.msgstr]
    empty = [entry for entry in entries if not entry.msgstr]
    percent = (len(translated) / len(entries) * 100) if entries else 0.0

    return "\n".join(
        [
            "PO summary:",
            f"  total entries      : {len(entries)}",
            f"  translated entries : {len(translated)}",
            f"  empty entries      : {len(empty)}",
            f"  coverage           : {percent:.2f}%",
        ]
    )


def compile_mo(po: polib.POFile, po_path: Path) -> Path:
    """Compile a PO file to a sibling MO file.

    Args:
        po: Parsed PO file.
        po_path: Path to the source PO file.

    Returns:
        Path to the generated MO file.
    """

    mo_path = po_path.with_suffix(".mo")
    po.save_as_mofile(str(mo_path))
    return mo_path


def main() -> int:
    """Run checks and return a process exit code.

    Returns:
        0 if no errors were found, 1 otherwise.
    """

    args = parse_args()
    po_path = args.po_file

    if not po_path.exists():
        print(f"ERROR: file not found: {po_path}", file=sys.stderr)
        return 1

    try:
        po = polib.pofile(str(po_path))
    except Exception as exc:  # noqa: BLE001 - report parse errors directly.
        print(f"ERROR: failed to parse PO file: {exc}", file=sys.stderr)
        return 1

    print(summarize(po))
    print()

    problems: list[str] = []
    for entry in po:
        problems.extend(check_entry(entry))

    errors = [message for message in problems if message.startswith("ERROR")]
    warnings = [message for message in problems if message.startswith("WARN")]

    if warnings:
        print("Warnings:")
        for message in warnings:
            print(message)
            print()

    if errors:
        print("Errors:")
        for message in errors:
            print(message)
            print()
    else:
        print("No blocking placeholder errors found.")

    if args.compile:
        try:
            mo_path = compile_mo(po, po_path)
        except Exception as exc:  # noqa: BLE001 - report compile errors directly.
            print(f"ERROR: failed to compile MO file: {exc}", file=sys.stderr)
            return 1
        print(f"Compiled MO file: {mo_path}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
