"""check_test_cases.py 的单元测试。

思路很朴素：测试脚本本身也是代码，也会写错，所以要被测试。
用临时目录造几份"合格 / 不合格"的用例文件，验证检查器能否正确判定。
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check_test_cases as checker  # noqa: E402


GOOD_CASE = """# 购物车模块测试用例

| 编号 | 场景 | 步骤 | 预期结果 |
|---|---|---|---|
| TC-101 | 加入商品 | 点击「加入购物车」 | 购物车角标 +1 |
| TC-102 | 移除商品 | 在购物车删除商品 | 角标 -1，商品消失 |
"""

BAD_ID_CASE = """| 编号 | 场景 | 步骤 | 预期结果 |
|---|---|---|---|
| 101 | 加入商品 | 点击加入 | 角标 +1 |
"""

DUPLICATE_CASE = """| 编号 | 场景 | 步骤 | 预期结果 |
|---|---|---|---|
| TC-101 | 重复编号 | 点击加入 | 角标 +1 |
"""

MISSING_COLUMN_CASE = """| 编号 | 场景 | 步骤 |
|---|---|---|
| TC-201 | 少一列 | 点击下单 |
"""

EMPTY_FIELD_CASE = """| 编号 | 场景 | 步骤 | 预期结果 |
|---|---|---|---|
| TC-301 | 空预期 | 点击提交 |  |
"""


@pytest.fixture
def make_dir(tmp_path):
    """在临时目录里生成用例文件，返回该目录。"""

    def _make(files: dict[str, str]) -> Path:
        for name, content in files.items():
            (tmp_path / name).write_text(content, encoding="utf-8")
        return tmp_path

    return _make


def run_checker(directory: Path) -> int:
    return checker.main(["check_test_cases.py", str(directory)])


def test_good_cases_pass(make_dir, capsys):
    directory = make_dir({"cart.md": GOOD_CASE})
    assert run_checker(directory) == 0
    assert "全部检查通过" in capsys.readouterr().out


def test_bad_id_is_rejected(make_dir, capsys):
    directory = make_dir({"bad.md": BAD_ID_CASE})
    assert run_checker(directory) == 1
    assert "编号必须形如 TC-001" in capsys.readouterr().out


def test_duplicate_id_across_files_is_rejected(make_dir, capsys):
    directory = make_dir({"a.md": GOOD_CASE, "b.md": DUPLICATE_CASE})
    assert run_checker(directory) == 1
    assert "编号重复" in capsys.readouterr().out


def test_missing_column_is_rejected(make_dir, capsys):
    directory = make_dir({"narrow.md": MISSING_COLUMN_CASE})
    assert run_checker(directory) == 1
    assert "缺少必需列" in capsys.readouterr().out


def test_empty_expected_result_is_rejected(make_dir, capsys):
    directory = make_dir({"empty.md": EMPTY_FIELD_CASE})
    assert run_checker(directory) == 1
    assert "为空或过短" in capsys.readouterr().out


def test_empty_directory_is_rejected(make_dir):
    directory = make_dir({})
    assert run_checker(directory) == 2


def test_real_test_cases_in_repo_pass(capsys):
    """仓库里真实的用例文件必须通过检查——这是最有价值的一条断言。"""
    repo_cases = Path(__file__).resolve().parents[1] / "test_cases"
    assert run_checker(repo_cases) == 0
    capsys.readouterr()
