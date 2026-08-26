# 湖湘文化数字化平台

[![Vue 3](https://img.shields.io/badge/Vue-3.5.21-42b883?style=flat&logo=vue.js)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?style=flat&logo=flask)](https://flask.palletsprojects.com)
[![Go](https://img.shields.io/badge/Go-1.26-00ADD8?style=flat&logo=go)](https://go.dev)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-00758F?style=flat&logo=mysql)](https://www.mysql.com)

## 项目简介

湖湘文化数字化平台是一个致力于通过数字化手段展示、传播和传承湖湘文化精髓的综合性 Web 应用。项目采用前后端分离架构，前端使用 Vue 3 + Vite 构建，后端拆分为 Flask（用户认证 + 文化资源 + 知识图谱 + AI助手）与 Go/Gin（社区帖子）两个服务，提供文化资源展示、社区互动、知识图谱、AI 助手等功能。

## 核心功能

| 功能模块 | 说明 |
|---------|------|
| 🏠 首页 | 平台门户，核心功能入口 |
| 📚 文化资源库 | 湖湘文化资源展示（历史遗迹、传统艺术、诗词、美食等） |
| 💬 互动社区 | 用户发帖、评论、点赞（Go 服务） |
| 🕸️ 知识图谱 | 文化元素关联可视化，支持节点拖拽、详情面板、后台管理 |
| 🎮 数字化展示 | 诗词数字化、建筑 3D |
| 🤖 AI 助手 | 智能问答服务，支持流式输出、对话历史、多分类 |
| 👤 用户系统 | 登录注册、个人中心、头像上传 |
| ⚙️ 管理后台 | 内容管理、知识图谱管理、用户管理、AI 配置 |

## 技术栈

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue.js | ^3.5.21 | 渐进式前端框架 |
| Vue Router | ^4.5.1 | 客户端路由 |
| Vite | ^7.1.7 | 现代化构建工具 |
| Font Awesome | ^7.0.1 | 图标库 |

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Flask | 2.3.3 | Python Web 框架（用户认证、文化资源、知识图谱、AI助手） |
| Flask-SQLAlchemy | 3.0.5 | ORM 数据库操作 |
| Flask-CORS | 4.0.0 | 跨域资源共享 |
| Flask-JWT-Extended | 4.5.3 | JWT 身份认证 |
| PyMySQL | 1.1.0 | MySQL 数据库驱动 |
| Werkzeug | 2.3.7 | WSGI 工具库 |
| Go/Gin | 1.26+ | 社区帖子服务，含限流、熔断、缓存、Prometheus 指标 |

## 项目结构

```
HuxXiang_culture_github/
│
├── src/                          # 前端 Vue 项目
│   ├── assets/                   # 静态资源
│   │   ├── css/                  # 样式文件
│   │   └── imgs/                 # 图片资源
│   ├── components/               # 公共组件
│   │   └── CommentsSection.vue   # 评论组件
│   ├── views/                    # 页面组件
│   │   ├── HomePage.vue          # 首页
│   │   ├── CommunityPage.vue     # 社区页
│   │   ├── CreatePostPage.vue    # 发帖页
│   │   ├── PostDetailPage.vue    # 帖子详情
│   │   ├── CulturalResourcesPage.vue  # 文化资源
│   │   ├── KnowledgeGraphPage.vue     # 知识图谱
│   │   ├── AiAssistantPage.vue        # AI 助手
│   │   ├── AdminPage.vue              # 管理后台
│   │   ├── LoginView.vue         # 登录
│   │   ├── RegisterView.vue      # 注册
│   │   └── ...                   # 其他页面
│   ├── router/
│   │   └── index.js              # 路由配置
│   ├── services/
│   │   ├── api.js                # API 服务
│   │   └── authService.js        # 认证服务
│   ├── main.js                   # 入口文件
│   ├── App.vue                   # 根组件
│   └── style.css                 # 全局样式
│
├── backend/                      # 后端
│   ├── app/                      # Flask 应用工厂
│   │   └── __init__.py           # create_app() 蓝图注册
│   ├── models/                   # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── community_post.py     # 帖子/评论模型
│   │   ├── cultural_resource.py  # 文化资源模型
│   │   ├── knowledge.py          # 知识图谱模型
│   │   ├── ai_config.py          # AI 配置模型
│   │   └── conversation.py       # 对话/消息模型
│   ├── routes/                   # API 路由
│   │   ├── auth.py               # 认证路由
│   │   ├── cultural_resources.py # 文化资源路由
│   │   ├── knowledge.py          # 知识图谱路由
│   │   ├── admin_users.py        # 用户管理路由
│   │   ├── ai.py                 # AI 对话路由
│   │   ├── admin_ai_config.py    # AI 配置管理路由
│   │   └── main.py               # 通用路由
│   ├── services/ai/              # 可插拔 AI Provider 架构
│   │   ├── base.py
│   │   ├── factory.py
│   │   └── openai_compatible.py
│   ├── go_post_service/          # Go 社区服务（Gin）
│   │   ├── cmd/server/           # 入口
│   │   ├── internal/             # handler/service/repository 三层
│   │   ├── configs/              # 配置示例
│   │   └── docs/                 # 迁移文档
│   ├── app.py                    # Flask 启动入口
│   ├── config.py                 # 配置文件
│   ├── init_db.py                # 数据库初始化 + 种子数据
│   ├── .env.example              # 环境变量示例
│   └── requirements.txt          # Python 依赖
│
├── public/                       # 公共静态资源
│
├── scripts/                      # 本地启动脚本（PowerShell）
│   ├── start-local.ps1           # 一键启动
│   └── stop-local.ps1            # 停止服务
│
├── index.html                    # HTML 入口
├── package.json                  # 前端依赖
├── vite.config.js                # Vite 配置（含 API 代理）
└── README.md                     # 项目文档
```

## 环境要求

| 环境 | 要求 |
|------|------|
| Node.js | 16+ |
| Python | 3.8+ |
| Go | 1.26+ |
| MySQL | 8.0+ |
| npm / pip | 最新版本 |

## 快速开始

### 一键启动（Windows）

```powershell
# 自动安装依赖、初始化数据库、启动全部三个服务
.\scripts\start-local.ps1

# 启动并打开浏览器
.\scripts\start-local.ps1 -OpenBrowser

# 停止所有服务
.\scripts\stop-local.ps1
```

默认管理员账号：`admin` / `admin123`

### 手动启动

#### 1. 克隆项目

```bash
git clone <repository-url>
cd HuxXiang_culture_github
```

#### 2. 前端配置

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端服务启动后访问：`http://localhost:5173`

#### 3. Flask 后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 配置环境变量（复制示例并修改）
cp .env.example .env

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
python app.py
```

后端服务启动后访问：`http://127.0.0.1:5000`

#### 4. Go 社区服务

```bash
cd backend/go_post_service

# 配置环境变量
cp configs/app.env.example configs/app.env

# 运行测试
go test ./...

# 启动服务
go run ./cmd/server
```

Go 服务启动后访问：`http://127.0.0.1:8080`

### API 代理说明

Vite 开发服务器已配置代理：
- `/api/community` → Go 服务（`http://127.0.0.1:8080`）
- `/api`（其余）→ Flask（`http://127.0.0.1:5000`）

可通过环境变量 `VITE_FLASK_API_URL` 和 `VITE_COMMUNITY_API_URL` 覆盖。

### 环境变量

#### Flask（`backend/.env`）

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | MySQL 连接串 |
| `SECRET_KEY` | Flask 密钥 |
| `JWT_SECRET_KEY` | JWT 签名密钥（需与 Go 服务一致） |
| `AVATAR_UPLOAD_PATH` | 头像上传目录（可选） |

#### Go（`backend/go_post_service/configs/app.env`）

| 变量 | 说明 | 默认 |
|------|------|------|
| `DATABASE_URL` | MySQL DSN | - |
| `READ_DATABASE_URL` | 只读库 DSN（可选） | - |
| `JWT_SECRET_KEY` | JWT 密钥（需与 Flask 一致） | - |
| `GO_POST_SERVICE_ADDR` | 监听地址 | `:8080` |

## API 接口文档

### 认证接口 (auth)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录 | 否 |
| GET | `/api/auth/profile` | 获取用户信息 | 是 |
| PUT | `/api/auth/profile` | 更新用户信息 | 是 |
| POST | `/api/auth/upload-avatar` | 上传头像 | 是 |
| POST | `/api/auth/logout` | 登出 | 是 |

### 文化资源接口 (resources)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/resources` | 获取资源列表 | 否 |
| GET | `/api/resources/<id>` | 获取资源详情 | 否 |
| POST | `/api/resources/<id>/like` | 点赞资源 | 是 |
| POST | `/api/resources` | 创建资源 | 是(管理员) |

### 知识图谱接口 (knowledge)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/knowledge/nodes` | 获取所有节点 | 否 |
| GET | `/api/knowledge/nodes/<id>` | 获取节点详情 | 否 |
| POST | `/api/knowledge/nodes` | 创建节点 | 是(管理员) |
| PUT | `/api/knowledge/nodes/<id>` | 更新节点 | 是(管理员) |
| DELETE | `/api/knowledge/nodes/<id>` | 删除节点 | 是(管理员) |

### AI 助手接口 (ai)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/ai/chat` | 非流式对话 | 否 |
| POST | `/api/ai/chat/stream` | 流式对话（SSE） | 可选 |
| GET | `/api/ai/conversations` | 对话列表 | 是 |
| GET | `/api/ai/conversations/<id>` | 对话详情 | 是 |
| DELETE | `/api/ai/conversations/<id>` | 删除对话 | 是 |

### 管理后台接口 (admin)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/admin/users/` | 用户列表 | 是(管理员) |
| POST | `/api/admin/users/` | 创建用户 | 是(管理员) |
| PUT | `/api/admin/users/<id>` | 更新用户 | 是(管理员) |
| DELETE | `/api/admin/users/<id>` | 删除用户 | 是(管理员) |
| GET | `/api/admin/ai-config/` | 获取 AI 配置 | 是(管理员) |
| PUT | `/api/admin/ai-config/` | 更新 AI 配置 | 是(管理员) |
| DELETE | `/api/admin/ai-config/` | 清除 AI 配置 | 是(管理员) |
| POST | `/api/admin/ai-config/test` | 测试 AI 连接 | 是(管理员) |

### 社区帖子接口 (community - Go 服务)

所有社区接口前缀 `/api/community`，详见 [go_post_service/README.md](backend/go_post_service/README.md)。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/community/posts` | 获取帖子列表 |
| GET | `/api/community/posts/<id>` | 获取帖子详情 |
| POST | `/api/community/posts` | 发布帖子 |
| PUT | `/api/community/posts/<id>` | 更新帖子 |
| DELETE | `/api/community/posts/<id>` | 删除帖子 |
| POST | `/api/community/posts/<id>/like` | 点赞帖子 |
| GET | `/api/community/posts/<id>/comments` | 获取评论列表 |
| POST | `/api/community/posts/<id>/comments` | 添加评论 |
| DELETE | `/api/community/comments/<id>` | 删除评论 |

### 通用接口 (main)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 首页 |
| GET | `/health` | 健康检查 |

## 数据模型

### User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String | 用户名 |
| email | String | 邮箱 |
| password_hash | String | 密码哈希 |
| avatar_url | String | 头像URL |
| role | String | 角色(user/admin) |
| is_active | Boolean | 是否启用 |
| created_at | DateTime | 创建时间 |

### CommunityPost（帖子）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String | 标题 |
| content | Text | 内容 |
| author_id | Integer | 作者ID |
| category | String | 分类 |
| status | String | 状态 |
| view_count | Integer | 浏览量 |
| like_count | Integer | 点赞数 |
| comment_count | Integer | 评论数 |
| created_at | DateTime | 创建时间 |

### Comment（评论）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| content | Text | 内容 |
| author_id | Integer | 作者ID |
| post_id | Integer | 帖子ID |
| parent_id | Integer | 父评论ID（支持嵌套） |
| created_at | DateTime | 创建时间 |

### CulturalResource（文化资源）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String | 标题 |
| description | Text | 描述 |
| category | String | 分类 |
| image_url | String | 图片URL |
| created_at | DateTime | 创建时间 |

### KnowledgeNode（知识图谱节点）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 节点名称 |
| category | String | 分类 |
| node_type | String | 类型(person/place/concept/culture) |
| description | Text | 节点描述 |
| color | String | 节点颜色 |
| level | Integer | 层级 |
| position_x | Float | X坐标 |
| position_y | Float | Y坐标 |

### AIConfig（AI 配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| provider_name | String | 服务商名称 |
| api_base_url | String | API 地址 |
| api_key | String | API Key |
| model | String | 模型名称 |
| updated_at | DateTime | 更新时间 |

### Conversation（对话）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID |
| title | String | 对话标题 |
| category | String | 分类 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 使用示例

### 前端 API 调用

```javascript
// 获取帖子列表
import { get } from './services/api';

const posts = await get('/community/posts');

// 登录
import { post } from './services/api';

const result = await post('/auth/login', {
  username: 'user123',
  password: 'password123'
});

// 获取 token
const token = result.access_token;
```

### 后端模型查询

```python
from app import db
from models.user import User
from models.community_post import CommunityPost, Comment

# 查询用户
user = User.query.filter_by(username='test').first()

# 查询帖子及评论
post = CommunityPost.query.get(1)
comments = Comment.query.filter_by(post_id=1, parent_id=None).all()

# 创建帖子
new_post = CommunityPost(
    title='新帖子',
    content='帖子内容',
    author_id=user.id,
    category='讨论'
)
db.session.add(new_post)
db.session.commit()
```

## 开发规范

### 前端规范

- 使用 Vue 3 Composition API
- 组件文件使用 PascalCase 命名
- API 请求统一通过 `services/api.js` 封装
- 样式使用原生 CSS 或 SCSS
- 2 空格缩进

### 后端规范

- 遵循 Flask 蓝图画分路由
- Go 遵循 handler/service/repository 三层架构
- 使用 SQLAlchemy ORM 操作数据库
- API 返回统一 JSON 格式
- 需要认证的接口使用 JWT
- 提交信息简洁明确，如 `backend: add auth guard`

## 常见问题

### Q: 前端无法连接后端？
A: 检查后端是否启动在 `http://127.0.0.1:5000`，确认 CORS 配置正确，Vite 代理配置是否正确。

### Q: 数据库连接失败？
A: 确认 MySQL 服务已启动，配置文件中用户名密码正确，数据库已创建。默认 root/123456，数据库名 huxiang_culture。

### Q: Go 社区服务启动失败？
A: 确认已复制 `configs/app.env.example` 为 `configs/app.env` 并配置正确的数据库连接和 JWT 密钥。

### Q: AI 助手无法使用？
A: 需要管理员在管理后台的 AI 配置中填入 API Key 和模型信息，支持所有兼容 OpenAI 格式的服务商。

### Q: 如何切换到生产环境？
A: 修改 `config.py` 中的数据库 URL，使用生产级服务器（如 Gunicorn）。

## 贡献指南

1. Fork 本仓库
2. 同步上游：`git fetch upstream && git merge upstream/main`
3. 创建特性分支 (`git checkout -b feature/xxx`)
4. 提交更改 (`git commit -m 'Add xxx'`)
5. 推送分支 (`git push origin feature/xxx`)
6. 创建 Pull Request

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目作者：[作者名称]
- 邮箱：[email@example.com]
- GitHub：[https://github.com/your-repo](https://github.com/your-repo)

---

<p align="center">
  湖湘文化数字化平台 | 致力于湖湘文化的保护与传承
</p>
