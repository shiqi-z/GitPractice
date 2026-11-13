# GitHub 公共 API 接口测试用例

被测接口定义见 `api/openapi.json`，数据源为 https://api.github.com（匿名访问限额 60 次/小时）。

| 编号 | 场景 | 步骤 | 预期结果 |
|---|---|---|---|
| TC-201 | 查询存在的用户 | GET /users/shiqi-z | 状态码 200，响应体 login 等于 shiqi-z，public_repos 大于 0 |
| TC-202 | 查询不存在的用户 | GET /users/this-user-not-exist-9999 | 状态码 404，响应体 message 等于 Not Found |
| TC-203 | 查询用户仓库列表 | GET /users/shiqi-z/repos | 状态码 200，返回数组，其中存在 name 等于 GitPractice 的仓库 |
| TC-204 | 分页参数生效 | GET /users/shiqi-z/repos?per_page=1 | 状态码 200，返回数组长度为 1 |
| TC-205 | 排序参数生效 | GET /users/shiqi-z/repos?sort=updated | 状态码 200，返回数组按更新时间倒序 |
| TC-206 | 用户名含非法字符 | GET /users/!!invalid!! | 状态码 404，响应体 message 等于 Not Found |
| TC-207 | 匿名访问限流响应头 | GET /users/shiqi-z，查看响应头 | 响应头包含 X-RateLimit-Limit 与 X-RateLimit-Remaining |
