# 登录模块测试项目

[![用例质量检查](https://github.com/shiqi-z/GitPractice/actions/workflows/qa-check.yml/badge.svg)](https://github.com/shiqi-z/GitPractice/actions/workflows/qa-check.yml)

练习用仓库，模拟软件测试岗位的日常资产：用例、脚本、缺陷记录都放在这里，
用 Git 记录每一次修改。

## 目录结构

```
test_cases/                     手工测试用例（Markdown 表格）
scripts/check_test_cases.py     用例格式检查器，CI 里自动运行
tests/                          检查器自身的单元测试（pytest）
.github/workflows/qa-check.yml  GitHub Actions 工作流
.gitignore                      忽略测试报告等临时产物
```

## 为什么用例也要进 Git

1. 用例会不断增补，改错了要能回到上一版
2. 每一次修改都有据可查：谁在什么时候为什么改了哪条预期结果
3. 团队共享，不用再靠"最新版-最终版-真的最终版.xlsx"

## 持续集成：每次推送自动检查

`.github/workflows/qa-check.yml` 会在推送到 main、提交 PR 或手动触发时自动运行：

1. 扫描 `test_cases/` 下所有 Markdown 表格，校验：
   - 表格必须包含 `编号 / 场景 / 步骤 / 预期结果` 四列
   - 编号格式必须为 `TC-001` 形式
   - 编号在全部用例文件中唯一，不能重复
   - 场景、步骤、预期结果不能为空
2. 运行检查器自身的单元测试，确认"检查逻辑"本身没被改坏
3. 任何一步失败，工作流变红，PR 会被拦住，问题用例进不了主干

## 本地怎么跑

```bash
python -m pip install -r requirements-dev.txt
python scripts/check_test_cases.py     # 只跑用例检查
python -m pytest tests -q              # 跑单元测试
```

## 用例编号约定

| 区间 | 用途 |
|---|---|
| TC-001 ~ TC-099 | 登录模块 |
| TC-100 ~ TC-199 | 购物车模块 |
| TC-200 以上 | 其他模块 |

新增用例时从对应区间的下一个空号开始，不要复用已删除的编号。
