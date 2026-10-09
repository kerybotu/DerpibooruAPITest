# Derpibooru API 状态表

状态含义：`DOCUMENTED`=归档仓库记录；`VERIFIED`=本次对当前服务器得到成功响应；`OUTDATED`=旧记录与当前行为不符；`UNKNOWN`=尚未安全验证；`FAILED`=已验证请求失败。

| API | 方法 | 旧文档 | 当前验证 | 状态 |
|---|---|---:|---:|---|
| `/{id}.json` | GET | YES | UNKNOWN | UNKNOWN |
| `/images/{id}.json` | GET | YES | UNKNOWN | UNKNOWN |
| `/api/v2/images/show.json` | GET | NO/历史提及 | UNKNOWN | UNKNOWN |
| `/api/v2/images/show.json?ids=` | GET | YES | UNKNOWN | UNKNOWN |
| `/api/v2/interactions/interacted.json` | GET | YES | UNKNOWN | UNKNOWN |
| `/api/v2/interactions/fave` | PUT/DELETE | YES | UNKNOWN | UNKNOWN |
| `/api/v2/interactions/vote` | PUT/DELETE | YES | UNKNOWN | UNKNOWN |
| `/api/v2/tags` | GET | NO | UNKNOWN | UNKNOWN |
| `/api/v2/users/{id}` | GET | NO | UNKNOWN | UNKNOWN |
| `/api/v2/search` | GET | NO | UNKNOWN | UNKNOWN |
| Session login cookie | Cookie | YES | UNKNOWN | UNKNOWN |
| CSRF token for session mutations | Header/form | YES (描述) | UNKNOWN | UNKNOWN |

本表只接受脱敏的探针记录作为“当前验证”。HTTP 错误（401/403/404/422/429/5xx）仍是有效观察，不应自动改用代理。
