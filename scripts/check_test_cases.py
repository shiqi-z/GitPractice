#!/usr/bin/env python3
"""测试用例格式检查器。

在 CI 里自动运行：扫描 test_cases/ 下的 Markdown 用例表格，
校验编号规则、必需字段、重复编号等问题。有问题就以非零状态码退出，
让 GitHub Actions 变红，从而在合并前拦住不合格的用例。

用法:
    python scripts/check_test_cases.py [用例目录]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["编号", "场景", "步骤", "预期结果"]
# 编号必须是 TC- 加至少三位数字，例如 TC-001
ID_PATTERN = re.compile(r"^TC-\d{3,}$")
# Markdown 表格的分隔行，例如 |---|---|
SEPARATOR_ROW = re.compile(r"^\|?[\s:|-]+\|[\s:|-]*$")


class Problem:
    """一条检查出来的问题。"""

    def __init__(self, path: Path, line_no: int, case_id: str, message: str) -> None:
        self.path = path
        self.line_no = line_no
        self.case_id = case_id
        self.message = message

    def __str__(self) -> str:
        return f"{self.path.name}:{self.line_no} [{self.case_id}] {self.message}"


def split_row(line: str) -> list[str]:
    """把 `| a | b |` 拆成 ['a', 'b']。"""
    cells = line.strip().strip("|").split("|")
    return [cell.strip() for cell in cells]


def find_tables(lines: list[str]) -> list[tuple[int, list[str], list[tuple[int, list[str]]]]]:
    """找出文件中的所有 Markdown 表格。

    返回 [(表头所在行号, 表头单元格, [(行号, 单元格), ...]), ...]
    """
    tables = []
    index = 0
    while index < len(lines):
        line = lines[index]
        is_header = (
            "|" in line
            and index + 1 < len(lines)
            and SEPARATOR_ROW.match(lines[index + 1].strip()) is not None
        )
        if not is_header:
            index += 1
            continue

        header = split_row(line)
        header_line = index + 1
        rows: list[tuple[int, list[str]]] = []
        index += 2
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            rows.append((index + 1, split_row(lines[index])))
            index += 1
        tables.append((header_line, header, rows))
    return tables


def check_file(path: Path, seen_ids: dict[str, str]) -> tuple[list[Problem], int]:
    """检查单个用例文件，返回 (问题列表, 有效用例数)。"""
    problems: list[Problem] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    valid_cases = 0

    for header_line, header, rows in find_tables(lines):
        missing = [name for name in REQUIRED_COLUMNS if name not in header]
        if missing:
            problems.append(
                Problem(path, header_line, "-", f"表格缺少必需列: {', '.join(missing)}")
            )
            continue

        index_of = {name: header.index(name) for name in REQUIRED_COLUMNS}

        for line_no, cells in rows:
            case_id = cells[index_of["编号"]] if len(cells) > index_of["编号"] else ""

            if len(cells) != len(header):
                problems.append(
                    Problem(
                        path,
                        line_no,
                        case_id or "-",
                        f"列数不匹配：表头 {len(header)} 列，本行 {len(cells)} 列",
                    )
                )
                continue

            if not ID_PATTERN.match(case_id):
                problems.append(
                    Problem(path, line_no, case_id or "(空)", "编号必须形如 TC-001")
                )
                continue

            if case_id in seen_ids:
                problems.append(
                    Problem(
                        path,
                        line_no,
                        case_id,
                        f"编号重复，已在 {seen_ids[case_id]} 中使用",
                    )
                )
                continue
            seen_ids[case_id] = path.name

            for name in ("场景", "步骤", "预期结果"):
                value = cells[index_of[name]]
                if len(value) < 2:
                    problems.append(
                        Problem(path, line_no, case_id, f"字段「{name}」为空或过短")
                    )

            if not any(p.case_id == case_id and p.path == path for p in problems):
                valid_cases += 1

    return problems, valid_cases


def main(argv: list[str]) -> int:
    case_dir = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1] / "test_cases"

    if not case_dir.is_dir():
        print(f"[ERROR] 用例目录不存在: {case_dir}")
        return 2

    files = sorted(case_dir.glob("*.md"))
    if not files:
        print(f"[ERROR] {case_dir} 下没有找到任何 .md 用例文件")
        return 2

    seen_ids: dict[str, str] = {}
    all_problems: list[Problem] = []
    total_cases = 0

    print(f"检查目录: {case_dir}")
    print("-" * 60)
    for path in files:
        problems, count = check_file(path, seen_ids)
        total_cases += count
        status = "OK" if not problems else f"{len(problems)} 个问题"
        print(f"{path.name:<24} 用例 {count:>2} 条   {status}")
        all_problems.extend(problems)

    print("-" * 60)
    print(f"合计: {len(files)} 个文件, {total_cases} 条用例, {len(seen_ids)} 个唯一编号")

    if all_problems:
        print(f"\n发现 {len(all_problems)} 个问题:\n")
        for problem in all_problems:
            print(f"  ✗ {problem}")
        return 1

    print("\n全部检查通过 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
