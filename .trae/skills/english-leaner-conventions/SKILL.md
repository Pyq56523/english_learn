---
name: "english-leaner-conventions"
description: "English_Leaner 项目开发规范：目录分层、命名、各层引用约定、响应/异常/日志、SM-2、双Token设计。在本项目 server/ 或 web/ 下编写、修改、重构代码时必须遵守。"
---

# English_Leaner 项目开发规范

本 skill 约束 English_Leaner（FastAPI + Vue3 背单词应用）项目的代码编写。**在本仓库 `server/`（后端）或 `web/`（前端）写代码时默认启用。**

## 1. 目录分层（后端 server/）

```
server/
├── main.py           # 入口：创建 app、中间件、全局异常、include_router(api_v1_router, prefix="/api/v1")
├── core/             # 【核心层】config(读 config/*.json) / database / redis / exceptions / response / security / middlewares / logger
├── api/              # 【接口层】deps.py(全局依赖) + router.py(总路由聚合) + 各资源端点文件
├── models/           # 【ORM层】base.py(唯一 declarative_base) + 各表模型，统一出口 from models import ...
├── schemas/          # 【DTO层】请求/响应模型（Pydantic）
├── crud/             # 【数据层】base.py(CrudBase 父类) + 各资源 *_crud，纯数据操作
├── services/         # 【业务层】*_service.py，核心业务逻辑（SM-2、统计过滤等）
├── common/           # 【工具层】constants.py(状态常量/SM-2参数) + utils.py(parse_date)
├── scripts/ tests/ alembic/ config/
```

- 分层铁律：**`api` 只做参数接收与响应组装；业务逻辑在 `services`；数据访问一律经 `crud.xxx_crud`；模型引用经 `models`。**
- 不设 `app` 目录，代码直接在 `server/` 下；不设 `services` 之外的业务包。
- `main.py` 的 `main()` 用 `uvicorn.run("main:app", ...)`（字符串形式，reload 默认关）。

## 2. 命名规范（Python）

- 变量 / 函数：`snake_case`（`user_name`、`get_current_user`）
- 类：`PascalCase`（`UserCrud`、`UserTokenResponse`）
- 常量：全大写（`MAX_AVATAR_SIZE`、`STATUS_NEW`）
- 路由端点函数名与业务函数名短、清晰（如 `login`、`today_cards`）

## 3. 模块引用约定（后端）

```python
# 模型 / 常量
from models import User, UserSetting, UserWordRecord
from common.constants import STATUS_NEW, DEFAULT_DAILY_TARGET

# 数据访问（业务层禁止直接操作 Session 写 ORM）
from crud.user import user_crud
user_crud.get_by_username(db, username)

# 日志（按业务分类，目录 server/log/YYYYMMDD/<category>.log，自动清理 14 天前）
from core.logger import get_logger
logger = get_logger("user")
logger.info("登录成功 | user_id=%s", user.id)

# 统一响应
from core.response import ok
return ok(data=..., message="...")   # → {"code": 0, "data": ..., "message": "..."}

# 全局依赖
from api.deps import get_current_user, get_db, get_current_user_id
```

## 4. 接口层规范

- 端点文件在 `api/`，每个文件一个 `router = APIRouter(tags=[...])`，在 `api/router.py` include 聚合。
- 需要登录的接口：`user: User = Depends(get_current_user)`。
- 新增接口三步：`api/<资源>.py` 写端点 → `api/router.py` include → 重启生效。

## 5. 统一响应 / 异常 / 日志

- 响应体 `BaseResp` 在 `core/response.py`；业务接口一律 `ok(...)`（`captcha` 除外，返回裸 `{captcha_id, image}`）。
- 错误处理：业务层直接 `raise HTTPException(status_code, detail)`；`BusinessException` 走统一错误响应。
- 日志：`get_logger(分类)`，控制台 INFO、文件 DEBUG，`log/YYYYMMDD/<分类>.log`。

## 6. 认证（当前实现 + 设计目标）

- **当前实现（简化单 Token）**：`create_access_token(user_id)`（JWT，`sub`+`exp`，`jwt.expire_days` 过期）；`/auth/refresh` 用旧 token 换新 token，不落库不撤销。
- **设计目标（双 Token，待实现）**：access_token 短时效无状态（`type=access`）+ refresh_token 48 字节随机串、只存 SHA-256 哈希、双写 Redis + MySQL、刷新轮换、旧 refresh 复用返 401。
- 依赖：`get_db`（请求级会话）/ `get_current_user`（解码 JWT→查库→401）/ `get_current_user_id`。

## 7. SM-2 算法（services/learning_service.py）

- 纯函数 `sm2_update(record, quality)`，不依赖 DB：
  - `quality >= 3`：interval 0→1天、1→6天、之后 `interval*ease`；repetition+1；`repetition>=5 → mastered`。
  - `quality < 3`：repetition=0、interval=1天、learning。
  - 更新 `last_review_at` / `next_review_at`。
- 新词配额 `daily_target`（默认 20）；复习不限量。

## 8. 前端规范（web/，Vue 3）

- `src/api/*.js` 经 `api/request.js`（axios）请求 `/api/v1`；401 用 refresh_token 单飞续期并重放。
- Pinia stores：`user / settings / wordBook / learning`；导航用 `APP_ROUTES` + `useNavigate()`。
- 新增页面：views + `router/index.js` 登记 + `APP_ROUTES`；通用组件抽到 `components/common` 并在 `main.js` 全局注册。
- 主题：颜色取 `var(--app-*)`，不硬编码；深浅色都需清晰。
