# Derpibooru API 开发手册

> 本文是对当前服务器的研究记录，不是官方承诺。每个结论带有 `DOCUMENTED`、`VERIFIED`、`INFERRED`、`OUTDATED` 或 `UNKNOWN` 标签。

## 1. 来源与范围

`Tschrock/derpibooru-api-docs` 是归档的非官方 OpenAPI 资料库，不等于 Derpibooru 官方文档。本文将其与当前 HTTP 响应、网站请求分开记录。

## 2. 基础 URL 与网络

当前站点通常为 `https://derpibooru.org`。API v2 历史路径以 `/api/v2/` 开头；JSON 页面也存在根路径 `.json` 形式。**UNKNOWN**：当前部署是否仍完整提供所有 v2 路径。

客户端默认直连；只有连接级异常（DNS、TLS、`ConnectionError`、连接超时）才可重试一次本地代理 `http://127.0.0.1:7898`。代理是测试环境 fallback，不是 API 要求。收到任何 HTTP 状态都不应切换代理。

## 3. 认证

### Anonymous

公开读取请求可不带凭据（**INFERRED/DOCUMENTED**，需逐 endpoint 验证）。

### API key

旧 OpenAPI 定义 `ApiKeyAuth` 为 query 参数 `key=<API_KEY>`（**DOCUMENTED**）。不要把 key 放入源码、日志或文档；示例使用 `<API_KEY>`。API key 能否读取用户私有数据或执行 mutation 是 **UNKNOWN**。

### Session cookie 与 CSRF

旧定义使用 Cookie `_booru-on-railsm5_session`（**DOCUMENTED**）。旧说明称 session mutation 需要 CSRF token；token 来源（HTML meta、Cookie、header 或表单）尚未验证（**UNKNOWN**）。不要为研究而登录或改变账户状态。

### 三种模式

匿名：无凭据，适合公开 GET。API key：query 认证，权限及 mutation 支持必须按响应确认。Session：浏览器登录态，可能需要 CSRF；不能假定 API key 与 session 等价。

## 4. 请求、响应与错误

优先 `Accept: application/json`；写请求的 body/content type 以当前响应为准。常见状态：401 未认证，403 禁止/CSRF，404 路径或资源不存在，422 参数/验证错误，429 限流，500/502/503 服务端错误。对 429 使用 `Retry-After`（如有）并指数退避；禁止循环重试或批量 mutation。

## 5. 图片与搜索

### GET `/{id}.json`

状态：`DOCUMENTED`; 当前：`UNKNOWN`。旧 schema 返回 `ImageWithInteractions` 或 `DeletedImage`。

### GET `/images/{id}.json`

状态：`DOCUMENTED`; 当前：`UNKNOWN`。旧文档称与 `/{id}.json` 相同。

### GET `/api/v2/images/show.json`

历史资料提及单图及 `ids=...` 多图形式；当前参数、interaction 字段和上限均 `UNKNOWN`。未验证前不得将其作为稳定批量接口。

### GET `/api/v2/search`

旧仓库未提供完整定义；查询语法、分页和过滤器需以当前站点请求为准（`UNKNOWN`）。

## 6. Interactions、收藏与投票

历史路径包括 `/api/v2/interactions/interacted.json`、`/api/v2/interactions/fave`、`/api/v2/interactions/vote`（`DOCUMENTED`）。动词、body、返回 JSON、取消操作及认证权限均需探针逐项确认（`UNKNOWN`）。

建议流程：先读取图片详情/interaction，再执行单个 mutation，收到服务器确认后更新本地状态；失败时回滚乐观状态并保留错误码。不要把 `fave`、`favorite`、`favourites` 视为同义路径。

## 7. 其他资源

归档 OpenAPI 包含 users、profiles、comments、forums、messages、notifications、galleries、filters、tags 等 schema/path（`DOCUMENTED`）。当前可用性未逐项验证，统一标记 `UNKNOWN`，不得据此推断认证或字段。

## 8. 分页、缓存与安全

分页参数及最大页大小是 endpoint-specific（`UNKNOWN`）；遵循响应中的 `Link`/分页字段。公开 GET 可按 URL 和响应头缓存；带用户 interaction 的响应必须按用户/凭据隔离，mutation 后使相关缓存失效。永不记录 API key、Cookie、CSRF 或完整 Authorization。

## 9. 实际请求模板

```http
GET https://derpibooru.org/<path>.json?key=<API_KEY>
Accept: application/json
```

写请求示例只能使用探针输出的当前格式；在验证前不要复制历史 body。所有示例响应必须脱敏保存于 `docs/examples/`。

## 10. Python 与 Android 对接建议

Python 使用 `tools/derpibooru_client.py` 的单次请求、超时和直连→代理 fallback。Android Retrofit 应将认证拦截器、DTO、Repository 和 UI 状态分层；把 interaction 读取与 mutation 分开，采用服务器确认后更新或可回滚的乐观更新。不要把 `127.0.0.1:7898` 写入正式 Android 网络层，因为 Android 的 localhost 指向设备自身。

## 11. 与旧资料的差异与验证状态

旧仓库只代表历史、非官方行为。当前差异必须以探针日志为依据；没有日志的接口保持 `UNKNOWN`，而不是补写推测。详见 [API_STATUS.md](API_STATUS.md)。

## 12. 当前探测结论

本轮只读探测得到三个可建立直连但返回 `400` 的请求（v2 image show、v2 interacted、根路径 search），以及两个旧 JSON 路径的 TLS/代理连接失败。没有进行收藏、投票、watch、filter 或任何账户修改，因此这些 mutation 仍为 `UNKNOWN`。`400` 说明服务器收到了请求但不接受该形式；在没有响应 JSON 或当前网页请求对照前，不应进一步猜测参数。
