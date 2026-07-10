"""Usage:
    poetry run python scripts/zh_cn/apply_bilingual_terms.py \
        translations/locales/zh/LC_MESSAGES/futurecoder.po

    poetry run python scripts/zh_cn/apply_bilingual_terms.py \
        translations/locales/zh/LC_MESSAGES/futurecoder.po \
        --check

    poetry run python scripts/zh_cn/apply_bilingual_terms.py \
        translations/locales/zh/LC_MESSAGES/futurecoder.po \
        --report translations/zh_bilingual_terms_report.txt

Normalize programming terminology in the Simplified Chinese gettext catalog.

Details:
    Every configured programming term is written in the mandatory form
    `中文术语（English term）` every time it appears in translated prose.

    The transformation is deliberately idempotent: running the script more than
    once does not duplicate English terms. Markdown inline code, fenced code,
    indented code blocks, and futurecoder special placeholders are preserved.

    The script only edits `msgstr` content. It never changes translation keys,
    source comments, Python code, or futurecoder placeholders.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import polib


@dataclass(frozen=True)
class TermRule:
    """Describe one mandatory bilingual programming term.

    Args:
        zh: Simplified Chinese term found in translated prose.
        en: Canonical English term shown in full-width parentheses.
        pattern: Optional regular expression used instead of the literal Chinese
            term. Custom patterns are used only where a short Chinese term could
            otherwise match an unrelated everyday word.
    """

    zh: str
    en: str
    pattern: str | None = None

    @property
    def canonical(self) -> str:
        """Return the required bilingual rendering for this term."""

        return f"{self.zh}（{self.en}）"

    @property
    def regex(self) -> re.Pattern[str]:
        """Return the compiled expression used to find the Chinese term."""

        return re.compile(self.pattern or re.escape(self.zh))


# Longer and more specific concepts are intentionally listed before their
# component words. Replacement uses temporary sentinels, so a term inserted by
# one rule cannot be modified again by a shorter rule.
TERM_RULES: tuple[TermRule, ...] = (
    TermRule("字符串字面量", "string literal"),
    TermRule("列表推导式", "list comprehension"),
    TermRule("字典推导式", "dictionary comprehension"),
    TermRule("集合推导式", "set comprehension"),
    TermRule("生成器表达式", "generator expression"),
    TermRule("上下文管理器", "context manager"),
    TermRule("可迭代对象", "iterable"),
    TermRule("异常处理", "exception handling"),
    TermRule("错误追踪信息", "traceback"),
    TermRule("交互式 Shell", "interactive shell"),
    TermRule("交互式 shell", "interactive shell"),
    TermRule("代码编辑器", "editor"),
    TermRule("数据结构", "data structure"),
    TermRule("数据类型", "data type"),
    TermRule("局部变量", "local variable"),
    TermRule("全局变量", "global variable"),
    TermRule("环境变量", "environment variable"),
    TermRule("变量名称", "variable name"),
    TermRule("变量名", "variable name"),
    TermRule("函数名称", "function name"),
    TermRule("函数名", "function name"),
    TermRule("类名称", "class name"),
    TermRule("类名", "class name"),
    TermRule("内置函数", "built-in function"),
    TermRule("高阶函数", "higher-order function"),
    TermRule("匿名函数", "lambda function"),
    TermRule("递归函数", "recursive function"),
    TermRule("返回语句", "return statement"),
    TermRule("返回值", "return value"),
    TermRule("默认参数", "default parameter"),
    TermRule("位置参数", "positional argument"),
    TermRule("关键字参数", "keyword argument"),
    TermRule("可变参数", "variadic parameter"),
    TermRule("命令行参数", "command-line argument"),
    TermRule("键值对", "key-value pair"),
    TermRule("默认值", "default value"),
    TermRule("初始值", "initial value"),
    TermRule("当前值", "current value"),
    TermRule("输入值", "input value"),
    TermRule("输出值", "output value"),
    TermRule("布尔值", "Boolean value"),
    TermRule("真值", "truth value"),
    TermRule("源代码", "source code"),
    TermRule("代码块", "code block"),
    TermRule("代码行", "line of code"),
    TermRule("测试用例", "test case"),
    TermRule("单元测试", "unit test"),
    TermRule("标准输入", "standard input"),
    TermRule("标准输出", "standard output"),
    TermRule("错误消息", "error message"),
    TermRule("错误信息", "error message"),
    TermRule("语法错误", "syntax error"),
    TermRule("运行时错误", "runtime error"),
    TermRule("类型错误", "type error"),
    TermRule("名称错误", "name error"),
    TermRule("索引错误", "index error"),
    TermRule("键错误", "key error"),
    TermRule("断言错误", "assertion error"),
    TermRule("逻辑运算符", "logical operator"),
    TermRule("布尔运算符", "Boolean operator"),
    TermRule("比较运算符", "comparison operator"),
    TermRule("算术运算符", "arithmetic operator"),
    TermRule("赋值运算符", "assignment operator"),
    TermRule("成员运算符", "membership operator"),
    TermRule("身份运算符", "identity operator"),
    TermRule("嵌套循环", "nested loop"),
    TermRule("无限循环", "infinite loop"),
    TermRule("for 循环", "for loop"),
    TermRule("while 循环", "while loop"),
    TermRule("循环变量", "loop variable"),
    TermRule("循环体", "loop body"),
    TermRule("条件语句", "conditional statement"),
    TermRule("赋值语句", "assignment statement"),
    TermRule("导入语句", "import statement"),
    TermRule("复合语句", "compound statement"),
    TermRule("表达式语句", "expression statement"),
    TermRule("格式字符串", "format string"),
    TermRule("f 字符串", "f-string"),
    TermRule("转义字符", "escape character"),
    TermRule("换行符", "newline character"),
    TermRule("下划线", "underscore"),
    TermRule("占位符", "placeholder"),
    TermRule("命名空间", "namespace"),
    TermRule("作用域", "scope"),
    TermRule("迭代器", "iterator"),
    TermRule("生成器", "generator"),
    TermRule("装饰器", "decorator"),
    TermRule("调试器", "debugger"),
    TermRule("断点", "breakpoint"),
    TermRule("堆栈", "stack"),
    TermRule("调用栈", "call stack"),
    TermRule("软件包", "package"),
    TermRule("包管理器", "package manager"),
    TermRule("模块", "module"),
    TermRule("属性", "attribute"),
    TermRule("实例", "instance"),
    TermRule("对象", "object"),
    TermRule("类方法", "class method"),
    TermRule("静态方法", "static method"),
    TermRule("方法", "method"),
    TermRule("形参", "parameter"),
    TermRule("实参", "argument"),
    TermRule("参数", "parameter"),
    TermRule("函数", "function"),
    TermRule("变量", "variable"),
    TermRule("常量", "constant"),
    TermRule("字符串", "string"),
    TermRule("浮点数", "float"),
    TermRule("整数", "integer"),
    TermRule("布尔", "Boolean"),
    TermRule("列表", "list"),
    TermRule("字典", "dictionary"),
    TermRule("元组", "tuple"),
    TermRule("集合", "set"),
    TermRule("索引", "index"),
    TermRule("下标", "subscript"),
    TermRule("切片", "slice"),
    TermRule("键", "key", r"(?<!按)键"),
    TermRule("值", "value", r"(?<![价数估权阈峰极面产市净均总幅])值(?!得)"),
    TermRule("类型", "type"),
    TermRule("字面量", "literal"),
    TermRule("标识符", "identifier"),
    TermRule("关键字", "keyword"),
    TermRule("运算符", "operator"),
    TermRule("操作数", "operand"),
    TermRule("表达式", "expression"),
    TermRule("语句", "statement"),
    TermRule("赋值", "assignment"),
    TermRule("条件", "condition"),
    TermRule("分支", "branch"),
    TermRule("循环", "loop"),
    TermRule("迭代", "iteration"),
    TermRule("递归", "recursion"),
    TermRule("算法", "algorithm"),
    TermRule("异常", "exception"),
    TermRule("错误", "error"),
    TermRule("调试", "debugging"),
    TermRule("断言", "assertion"),
    TermRule("测试", "test"),
    TermRule("输入", "input"),
    TermRule("输出", "output"),
    TermRule("缩进", "indentation"),
    TermRule("注释", "comment"),
    TermRule("程序", "program"),
    TermRule("代码", "code"),
    TermRule("编辑器", "editor"),
    TermRule("控制台", "console"),
    TermRule("终端", "terminal"),
    TermRule("命令", "command"),
    TermRule("提示", "hint"),
    TermRule("解决方案", "solution"),
    TermRule("要求", "requirements"),
    TermRule("评估", "evaluation"),
)

INLINE_PROTECTED_RE = re.compile(
    r"(`[^`\n]*`|__[A-Za-z][A-Za-z0-9_]*__)",
)
LATIN_PAREN_RE = re.compile(r"^[（(][^）)]*[A-Za-z][^）)]*[）)]")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Apply mandatory Chinese-English programming terminology to a PO file."
    )
    parser.add_argument("po_file", type=Path, help="Path to the Simplified Chinese PO file")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not modify the file; fail if terminology normalization is required.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path for a detailed normalization report.",
    )
    return parser.parse_args()


def reserve(text: str, protected: dict[str, str]) -> str:
    """Replace text with a temporary sentinel and return that sentinel.

    Args:
        text: Text that must be protected from later rules.
        protected: Mutable sentinel-to-text mapping.

    Returns:
        Unique sentinel string.
    """

    token = f"\x00FC_TERM_{len(protected):06d}\x00"
    protected[token] = text
    return token


def restore_reserved(text: str, protected: dict[str, str]) -> str:
    """Restore all temporary sentinels in a transformed string.

    Args:
        text: String containing temporary sentinels.
        protected: Sentinel-to-original-text mapping.

    Returns:
        String with all protected text restored.
    """

    for token, original in protected.items():
        text = text.replace(token, original)
    return text


def normalize_existing_forms(segment: str) -> str:
    """Normalize existing bilingual terms to the canonical Chinese-first format.

    Details:
        Handles half-width parentheses and legacy English-first forms such as
        `variable（变量）` without changing code spans, which are protected by the
        caller.

    Args:
        segment: Plain prose segment outside protected Markdown/code regions.

    Returns:
        Segment with existing bilingual forms normalized.
    """

    for rule in TERM_RULES:
        zh = re.escape(rule.zh)
        en = re.escape(rule.en)
        segment = re.sub(
            rf"{zh}\s*[（(]\s*{en}\s*[）)]",
            rule.canonical,
            segment,
            flags=re.IGNORECASE,
        )
        segment = re.sub(
            rf"{en}\s*[（(]\s*{zh}\s*[）)]",
            rule.canonical,
            segment,
            flags=re.IGNORECASE,
        )
    return segment


def protect_existing_bilingual_terms(segment: str, protected: dict[str, str]) -> str:
    """Protect terms that already have a Latin parenthetical translation.

    Args:
        segment: Normalized plain prose.
        protected: Mutable sentinel-to-text mapping.

    Returns:
        Segment with existing bilingual terms replaced by sentinels.
    """

    for rule in TERM_RULES:
        pattern = re.compile(
            rf"{re.escape(rule.zh)}[（(][^）)]*[A-Za-z][^）)]*[）)]"
        )
        segment = pattern.sub(lambda match: reserve(match.group(0), protected), segment)
    return segment


def annotate_plain_segment(segment: str, counts: Counter[str]) -> str:
    """Apply all terminology rules to one plain-text segment.

    Args:
        segment: Prose outside inline code, code blocks, and placeholders.
        counts: Mutable counter receiving the number of inserted terms.

    Returns:
        Bilingual-normalized segment.
    """

    segment = normalize_existing_forms(segment)
    protected: dict[str, str] = {}
    segment = protect_existing_bilingual_terms(segment, protected)

    for rule in TERM_RULES:
        def replacement(match: re.Match[str], *, current_rule: TermRule = rule) -> str:
            counts[current_rule.canonical] += 1
            return reserve(current_rule.canonical, protected)

        segment = rule.regex.sub(replacement, segment)

    return restore_reserved(segment, protected)


def transform_text(text: str, counts: Counter[str]) -> str:
    """Normalize bilingual terms while preserving Markdown and code regions.

    Details:
        Fenced code blocks, indented code lines, inline code spans, and
        futurecoder placeholders such as `__code0__` are copied verbatim.

    Args:
        text: PO translation text.
        counts: Mutable counter receiving inserted-term statistics.

    Returns:
        Transformed translation text.
    """

    result: list[str] = []
    in_fenced_code = False

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fenced_code = not in_fenced_code
            result.append(line)
            continue

        if in_fenced_code or line.startswith(("    ", "\t")):
            result.append(line)
            continue

        pieces = INLINE_PROTECTED_RE.split(line)
        for piece in pieces:
            if not piece:
                continue
            if INLINE_PROTECTED_RE.fullmatch(piece):
                result.append(piece)
            else:
                result.append(annotate_plain_segment(piece, counts))

    return "".join(result)


def transform_catalog(po: polib.POFile) -> tuple[int, Counter[str], list[str]]:
    """Transform every active translation in a PO catalog.

    Args:
        po: Parsed Simplified Chinese PO catalog.

    Returns:
        Tuple containing changed-entry count, term insertion counts, and changed
        msgids.

    Raises:
        AssertionError: If the transformation is not idempotent.
    """

    changed_msgids: list[str] = []
    counts: Counter[str] = Counter()

    for entry in po:
        if entry.obsolete or not entry.msgid:
            continue

        changed = False
        if entry.msgstr:
            transformed = transform_text(entry.msgstr, counts)
            second_pass = transform_text(transformed, Counter())
            if second_pass != transformed:
                raise AssertionError(f"non-idempotent terminology transform: {entry.msgid}")
            if transformed != entry.msgstr:
                entry.msgstr = transformed
                changed = True

        for plural_index, plural_text in list(entry.msgstr_plural.items()):
            transformed = transform_text(plural_text, counts)
            second_pass = transform_text(transformed, Counter())
            if second_pass != transformed:
                raise AssertionError(
                    f"non-idempotent plural terminology transform: {entry.msgid}"
                )
            if transformed != plural_text:
                entry.msgstr_plural[plural_index] = transformed
                changed = True

        if changed:
            changed_msgids.append(entry.msgid)

    return len(changed_msgids), counts, changed_msgids


def build_report(
    po_path: Path,
    changed_entries: int,
    counts: Counter[str],
    changed_msgids: list[str],
) -> str:
    """Build a detailed text report for one normalization run.

    Args:
        po_path: Catalog path shown in the report header.
        changed_entries: Number of entries requiring changes.
        counts: Number of insertions per canonical bilingual term.
        changed_msgids: Translation keys requiring changes.

    Returns:
        Human-readable report text.
    """

    lines = [
        "futurecoder Simplified Chinese bilingual terminology report",
        f"Catalog: {po_path}",
        f"Changed entries: {changed_entries}",
        f"Inserted/normalized terms: {sum(counts.values())}",
        "",
        "Term counts:",
    ]
    for term, count in counts.most_common():
        lines.append(f"  {count:5d}  {term}")

    lines.extend(["", "Changed msgids:"])
    lines.extend(f"  - {msgid}" for msgid in changed_msgids)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """Normalize the PO file and return a process exit code.

    Returns:
        Zero when the catalog already conforms or was updated successfully; one
        when check mode finds required changes or processing fails.
    """

    args = parse_args()
    if not args.po_file.exists():
        print(f"ERROR: PO file not found: {args.po_file}", file=sys.stderr)
        return 1

    try:
        po = polib.pofile(str(args.po_file))
        changed_entries, counts, changed_msgids = transform_catalog(po)
    except Exception as exc:  # noqa: BLE001 - show concrete catalog/transform error.
        print(f"ERROR: failed to normalize bilingual terms: {exc}", file=sys.stderr)
        return 1

    report = build_report(args.po_file, changed_entries, counts, changed_msgids)
    print("Bilingual terminology summary:")
    print(f"  changed entries          : {changed_entries}")
    print(f"  inserted/normalized terms: {sum(counts.values())}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
        print(f"  report                   : {args.report}")

    if args.check:
        if changed_entries:
            print(
                "ERROR: the Chinese catalog contains terms that are not in mandatory "
                "bilingual form.",
                file=sys.stderr,
            )
            for msgid in changed_msgids[:50]:
                print(f"  - {msgid}", file=sys.stderr)
            if len(changed_msgids) > 50:
                print(
                    f"  ... and {len(changed_msgids) - 50} more entries",
                    file=sys.stderr,
                )
            return 1
        print("All configured programming terms use mandatory bilingual form.")
        return 0

    if changed_entries:
        po.save(str(args.po_file))
        print(f"Updated bilingual terminology in: {args.po_file}")
    else:
        print("No bilingual terminology changes were needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
