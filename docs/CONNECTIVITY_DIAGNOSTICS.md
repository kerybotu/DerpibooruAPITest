# Connectivity Diagnostics

本报告只记录低频、只读诊断。它不把 HTTP 错误当成网络错误，也不把代理错误当成 Derpibooru 接口失效。响应头中的 Cookie/Authorization 类字段应脱敏；本次响应没有这些字段。

## 方法

- 每个目标最多一次显式直连请求；只有连接级异常才尝试一次 `http://127.0.0.1:7898`。
- Python `requests.Session.trust_env = False`，因此 DIRECT 不继承系统代理变量。
- 请求使用 `Accept: application/json`、有限超时；不执行 PUT/POST/DELETE。

## 网络阶段

| 阶段 | 结果 | 证据 | 标记 |
|---|---|---|---|
| DNS `derpibooru.org` | 解析到 `104.16.154.180` | `getaddrinfo` 成功 | VERIFIED |
| TCP `443` | 建立成功 | `socket.create_connection` 成功 | VERIFIED |
| TLS | `TLSv1.3` 握手成功 | 标准 CA 校验成功 | VERIFIED |
| 本地代理 `127.0.0.1:7898` | TCP 连接被拒绝 | `ProxyError` / `WinError 10061` | VERIFIED |
| 代理协议不匹配 | 无证据 | 没有代理响应 | UNKNOWN |

## HTTP 400 证据

以下请求均为显式直连，服务器返回 HTTP `400`，没有触发代理 fallback：

| 请求 | 状态 | 响应头摘要 | 正文 | 标记 |
|---|---:|---|---|---|
| `/api/v2/images/show.json?ids=1` | 400 | `Server: cloudflare`, `Content-Length: 0`, 无 `Content-Type`, `cf-cache-status: DYNAMIC` | 0 字节 | VERIFIED |
| `/api/v2/interactions/interacted.json?class=Image&ids=1` | 400 | 同上 | 0 字节 | VERIFIED |
| `/search.json?q=pony&page=1` | 400 | 同上 | 0 字节 | VERIFIED |
| `/1.json` | 400 | 同上 | 0 字节 | VERIFIED |

旧 OpenAPI/README 只明确记录 v2 image show 的 `ids=1,2,3` 和 interacted 的 `class=Image&ids=<numeric>` 形式；没有证明 `1` 是当前可见图片。因此不能从空 400 响应推断是参数、资源、认证或路由原因。

## 人机验证与浏览器状态

响应分类器检查状态码、最终 URL、`Content-Type`、重定向历史和有限正文标记（`Anubis`、`captcha`、`I'm not a robot`、`verify you are human` 等）：

- 当前四个 400 响应正文为 0 字节、无 `Content-Type`，没有 Anubis 或人机验证证据：`NO_CHALLENGE_EVIDENCE`（**VERIFIED**）。HTTP 400 本身不能判定挑战页面。
- 401/403/429 或 HTML 重定向只能标记 `POSSIBLE_CHALLENGE`，除非正文或 URL 出现明确标记。
- 当前可见浏览器工具启动失败（模块导出错误），没有打开浏览器窗口，也没有人工验证动作：`MANUAL_ACTION_REQUIRED`（**VERIFIED**）、`API_ACCESS_UNVERIFIED`（**VERIFIED**）。
- 没有证据表明浏览器访问已恢复，也没有证据表明 Python 请求获得了浏览器会话：`BROWSER_ACCESS_RESTORED` = 未验证。
- 未读取、导出或记录任何浏览器 Cookie；Cookie 名称/存在状态 = 未检查。Anubis 验证不能替代 API Key、Session 或 CSRF。

若后续需要人工操作，应使用用户授权的可见浏览器窗口：先确认网页打开，再在开发者工具记录请求 URL/方法/状态和非敏感头；只报告 Cookie 名称及存在状态。不得自动点击、绕过验证、导出完整 Cookie 或把浏览器会话写入 Python/Git。

## API Key 与连接诊断

旧 OpenAPI 的 `ApiKeyAuth` 是 query `key`，不是 header；这是 **DOCUMENTED**。客户端通过 `params` 交给 `requests` 编码，避免手工拼 URL。当前诊断未使用真实 key，因此 key 是否改变 400 结果是 **UNKNOWN**。下一步应使用明确公开图片 ID，分别做匿名和 API Key 单次 GET。

## 连接失败解释

目标 TLS 成功，不能把旧 TLS 失败推广为服务器不可达。代理端口拒绝连接只证明本地代理未监听或端口不匹配，不能证明 API 失效。检查系统代理环境变量、VPN/代理监听端口和协议即可，不应增加 API 重试次数。

## 下一步

1. 用浏览器开发者工具确认当前网页实际 JSON 请求路径和必需参数。
2. 选择已知公开图片 ID，匿名请求一次；仅在需要确认权限差异时再用临时 API Key 请求一次。
3. 保留状态码、脱敏响应头、正文长度；没有错误正文时将参数原因标为 UNKNOWN。
