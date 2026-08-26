# 湖湘文化数字化平台

[![Vue 3](https://img.shields.io/badge/Vue-3.5-42b883?style=flat&logo=vue.js)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?style=flat&logo=flask)](https://flask.palletsprojects.com)
[![Go](https://img.shields.io/badge/Go-1.26-00ADD8?style=flat&logo=go)](https://go.dev)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-00758F?style=flat&logo=mysql)](https://www.mysql.com)

## 项目简介

湖湘文化数字化平台是一个通过数字化手段展示、传播和传承湖湘文化的综合性 Web 应用。采用前后端分离架构，前端 Vue 3 + Vite，后端拆分为 Flask（用户认证 + 文化资源）与 Go/Gin（社区帖子）两个服务。

## 核心功能

| 模块 | 说明 |
|------|------|
| 首页 | 平台门户，功能入口 |
| 文化资源库 | 历史遗迹、传统艺术、诗词、美食等资源展示 |
| 互动社区 | 用户发帖、评论、点赞（Go 服务） |
| 知识图谱 | 文化元素关联可视化 |
| 数字化展示 | Unity WebGL 3D 体验、诗词数字化、建筑 3D |
| AI 助手 | 智能问答 |
| 用户系统 | 登录注册、个人中心、头像上传 |
| 管理后台 | 内容管理、用户管理 |

## 技术栈

### 前端
- Vue 3 + Vue Router 4 + Vite 7
- Font Awesome 图标库

### 后端
- **Flask**：用户认证、文化资源 API（端口 5000）
- **Go/Gin**：社区帖子 API，含限流、熔断、缓存、Prometheus 指标（端口 8080）
- MySQL 8.0 + SQLAlchemy（Flask）/ sqlx（Go）
- JWT 身份认证

## 项目结构

```
HuxXiang_culture_github/
├── src/                          # 前端 Vue 项目
│   ├── assets/                   # 静态资源（css、imgs）
│   ├── components/               # 公共组件（Navbar、CommentsSection）
│   ├── views/                    # 页面组件
│   ├── router/index.js           # 路由配置
│   ├── services/                 # API 服务（api.js、authService.js）
│   ├── main.js                   # 入口文件
│   ├── App.vue                   # 根组件
│   └── style.css                 # 全局样式
├── backend/                      # 后端
│   ├── app/                      # Flask 应用工厂（__init__.py）
│   ├── models/                   # 数据模型（user、cultural_resource）
│   ├── routes/                   # API 路由（auth、cultural_resources、main）
│   ├── go_post_service/          # Go 社区服务（Gin）
│   │   ├── cmd/server/           # 入口
│   │   ├── internal/             # handler/service/repository 三层
│   │   ├── configs/              # 配置示例
│   │   └── docs/                 # 迁移文档
│   ├── app.py                    # Flask 启动入口
│   ├── config.py                 # 配置
│   ├── init_db.py                # 数据库初始化 + 种子数据
│   └── requirements.txt          # Python 依赖
├── public/                       # 公共静态资源（含 Unity WebGL 构建）
├── scripts/                      # 本地启动脚本（PowerShell）
├── index.html                    # HTML 入口
├── package.json                  # 前端依赖
├── vite.config.js                # Vite 配置（含 API 代理）
└── README.md
```

## 环境要求

| 环境 | 要求 |
|------|------|
| Node.js | 16+ |
| Python | 3.8+ |
| Go | 1.26+ |
| MySQL | 8.0+ |

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

#### 2. 前端

```bash
npm install
npm run dev          # http://localhost:5173
npm run build        # 生产构建
```

#### 3. Flask 后端

```bash
cd backend

# 配置环境变量（复制示例并修改）
cp .env.example .env

pip install -r requirements.txt
python init_db.py    # 创建表 + 种子数据
python app.py        # http://127.0.0.1:5000
```

#### 4. Go 社区服务

```bash
cd backend/go_post_service

# 配置环境变量
cp configs/app.env.example configs/app.env

go test ./...        # 运行测试
go run ./cmd/server  # http://127.0.0.1:8080
```

### API 代理说明

Vite 开发服务器已配置代理：
- `/api/community` → Go 服务（`http://127.0.0.1:8080`）
- `/api`（其余）→ Flask（`http://127.0.0.1:5000`）

可通过环境变量 `VITE_FLASK_API_URL` 和 `VITE_COMMUNITY_API_URL` 覆盖。

## API 接口

### Flask（端口 5000）

**认证** `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/register` | 注册 | 否 |
| POST | `/login` | 登录 | 否 |
| GET | `/profile` | 获取用户信息 | 是 |
| PUT | `/profile` | 更新用户信息 | 是 |
| POST | `/upload-avatar` | 上传头像 | 是 |
| POST | `/logout` | 登出 | 是 |

**文化资源** `/api/resources`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/` | 资源列表（支持分页、分类、搜索） | 否 |
| GET | `/<id>` | 资源详情 | 否 |
| POST | `/` | 创建资源 | 是(管理员) |
| POST | `/<id>/like` | 点赞 | 是 |

**通用**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |

### Go 社区服务（端口 8080）

所有社区接口前缀 `/api/community`，详见 [go_post_service/README.md](backend/go_post_service/README.md)。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/posts` | 帖子列表（分页、搜索、分类） |
| GET | `/posts/<id>` | 帖子详情 |
| POST | `/posts` | 发布帖子 |
| PUT | `/posts/<id>` | 更新帖子 |
| DELETE | `/posts/<id>` | 删除帖子 |
| POST | `/posts/<id>/like` | 点赞 |
| GET | `/posts/<id>/comments` | 评论列表 |
| POST | `/posts/<id>/comments` | 添加评论 |
| DELETE | `/comments/<id>` | 删除评论 |

## 环境变量

### Flask（`backend/.env`）

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | MySQL 连接串 |
| `SECRET_KEY` | Flask 密钥 |
| `JWT_SECRET_KEY` | JWT 签名密钥（需与 Go 服务一致） |
| `AVATAR_UPLOAD_PATH` | 头像上传目录（可选） |

### Go（`backend/go_post_service/configs/app.env`）

| 变量 | 说明 | 默认 |
|------|------|------|
| `DATABASE_URL` | MySQL DSN | - |
| `READ_DATABASE_URL` | 只读库 DSN（可选） | - |
| `JWT_SECRET_KEY` | JWT 密钥（需与 Flask 一致） | - |
| `GO_POST_SERVICE_ADDR` | 监听地址 | `:8080` |

## 开发规范

- 前端：Vue 3 Composition API，组件 PascalCase 命名，2 空格缩进
- 后端：Flask 蓝图画分路由，Go 遵循 handler/service/repository 三层
- API 返回统一 JSON 格式，认证使用 JWT
- 提交信息简洁明确，如 `backend: add auth guard`

## 贡献指南

1. Fork 本仓库
2. 同步上游：`git fetch upstream && git merge upstream/main`
3. 创建分支：`git checkout -b feature/xxx`
4. 提交更改：`git commit -m 'Add xxx'`
5. 推送：`git push origin feature/xxx`
6. 创建 Pull Request

---

<p align="center">湖湘文化数字化平台 | 致力于湖湘文化的保护与传承</p>
