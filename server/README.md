# English_Leaner 前后端开发架构设计文档

> 一个基于 **间隔重复（SM-2）算法** 的英语背单词应用。
> 后端：FastAPI + SQLAlchemy + MySQL + Redis；前端：Vue 3 + Pinia + Vue Router + Element Plus。

---

## 目录

1. [总体架构](#一总体架构)
2. [目录结构](#二目录结构)
3. [后端设计](#三后端设计)
   - 3.1 技术栈与依赖
   - 3.2 启动流程
   - 3.3 配置体系
   - 3.4 路由注册机制
   - 3.5 分层设计（core / api / models / schemas / crud / services / common）
   - 3.6 统一响应格式、异常与日志
   - 3.7 认证与安全
   - 3.8 数据库设计
   - 3.9 核心算法：SM-2
   - 3.10 数据导入脚本
   - 3.11 API 接口清单
4. [前端设计](#四前端设计)
   - 4.1 技术栈
   - 4.2 目录结构
   - 4.3 路由与导航
   - 4.4 状态管理（Pinia stores）
   - 4.5 API 请求层
   - 4.6 布局与页面
   - 4.7 通用组件
   - 4.8 主题系统
   - 4.9 业务时序（学习/复习/拼写/统计）
5. [数据流与核心业务串讲](#五数据流与核心业务串讲)
6. [联调与本地开发](#六联调与本地开发)
7. [生产部署](#七生产部署)
8. [贡献与编码规范](#八贡献与编码规范)

---

## 一、总体架构

```
┌───────────────────────────────┐
│          浏览器 (用户端)         │
│   Vue 3 SPA  <dist>            │
│   views 页面 + Pinia stores    │
│   api/* 通过 axios 请求 /api/v1 │
└──────────────┬────────────────┘
               │  HTTP (JSON, JWT Bearer)
               ▼
┌───────────────────────────────┐
│       FastAPI  应用            │
│  main.py 启动 uvicorn          │
│  api/router 静态聚合路由        │
│  api → services → crud         │
│  core/*  安全 / 配置 / 日志     │
└──────────────┬────────────────┘
               │  SQLAlchemy / PyMySQL / Redis
               ▼
        ┌──────────────┐
        │    MySQL     │
        │ english_leaner│
        └──────────────┘
```

- **前后端分离**：开发期前端运行在 5173（Vite），通过代理 `/api`、`/uploads` 到后端 8000；后端起在 8000。
- **统一入口**：所有 HTTP API 一律以 `/api/v1/...` 暴露，由 `api/router.py` 静态聚合、`main.py` 统一挂载。
- **统一响应**：业务接口返回 `{ "code": 0, "data": ..., "message": "ok" }`（`captcha` 接口除外，见[接口清单](#311-api-接口清单全部经-apiv1)）。
- **静态托管**：头像上传到 `server/uploads/`，后端在 `main.py` 把 `/uploads` 挂载为静态目录；前端构建产物可放入 `server/static/web` 由后端托管（见[生产部署](#七生产部署)）。

---

## 二、目录结构

```
English_Leaner/
├── server/                    # 后端（本文档所在目录）
│   ├── main.py                # 应用入口：创建 app、加载中间件/异常、路由聚合、启动 uvicorn
│   ├── requirements.txt       # pip 依赖清单
│   ├── alembic.ini            # 数据库迁移配置（脚本目录 alembic/）
│   ├── .gitignore             # 忽略 venv / __pycache__ / .env / uploads / log
│   ├── config/                # 运行配置（JSON）
│   │   ├── main_leaner.json   # 应用名 / env / host / port / jwt
│   │   └── database.json      # MySQL / Redis 连接参数
│   ├── core/                  # 【核心层】全局核心配置 & 基础能力
│   │   ├── config.py          # 全局配置读取（config/*.json → 常量）
│   │   ├── database.py        # 数据库引擎、SessionLocal、建表
│   │   ├── redis.py           # Redis 连接（惰性单例，验证码/Token）
│   │   ├── exceptions.py      # BusinessException + 全局异常处理器
│   │   ├── response.py        # 统一响应体 BaseResp + ok()
│   │   ├── security.py        # JWT 生成/校验 + bcrypt 密码哈希
│   │   ├── middlewares.py     # 跨域 + 请求日志/耗时
│   │   └── logger.py          # 按业务分类 + 日期归档日志，自动清理 14 天前
│   ├── api/                   # 【接口层】只做请求接收、参数校验、路由分发
│   │   ├── deps.py            # 全局依赖：DB 会话、登录用户（get_db / get_current_user）
│   │   ├── router.py          # api_v1_router 总路由聚合
│   │   ├── user.py            # 认证、个人信息、头像
│   │   ├── captcha.py         # 图形验证码（生成/校验，存 Redis）
│   │   ├── word.py            # 单词
│   │   ├── word_book.py       # 单词书
│   │   ├── learning.py        # 今日卡片 / 开始学习 / 复习 / 进度
│   │   ├── settings.py        # 用户设置
│   │   └── stats.py           # 仪表盘 / 热力图 / 连续打卡
│   ├── models/                # 【ORM 层】数据库实体模型（仅表结构）
│   │   ├── base.py            # ORM 公共基类（全项目唯一 declarative_base）
│   │   └── user.py / word.py / word_book.py / record.py
│   ├── schemas/               # 【DTO 层】请求/响应模型（参数校验、脱敏）
│   │   ├── common.py          # 分页请求/响应 DTO
│   │   └── user.py / word.py / learning.py / settings.py / stats.py
│   ├── crud/                  # 【数据层 Repository】纯数据操作，无业务逻辑
│   │   ├── base.py            # 通用 CRUD 父类（CrudBase）
│   │   └── user.py / word.py / word_book.py / record.py / settings.py
│   ├── services/              # 【业务层】核心业务逻辑（SM-2、统计过滤等）
│   │   ├── user_service.py / word_service.py / word_book_service.py
│   │   ├── learning_service.py / settings_service.py / stats_service.py
│   ├── common/                # 【工具层】通用工具、常量
│   │   ├── constants.py       # 状态常量与 SM-2 初始参数
│   │   └── utils.py           # parse_date 等
│   ├── scripts/               # 脚本目录
│   │   └── init_db.py         # 手动建表（dev 启动时也会自动建表）
│   ├── tests/                 # pytest 单元测试
│   │   └── test_sm2.py        # SM-2 算法与工具函数测试
│   ├── alembic/               # 数据库迁移（env.py + versions/）
│   └── uploads/               # 上传文件（头像等）
│
└── web/                       # 前端
    ├── index.html
    ├── package.json
    ├── vite.config.js         # dev server + 代理 + 别名 @ → src
    ├── .env.example           # VITE_API_BASE_URL
    └── src/
        ├── main.js            # 创建 app、注册全局组件、挂载主题
        ├── App.vue            # 根组件 <router-view/>
        ├── router/index.js    # 路由表 + 导航守卫 + useNavigate
        ├── api/               # axios 请求封装（分量按资源）
        ├── stores/            # Pinia（user / settings / wordBook / learning）
        ├── components/
        │   ├── common/        # 全局通用组件
        │   ├── layout/        # AppLayout / AppSidebar / AppHeader
        │   └── word/          # 词卡学习相关组件
        └── views/             # 页面
```

> 项目不设 `app` 目录，代码直接在 `server/` 下；`api` 为接口层（只做参数接收与响应组装），`services` 为业务逻辑层，`crud` 为数据访问层，`models` 为 ORM 层。

---

## 三、后端设计

### 3.1 技术栈与依赖

见 [`requirements.txt`](requirements.txt)，核心：

| 依赖 | 用途 |
| --- | --- |
| fastapi | Web 框架 |
| uvicorn[standard] | ASGI 服务器 |
| SQLAlchemy 2.x | ORM |
| PyMySQL | MySQL 驱动 |
| pydantic / email-validator | 请求/响应校验 |
| python-jose + cryptography | JWT 编解码 |
| passlib[bcrypt] + bcrypt | 密码哈希 |
| python-multipart | 文件上传 |
| Pillow + redis | 图形验证码生成 / 存储 |
| alembic | SQL 迁移（当前 dev 用自动建表） |
| pytest + httpx | 测试 |

### 3.2 启动流程（main.py）

文件 [`server/main.py`](main.py)：

1. 模块级导入：`api.router.api_v1_router`、`core.config` 全局常量、`core.middlewares`、`core.exceptions`。
2. `app = FastAPI(title=APP_NAME, lifespan=lifespan)`。
3. `add_cors_middleware(app, CORS_ORIGINS)` + `add_request_logging_middleware(app)`：跨域 + 请求日志/耗时。
4. `register_exception_handlers(app)`：注册 `BusinessException` / `HTTPException` / 兜底 `Exception` 处理器。
5. 挂载 `/uploads` 静态目录（头像等图片可被浏览器访问）。
6. `app.include_router(api_v1_router, prefix=API_V1_PREFIX)`：一次性挂载 `/api/v1` 下全部接口。
7. `@app.get("/")`：健康检查，返回 `{"app": APP_NAME, "status": "running"}`。
8. **lifespan 上下文**：启动时打印环境信息；`env == dev` 时 `create_all_tables()` 自动建表；关闭时打印应用关闭。
9. `main()`：`uvicorn.run`（必须传 `"main:app"` 字符串）。

> **关键约定**：路由在 `api/router.py` 中静态聚合，`main.py` 只做一次挂载，无需 JSON 清单。

### 3.3 配置体系

| 文件 | 内容 | 读取方 |
| --- | --- | --- |
| `config/main_leaner.json` | app_name / env / host / port / jwt | core/config.py |
| `config/database.json` | MySQL host/port/user/password/database/charset/pool、Redis | core/config.py |

`core/config.py` 在模块加载时读取 JSON，导出全局常量：`APP_NAME`、`ENV`、`HOST`、`PORT`、`API_PREFIX`、`CORS_ORIGINS`、`JWT_*`、`MYSQL`、`REDIS`。

示例（`main_leaner.json`）：

```json
{
  "main": { "app_name": "English_Leaner", "env": "dev", "host": "0.0.0.0", "port": 8000 },
  "jwt": { "secret_key": "...", "algorithm": "HS256", "expire_days": 1 }
}
```

> `env=dev` 时应用启动自动建表；`production` 关闭自动建表改用 Alembic。JWT 当前为单 Token（`expire_days` 过期天数），双 Token 配置项见 3.7 设计目标。

### 3.4 路由注册机制

路由不再使用 JSON 清单动态注册，改为 `api/router.py` 中**静态聚合**：

```python
from fastapi import APIRouter
from api import captcha, learning, settings, stats, user, word, word_book

api_v1_router = APIRouter()
api_v1_router.include_router(user.router)       # /api/v1/auth/*
api_v1_router.include_router(captcha.router)    # /api/v1/captcha
api_v1_router.include_router(word.router)       # /api/v1/words
api_v1_router.include_router(word_book.router)  # /api/v1/word-books
api_v1_router.include_router(learning.router)   # /api/v1/learning/*
api_v1_router.include_router(settings.router)   # /api/v1/settings
api_v1_router.include_router(stats.router)      # /api/v1/stats/*
```

`main.py` 通过 `app.include_router(api_v1_router, prefix="/api/v1")` 一次性挂载。

**新增接口三步**：在对应 `api/<资源>.py` 写端点函数（`router = APIRouter(tags=[...])` + `@router.get/post(...)`）→ 在 `api/router.py` include 该资源 router → 重启/热重载即生效。前端无需知道后端实现，只按路径调用。

### 3.5 分层设计

#### core/（核心层：全局配置 & 基础能力）

- `config.py`：读取 `config/*.json`，导出全局常量（`APP_NAME`、`API_PREFIX`、`JWT_*`、`MYSQL`、`REDIS` 等）。
- `database.py`：`engine` / `SessionLocal` / `create_all_tables()`（唯一 `Base` 在 `models/base.py`）。
- `redis.py`：Redis 连接（惰性单例），验证码/Token 高速读写。
- `exceptions.py`：`BusinessException` + `register_exception_handlers`（统一错误响应，兼容前端 `{code, data, message}` 与 `{detail}` 两种格式）。
- `response.py`：统一响应体 `BaseResp` + `ok(data, message)`。
- `security.py`：`hash_password` / `verify_password`（bcrypt）；JWT `create_access_token` / `decode_token`。
- `middlewares.py`：跨域（CORSMiddleware）+ 请求日志/耗时。
- `logger.py`：`get_logger(category)` 按业务分类写日志，目录 `server/log/YYYYMMDD/<category>.log`，自动清理 14 天前日志。

#### api/（接口层）

- `deps.py`：全局依赖——`get_db()`（请求级会话）、`get_current_user()`（解码 JWT → 查库返回 User，无效抛 401）、`get_current_user_id()`。
- 各资源文件（`user.py`、`captcha.py`、`word.py`、`word_book.py`、`learning.py`、`settings.py`、`stats.py`）只做请求接收、参数校验、调用 `services`、组装返回；`router.py` 聚合总路由。

#### models/（ORM 层）

- `base.py`：全项目唯一 `declarative_base()`（保证 FK 跨表解析）。
- 各表模型（`user.py` / `word.py` / `word_book.py` / `record.py`），统一出口 `from models import User, ...`。

#### schemas/（DTO 层）

- `common.py`：分页请求/响应 DTO（`PageQuery` / `PageResponse`）。
- 各资源 Schema：`LoginRequest`、`UserCreate`、`UserTokenResponse`、`WordCard`、`TodayCardsResponse`、`DashboardStats`、`SettingsResponse` 等。

#### crud/（数据层 Repository）

- `base.py`：通用 CRUD 父类（`CrudBase`：`get` / `get_by` / `list` / `count` / `add` / `add_all` / `commit`）。
- 各资源 Repository：`user_crud` / `word_crud` / `word_book_crud` / `record_crud` / `setting_crud`，**纯数据操作，无业务逻辑**。

#### services/（业务层）

- 与接口一一对应的 `*_service.py`：注册/登录、SM-2 复习、统计过滤、设置读写等核心业务都在这里。
- 通过 `crud.xxx_crud` 访问数据，通过 `models` 引用模型、`common.constants` 引用常量。

#### common/（工具层）

- `constants.py`：`STATUS_NEW/STATUS_LEARNING/STATUS_MASTERED`、SM-2 初始参数（`DEFAULT_EASE_FACTOR`、`MIN_EASE_FACTOR` 等）、`DEFAULT_DAILY_TARGET`。
- `utils.py`：`parse_date` 等纯函数工具。

> **约定**：接口层只做参数接收与响应组装；业务逻辑放 `services`；业务层不直接写 SQLAlchemy 会话操作，一律经 `crud.xxx_crud` 访问数据，经 `models` 引用模型。

### 3.6 统一响应格式、异常与日志

**响应**（`core/response.py`）：`ok(data, message="ok")` → `{ "code": 0, "data": data, "message": "ok" }`。

**异常**（`core/exceptions.py`）：

- `BusinessException(status_code, message, code)` → `{ "code": code, "data": None, "message": message }`。
- `HTTPException` → `{ "detail": ... }`（与 FastAPI 默认一致，前端兼容）。
- 兜底 `Exception` → 500 `{ "detail": "Internal server error" }`。

业务层错误一般直接 `raise HTTPException(status_code, detail)`；前端 axios 拦截器根据 `code !== 0` 或非 2xx 提示。

**日志**（`core/logger.py`）：

```python
from core.logger import get_logger
logger = get_logger("user")   # 按业务分类
logger.info("登录成功 | user_id=%s", 1)
```

- 按业务分类 + 按日期归档：`server/log/20260909/user.log`。
- 启动时自动清理 14 天前的日志目录。
- 控制台只输出 INFO 及以上，文件记录 DEBUG 及以上。

### 3.7 认证与安全（双 Token 设计目标：access + refresh）

> ⚠️ **本节为双 Token 设计目标（待实现）**。当前代码为简化实现（见本节末尾「当前实现」），后续按本设计升级：access_token 短时效无状态，refresh_token 长时效可撤销、双写 Redis + MySQL、刷新轮换。

- **密码**：`passlib` + bcrypt，`hash_password` / `verify_password`。
- **access_token（短时效，无状态，不落库）**：JWT，`sub=user_id`、`type=access`、`exp=30 分钟`（`jwt.access_expire_minutes`）。前端每次请求携带 `Authorization: Bearer <access_token>`，后端 `decode_token` 校验签名与 `type`。
- **refresh_token（长时效，可撤销）**：48 字节随机不透明串，服务端只存 `SHA-256` 哈希，**双写 Redis + MySQL**：
  - Redis（`core/redis.py`）：`refresh:{hash}` → user_id，TTL 7 天自动淘汰，校验优先走 Redis。
  - MySQL（`user_refresh_tokens` 表）：持久化兜底，`RefreshToken_Get` 校验"未撤销且未过期"；Redis 不可用时自动降级。
- **刷新轮换**：`POST /auth/refresh`（传 `refresh_token`）→ 校验通过 → 撤销旧 refresh（Redis del + MySQL `revoked=1`）→ 签发新的一对。**旧 refresh 再使用返回 401**。
- **依赖注入**：
  - `get_db()`：每个请求新建 Session，finally 关闭。
  - `get_current_user()`：从 `Authorization: Bearer <token>` 解码 access_token → 查库返回 User，无效则抛 401。
  - `get_current_user_id()`：便捷取 id。
- **前端续期**：登录后存 access + refresh（localStorage）；axios 响应 401 时用 refresh_token **单飞静默续期**（并发 401 只刷新一次），成功后重放原请求；refresh 也失败才登出跳登录。

#### 当前实现（简化版）

- **单 Token**：`create_access_token(user_id)` 签发 JWT（`sub` + `exp`），过期时间取 `jwt.expire_days`（默认 1 天）；`decode_token` 校验签名与过期。
- **刷新**：`POST /auth/refresh` 传 `{ "token": "<旧 token>" }`，后端解码旧 token 取出 `user_id`，签发新的 access_token 返回。当前不落库、不撤销旧 token。
- **登录响应**：`{ access_token, token_type: "bearer", user }`（见 `UserTokenResponse`）。
- 依赖注入 `get_db` / `get_current_user` / `get_current_user_id` 与设计一致。

### 3.8 数据库设计

库：`english_leaner`（utf8mb4）。表由 `Base.metadata.create_all` 建（dev），生产用 Alembic 迁移（`alembic/`）。

#### users（用户）
| 字段 | 说明 |
| --- | --- |
| id / username / email / password | 唯一（username、email 带索引） |
| avatar / age / gender / bio | 头像 URL、年龄、性别、简介 |
| created_at / updated_at | 时间戳 |

#### word_books（单词书）
| 字段 | 说明 |
| --- | --- |
| id / name / category / description | 名称、分类（CET4/CET6...）、描述 |
| word_count | 冗余计数（加速查询，导入后 SQL 同步） |
| created_at | 时间 |

#### words（单词，一词可属多书）
| 字段 | 说明 |
| --- | --- |
| id / word | 单词，word 带索引 |
| phonetic / meaning / example | 音标、释义、例句 |

#### word_book_words（单词书 ↔ 单词 多对多）
| 字段 | 说明 |
| --- | --- |
| book_id / word_id | 外键 |
| position | 该书内顺序 |
| 唯一约束 | (book_id, word_id) |

#### user_word_records（用户学习记录，SM-2 核心表）
| 字段 | 说明 |
| --- | --- |
| user_id / word_id | 唯一 (user_id, word_id) |
| status | new / learning / mastered |
| ease_factor / interval_days / repetition | SM-2 三参数 |
| next_review_at / last_review_at | 下次复习 / 上次复习 |
| learned_at | 首次学习时间（用于统计"今日新学"） |
| created_at | 时间 |

#### user_settings（用户设置，key-value）
| 字段 | 说明 |
| --- | --- |
| user_id / key / value | 唯一 (user_id, key)，如 daily_target、current_book_id |
| updated_at | 时间 |

#### user_refresh_tokens（刷新令牌，持久化兜底，设计目标：当前代码未建此表）
| 字段 | 说明 |
| --- | --- |
| user_id | 外键 users.id |
| token_hash | 刷新令牌的 SHA-256 哈希（唯一），不存明文 |
| expires_at | 过期时间（默认 7 天） |
| revoked | 0 有效 / 1 已撤销（刷新轮换时置 1） |
| created_at | 时间 |

### 3.9 核心算法：SM-2（services/learning_service.py）

`sm2_update(record, quality)` 纯函数：

```
quality = int(quality)
ease_factor = max(1.3, ease_factor + (0.1 - (5-quality)*(0.08 + (5-quality)*0.02)))
if quality >= 3:
    repetition 0→interval 1天; 1→6天; 之后 interval*ease
    repetition ++ ; repetition>=5 → mastered, else learning
else:
    repetition=0; interval=1天; status=learning
last_review_at=now; next_review_at = now + interval_days
```

- **学习（新词）**：每日新学上限由 `daily_target`（settings）决定。前端读 `today_cards` 中 `new_cards`；达到配额后刷新不再派发（配额逻辑：`learn_count = min(未学总数, daily_target)`）。
- **复习（due）**：`next_review_at <= now` 的都进入复习，不限量，一次清完当天到期。
- **拼写**：前端用 `learned_cards`（今日已学，含 `learned_at` 的记录），不受每日配额影响。

### 3.10 数据导入脚本

> 导入逻辑原先在 `server/import_words.py`，当前仓库未保留该文件。以下是设计说明：

- 读取 Navicat 导出的 `xxx.sql`（模板 `C:/Users/29504/Desktop/{}.sql`），按 `INSERT INTO \`表\` VALUES (` 前缀逐行解析。
- 字段映射：`english→word`、`sent→phonetic`、`chinese→meaning`；并使用 `csv`（`quotechar="'"`, `doublequote=True`, `skipinitialspace=True`）解析以处理引号。
- 清洗：去掉外围字面单引号、合并 meaning 成对重复（`''` 去重）。
- **多对多**：words 全局去重，一本书内按 `seen_word_ids` 去重，通过 `word_book_words` 建关联。
- 幂等：词书/单词存在则复用；`word_count` 用关联表实时统计，并在末尾用 SQL 同步所有书冗余计数。

### 3.11 API 接口清单（全部经 `/api/v1`）

| 方法 | 路径 | 端点函数 | 说明 |
| --- | --- | --- | --- |
| GET | /captcha | captcha.generate | 获取注册验证码（返回 `{captcha_id, image}` 裸对象，非统一响应体） |
| POST | /auth/register | user.register | 注册（携带验证码） |
| POST | /auth/login | user.login | 登录（用户名或邮箱 + 密码） |
| POST | /auth/refresh | user.refresh | 刷新令牌（当前实现：旧 token 换新 token；设计目标：refresh_token 轮换） |
| GET | /auth/me | user.me | 当前用户 |
| PUT | /auth/update_me | user.update_me | 更新个人信息 |
| POST | /auth/change_password | user.change_password | 修改密码 |
| POST | /auth/reset_password | user.reset_password | 找回密码（携带验证码） |
| POST | /auth/upload_avatar | user.upload_avatar | 上传头像 |
| GET | /word-books | word_book.list_books | 单词书列表（可按分类） |
| GET | /word-books/{book_id} | word_book.get_book | 单词书详情 + 学习进度 |
| GET | /words | word.list_words | 单词列表（可按书/关键词分页） |
| GET | /words/{word_id} | word.get_word | 单词详情 |
| GET | /learning/today | learning.today_cards | 今日卡片（新词/复习/已学） |
| POST | /learning/start | learning.start_learning | 初始化某书学习记录 |
| POST | /learning/review | learning.review | 提交复习评分（SM-2） |
| GET | /learning/progress/{book_id} | learning.get_progress | 某书学习进度 |
| GET | /settings | settings.get_settings | 读用户设置 |
| PUT | /settings | settings.update_settings | 写用户设置 |
| GET | /stats/dashboard | stats.dashboard | 仪表盘（按当前词书过滤） |
| GET | /stats/heatmap | stats.heatmap | 365 天热力图 |
| GET | /stats/streak | stats.streak | 连续打卡 |

> 需要登录的接口通过 `Depends(get_current_user)` 鉴权，前端请求头携带 `Authorization: Bearer <token>`。

---

## 四、前端设计

### 4.1 技术栈

Vue 3（`<script setup>`）、Vite 5、Pinia、Vue Router 4（history 模式）、Element Plus、Axios、Dayjs、Sass。

### 4.2 目录结构

```
web/src/
├── main.js               # 入口：Pinia/router/ElementPlus/全局组件/主题
├── App.vue               # <router-view/>
├── router/index.js       # 路由表 + 守卫 + useNavigate + APP_ROUTES
├── api/                  # axios 封装
│   ├── request.js        # 实例 + 拦截器
│   ├── auth.js / learning.js / word.js / wordBook.js / settings.js / stats.js
├── stores/               # Pinia
│   ├── index.js / user.js / settings.js / wordBook.js / learning.js
├── components/
│   ├── common/           # PageHeader / StatCard / SettingItem / BookCard / CurrentBookCard / AuthCard / StreakBadge / Heatmap
│   ├── layout/           # AppLayout / AppSidebar / AppHeader
│   └── word/             # WordCard / ReviewRating / WordProgress / SpellingPractice
└── views/                # Home / WordBooks / Learning / Settings / Profile / Login / Register
```

### 4.3 路由与导航

`router/index.js`：

- `routes`：`/login`、`/register`（public），`/` 下挂 `AppLayout` 与子路由 `''(/)、books、learning、settings、profile`。
- **导航守卫** `beforeEach`：public 放行；无 token 去登录；有 token 首次校验 `/auth/me`（缓存 `validatedToken`，每会话只调一次后端）；校验失败清 token 回登录页。
- **集中导航** `APP_ROUTES` + `useNavigate()`：新增页面只需在 `APP_ROUTES` 登记，业务组件用 `const { toHome, toBooks, toLearning } = useNavigate()` 跳转，不写死路径。

```js
export const APP_ROUTES = {
  home: { path: '/', name: 'Home' },
  books: { path: '/books', name: 'WordBooks' },
  learning: { path: '/learning', name: 'Learning' },
  settings: { path: '/settings', name: 'Settings' },
  profile: { path: '/profile', name: 'Profile' },
  login: { path: '/login', name: 'Login' },
  register: { path: '/register', name: 'Register' }
}
```

> 由于路由用 history 模式，**生产必须配置 SPA fallback**（见部署）。

### 4.4 状态管理（Pinia stores）

| store | 职责 |
| --- | --- |
| `user` | access + refresh token + user；login/register/refreshTokens/setTokens/fetchMe/logout，操作 localStorage |
| `settings` | dailyTarget、theme、currentBookId；init 从后端加载，setDailyTarget/setCurrentBook 持久化后端，setTheme 应用 `<html.dark>` |
| `wordBook` | books、current、progress；fetchBooks/selectBook/restoreCurrent |
| `learning` | newCards、learnedCards、summary、queue、queueIndex、current；fetchTodayCards/nextCard/rateCard/reset |

### 4.5 API 请求层（api/request.js）

- `baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'`。
- 请求拦截器：带 `Authorization: Bearer <access_token>`。
- 响应拦截器：`code !== 0` 弹错；网络失败统一提示；**401 → 用 refresh_token 单飞静默续期并重放原请求，刷新失败才登出跳登录**。
- 各 `api/*.js` 按资源导出函数，只调对应路径。

### 4.6 布局与页面

- `AppLayout.vue`：`el-container` = 侧边栏 + 头部 + `el-main`（内含路由过渡 `fade-up`）。
- `AppSidebar.vue`：Logo + el-menu（学习仪表盘 / 选择单词书 / 开始学习 / 学习设置），`router` 模式按 `$route.path` 高亮。
- 页面（views）：
  - `Home.vue` 学习仪表盘：Hero 欢迎区 + 连续打卡、当前词书卡、三张统计卡（已学/目标、今日学习、累计学习天数）、签到周历。
  - `WordBooks.vue` 选择单词书：PageHeader + 分类筛选 + BookCard 网格 + 继续学习。
  - `Learning.vue` 今日学习：PageHeader + 卡片学习/键盘拼写切换。
  - `Settings.vue`：每日目标 + 页面模式。
  - `Profile.vue` 个人中心：展示 / 修改信息 / 修改密码 / 头像上传。
  - `Login.vue`、`Register.vue`：AuthCard 认证外壳。

### 4.7 通用组件

- **全局注册**（`main.js` 直接 `app.component`）：`PageHeader`、`StatCard`、`SettingItem`、`BookCard`、`CurrentBookCard`、`AuthCard`。页面无需 import 即可使用。
- 按需 import：`StreakBadge`、`Heatmap` 及 `components/word/*`。
- 业务组件：`WordCard`（卡片翻面）、`ReviewRating`（0-5 评分）、`WordProgress`（进度）、`SpellingPractice`（键盘拼写）。

### 4.8 主题系统

- `assets/styles/variables.scss`：浅色 + `html.dark` 深色两套 CSS 变量（`--app-*` 与 Element Plus 覆盖变量）。
- `assets/styles/main.scss`：全局 `.page-container`、`.card`、`.card-hover`、`.stat-num`、滚动条、路由过渡。
- `settings.js`：`theme` 状态 + `applyTheme()`（增删 `<html class="dark">`）；登录页遵循系统偏好，用户可在设置切换并持久化。

### 4.9 业务时序

**今日卡片加载（Learning 页面）**

```
Learning.onMounted → learning.fetchTodayCards()
  → GET /learning/today
  → newCards / learnedCards / summary 写入 store
  → queue = newCards（学习新词）；拼写模式用 learnedCards
```

**词卡评分（卡片学习）**

```
ReviewRating @rate(quality) → learning.rateCard(quality)
  → POST /learning/review { record_id, quality }
  → 后端 SM-2 更新, 返回新状态 → nextCard()
```

**界面翻面/发音**：换卡片自动 `speechSynthesis` 朗读单词；点击卡片翻面显示释义。

**统计（Home 页面）**

```
Home.onMounted → settings.init() → wordBook.fetchBooks() → restoreCurrent → loadDashboard()
  → GET /stats/dashboard?start_date&end_date（默认最近一周）
  → today / total / streak / days 渲染首页仪表盘与签到周历
```

---

## 五、数据流与核心业务串讲

1. **选词书**：`WordBooks` 选中某书 → `wordBook.selectBook(id)`（写 current 并 `settings.setCurrentBook` 持久化）→ `startLearning(id)`（为该用户该书所有词建 `status=new` 记录，幂等）。
2. **今日学习量**：`GET /settings` 提供 `daily_target`（默认 20）。`GET /learning/today` 计算 `learn_count = min(未学总数, daily_target)`，达到后刷新不再给新词。
3. **复习队列**：`next_review_at <= now` 的 due 记录全部返回，遵循遗忘曲线，不限量。
4. **评分 → SM-2**：`POST /learning/review` 更新 ease/interval/repetition/status，并写 `learned_at`（首次）、`last_review_at`、`next_review_at`。
5. **统计**：仪表盘按 `settings.current_book_id` 关联 `word_book_words` 过滤，保证只统计当前书；未选书时数据为 0，不显历史残留。

---

## 六、联调与本地开发

### 后端启动

```bash
cd server
pip install -r requirements.txt   # 或 pip install -e .
python main.py
```

- 默认监听 `0.0.0.0:8000`，dev 自动建表（`reload` 需在 `main()` 中手动开启，当前默认关闭）。
- 配置数据库/Redis：修改 `config/database.json`；应用/JWT：修改 `config/main_leaner.json`。
- 健康检查：`GET http://127.0.0.1:8000/`。
- 运行测试：`python -m pytest tests`。

### 前端启动

```bash
cd web
npm install
npm run dev
```

- Vite 起在 `:5173`；`/api`、`/uploads` 代理到 `127.0.0.1:8000`（见 `vite.config.js`）。
- 如需覆盖 API 前缀，复制 `.env.example` 为 `.env` 修改 `VITE_API_BASE_URL`。

### 首次体验流程

注册 → 登录 → 设置页设定每日目标 → 选择单词书 → 开始学习（卡片/拼写）→ 回首页看仪表盘。

---

## 七、生产部署

### 方案 A：后端托管前端（单进程）

1. 构建前端：`cd web && npm run build` → 产物在 `web/dist`。
2. 把 `web/dist/*` 拷贝到 `server/static/web/`。
3. 在 `server/main.py` 增加静态托管与 SPA fallback（示例，必须放在路由注册之后）：

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

DIST_DIR = Path(__file__).parent / "static" / "web"

app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    if full_path == "api" or full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return FileResponse(DIST_DIR / "index.html")
```

> `/uploads` 静态目录已在 `main.py` 挂载，头像可正常访问。
> SPA fallback 必须放最后（注册顺序），避免吞掉 API/静态路由。

4. 生产关闭 dev 自动建表（`config/main_leaner.json` 的 `env` 改 `production`），改用 Alembic 迁移管理表结构：

```bash
cd server
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### 方案 B：前端 nginx + 后端分离（更标准）

`web/dist` 交给 nginx，配置：

```nginx
server {
  listen 80;
  root /path/to/web/dist;
  location / { try_files $uri $uri/ /index.html; }   # SPA fallback
  location /api/  { proxy_pass http://127.0.0.1:8000; }
  location /uploads/ { proxy_pass http://127.0.0.1:8000; }
}
```

### 安全与运维注意

- 生产务必替换 `config/main_leaner.json` 的 `jwt.secret_key`。
- 生产使用 `uvicorn main:app --host 0.0.0.0 --port 8000 --workers N` 或对接 gunicorn。
- MySQL 连接串已做密码 URL 编码（`quote_plus`）。
- 日志按日期归档在 `server/log/`，自动清理 14 天前日志；`.gitignore` 已忽略 `venv`、`__pycache__`、`log/`、`.env`。

---

## 八、贡献与编码规范

- **Python 命名规范**：
  - 变量 / 函数：`snake_case`（`user_name`、`get_current_user`）
  - 类：`PascalCase`（`UserCrud`、`UserTokenResponse`）
  - 常量：全大写（`MAX_AVATAR_SIZE`、`STATUS_NEW`）
- **后端模块引用**：
  - 模型/常量：`from models import User, UserSetting, ...` + `from common.constants import STATUS_NEW`
  - 数据访问：`from crud.user import user_crud` + `user_crud.xxx(db, ...)`
  - 日志：`from core.logger import get_logger` + `get_logger("业务分类")`
  - 响应：`from core.response import ok` + `ok(data=..., message=...)`
- **分层职责**：`api` 只做参数接收与响应组装；业务逻辑放 `services`；数据访问一律走 `crud` 层。
- **接口暴露**：在 `api/<资源>.py` 定义端点并在 `api/router.py` include，前端按 `/api/v1/...` 路径访问。
- **不设 app 目录**：代码直接在 `server/` 下，入口 `main.py` 的 `main()`。
- **建表**：dev 用 `Base.metadata.create_all` 自动建，勿手写 DDL/seed.py；生产用 Alembic。
- **前端**：新增页面 → views + router 登记录（含 `APP_ROUTES`）；通用 UI 抽到 `components/common` 并在 `main.js` 全局注册；导航用 `useNavigate()`。
- **主题**：颜色一律取 `var(--app-*)`，不硬编码，保证深浅色都清晰。
