"""Usage:
    poetry run python scripts/zh_cn/sync_zh_catalog.py \
        translations/english.po \
        translations/locales/zh/LC_MESSAGES/futurecoder.po

    poetry run python scripts/zh_cn/sync_zh_catalog.py \
        translations/english.po \
        translations/locales/zh/LC_MESSAGES/futurecoder.po \
        --fill-missing-with-source \
        --report translations/zh_missing_report.txt

Synchronize the Simplified Chinese gettext catalog with the current source catalog.

Details:
    futurecoder uses stable key-based msgids. The generated `translations/english.po`
    therefore acts as the current source catalog: its `msgid` is the translation key
    and its `msgstr` is the current English source text.

    This script compares that generated catalog with the Chinese PO file. Missing
    entries can be copied into the Chinese catalog as temporary English fallbacks so
    that local builds continue to work. Every copied entry receives an
    `AUTO-FALLBACK` translator comment and is listed in a report for later translation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import polib

AUTO_FALLBACK_MARKER = (
    "AUTO-FALLBACK: copied from the current English source catalog; "
    "translate this entry into Simplified Chinese."
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Synchronize futurecoder's Chinese PO catalog with english.po."
    )
    parser.add_argument("reference_po", type=Path, help="Generated translations/english.po")
    parser.add_argument("zh_po", type=Path, help="Chinese futurecoder.po")
    parser.add_argument(
        "--fill-missing-with-source",
        action="store_true",
        help=(
            "Add missing entries using their English source text as a temporary "
            "runtime fallback."
        ),
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional text report containing all missing keys and English source text.",
    )
    return parser.parse_args()


def load_po(path: Path) -> polib.POFile:
    """Load one PO file with a clear error if it is unavailable or malformed.

    Args:
        path: PO file path.

    Returns:
        Parsed PO file.

    Raises:
        FileNotFoundError: If the path does not exist.
        OSError: If the file cannot be read.
        ValueError: If polib cannot parse the file.
    """

    if not path.exists():
        raise FileNotFoundError(path)
    return polib.pofile(str(path))


def active_entries(po: polib.POFile) -> list[polib.POEntry]:
    """Return non-obsolete entries that have a msgid.

    Args:
        po: Parsed PO catalog.

    Returns:
        Active PO entries.
    """

    return [entry for entry in po if entry.msgid and not entry.obsolete]


def add_marker(entry: polib.POEntry) -> None:
    """Attach the auto-fallback marker without duplicating it.

    Args:
        entry: Chinese PO entry being updated.
    """

    comments = [line for line in (entry.tcomment or "").splitlines() if line]
    if AUTO_FALLBACK_MARKER not in comments:
        comments.append(AUTO_FALLBACK_MARKER)
    entry.tcomment = "\n".join(comments)


def create_fallback_entry(reference: polib.POEntry) -> polib.POEntry:
    """Create a Chinese-catalog entry containing temporary English fallback text.

    Args:
        reference: Entry from the generated English source catalog.

    Returns:
        New PO entry suitable for appending to the Chinese catalog.
    """

    entry = polib.POEntry(
        msgid=reference.msgid,
        msgstr=reference.msgstr,
        comment=reference.comment,
        occurrences=list(reference.occurrences),
        flags=list(reference.flags),
    )
    add_marker(entry)
    return entry


def build_report(missing: list[polib.POEntry]) -> str:
    """Build a readable report for untranslated source-catalog entries.

    Args:
        missing: Missing entries from the generated English catalog.

    Returns:
        Human-readable report text.
    """

    lines = [
        "futurecoder Simplified Chinese missing-entry report",
        f"Missing entries: {len(missing)}",
        "",
    ]
    for index, entry in enumerate(missing, start=1):
        lines.extend(
            [
                f"[{index}] {entry.msgid}",
                "English source:",
                entry.msgstr,
                "",
                "-" * 80,
                "",
            ]
        )
    return "\n".join(lines)


def synchronize(
    reference: polib.POFile,
    zh: polib.POFile,
    fill_missing_with_source: bool,
) -> list[polib.POEntry]:
    """Find missing keys and optionally add temporary English fallback entries.

    Args:
        reference: Current generated English source catalog.
        zh: Simplified Chinese catalog to inspect and possibly update.
        fill_missing_with_source: Whether to add English fallback entries.

    Returns:
        Reference entries missing from the Chinese catalog before synchronization.
    """

    zh_by_msgid = {entry.msgid: entry for entry in active_entries(zh)}
    missing: list[polib.POEntry] = []

    for reference_entry in active_entries(reference):
        zh_entry = zh_by_msgid.get(reference_entry.msgid)
        if zh_entry is not None and zh_entry.msgstr:
            continue

        missing.append(reference_entry)
        if not fill_missing_with_source:
            continue

        if zh_entry is None:
            zh_entry = create_fallback_entry(reference_entry)
            zh.append(zh_entry)
            zh_by_msgid[zh_entry.msgid] = zh_entry
        else:
            zh_entry.msgstr = reference_entry.msgstr
            zh_entry.comment = reference_entry.comment
            add_marker(zh_entry)

    if fill_missing_with_source and missing:
        zh.sort(key=lambda entry: entry.msgid)

    return missing


def main() -> int:
    """Synchronize catalogs, write a report, and return a process exit code.

    Returns:
        Zero when catalogs are synchronized or fallback filling was requested;
        one when untranslated keys remain and no filling mode was enabled.
    """

    args = parse_args()

    try:
        reference = load_po(args.reference_po)
        zh = load_po(args.zh_po)
    except Exception as exc:  # noqa: BLE001 - print the concrete catalog error.
        print(f"ERROR: failed to load PO catalog: {exc}", file=sys.stderr)
        return 1

    missing = synchronize(reference, zh, args.fill_missing_with_source)
    reference_ids = {entry.msgid for entry in active_entries(reference)}
    zh_ids = {entry.msgid for entry in active_entries(zh)}
    extra = sorted(zh_ids - reference_ids)

    print("Catalog synchronization summary:")
    print(f"  current source entries : {len(reference_ids)}")
    print(f"  Chinese catalog entries: {len(zh_ids)}")
    print(f"  missing before sync    : {len(missing)}")
    print(f"  Chinese-only entries   : {len(extra)}")

    report_text = build_report(missing)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report_text, encoding="utf-8")
        print(f"  missing-entry report   : {args.report}")

    if missing:
        print()
        print("Missing translation keys:")
        for entry in missing:
            print(f"  - {entry.msgid}")

    if args.fill_missing_with_source and missing:
        zh.save(str(args.zh_po))
        print()
        print(f"Added {len(missing)} temporary English fallback entries to: {args.zh_po}")
        print("Translate entries marked AUTO-FALLBACK after the local build is verified.")
        return 0

    if missing:
        print(
            "ERROR: the Chinese catalog is older than the current source catalog.",
            file=sys.stderr,
        )
        return 1

    print("Chinese catalog is synchronized with the current source catalog.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
