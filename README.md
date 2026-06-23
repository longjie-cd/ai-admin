# AI Admin

企业级全栈管理系统，提供用户、团队、角色、权限、数据字典、API 接口、菜单等核心功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI · Python 3.10 · JWT 认证 |
| 前端 | Vue 3 · TypeScript · Tailwind CSS · shadcn-vue |
| 状态 | Pinia |
| 密码 | bcrypt |

## 功能模块

- **用户管理** — 创建/编辑用户，支持个人角色、所属团队、数据权限（个人/部门/全部）
- **团队管理** — 部门创建，成员管理，部门角色（用户角色 = 个人角色 + 部门角色）
- **角色管理** — 角色与权限的多对多关联
- **权限管理** — 细粒度权限码（`module:action` 格式）
- **数据字典** — 树形结构，支持 string/number/boolean/textarea/json 类型
- **API 接口管理** — 手动维护或通过 OpenAPI 规范 URL 批量同步
- **菜单管理** — 树形菜单，关联 API 与权限，动态渲染（超级管理员返回全量，普通用户按权限过滤）

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 启动

```bash
# 一键启动前后端
bash start.sh
```

或分别启动：

```bash
# 后端
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# 前端
cd vue
npm install
npm run dev
```

访问 [http://localhost:5173](http://localhost:5173)

### 默认账户

| 用户名 | 密码 | 权限 |
|--------|------|------|
| admin | Admin!123 | 超级管理员 |

## 项目结构

```
ai-admin/
├── api/                    # FastAPI 后端
│   ├── core/               # 配置、JWT、依赖注入、响应格式
│   ├── main.py             # 应用入口
│   └── sys/                # 业务模块
│       ├── auth/           # 登录认证
│       ├── user/           # 用户管理
│       ├── team/           # 团队（部门）管理
│       ├── role/           # 角色管理
│       ├── permission/     # 权限管理
│       ├── dict/           # 数据字典
│       ├── api_interface/  # API 接口管理
│       ├── menu/           # 菜单管理
│       └── router.py       # 统一路由注册
├── vue/                    # Vue 3 前端
│   └── src/
│       ├── api/sys/        # API 请求封装
│       ├── views/sys/      # 各模块页面
│       ├── components/     # 通用组件
│       ├── stores/         # Pinia 状态
│       ├── router/         # 路由配置
│       └── layouts/        # 布局组件
├── requirements.txt        # Python 依赖
└── start.sh                # 一键启动脚本
```

## API 文档

后端启动后访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看 Swagger 文档。

## 核心设计

### 用户角色合并

```
用户完整角色 = 个人角色 (role_ids) + 所在团队角色 (team.role_ids)
```

通过 `GET /api/sys/user/{id}/roles` 获取合并后的角色详情。

### 动态菜单渲染

- 超级管理员（`role.code == "super_admin"`）直接返回全部菜单
- 普通用户根据其完整角色拥有的权限过滤菜单树

### 数据权限

| 类型 | 说明 |
|------|------|
| `personal` | 仅访问本人数据 |
| `department` | 访问指定部门的数据 |
| `all` | 访问全部数据 |
