# 刷单选题系统

前后端分离的刷单选题系统，支持管理员、教师、学生三种角色，Docker 一键部署。

## 技术栈

- **后端**：Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite
- **前端**：Vue 2.7 + Element UI 2.15 + Vue Router + Vuex
- **部署**：Docker + docker-compose（Nginx 反向代理）

## 快速启动

### 前置条件

- Docker Engine 20.10+
- Docker Compose 2.0+

### 一键部署

```bash
cd single-choice-practice
docker-compose up -d --build
```

启动后访问：
- 前端页面：http://localhost
- API 文档：http://localhost:8000/docs

### 默认管理员

- 用户名：`admin`
- 密码：`admin123`

## 用户角色

| 角色 | 权限 |
|------|------|
| 管理员 | 全局管理（用户管理、题库管理、题库导入） |
| 教师 | 题库管理（CRUD 题目、批量导入） |
| 学生 | 刷题练习、查看历史记录 |

## 功能模块

1. **用户管理** - 管理员进行用户的增删改查、角色分配、密码重置
2. **题库管理** - 创建、编辑、删除题目，支持学科分类和难度分级，分页查询和多条件筛选
3. **题库导入** - 支持 Excel(.xlsx)、CSV、JSON 三种格式批量导入
4. **刷题练习** - 随机抽题（排除已答对题目）、即时判定正误、查看解析
5. **练习统计** - 总答题数、正确率等统计数据

## API 文档

启动后端后访问 http://localhost:8000/docs 查看自动生成的 Swagger 文档。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SECRET_KEY` | `change-this-...` | JWT 签名密钥（生产环境请更换） |
| `ACCESS_TOKEN_EXPIRE_HOURS` | `8` | Token 过期时间（小时） |
| `DEFAULT_ADMIN_USERNAME` | `admin` | 默认超级管理员用户名 |
| `DEFAULT_ADMIN_PASSWORD` | `admin123` | 默认超级管理员密码 |

## 安全建议（生产环境）

1. 修改 `docker-compose.yml` 中的 `SECRET_KEY` 为随机字符串
2. 修改默认管理员密码
3. 配置 HTTPS（推荐使用 Nginx + Let's Encrypt）
