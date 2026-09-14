"""接口层：只做请求接收、参数校验、路由分发

- api.deps   : 全局依赖（DB 会话、登录用户）
- api.router : /api/v1 总路由聚合（api_v1_router）
- api.*      : 各资源端点（user / captcha / word / word_book / learning / settings / stats）
"""
