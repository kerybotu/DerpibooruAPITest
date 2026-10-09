# DerpiViewer API 对接指南

本文只提供 Android 集成建议，不修改 DerpiViewer 源码。

## 分层

`Retrofit service -> DTO -> ImageRepository/InteractionRepository -> ViewModel -> UI`。图片详情映射 `ImageDto`；interaction 单独建可空字段，兼容匿名响应缺少用户状态的情况。

## 认证与网络

API key 由安全存储注入 query/header 拦截器，禁止写入日志。Session cookie 仅在明确支持并取得 CSRF 后启用。Android 正式环境不要硬编码 `127.0.0.1:7898`；代理应由网络层配置或系统 VPN 管理。

## 收藏与投票

进入详情页先调用已验证的 interaction/image endpoint；点击后发送单目标 mutation。推荐服务器确认后更新 UI；如采用乐观更新，必须保存旧值、处理 401/403/422/429 并在失败时回滚。禁止离线队列自动批量重放。

## 缓存与错误

按 image id 和用户身份隔离缓存；mutation 成功后失效详情和 interaction 缓存。将 401 映射为重新认证提示，403 映射为权限/CSRF 提示，404 为资源消失，422 展示参数错误，429 按 Retry-After 退避，5xx 可有限重试。

## 当前限制

除非 `docs/API_STATUS.md` 标记 `VERIFIED`，不要在 Retrofit contract 中把历史路径视为稳定 API。对 `fave`/`vote` 的动词和 JSON 使用探针实测结果更新 DTO。
