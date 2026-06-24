# AI Admin - 项目指南

## 项目概述
完整的企业级全栈管理系统，包含用户、团队、角色、权限、数据字典、API 接口、菜单管理等功能。

### 技术栈
- **后端**: FastAPI + Python 3.10 (内存数据库，可扩展)
- **前端**: Vue 3 + TypeScript + Tailwind CSS + shadcn-vue
- **认证**: JWT (Bearer Token)
- **密码**: bcrypt 4.0.1

## 项目结构

### 后端 (api/)
```
api/
├── core/              # 核心配置和工具
│  ├── config.py       # 配置
│  ├── security.py     # JWT、密码哈希
│  ├── deps.py         # 依赖注入
│  ├── response.py     # API 响应格式
│  └── init.py         # 初始化数据
├── main.py            # FastAPI 应用入口
└── sys/              # 系统管理模块
   ├── auth/          # 认证（登录）
   ├── user/          # 用户管理
   ├── team/          # 团队管理
   ├── role/          # 角色管理
   ├── permission/    # 权限管理
   ├── dict/          # 数据字典
   ├── api_interface/ # API 接口管理
   ├── menu/          # 菜单管理
   ├── bing/          # Bing 壁纸服务
   └── router.py      # 统一路由
```

### 前端 (vue/src/)
```
src/
├── api/              # API 定义
│  └── sys/
│     ├── user.ts
│     ├── team.ts
│     ├── role.ts
│     ├── permission.ts
│     ├── dict.ts
│     ├── api_interface.ts
│     └── menu.ts
├── views/            # 页面
├── components/       # 组件
├── stores/          # Pinia 状态管理
├── router/          # 路由
└── layouts/         # 布局
```

## 核心数据模型

### User (用户)
```python
{
  id: int,
  username: str,           # 唯一
  hashed_password: str,
  nickname: str,
  email: str,
  disabled: bool,
  role_ids: list[int],     # 个人角色
  team_id: int,            # 所属部门
  data_scope: str,         # personal|department|all
  department_ids: list[int] # 关联部门列表
}
```

### Team (部门)
```python
{
  id: int,
  name: str,
  code: str,               # 唯一
  description: str,
  role_ids: list[int],     # 部门角色
  user_ids: list[int]
}
```

### Role (角色)
```python
{
  id: int,
  name: str,
  code: str,               # 唯一
  description: str,
  permission_ids: list[int]
}
```

### Permission (权限)
```python
{
  id: int,
  name: str,
  code: str,               # 唯一，格式: "module:action"
  group: str,
  description: str
}
```

### Menu (菜单)
```python
{
  id: int,
  name: str,
  path: str,
  icon: str,
  parent_id: int,          # 树形结构
  sort: int,
  api_id: int,             # 关联 API
  permission_ids: list[int],
  children: list[Menu]
}
```

### ApiInterface (API 接口)
```python
{
  id: int,
  name: str,
  path: str,
  method: str,             # GET|POST|PUT|DELETE 等
  description: str,
  openapi_url: str         # 预留：OpenAPI 规范 URL
}
```

## API 端点列表

### 认证
- `POST /api/auth/login` - 登录

### 用户管理
- `GET /api/sys/user` - 获取用户列表
- `GET /api/sys/user/{id}` - 获取用户详情
- `POST /api/sys/user` - 创建用户
- `PUT /api/sys/user/{id}` - 更新用户
- `DELETE /api/sys/user/{id}` - 删除用户
- `GET /api/sys/user/{id}/roles` - 获取用户完整角色（个人+部门）
- `GET /api/sys/user/profile/me` - 获取当前用户信息
- `PUT /api/sys/user/profile/me` - 更新个人信息
- `POST /api/sys/user/profile/change-password` - 修改密码

### 团队管理
- `GET /api/sys/team` - 获取团队列表
- `POST /api/sys/team` - 创建团队
- `PUT /api/sys/team/{id}` - 更新团队
- `DELETE /api/sys/team/{id}` - 删除团队
- `PUT /api/sys/team/{id}/members` - 更新团队成员

### 角色管理
- `GET /api/sys/role` - 获取角色列表
- `POST /api/sys/role` - 创建角色
- `PUT /api/sys/role/{id}` - 更新角色
- `DELETE /api/sys/role/{id}` - 删除角色

### 权限管理
- `GET /api/sys/permission` - 获取权限列表
- `POST /api/sys/permission` - 创建权限
- `PUT /api/sys/permission/{id}` - 更新权限
- `DELETE /api/sys/permission/{id}` - 删除权限

### 数据字典
- `GET /api/sys/dict` - 获取字典树
- `GET /api/sys/dict/flat` - 获取字典平列表
- `POST /api/sys/dict` - 创建字典
- `PUT /api/sys/dict/{id}` - 更新字典
- `DELETE /api/sys/dict/{id}` - 删除字典

### API 接口管理
- `GET /api/sys/api` - 获取 API 接口列表
- `GET /api/sys/api/{id}` - 获取 API 接口详情
- `POST /api/sys/api` - 创建 API 接口
- `PUT /api/sys/api/{id}` - 更新 API 接口
- `DELETE /api/sys/api/{id}` - 删除 API 接口

### 菜单管理
- `GET /api/sys/menu` - 获取全部菜单（管理员视图）
- `GET /api/sys/menu/user` - 获取当前用户菜单（动态渲染）
- `GET /api/sys/menu/{id}` - 获取菜单详情
- `POST /api/sys/menu` - 创建菜单
- `PUT /api/sys/menu/{id}` - 更新菜单
- `DELETE /api/sys/menu/{id}` - 删除菜单

## 特殊实现说明

### 用户角色计算
```
用户的完整角色 = 个人角色 + 所在部门的角色
通过 GET /api/sys/user/{id}/roles 获取：
{
  personal_role_ids: [1],      # 个人直接分配的角色
  department_role_ids: [2],    # 部门提供的角色
  all_role_ids: [1, 2]         # 合并后的完整角色
}
```

### 菜单动态渲染
- **超级管理员** (`role.code == "super_admin"`) - 直接返回全部菜单
- **普通用户** - 根据权限过滤菜单
  - 获取用户的完整角色（个人+部门）
  - 获取这些角色拥有的权限
  - 返回菜单权限 ID 在用户权限范围内的菜单

### 数据权限类型
- `personal` - 用户仅能访问自己的数据
- `department` - 用户能访问所在部门及指定部门的数据
- `all` - 用户能访问全部数据

## 常见工作流

### 设置用户权限
1. 创建权限 (Permission)
2. 创建角色 (Role)，关联权限
3. 将角色分配给用户或部门

### 创建菜单结构
1. 创建根菜单
2. 创建子菜单，设置 `parent_id`
3. 为菜单关联权限 (`permission_ids`)
4. 前端通过 `GET /api/sys/menu/user` 获取动态菜单

### 管理用户数据权限
1. 创建用户时设置 `data_scope` 和 `department_ids`
2. 在数据查询时应用权限过滤（需要在业务逻辑中实现）

## 默认账户
- **用户名**: admin
- **密码**: Admin!123
- **权限**: 超级管理员（所有权限）

## 启动应用

### 后端
```bash
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

### 前端
```bash
cd vue
npm install
npm run dev
```

### 一键启动
```bash
bash start.sh
```

## 开发规范

### 后端
- 使用 FastAPI 的依赖注入 (`Depends`)
- 所有路由必须检查认证 (`get_current_user`)
- 使用 Pydantic Schema 进行数据验证
- 错误返回 `ApiResponse` 格式

### 前端
- 使用 TypeScript 类型定义
- 组件使用 `<script setup>` 语法
- API 调用通过 `src/api/` 统一管理
- 状态管理使用 Pinia

## 常见问题

### Q: 如何添加新的权限？
A: 在 permission 模块中创建新的权限记录，然后在角色中关联。

### Q: 超级管理员如何跳过权限检查？
A: 在服务层检查用户的角色，如果包含 `super_admin` 则跳过权限过滤。

### Q: 如何实现部门管理？
A: 当前通过 Team 模块实现部门，Team 可关联角色和用户。

### Q: 数据权限在哪里应用？
A: 需要在数据查询的服务层中实现，根据用户的 `data_scope` 过滤数据。

## 下一步改进方向

1. **持久化** - 替换内存数据库为 PostgreSQL/MySQL
2. **OpenAPI 同步** - 实现从 OpenAPI 规范 URL 自动同步 API 接口
3. **权限缓存** - 缓存用户权限，提高查询性能
4. **审计日志** - 记录所有数据修改操作
5. **多租户** - 支持多租户模式
6. **文件上传** - 支持头像、附件上传
