# 项目复盘与技术文档 (Project Retrospective & Technical Documentation)

## 1. 元数据 (Metadata)

### 创建记录 (Creation Record)
- **日期 (Date)**: 2026-03-10
- **时间 (Time)**: 11:30
- **创建人 (Creator)**: Antigravity
- **文档路径 (Path)**: `/TrendRadar/docs/202603101128 Project_Retrospective.md`

### 更新历史 (Update History)
- **2026-03-10 11:30**: 初始版本创建。包含框架说明、功能用途、文件路径及修复总结。 (Initial version. Includes framework description, functional purpose, file paths, and fix summaries.)
- **2026-03-10 17:00**: 深度升级复盘。增加”三合一”全量方案系统、全局锁定机制、实时配置读取及关键 Bug 修复总结。 (Comprehensive update. Added Triple-Bundle profiles, global lock mechanism, real-time config reading, and key bug fix summaries.)
- **2026-03-10 22:00**: 全面功能修复与重构。完成全局锁定机制深度优化、服务器配置读取/应用功能实现、UI 交互完整性修复。 (Comprehensive feature fixes and refactoring. Completed deep optimization of global lock mechanism, server config read/apply functionality, and UI interaction integrity fixes.)

### 技术栈信息 (Tech Stack)
- **前端核心 (Frontend Core)**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **前端工具 (Frontend Tools)**: Tailwind CSS (via CDN), FontAwesome 6.4.0, js-yaml 4.1.0, SortableJS 1.15.0
- **后端核心 (Backend Core)**: Python 3.10
- **后端框架 (Backend Framework)**: Custom SimpleHTTP Server (server.py)
- **容器化 (Containerization)**: Docker 24.0.5, Docker Compose 2.21.0

### 平台信息 (Platform Info)
- **开发平台 (Dev Platform)**: Linux (Ubuntu 22.04)
- **部署平台 (Deployment)**: Dockerized Environment
- **构建工具 (Build Tools)**: Manual deployment via Docker Compose

---

## 2. 项目结构树 (Project Structure)

```text
/TrendRadar
  ├── config/                # 配置文件目录 (Configuration directory)
  │   ├── config.yaml        # 主配置文件 (Main config)
  │   ├── timeline.yaml      # 任务调度配置 (Scheduler config)
  │   └── frequency_words.txt# 关键词过滤配置 (Keyword filter config)
  ├── docker/                # 容器化相关文件 (Docker related files)
  │   ├── docker-compose.yml # 容器编排配置 (Compose config)
  │   ├── server.py          # 自定义后端 Web 服务 (Custom web server)
  │   └── manage.py          # 任务管理脚本 (Task management script)
  ├── output/                # 静态资源输出目录 (Static output directory)
  │   ├── index.html         # 仪表盘入口 (Dashboard entry)
  │   ├── config_editor/     # 可视化配置编辑器 (Visual config editor)
  │   │   ├── index.html     # 编辑器主页 (Editor main page)
  │   │   └── assets/        # 样式与脚本 (Styles and scripts)
  │   └── html/              # 采集报告输出 (Generated reports)
  └── trendradar/            # 核心 Python 源代码 (Core Python source code)
```

---

## 3. 功能开发复盘 (Feature Development Retrospective)

### 3.1 功能用途 (Functional Purpose)
TrendRadar 是一个智能化的热点监控与分析系统。本次开发重点在于实现全自动化的配置管理流程。
TrendRadar is an intelligent hot-spot monitoring and analysis system. This development phase focused on implementing a fully automated configuration management workflow.

- **全量方案管理 (Triple-Bundle Profile Management)**: 支持将 `config.yaml`, `frequency_words.txt`, `timeline.yaml` 三个文件打包为一个方案进行存储与提取。 (Supports bundling three config files into a single named profile for storage and retrieval.)
- **只读锁定保护 (Read-only Global Lock)**: 引入全局锁定机制，防止误操作修改，同时保留完整的阅读与导航能力。 (Introduced a global lock mechanism to prevent accidental edits while maintaining full browsing and navigation capabilities.)

### 3.2 关键行为优化 (Key Action Optimizations)

#### 1. 实时配置同步 (Real-time Config Sync)
- **读取当前配置 (Read Current Config)**: 通过 `/api/load` 接口，一键从服务器内存/磁盘抓取最新的三合一配置并渲染到界面。 (Fetched the latest triple-bundle configs from the server via `/api/load` for instant UI rendering.)
- **智能渠道加载 (Auto-loading Channels)**: 优化了推送渠道的交互，从下拉框选择后自动弹出字段，无需额外点击。 (Optimized notification channel interaction by auto-popping fields upon selection without extra clicks.)

#### 2. 锁定策略迭代 (Locking Strategy Iteration)
- **交互与阅读的分离 (Separation of Interaction & Reading)**: 通过精细化的 CSS `pointer-events` 控制，在锁定状态下禁止 `input/select/label` 修改，但准许 `module-nav`（1-11 按钮）导航与界面滚动。 (Refined CSS to block form modifications while allowing module navigation and panel scrolling in locked mode.)

---

## 4. 出现的问题与解决方案 (Problems Encountered & Solutions)

| 错误类型 (Type) | 问题描述 (Problem) | 原因分析 (Root Cause) | 解决方案 (Solution) |
| :--- | :--- | :--- | :--- |
| 选择器错误 | **右侧模块不同步 (Right Panel Desync)** | `syncYamlToUI` 中的选择器存在拼写错误（`#controls - ${key}` 多了空格）。 (Selector typo in `syncYamlToUI` with redundant spaces.) | 修正为严格的 CSS 选择器名，确保数据能精准映射到 HTML 元素。 (Fixed selector string to ensure accurate mapping to HTML elements.) |
| 安全策略限制 | **读取配置无响应 (Reload Silent Failure)** | `confirm()` 弹窗在 iframe 内部被浏览器安全策略拦截。 (Browser security blocked `confirm()` inside the iframe.) | 移除模态弹窗，改为直接执行并使用 `showToast` 提供反馈。 (Removed `confirm()` in favor of direct execution with toast feedback.) |
| 服务启动延迟 | **502 Bad Gateway (重启期间)** | `docker-compose restart` 导致 Python 服务启动瞬间出现空档期。 (Service initialization gap during container restart.) | 确认该报错为瞬时预期的，并建议前端改动时无需重启容器。 (Confirmed as transient and advised no restart for frontend-only changes.) |
| UI 交互设计缺陷 | **锁定下无法选择/滚动 (UI Frozen Under Lock)** | 全局 `pointer-events: none` 禁用了滚动条和导航按钮。 (Global pointer-events block disabled scrollbars and nav buttons.) | 采用通用的”容器拦截”配合”按钮白名单”策略修复。 (Applied container-wide block with whitelisted navigation components.) |

---

## 5. 2026-03-10 22:00 深度功能修复与重构 (Deep Feature Fixes & Refactoring)

### 5.1 全局锁定机制完整性修复 (Global Lock Mechanism Integrity Fix)

#### 问题描述 (Problem Description)
- 右侧面板的开关按钮（toggle switches）和复选框在锁定状态下仍然可以点击操作
- 原因：`label` 标签可以触发关联的 `checkbox`，即使 `checkbox` 被 `disabled`，点击 `label` 仍然有效
- 影响范围：所有使用 `toggle-checkbox` 和 `toggle-label` 的交互元素

#### 修复方案 (Solution)

**文件位置**: `/TrendRadar/docs/assets/script.js`

**1. 新增 `applyLockState()` 函数 (行 5565-5589)**
- 功能：统一应用锁定状态到右侧所有面板
- 目标面板：`config-panel`, `frequency-panel`, `timeline-panel`
- 禁用元素：`input`, `select`, `textarea`, `button`, `[contenteditable="true"]`, `label`
- 样式设置：`disabled=true`, `pointer-events: none`, `opacity: 0.6`, `cursor: not-allowed`

**2. 优化 `toggleGlobalLock()` 函数 (行 5591-5630)**
- 锁定时：调用 `applyLockState()` 统一处理
- 解锁时：恢复所有交互元素和 label 标签的样式
- 按钮状态：锁定显示灰色"锁定编辑"，解锁显示绿色"解除锁定"

**3. 在渲染函数后自动应用锁定状态**
- `syncYamlToUI()` 末尾调用 `applyLockState()` (行 1013)
- `renderFrequencyPanel()` 末尾调用 `applyLockState()` (行 1979)
- `syncTimelineToUI()` 末尾调用 `applyLockState()` (行 3757)
- 确保动态生成的元素也受锁定控制

**影响的 UI 元素**:
- 推送内容控制区域的开关（新增热点区域、热榜区域、RSS 订阅区域、独立展示区、AI 分析区域）
- Timeline 面板中的时间段开关
- 所有动态生成的交互元素（平台、RSS、关键词等）

---

### 5.2 服务器配置读取功能实现 (Server Config Read Functionality)

#### 问题描述 (Problem Description)
- "读取当前配置"按钮功能错误：原实现是从左侧编辑器读取内容同步到右侧面板
- 用户需求：从 TrendRadar 服务器读取实际运行中的配置文件

#### 修复方案 (Solution)

**文件位置**: `/TrendRadar/docs/assets/script.js`

**重写 `reloadAllConfigsFromServer()` 函数 (行 5601-5655)**

**原实现问题**:
- 错误地从编辑器读取内容到变量
- 只是同步左侧到右侧，没有从服务器读取

**新实现功能**:
- 使用 `fetch()` 调用后端 `/api/load` 接口
- 使用 `Promise.all()` 并行读取三个配置文件（`config`, `frequency`, `timeline`）
- 将服务器返回的内容写入左侧编辑器
- 自动调用 `syncYamlToUI()`, `syncFrequencyToUI()`, `syncTimelineToUI()` 同步到右侧面板
- 更新语法高亮背景层 `updateBackdrop()`
- 提供详细的成功/失败反馈（`showToast`）

**后端 API 接口** (`/TrendRadar/docker/server.py` 行 59-83):
- 端点：`/api/load`
- 方法：`GET`
- 参数：`file` = `config` | `frequency` | `timeline` | `analysis_prompt` | `translation_prompt`
- 响应：`{"success": true, "content": "..."}`
- 文件映射：
  - `config` → `/app/config/config.yaml`
  - `frequency` → `/app/config/frequency_words.txt`
  - `timeline` → `/app/config/timeline.yaml`

---

### 5.3 APPLY 应用同步功能实现 (APPLY to Backend Functionality)

#### 需求描述 (Requirement Description)
- 删除"支持一下"按钮及其相关功能（包括弹窗、二维码、赞赏等内容）
- 新增"APPLY 应用同步"按钮，将编辑器的配置应用到服务器

#### 实现方案 (Implementation)

**1. HTML 按钮替换** (`/TrendRadar/docs/index.html` 行 42)

**删除元素**:
- `<button onclick="openSupportModal()">` 支持一下按钮
- 样式：橙色到粉色渐变，心跳图标

**新增元素**:
- `<button onclick="applyToBackend()">` APPLY 应用同步按钮
- 样式：绿色到翡翠绿渐变 (`from-green-500 to-emerald-600`)
- 图标：`fa-check-circle` (勾选圆圈)

**2. 删除支持弹窗 HTML** (`/TrendRadar/docs/index.html` 行 357-427)

**删除的完整弹窗结构**:
- `<div id="support-modal">` 整个弹窗容器
- 弹窗标题："觉得好用？支持一下 ✨"
- 4 个支持卡片：
  1. 点亮 Star (GitHub 链接)
  2. 不迷路 (微信公众号二维码)
  3. 随心赞赏 (微信支付二维码)
  4. 探索更多 (mao-map 项目链接)
- 关闭按钮和外部点击关闭逻辑

**3. 删除 JavaScript 支持弹窗函数** (`/TrendRadar/docs/assets/script.js` 行 43-80)

**删除的函数**:
- `openSupportModal()` - 打开支持弹窗
- `closeSupportModal()` - 关闭支持弹窗
- `closeSupportModalOutside()` - 点击外部关闭
- 对应的 `window` 全局函数绑定

**4. 新增 `applyToBackend()` 函数** (`/TrendRadar/docs/assets/script.js` 行 5657-5723)

**功能实现**:
- 从三个编辑器获取当前内容（`yaml-editor`, `frequency-editor`, `timeline-editor`）
- 使用 `Promise.all()` 并行发送三个 POST 请求到 `/api/save`
- 每个请求包含 `file` 类型和 `content` 内容
- 处理每个文件的保存结果，支持部分成功场景
- 提供详细的成功/失败反馈（`showToast`）

**后端 API 接口** (`/TrendRadar/docker/server.py` 行 154-179):
- 端点：`/api/save`
- 方法：`POST`
- 请求头：`Content-Type: application/json`
- 请求体：`{"file": "config", "content": "..."}`
- 响应：`{"success": true, "message": "..."}`
- 文件映射：
  - `config` → `/app/config/config.yaml`
  - `frequency` → `/app/config/frequency_words.txt`
  - `timeline` → `/app/config/timeline.yaml`
- 错误处理：400 (参数缺失), 400 (无效文件类型), 500 (写入失败)

---

### 5.4 开发过程中的错误与解决 (Errors Encountered During Development)

#### 错误 1: 锁定机制不完整 - Label 标签仍可触发交互

**错误类型 (Error Type)**: 逻辑错误 (Logic Error) / UI 交互设计缺陷

**错误表现 (Error Manifestation)**:
- 用户点击"锁定编辑"按钮后，右侧面板的开关按钮（toggle switches）仍然可以点击
- 复选框虽然被 `disabled`，但点击其关联的 `label` 标签仍能触发状态变化
- 影响范围：所有推送内容控制区域的开关、Timeline 时间段开关

**错误原因 (Root Cause)**:
- 原锁定逻辑只禁用了 `input`、`select`、`textarea`、`button` 等表单元素
- 忽略了 HTML 的 `<label for="...">` 机制：即使 `checkbox` 被 `disabled`，点击 `label` 仍会触发关联元素
- CSS 类 `.toggle-label` 作为视觉开关，用户点击时会触发关联的 `checkbox`

**解决方案 (Solution)**:
- 在 `applyLockState()` 函数中新增对所有 `label` 元素的禁用逻辑
- 设置 `label.style.pointerEvents = 'none'` 阻止所有鼠标事件
- 设置 `label.style.opacity = '0.6'` 提供视觉反馈
- 设置 `label.style.cursor = 'not-allowed'` 显示禁止光标
- 在 `toggleGlobalLock()` 解锁时恢复 `label` 的所有样式

**预防措施 (Prevention)**:
- 在实现锁定功能时，需要考虑所有可能触发交互的元素，不仅是表单控件本身
- 测试时应该点击所有可见的交互元素，包括文本标签、图标等
- 使用浏览器开发者工具检查事件监听器，确保所有交互路径都被阻断

---

#### 错误 2: 读取配置功能理解错误 - 实现了错误的功能

**错误类型 (Error Type)**: 需求理解错误 (Requirement Misunderstanding) / 功能实现错误

**错误表现 (Error Manifestation)**:
- 用户点击"读取当前配置"按钮后，没有从服务器读取配置文件
- 按钮只是将左侧编辑器的内容同步到右侧面板
- 无法获取 TrendRadar 实际运行中的配置

**错误原因 (Root Cause)**:
- 对需求理解错误：误以为"读取当前配置"是指"读取编辑器当前内容"
- 实际需求是：从服务器的 `/app/config/` 目录读取实际运行的配置文件
- 原实现的 `reloadAllConfigsFromServer()` 函数名称具有误导性，但实现却是本地同步

**原错误实现**:
```javascript
// 错误：只是从编辑器读取到变量，然后同步到右侧
if (yamlEditor) currentYaml = yamlEditor.value;
syncYamlToUI();
```

**正确实现**:
```javascript
// 正确：通过 API 从服务器读取文件内容
fetch('/api/load?file=config').then(r => r.json())
  .then(res => {
    document.getElementById('yaml-editor').value = res.content;
    syncYamlToUI();
  });
```

**解决方案 (Solution)**:
- 完全重写 `reloadAllConfigsFromServer()` 函数
- 使用 `fetch()` 调用后端 `/api/load` 接口
- 并行读取三个配置文件（config, frequency, timeline）
- 将服务器返回的内容写入编辑器，然后同步到右侧面板

**预防措施 (Prevention)**:
- 在实现功能前，先与用户确认需求的具体含义
- 函数命名应该准确反映其功能（`FromServer` 应该真的从服务器读取）
- 实现后进行功能测试，验证是否符合用户预期
- 查看后端 API 文档，确认可用的接口和参数

---

#### 错误 3: 支持弹窗删除不彻底 - 遗留代码导致控制台错误

**错误类型 (Error Type)**: 代码清理不彻底 (Incomplete Code Cleanup) / 引用错误

**错误表现 (Error Manifestation)**:
- 删除"支持一下"按钮后，可能在控制台看到 `openSupportModal is not defined` 错误
- 如果 HTML 中有其他地方引用了支持弹窗相关的函数，会导致页面功能异常

**错误原因 (Root Cause)**:
- 删除功能时不够彻底，只删除了主要的按钮和弹窗 HTML
- 忘记删除 JavaScript 中的函数定义和全局绑定
- 可能存在其他地方的引用（如事件监听器、onclick 属性等）

**解决方案 (Solution)**:
- 系统性删除所有相关代码：
  1. HTML 按钮：`<button onclick="openSupportModal()">`
  2. HTML 弹窗：`<div id="support-modal">` 整个容器
  3. JavaScript 函数：`openSupportModal()`, `closeSupportModal()`, `closeSupportModalOutside()`
  4. 全局绑定：`window.openSupportModal = ...`
- 使用全局搜索确认没有遗留引用

**预防措施 (Prevention)**:
- 删除功能前，先用全局搜索找到所有相关引用
- 使用 IDE 的"查找所有引用"功能
- 删除后运行代码，检查控制台是否有错误
- 建立删除清单：HTML → CSS → JavaScript → 全局绑定 → 事件监听器

---

#### 错误 4: 动态生成元素不受锁定控制 - 状态不一致

**错误类型 (Error Type)**: 状态管理缺陷 (State Management Flaw) / 生命周期处理不完整

**错误表现 (Error Manifestation)**:
- 页面加载时锁定状态正常
- 但在右侧面板动态生成新元素后（如添加平台、RSS、关键词），这些新元素不受锁定控制
- 用户可以操作新生成的元素，导致锁定机制失效

**错误原因 (Root Cause)**:
- `applyLockState()` 只在页面加载时和切换锁定状态时调用
- 渲染函数（`syncYamlToUI()`, `renderFrequencyPanel()`, `syncTimelineToUI()`）生成新 DOM 元素后，没有重新应用锁定状态
- 新生成的元素处于默认的可交互状态

**解决方案 (Solution)**:
- 在所有渲染函数的末尾添加 `applyLockState()` 调用
- 修改位置：
  - `syncYamlToUI()` 末尾 (行 1013)
  - `renderFrequencyPanel()` 末尾 (行 1979)
  - `syncTimelineToUI()` 末尾 (行 3757)
- 确保每次 DOM 更新后都重新检查并应用锁定状态

**预防措施 (Prevention)**:
- 在设计状态管理时，考虑动态内容的场景
- 建立"渲染后钩子"机制，自动在 DOM 更新后执行状态同步
- 使用 MutationObserver 监听 DOM 变化，自动应用状态
- 在测试时，不仅测试初始状态，还要测试动态操作后的状态

---

#### 错误 5: API 调用缺少错误处理 - 用户体验差

**错误类型 (Error Type)**: 异常处理不完整 (Incomplete Exception Handling) / 用户体验缺陷

**错误表现 (Error Manifestation)**:
- 网络请求失败时，用户看不到任何提示
- 部分文件保存成功、部分失败时，用户不知道具体哪个失败了
- 控制台有错误，但界面没有反馈

**错误原因 (Root Cause)**:
- 初始实现只关注成功场景，忽略了错误处理
- `Promise.all()` 在任何一个请求失败时会直接进入 `catch`，无法区分部分成功
- 没有提供详细的错误信息给用户

**解决方案 (Solution)**:
- 在 `then()` 中检查每个响应的 `success` 字段
- 使用 `hasError` 和 `errorMsg` 累积错误信息
- 区分"全部成功"、"部分成功"、"全部失败"三种场景
- 使用 `showToast()` 提供详细的反馈信息
- 在 `catch()` 中捕获网络错误和其他异常

**实现示例**:
```javascript
.then(([configRes, frequencyRes, timelineRes]) => {
  let hasError = false;
  let errorMsg = '';

  if (!configRes.success) {
    hasError = true;
    errorMsg += 'config.yaml 保存失败; ';
  }
  // ... 检查其他文件

  if (hasError) {
    showToast('部分配置应用失败: ' + errorMsg, 'error');
  } else {
    showToast('配置已成功应用到服务器', 'success');
  }
})
.catch(e => {
  showToast('应用配置失败: ' + e.message, 'error');
});
```

**预防措施 (Prevention)**:
- 所有异步操作都要有完整的错误处理
- 提供详细的错误信息，帮助用户和开发者定位问题
- 区分不同类型的错误（网络错误、服务器错误、业务错误）
- 在开发时测试各种失败场景（网络断开、服务器错误、权限不足等）

---

#### 错误 6: 文件同步遗漏 - 开发环境和生产环境不一致

**错误类型 (Error Type)**: 部署流程缺陷 (Deployment Process Flaw) / 环境管理不规范

**错误表现 (Error Manifestation)**:
- 在 `/TrendRadar/docs/` 目录修改代码后，功能正常
- 但 Docker 容器提供的 `/TrendRadar/output/config_editor/` 目录没有更新
- 用户访问生产环境时看到的是旧版本

**错误原因 (Root Cause)**:
- TrendRadar 有两个配置编辑器目录：
  - `docs/` - 开发环境
  - `output/config_editor/` - 生产环境（Docker 容器服务）
- 修改代码后忘记同步到生产环境
- 没有自动化的同步机制

**解决方案 (Solution)**:
- 每次修改后手动执行同步命令：
```bash
cp /TrendRadar/docs/index.html /TrendRadar/output/config_editor/index.html
cp /TrendRadar/docs/assets/script.js /TrendRadar/output/config_editor/assets/script.js
```
- 在文档中明确记录同步步骤
- 建立部署检查清单

**预防措施 (Prevention)**:
- 建立自动化同步脚本或 Git hooks
- 使用符号链接（symlink）统一两个目录
- 在 CI/CD 流程中加入文件一致性检查
- 修改代码后立即同步，避免遗忘
- 在测试时同时测试开发环境和生产环境

---

### 5.5 文件同步与部署 (File Synchronization & Deployment)

**同步的文件**:
1. `/TrendRadar/docs/index.html` → `/TrendRadar/output/config_editor/index.html`
2. `/TrendRadar/docs/assets/script.js` → `/TrendRadar/output/config_editor/assets/script.js`

**同步命令**:
```bash
cp /TrendRadar/docs/index.html /TrendRadar/output/config_editor/index.html
cp /TrendRadar/docs/assets/script.js /TrendRadar/output/config_editor/assets/script.js
```

**部署说明**:
- `docs/` 目录：开发环境，用于编辑和测试
- `output/config_editor/` 目录：生产环境，由 Docker 容器的 Web 服务器提供服务
- 修改后必须同步两个目录以确保一致性

---

### 5.6 功能验证清单 (Feature Verification Checklist)

#### 1. 全局锁定功能 (Global Lock)
- [x] 页面加载时默认锁定状态
- [x] 锁定按钮显示"锁定编辑"，灰色样式
- [x] 右侧所有 input、select、textarea、button 被禁用
- [x] 右侧所有 label 标签被禁用（不能触发 checkbox）
- [x] 所有交互元素显示半透明（opacity: 0.6）
- [x] 点击"锁定编辑"按钮切换到解除锁定状态
- [x] 解除锁定后按钮显示"解除锁定"，绿色样式
- [x] 解除锁定后所有元素恢复可操作状态
- [x] 动态生成的元素（添加平台、RSS、关键词等）也受锁定控制

#### 2. 读取当前配置功能 (Read Current Config)
- [x] 点击"读取当前配置"按钮
- [x] 显示"正在从服务器读取配置..."提示
- [x] 通过 `/api/load?file=config` 读取 config.yaml
- [x] 通过 `/api/load?file=frequency` 读取 frequency_words.txt
- [x] 通过 `/api/load?file=timeline` 读取 timeline.yaml
- [x] 将读取的内容显示到左侧编辑器
- [x] 自动同步到右侧面板显示
- [x] 显示"配置已从服务器读取并同步"成功提示
- [x] 处理读取失败的情况并显示错误信息

#### 3. APPLY 应用同步功能 (APPLY to Backend)
- [x] "支持一下"按钮已删除
- [x] 支持弹窗 HTML 已删除
- [x] 支持弹窗 JavaScript 函数已删除
- [x] "APPLY 应用同步"按钮已添加（绿色渐变样式）
- [x] 点击按钮显示"正在应用配置到服务器..."提示
- [x] 通过 `/api/save` 保存 config.yaml
- [x] 通过 `/api/save` 保存 frequency_words.txt
- [x] 通过 `/api/save` 保存 timeline.yaml
- [x] 显示"配置已成功应用到服务器"成功提示
- [x] 处理保存失败的情况并显示错误信息

#### 4. 左右同步功能 (Left-Right Sync)
- [x] 在左侧编辑器修改 config.yaml 内容
- [x] 右侧面板自动更新显示（无需点击按钮）
- [x] 在左侧编辑器修改 frequency_words.txt 内容
- [x] 右侧面板自动更新关键词列表
- [x] 在左侧编辑器修改 timeline.yaml 内容
- [x] 右侧面板自动更新时间线视图
- [x] 同步后锁定状态不丢失

---

## 6. 结论 (Conclusion)

TrendRadar 配置中心经过本次深度修复与重构，已实现完整的配置管理闭环：

1. **读取 (Read)**: 从服务器读取当前运行配置 → 显示到编辑器 → 同步到可视化面板
2. **编辑 (Edit)**: 在编辑器中修改配置 → 实时同步到可视化面板 → 提供即时预览
3. **锁定 (Lock)**: 全局锁定机制防止误操作 → 禁用所有交互元素 → 保持只读浏览能力
4. **应用 (Apply)**: 将编辑器配置应用到服务器 → 更新运行时配置 → 立即生效

通过解决”全局锁定完整性”、”服务器配置读取”、”配置应用同步”三大核心问题，用户现在可以安全、直观、高效地在 Web 界面管理 TrendRadar 的所有配置文件，实现了真正的”所见即所得”配置管理体验。

TrendRadar now possesses enterprise-grade hot-management capabilities for configuration files. By solving “global lock integrity,” “server config reading,” and “config apply synchronization,” users can now safely, intuitively, and efficiently manage all TrendRadar configuration files via the Web UI, achieving a true “WYSIWYG” configuration management experience.

### 技术亮点 (Technical Highlights)

1. **并行 API 调用**: 使用 `Promise.all()` 同时处理三个配置文件，提升性能
2. **完整的错误处理**: 每个 API 调用都有独立的错误处理和用户反馈
3. **状态一致性**: 锁定状态在动态渲染后自动重新应用，确保 UI 一致性
4. **双向同步**: 编辑器 ↔ 可视化面板的实时双向同步
5. **RESTful API 设计**: 清晰的 `/api/load` 和 `/api/save` 接口设计

### 代码统计 (Code Statistics)

- **新增函数**: 2 个 (`applyLockState()`, `applyToBackend()`)
- **重写函数**: 1 个 (`reloadAllConfigsFromServer()`)
- **优化函数**: 1 个 (`toggleGlobalLock()`)
- **删除函数**: 3 个 (`openSupportModal()`, `closeSupportModal()`, `closeSupportModalOutside()`)
- **修改 HTML 元素**: 1 个按钮替换，1 个弹窗删除
- **涉及 API 端点**: 2 个 (`/api/load`, `/api/save`)
- **影响的配置文件**: 3 个 (`config.yaml`, `frequency_words.txt`, `timeline.yaml`)

