# 单选刷题系统 - 升级改造进度文档

> 本文档记录每次迭代的完成内容、遇到的问题及解决方案。
> 用于跟踪开发进度，防止异常中断后丢失上下文，方便重连。

---

## Step 1: 修复管理员密码

**状态**: ✅ 已完成

### 完成内容

| 文件 | 变更 |
|------|------|
| `.env` | `DEFAULT_ADMIN_PASSWORD` 从 `admin123` → `Admin@123` |
| `.env.example` | 同步修改为 `Admin@123` |
| `backend/app/config.py` | 默认值从 `admin123` → `Admin@123` |
| `backend/app/main.py` | `init_default_admin()` 增强：现在会检测管理员已存在但密码与 .env 配置不一致时，自动更新为新密码 |

### 涉及的逻辑变更

- `init_default_admin()` 函数新增 `else` 分支：当管理员已存在时，使用 `verify_password()` 校验当前密码是否与 `.env` 配置一致
- 若不一致（如老密码 `admin123` 与新密码 `Admin@123`），自动用新密码重新哈希并更新数据库
- 需 `from .services.auth_service import verify_password`（已在 `main.py` 顶部添加）

### 遇到的困难/注意事项

| # | 问题 | 解决方案 |
|---|------|----------|
| 1 | 数据库中已有的管理员密码是 bcrypt 哈希，无法直接对比 | 使用 `verify_password(plaintext, hash)` 验证是否匹配，不匹配则更新 |

### 密码强度验证

新密码 `Admin@123` 满足所有规则：
- ✅ 长度 ≥ 8
- ✅ 包含大写字母（A）
- ✅ 包含小写字母（dmin）
- ✅ 包含数字（123）
- ✅ 包含特殊字符（@）

### 已清理旧容器并重建

- `docker compose down -v` 清除旧数据卷（含旧密码哈希）
- `docker compose up -d --build` 重新构建并启动
- 验证：新密码 `Admin@123` 登录成功 ✓

### 补充修改

| 文件 | 变更 |
|------|------|
| `README.md` | 默认密码 `admin123` → `Admin@123`（两处：简介 + 环境变量表） |
| `docker-compose.yml` | 默认值 `admin123` → `Admin@123` |

### 下一步

→ Step 2: 分类系统 - 后端（Category 模型 + CRUD 路由 + Question 关联）

---

## Step 2: 分类系统 - 后端

**状态**: ✅ 已完成

### 完成内容

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/models/category.py` | **新建** | `Category` 模型（id/name/description/created_at/updated_at），name 字段 unique 索引 |
| `backend/app/models/question.py` | 修改 | 添加 `category_id` 外键（FK → categories.id）+ `category` 关系（lazy="joined"） |
| `backend/app/models/__init__.py` | 修改 | 导出 `Category` 模型 |
| `backend/app/schemas/category.py` | **新建** | `CategoryCreate/Update/Response/ListResponse` 完整 Pydantic schema |
| `backend/app/schemas/question.py` | 修改 | 所有 Question schema 增加 `category_id: Optional[int]` |
| `backend/app/schemas/practice.py` | 修改 | `PracticeHistoryItem` 增加 `category_id` 字段 |
| `backend/app/services/category_service.py` | **新建** | 分类 CRUD 服务（创建带名称去重、删除前检查题目关联） |
| `backend/app/services/question_service.py` | 修改 | `get_question_list` 增加 `category_id` 筛选参数 |
| `backend/app/services/practice_service.py` | 修改 | `get_random_question`/`get_history` 增加 `category_id` 筛选 |
| `backend/app/services/import_service.py` | 修改 | `_row_to_question` 支持可选的 `category_id` 导入字段 |
| `backend/app/routers/categories.py` | **新建** | 分类 CRUD 路由（CRUD + `/all` 全量列表供下拉选择） |
| `backend/app/routers/questions.py` | 修改 | `list_questions` 增加 `category_id` 查询参数 |
| `backend/app/routers/practice.py` | 修改 | `get_random_question`/`get_history` 增加 `category_id` 参数 |
| `backend/app/main.py` | 修改 | 导入 `Category` 模型 + 注册 `categories` 路由 |

### 接口清单

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/categories` | 登录 | 分类列表（分页+关键词） |
| GET | `/api/categories/all` | 登录 | 全部分类（不分页，前端下拉用） |
| POST | `/api/categories` | admin | 创建分类 |
| GET | `/api/categories/{id}` | 登录 | 分类详情 |
| PUT | `/api/categories/{id}` | admin | 更新分类 |
| DELETE | `/api/categories/{id}` | admin | 删除分类（需先移除题目关联） |
| GET | `/api/questions?category_id=N` | 登录 | 按分类筛选题目 |
| GET | `/api/practice/random?category_id=N` | 学生 | 按分类随机抽题 |
| GET | `/api/practice/history?category_id=N` | 学生 | 按分类筛选历史 |

### 遇到的困难/注意事项

| # | 问题 | 解决方案 |
|---|------|----------|
| 1 | 旧数据库中有已存在的管理员（`admin123` 哈希），Docker 重启时我们的密码自动迁移代码未触发 | 原因：之前是 `docker compose up -d`（容器未重建）。**解决方案**：`docker compose down -v` 清理卷后重建即可。生产环境中如果已有数据，手动执行一次密码更新或管理后台重置即可 |
| 2 | `PracticeResult` 引用了 `QuestionResponse`（在 `schemas/practice.py` 中），移除导入后需恢复 | 在 `schemas/practice.py` 中恢复 `from .question import QuestionResponse` 导入 |
| 3 | `subject` 字段保留不删除，与 `category_id` 并存 | 向后兼容：既有的导入文件和题库仍可用 `subject`，新数据推荐使用 `category_id` |

### 下一步

→ Step 3: 分类系统 - 前端

---

## Step 3: 分类系统 - 前端

**状态**: ✅ 已完成

### 完成内容

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/api/category.js` | **新建** | 分类 API（`getAllCategories`/`getCategories`/`createCategory`/`updateCategory`/`deleteCategory`） |
| `frontend/src/views/Categories.vue` | **新建** | 分类管理页面（表格列表 + 搜索 + 新增/编辑弹窗 + 删除确认） |
| `frontend/src/router/index.js` | 修改 | 添加 `/categories` 路由（admin/teacher 可访问） |
| `frontend/src/views/Layout.vue` | 修改 | 侧边栏「题库管理」子菜单增加「分类管理」入口 |
| `frontend/src/views/Questions.vue` | 修改 | 筛选栏增加分类下拉选择器；表格增加「分类」列显示分类名称；详情弹窗显示分类信息 |
| `frontend/src/views/QuestionEdit.vue` | 修改 | 学科输入框改为分类下拉选择器（从 API 获取分类列表）；保留原有学科字段作为可选标签 |
| `frontend/src/views/Practice.vue` | 修改 | 题目卡片上方增加分类/难度筛选条；随机抽题传递筛选参数；题目标签显示分类名称 |
| `frontend/src/api/practice.js` | 修改 | `getRandomQuestion()` 增加 `params` 参数支持 `category_id` 过滤 |

### 详细变更说明

1. **分类管理页面** (`Categories.vue`)：完整的 CRUD 页面，支持分类名称搜索、分页表格、新增/编辑弹窗（带表单验证）、删除确认（后端检查题目关联，无法删除时返回错误提示）

2. **题库管理集成** (`Questions.vue`)：
   - 筛选条件新增「分类」下拉选择器，排序在「学科」之前
   - 表格新增「分类」列，通过 `category_id` 映射到分类名称
   - 题目详情弹窗增加「分类」显示项

3. **题目编辑集成** (`QuestionEdit.vue`)：
   - 「分类」改为下拉选择器，从 `GET /api/categories/all` 获取全量分类列表
   - 保留「学科标签」输入框作为可选标签字段，用于向下兼容

4. **练习模式集成** (`Practice.vue`)：
   - 统计卡片下方增加分类/难度筛选栏
   - 切换筛选条件自动重新抽题
   - 题目标签优先显示分类名称，降级到学科字段

5. **侧边栏与路由**：
   - 分类管理位于「题库管理」子菜单下，仅 admin/teacher 可见
   - 路由 `/categories`，权限角色 `['admin', 'teacher']`

### 遇到的困难/注意事项

| # | 问题 | 解决方案 |
|---|------|----------|
| 1 | `Categories.vue` 删除分类时需处理后端 400 错误（关联题目） | 在 `catch` 中提取 `err.response.data.detail` 显示给用户 |
| 2 | 题目详情弹窗中 `category_id` 需映射为 `category_name` | 添加 `categoryName()` 辅助方法，通过 `categories` 数组查找匹配 |

### 构建验证

- `docker compose up -d --build` ✅ 构建成功
- 前端 dist 编译完成，所有容器启动正常
- 前端页面可正常加载

### 下一步

→ Step 4: 考试模式 - 后端

---

## Step 4: 考试模式 - 后端

**状态**: ✅ 已完成

### 完成内容

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/models/exam.py` | **新建** | 4 个模型：`Exam`、`ExamQuestion`、`ExamAttempt`、`ExamAnswer` |
| `backend/app/schemas/exam.py` | **新建** | 全流程 Schema：CRUD + 开始考试 + 提交 + 结果 + 历史记录 |
| `backend/app/services/exam_service.py` | **新建** | 完整业务逻辑：CRUD + 随机选题 + 开始考试 + 自动评分 + 超时检查 |
| `backend/app/routers/exams.py` | **新建** | 9 个 API 端点 |
| `backend/app/models/__init__.py` | 修改 | 导出 Exam 系列模型 |
| `backend/app/routers/__init__.py` | 修改 | 添加 exams 模块导出 |
| `backend/app/main.py` | 修改 | 导入 Exam 模型 + 注册 exams 路由 |

### 数据模型

**Exam** (`exams`):
| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | VARCHAR(200) | 考试标题 |
| `description` | TEXT | 考试说明 |
| `category_id` | FK→categories | 限定分类（可选） |
| `difficulty` | VARCHAR(10) | 限定难度（easy/medium/hard，可选） |
| `question_count` | INT | 题目数量 |
| `time_limit_minutes` | INT | 时间限制（分钟） |
| `passing_score` | INT | 及格分数（0-100） |
| `shuffle_questions` | BOOL | 是否随机打乱题序 |
| `created_by` | FK→users | 创建者 |
| `is_active` | BOOL | 是否启用 |

**ExamQuestion** (`exam_questions`): Exam 与 Question 的多对多关联表，含 `sort_order` 排序

**ExamAttempt** (`exam_attempts`): 考试记录，含 `status`（in_progress/submitted/timed_out）、`score`、`correct_count`

**ExamAnswer** (`exam_answers`): 单题作答记录，含 `selected_answer`（A-D）和 `is_correct` 判定

### API 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/exams` | 登录 | 考试列表（学生只看已发布，管理员看全部） |
| POST | `/api/exams` | admin/teacher | 创建考试（自动按条件随机选题） |
| GET | `/api/exams/{id}` | 登录 | 考试详情 |
| PUT | `/api/exams/{id}` | admin/teacher | 更新考试（变化时自动重新选题） |
| DELETE | `/api/exams/{id}` | admin/teacher | 删除考试（级联清理） |
| GET | `/api/exams/{id}/questions` | 登录 | 查看考试题目列表 |
| POST | `/api/exams/{id}/start` | 学生 | 开始考试（返回题目，不含答案） |
| POST | `/api/exams/{id}/submit` | 学生 | 提交答案（自动评分 + 超时检查） |
| GET | `/api/exams/attempt/{id}/result` | 学生 | 考试结果详情 |
| GET | `/api/exams/attempts/mine` | 学生 | 我的考试记录 |

### 关键逻辑

1. **创建考试时自动选题**: 根据 `category_id`/`difficulty` 筛选条件，从题库中随机抽取指定数量的题目
2. **开始考试**: 检查是否已有进行中的考试（防止重复开始）→ 创建 `ExamAttempt` 和对应的空 `ExamAnswer` 记录 → 按 `shuffle_questions` 配置决定是否打乱返回
3. **提交评分**: 遍历 `ExamAnswer` 匹配用户提交的答案 → 逐题判定 `is_correct` → 计算总分 → 检查是否超时
4. **更新考试**: 若 `question_count`/`category_id`/`difficulty` 变化，自动清理旧选题并重新随机选题
5. **删除考试**: 级联删除 `ExamAnswer` → `ExamAttempt` → `ExamQuestion` → `Exam`

### 构建验证

- `docker compose up -d --build backend` ✅ 构建成功
- `GET /api/exams` 返回 `{"total":0,"items":[]}` ✅
- `POST /api/exams` 创建考试成功（id=1）✅
- API 文档 http://localhost:8000/docs 可查看所有考试相关端点

### 下一步

→ Step 5: 考试模式 - 前端

---

## Step 5: 考试模式 - 前端

**状态**: ✅ 已完成

### 完成内容

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/api/exam.js` | **新建** | 考试模块 API 封装（10 个接口） |
| `frontend/src/views/ExamList.vue` | **新建** | 考试中心页（管理员表格视图 + 学生卡片视图） |
| `frontend/src/views/ExamTaking.vue` | **新建** | 考试进行页（倒计时 + 题号导航 + 逐题作答 + 交卷确认） |
| `frontend/src/views/ExamResult.vue` | **新建** | 考试结果页（得分/用时/及格线 + 逐题答案解析） |
| `frontend/src/views/ExamHistory.vue` | **新建** | 考试记录页（状态标签 + 得分 + 正确率 + 查看结果） |
| `frontend/src/router/index.js` | 修改 | 添加 5 个考试路由（ExamList/ExamTaking/ExamResult/ExamResultById/ExamHistory） |
| `frontend/src/views/Layout.vue` | 修改 | 侧边栏添加「考试中心」和「考试记录」菜单项 |

### 页面功能详解

#### 1. 考试中心 (`ExamList.vue`)
- **管理员/教师视图**：表格列表（ID/标题/分类/题数/时长/及格分/状态/创建者/操作）
  - 创建考试对话框：标题、说明、分类、难度、题数、时间限制、及格分、打乱题序
  - 编辑考试：同创建对话框，回填已有数据
  - 切换发布/关闭状态
  - 删除考试（带确认弹窗，级联清理关联数据）
- **学生视图**：卡片布局，显示考试标题/说明/分类/题数/时长，点击「开始考试」
  - 如已有进行中的考试，弹窗提示并引导跳转

#### 2. 考试进行 (`ExamTaking.vue`)
- **顶部栏**（sticky）：考试标题 + 题号进度 + 倒计时 + 交卷按钮
- **题号进度条**：用圆点导航显示每题的作答状态
  - 绿色已答 / 蓝色当前 / 灰色未答
  - 点击圆点可跳转
- **题目区**：显示题目文本 + 四个选项（单选，选中高亮）
- **导航**：上一题 / 下一题（最后一题显示「完成！去交卷」）
- **倒计时实现**：
  - 使用 `localStorage` 存储结束时间戳，页面刷新不丢失
  - `setInterval` 每秒更新，最后 120 秒变红闪烁
  - 超时自动交卷
- **交卷确认**：弹窗显示已作答/未作答数量
- **状态持久化**：`sessionStorage` 保存作答和进度，刷新页面可恢复

#### 3. 考试结果 (`ExamResult.vue`)
- **顶部卡片**：通过/未通过渐变背景，大型图标 + 得分/正确数/用时/及格线四项数据展示
- **逐题答案解析**：每题显示难度标签、题目、各选项标记（绿色正确/红色错误）、你的答案 vs 正确答案
- **操作**：返回考试列表 / 查看考试记录

#### 4. 考试记录 (`ExamHistory.vue`)
- 表格：考试名称 / 状态（进行中-黄/已交卷-绿/超时-红）/ 得分 / 正确率 / 结果图标 / 开始时间
- 未完成的考试「查看结果」按钮禁用
- 点击查看结果跳转至考试结果页面

### API 封装 (`api/exam.js`)

| 函数 | 方法 | 路径 |
|------|------|------|
| `getExams` | GET | `/api/exams` |
| `getExam` | GET | `/api/exams/{id}` |
| `createExam` | POST | `/api/exams` |
| `updateExam` | PUT | `/api/exams/{id}` |
| `deleteExam` | DELETE | `/api/exams/{id}` |
| `getExamQuestions` | GET | `/api/exams/{id}/questions` |
| `startExam` | POST | `/api/exams/{id}/start` |
| `submitExam` | POST | `/api/exams/{id}/submit` |
| `getExamResult` | GET | `/api/exams/attempt/{attemptId}/result` |
| `getMyExamAttempts` | GET | `/api/exams/attempts/mine` |

### 构建验证

- `docker compose up -d --build` 前端构建成功 ✅
- 前端页面 http://localhost 可正常加载 ✅

### 下一步

→ Step 6: 增强练习模式

---

## Step 6: 增强练习模式

**状态**: ✅ 已完成

### 完成内容

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/routers/practice.py` | 修改 | `get_random_question` 增加 `difficulty` 查询参数 |
| `backend/app/services/practice_service.py` | 修改 | `get_random_question` 服务层增加 `difficulty` 筛选逻辑 |
| `frontend/src/views/Practice.vue` | ✅ 已有 | 分类/难度筛选已在 Step 3 实现，筛选切换自动重新抽题 |
| `frontend/src/views/History.vue` | 修改 | 练习记录增加分类筛选下拉 |

### 增强点

1. **Practice.vue**（已在 Step 3 实现）：
   - 分类下拉筛选（从 API 加载全量分类列表）
   - 难度下拉筛选（简单/中等/困难）
   - 切换筛选条件自动调用 `getRandomQuestion(params)` 重新抽题
   - 题目标签显示分类名称（降级为 subject 字段）

2. **后端增强**（本次新增）：
   - `GET /api/practice/random` 现在支持 `difficulty=easy|medium|hard` 参数
   - 由 `practice_service.get_random_question()` 执行 `Question.difficulty == difficulty` 筛选

3. **History.vue**（本次增强）：
   - 筛选条件从「学科输入框」改为「分类下拉选择器」
   - 保留难度筛选
   - 分类从 API 动态加载

### 构建验证

- `docker compose up -d --build` 后端构建成功 ✅
- `GET /api/practice/random?difficulty=easy` 返回正确的题目 ✅

---

## Step 7: 集成测试 + 部署

**状态**: ✅ 已完成

### 集成测试结果

#### 考试全流程测试

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 创建 10 道测试题目（easy×3, medium×3, hard×4） | ✅ 全部成功 |
| 2 | 管理员创建考试（5 题，10 分钟，60 分及格） | ✅ 自动随机选题成功 |
| 3 | 学生开始考试 | ✅ 返回 5 道题，不含答案 |
| 4 | 学生提交答案（全部选 B） | ✅ 得分 100，5/5 正确，通过 |
| 5 | 查询考试结果详情（逐题判定 + 正确答案） | ✅ 正确返回 |
| 6 | 查询考试历史记录 | ✅ 记录完整 |
| 7 | 练习模式无筛选抽题 | ✅ 随机返回题目 |
| 8 | 练习模式带难度筛选 | ✅ 返回 easy 难度题目 |
| 9 | 前端页面加载 | ✅ HTTP 200，标题 "刷单选题系统" |
| 10 | Swagger API 文档 | ✅ http://localhost:8000/docs 可访问 |

#### 考试核心逻辑验证

- ✅ 创建考试时自动随机选题（按 category_id/difficulty 条件过滤）
- ✅ 开始考试时检查重复进行中
- ✅ 提交答案逐题判定正确性
- ✅ 超时检查（elapsed > time_limit_minutes * 60）
- ✅ 及格判定（score >= passing_score）
- ✅ 考试记录持久化，可反复查看结果
- ✅ 倒计时跨页面刷新不丢失（localStorage 存结束时间戳）
- ✅ 状态保存跨刷新不丢失（sessionStorage）

### Docker 部署

```
docker compose up -d --build
```

| 容器 | 镜像 | 端口 | 状态 |
|------|------|------|------|
| quiz-frontend | single-choice-practice-frontend | 80:80 | ✅ Healthy |
| quiz-backend | single-choice-practice-backend | 8000:8000 | ✅ Healthy |

### 新增路由清单

| 路径 | 名称 | 组件 | 说明 |
|------|------|------|------|
| `/exams` | Exams | ExamList | 考试中心（创建/参加） |
| `/exam-taking` | ExamTaking | ExamTaking | 考试进行（倒计时） |
| `/exam-result` | ExamResult | ExamResult | 考试结果 |
| `/exam-result/:attemptId?` | ExamResultById | ExamResult | 按 ID 查看结果 |
| `/exam-history` | ExamHistory | ExamHistory | 考试记录 |

### 侧边栏菜单（新增 2 项）

| 菜单项 | 图标 | 路径 |
|--------|------|------|
| 考试中心 | tickets | /exams |
| 考试记录 | document-copy | /exam-history |

---

---

## Step 8: 批量导入 10000 道题目

**状态**: ✅ 已完成

### 完成内容

- 从「完整题库（带解析）.xlsx」导入了 **10000 道** 选择题（全部为计算机基础类题目，难度分布 easy/medium/hard）
- 自动创建了 10 个分类文件夹（计算机基础、计算机应用基础、计算机操作系统、数据库、编程语言、数据结构与算法、计算机网络、软件工程、信息安全、办公自动化）
- 通过 SQLAlchemy 批量导入脚本，按行读取 Excel 并写入 SQLite
- API 验证通过：`GET /api/questions?page=1&page_size=5` 返回 10000 题总数

### 导入脚本逻辑

| 步骤 | 操作 |
|------|------|
| 1 | 用 `openpyxl` 读取 Excel 题库文件 |
| 2 | 遍历每行数据：科目 → 映射分类（含模糊匹配 fallback）；难度转换（已存在 or FALLBACK） |
| 3 | 去重后创建分类记录，再插入题目 |
| 4 | 分类未命中时 fallback 到已有分类 |

### 数据统计

- 总题目数：**10000**
- 分类数：**10**
- 来源文件：`G:\Documents\完整题库（带解析）.xlsx`

### 注意事项

- 导入脚本和 Excel 源文件已清理，不提交到 Git
- `*.xlsx` 和 `import_questions.py` 已加入 `.gitignore`
- 如后续需要重新导入，需将 Excel 复制到容器 `quiz-backend:/app/` 目录

---

## 项目完成状态总览

| Step | 内容 | 状态 |
|------|------|------|
| Step 1 | 修复管理员密码 | ✅ |
| Step 2 | 分类系统 - 后端 | ✅ |
| Step 3 | 分类系统 - 前端 | ✅ |
| Step 4 | 考试模式 - 后端 | ✅ |
| Step 5 | 考试模式 - 前端 | ✅ |
| Step 6 | 增强练习模式 | ✅ |
| Step 7 | 集成测试 + 部署 | ✅ |
| Step 8 | 批量导入 10000 道题目 | ✅ |
