# TrendRadar 可视化配置编辑器集成技术文档 / TrendRadar Visual Config Editor Integration Technical Manual

## 声明 / Declaration
本文件详细记录了 TrendRadar 可视化配置编辑器的集成设计、实现逻辑、文件路径及功能说明。
This document details the integration design, implementation logic, file paths, and functional descriptions of the TrendRadar Visual Configuration Editor.

---

## 1. 元数据 / Metadata

### 1.1 创建记录 / Creation Record
- **创建日期 (Date):** 2026-03-07
- **创建时间 (Time):** 10:10
- **创建人 (Author):** Antigravity
- **文档路径 (Path):** `/TrendRadar/docs/202603071010 Visual_Config_Integration_Manual.md`

### 1.2 更新历史 / Update History
- **2026-03-07 10:10:** 初始版本创建，涵盖 Dashboard 重构与弹窗集成逻辑。/ Initial version creation, covering Dashboard refactoring and popup integration logic.
- **2026-04-19 16:00:** 增强保存方案功能，支持方案列表显示与覆盖确认；修复锁定编辑功能的三个问题（右侧面板禁用状态、滚动功能、AI提示词编辑器）；更新品牌名称为 AiYX Data Radar。/ Enhanced profile save feature with list display and overwrite confirmation; fixed three lock edit issues (right panel disabled state, scrolling, AI prompt editors); updated brand name to AiYX Data Radar.
- **2026-04-20 14:30:** 修复数字导航按钮在锁定状态下的可用性，确保用户在锁定编辑时仍可快速定位配置模块；移除 AiYX Data Radar 标题的超链接，使文字可直接复制。/ Fixed module navigation buttons (1-11) to remain functional in locked state for quick module navigation; removed hyperlink from AiYX Data Radar title to allow direct text copying.
- **2026-04-23 08:54:** 修复 Nginx 反向代理端口配置错误（8084 → 8080），解决 502 Bad Gateway 问题；修复数据库查询字段不匹配（published_at → first_crawl_time），确保所有 API 功能正常工作。/ Fixed Nginx reverse proxy port configuration (8084 → 8080) to resolve 502 Bad Gateway; fixed database query field mismatch (published_at → first_crawl_time) to ensure all APIs work correctly.
- **2026-04-24 16:30:** 优化 AI 模型查询弹出框，添加搜索过滤功能和可调整大小功能；增强拖拽区域可视化，提升用户体验。/ Optimized AI model query modal with search filtering and resizable functionality; enhanced drag area visualization for better UX.

### 1.3 技术栈信息 / Tech Stack
- **前端核心 (Frontend Core):** HTML5, Vanilla CSS3, Vanilla JavaScript (ES6+)
- **后端框架 (Backend):** Python 3.10+ (TrendRadar Core)
- **部署工具 (Deployment):** Docker & Docker Compose
- **Web 服务 (Web Server):** Python `http.server` (Internal) / Nginx (Reverse Proxy)

### 1.4 平台信息 / Platform Info
- **开发平台 (Dev Platform):** Linux (Ubuntu/Debian recommended)
- **部署平台 (Deployment):** Docker Container (`wantcat/trendradar:latest`)
- **构建工具 (Build):** Docker Volume Mounting & In-container Patching

---

## 2. 项目结构树 / Project Structure
```text
/TrendRadar
  ├── trendradar/
  │   └── report/
  │       └── generator.py        # [Modify] 拦截首页覆盖逻辑 / Intercepted home overwrite logic
  ├── output/
  │   ├── index.html              # [New] 全局控制面板 / Global Dashboard
  │   ├── config_editor/          # [New] 编辑器静态资源 / Editor static assets
  │   │   ├── index.html          # 可视化编辑器入口 / Editor entry
  │   │   └── assets/             # 编辑器依赖资源 / Editor dependencies
  │   └── html/latest/current.html # 原始新闻报告快照 / Original news report snapshot
  └── docs/
      └── 202603071010 Visual_Config_Integration_Manual.md # 本文档 / This document
```

---

## 3. 功能复盘 / Functionality Review

### 3.1 核心功能说明 / Core Functionality
1. **全局控制面板 (Global Dashboard):** 
   - 彻底替换了原先“单篇新闻快照即首页”的僵硬逻辑。
   - 采用 `iframe` 容器技术，在根路径下无缝嵌套展示最新的新闻聚合结果。
   - Completely replaced the rigid logic where a single news snapshot served as the homepage. Uses iframe container to seamlessly display the latest news aggregates at the root path.

2. **浮动配置窗口 (Floating Config Window):**
   - **交互触发 (Trigger):** 页面右下角常驻紫色”⚙️ 可视化配置”悬浮按钮。
   - **窗口特性 (Window Features):** 
     - **可拖拽 (Draggable):** 通过原生 JS 监听标题栏实现自由移动。
     - **可缩放 (Resizable):** 利用原生 CSS `resize: both` 允许用户自由调节窗口大小。
     - **内嵌集成:** 弹窗内嵌可视化 YAML 编辑器，支持实时修改 `config.yaml`。
   - Interaction: Persistent purple “Visual Config” button at bottom-right. Features: Draggable via header, Resizable via CSS, and Embedded YAML editor inside the modal.

3. **方案管理功能 (Profile Management):**
   - **保存方案 (Save Profile):** 支持显示已保存的方案列表，用户可选择序号覆盖现有方案或输入新名称保存。覆盖时弹出确认对话框。留空则自动生成时间戳名称。
   - **提取方案 (Load Profile):** 从服务器加载已保存的方案列表，支持一键切换爬取策略。
   - **持久化存储 (Persistence):** 方案以 JSON 对象形式打包所有配置文件，存储在服务器 `profiles/` 目录，自动维持最近 5 个方案。
   - Save Profile: Display existing profiles list, allow selecting by index to overwrite or input new name. Confirmation dialog on overwrite. Auto-generate timestamp if empty.
   - Load Profile: Load saved profiles from server, one-click strategy switching.
   - Persistence: Bundle all configs as JSON, store in server `profiles/` directory, auto-maintain last 5 profiles.

4. **锁定编辑功能 (Lock Edit Mode):**
   - **默认锁定 (Default Locked):** 系统启动时默认为锁定状态，保护配置不被误修改。
   - **细粒度控制 (Fine-grained Control):** 锁定状态下，只禁用修改类按钮（APPLY、SAVE & RUN），保留浏览/加载类按钮可用。
   - **滚动保留 (Scroll Preserved):** 右侧配置面板和左侧编辑器在锁定状态下仍可滚动浏览内容。
   - **全面禁用 (Comprehensive Disable):** 右侧配置面板的所有输入元素（input、select、textarea、button）在锁定状态下显示为禁用（变灰）。
   - Default Locked: System starts in locked state to prevent accidental config changes.
   - Fine-grained Control: Only modify buttons (APPLY, SAVE & RUN) disabled; browse/load buttons remain available.
   - Scroll Preserved: Right panels and left editors remain scrollable in locked state.
   - Comprehensive Disable: All input elements in right panels show disabled state (grayed out) when locked.

### 3.2 实现路径与关键文件 / Key Files & Paths
- **前端主页 (Dashboard Entrance):** `/TrendRadar/output/index.html`
- **编辑器工作区 (Editor Workspace):** `/TrendRadar/output/config_editor/`
- **后端拦截点 (Backend Patch):** `/TrendRadar/trendradar/report/generator.py`
  - *修改点:* 注释掉了 `shutil.copy2` 到 `index.html` 的步骤，防止自定义 Dashboard 被每日生成的新闻覆盖。
  - *Patch Detail:* Commented out `shutil.copy2` to `index.html` to prevent the custom Dashboard from being overwritten by daily news reports.

### 3.2.1 Nginx 反向代理配置 / Nginx Reverse Proxy Configuration

#### 配置文件位置 / Configuration File Location
- **路径:** `/etc/nginx/sites-available/trendradar.aiyxtech.us.kg.conf`
- **启用方式:** 通过符号链接 `/etc/nginx/sites-enabled/trendradar.aiyxtech.us.kg.conf` 启用

#### 核心配置说明 / Core Configuration Details

**1. HTTP 到 HTTPS 重定向 (HTTP to HTTPS Redirect)**
```nginx
server {
    listen 80;
    server_name trendradar.aiyxtech.us.kg;
    return 301 https://$host$request_uri;
}
```
- **功能:** 将所有 HTTP 请求重定向到 HTTPS
- **状态码:** 301 (永久重定向)

**2. HTTPS 服务器配置 (HTTPS Server Configuration)**
```nginx
server {
    listen 443 ssl;
    server_name trendradar.aiyxtech.us.kg;
    
    # SSL 证书配置 / SSL Certificate Configuration
    ssl_certificate /etc/nginx/ssl/werss.crt;
    ssl_certificate_key /etc/nginx/ssl/werss.key;
}
```
- **监听端口:** 443 (HTTPS)
- **SSL 证书:** Cloudflare Universal SSL 通配符证书
- **证书路径:** `/etc/nginx/ssl/werss.crt` 和 `/etc/nginx/ssl/werss.key`

**3. 反向代理配置 (Reverse Proxy Configuration) - 关键部分**
```nginx
location / {
    proxy_pass http://127.0.0.1:8080;  # ⚠️ 必须与 Flask 服务器端口一致
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 超时配置 / Timeout Configuration
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    
    # WebSocket 支持 / WebSocket Support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # 缓冲配置 / Buffering Configuration
    chunked_transfer_encoding off;
    proxy_buffering off;
    proxy_cache off;
}
```

#### 关键配置项说明 / Key Configuration Items

| 配置项 / Item | 值 / Value | 说明 / Description |
| :--- | :--- | :--- |
| `proxy_pass` | `http://127.0.0.1:8080` | **必须与 Flask 服务器监听端口一致** / Must match Flask server listening port |
| `proxy_connect_timeout` | `300s` | 连接超时时间，适合长时间数据处理 / Connection timeout for long-running operations |
| `proxy_send_timeout` | `300s` | 发送超时时间 / Send timeout |
| `proxy_read_timeout` | `300s` | 读取超时时间 / Read timeout |
| `proxy_buffering` | `off` | 禁用缓冲，实时转发响应 / Disable buffering for real-time response forwarding |
| `proxy_cache` | `off` | 禁用缓存，确保每次请求都到达后端 / Disable caching to ensure fresh data |

#### 常见问题与排查 / Troubleshooting

**问题 1: 502 Bad Gateway 错误**
- **原因:** `proxy_pass` 指向的端口与实际 Flask 服务器端口不匹配
- **排查步骤:**
  1. 检查 Flask 服务器监听端口: `ss -tlnp | grep python`
  2. 检查 Nginx 配置中的 `proxy_pass` 端口
  3. 确保两者一致
- **修复:** 更新 `proxy_pass` 为正确的端口，然后执行 `nginx -s reload`

**问题 2: 连接超时**
- **原因:** Flask 服务器响应缓慢或未启动
- **排查步骤:**
  1. 检查 Flask 服务器是否运行: `ps aux | grep "python.*server.py"`
  2. 检查 Flask 服务器日志: `docker logs trendradar` 或查看日志文件
  3. 检查网络连接: `curl http://127.0.0.1:8080/api/search?kw=test`
- **修复:** 启动 Flask 服务器或增加超时时间

**问题 3: SSL 证书错误**
- **原因:** 证书文件不存在或路径错误
- **排查步骤:**
  1. 检查证书文件: `ls -la /etc/nginx/ssl/`
  2. 验证 Nginx 配置: `nginx -t`
- **修复:** 确保证书文件存在且路径正确

#### 配置验证与重新加载 / Configuration Validation & Reload

**验证配置语法 (Validate Configuration Syntax)**
```bash
nginx -t
# 输出: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
#       nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**重新加载配置 (Reload Configuration)**
```bash
# 方式 1: 使用 nginx 命令
nginx -s reload

# 方式 2: 使用 systemctl
systemctl reload nginx

# 方式 3: 使用 service
service nginx reload
```

**验证修复 (Verify Fix)**
```bash
# 本地测试
curl http://127.0.0.1/api/search?kw=AI

# 远程测试 (需要 HTTPS)
curl -k https://trendradar.aiyxtech.us.kg/api/search?kw=AI
```

#### 监控与日志 / Monitoring & Logging

**查看 Nginx 错误日志 (View Error Log)**
```bash
tail -f /var/log/nginx/error.log
```

**常见错误信息 (Common Error Messages)**
- `upstream timed out` - 后端服务器响应超时
- `connection refused` - 后端服务器未启动或端口错误
- `recv() failed (104: Connection reset by peer)` - 后端服务器主动关闭连接

---

## 3.3 可视化配置中心面板详细规范 / Visual Config Center Panel Detailed Specification

### 3.3.1 面板布局与结构 / Panel Layout & Structure

#### 整体架构 / Overall Architecture
```
┌─────────────────────────────────────────────────────────────┐
│  AiYX Data Radar 配置文件编辑器 / Config Editor             │
├─────────────────────────────────────────────────────────────┤
│  [锁定编辑] [读取配置] [加载默认] [读取方案] [保存方案]      │
├──────────────────────┬──────────────────────────────────────┤
│                      │                                       │
│   左侧编辑框         │      右侧配置框                       │
│   (Left Editor)      │      (Right Config Panel)             │
│                      │                                       │
│  - YAML编辑器        │  - 配置项输入框                       │
│  - 频率编辑器        │  - 下拉选择框                         │
│  - 时间线编辑器      │  - 文本区域                           │
│  - AI提示词编辑器    │  - 按钮组                             │
│                      │                                       │
│  [可滚动]            │  [可滚动] [锁定时禁用]                │
│  [锁定时只读]        │                                       │
└──────────────────────┴──────────────────────────────────────┘
```

#### 面板尺寸与响应式 / Panel Dimensions & Responsiveness
- **编辑器容器宽度 (Editor Container Width):** 100% 自适应
- **左侧编辑框宽度 (Left Editor Width):** 45% - 50%
- **右侧配置框宽度 (Right Config Width):** 50% - 55%
- **最小高度 (Minimum Height):** 600px（可通过 CSS `resize: both` 调整）
- **最大高度 (Maximum Height):** 无限制（由浏览器视口决定）

### 3.3.2 左侧编辑框详细要求 / Left Editor Panel Requirements

#### 编辑框类型与功能 / Editor Types & Functions
1. **YAML 配置编辑器 (YAML Config Editor)**
   - **ID:** `yaml-editor`
   - **功能:** 显示和编辑 `config.yaml` 的完整内容
   - **特性:**
     - 只读模式（锁定时）/ Read-only mode (when locked)
     - 语法高亮（可选）/ Syntax highlighting (optional)
     - 行号显示 / Line numbers
     - 自动换行 / Word wrap
   - **滚动同步:** 与 `yaml-backdrop` 同步滚动位置
   - **代码位置:** `/TrendRadar/output/config_editor/assets/script.js:194-198`

2. **频率配置编辑器 (Frequency Config Editor)**
   - **ID:** `frequency-editor`
   - **功能:** 显示和编辑爬取频率配置
   - **特性:** 同 YAML 编辑器
   - **滚动同步:** 与 `frequency-backdrop` 同步滚动位置

3. **时间线配置编辑器 (Timeline Config Editor)**
   - **ID:** `timeline-editor`
   - **功能:** 显示和编辑时间线相关配置
   - **特性:** 同 YAML 编辑器
   - **滚动同步:** 与 `timeline-backdrop` 同步滚动位置

4. **AI 提示词编辑器 (AI Prompt Editors)**
   - **分析提示词编辑器 (Analysis Prompt Editor)**
     - **ID:** `analysis_prompt-editor`
     - **功能:** 显示和编辑数据分析提示词
     - **滚动同步:** 与 `analysis_prompt-backdrop` 同步滚动位置
   - **翻译提示词编辑器 (Translation Prompt Editor)**
     - **ID:** `translation_prompt-editor`
     - **功能:** 显示和编辑翻译提示词
     - **滚动同步:** 与 `translation_prompt-backdrop` 同步滚动位置

#### 编辑框浏览要求 / Editor Browsing Requirements
- **滚动功能 (Scrolling):** 所有编辑框均支持垂直滚动，无论锁定状态如何
- **滚动条样式 (Scrollbar Style):** 
  - 宽度: 8px
  - 背景色: `#f0f0f0`
  - 滑块色: `#999`
  - 悬停时滑块色: `#666`
- **文本选择 (Text Selection):** 锁定状态下支持文本选择和复制（`user-select: text`）
- **指针事件 (Pointer Events):** 锁定状态下 `pointer-events: auto`，允许滚动和选择
- **只读属性 (Read-only):** 锁定状态下 `readOnly: true`，禁止编辑
- **背景色 (Background):** 锁定状态下 `background-color: #f5f5f5`（浅灰色）
- **不透明度 (Opacity):** 锁定状态下 `opacity: 0.8`（保持可见）

#### 编辑框同步机制 / Editor Sync Mechanism
```javascript
// 滚动同步函数 / Scroll Sync Function
function syncScroll(editorId, backdropId) {
  const editor = document.getElementById(editorId);
  const backdrop = document.getElementById(backdropId);
  
  editor.addEventListener('scroll', () => {
    backdrop.scrollTop = editor.scrollTop;
    backdrop.scrollLeft = editor.scrollLeft;
  });
}

// 初始化所有编辑器滚动同步 / Initialize all editor scroll sync
syncScroll('yaml-editor', 'yaml-backdrop');
syncScroll('frequency-editor', 'frequency-backdrop');
syncScroll('timeline-editor', 'timeline-backdrop');
syncScroll('analysis_prompt-editor', 'analysis_prompt-backdrop');
syncScroll('translation_prompt-editor', 'translation_prompt-backdrop');
```

### 3.3.3 右侧配置框详细要求 / Right Config Panel Requirements

#### 配置项类型与结构 / Config Item Types & Structure
1. **文本输入框 (Text Input)**
   - **HTML 标签:** `<input type="text">`
   - **锁定状态:** `disabled: true` + `pointer-events: none` + `opacity: 0.6`
   - **样式:** 边框变灰，背景色变浅
   - **交互:** 锁定时无法输入，鼠标悬停无反应

2. **下拉选择框 (Select Dropdown)**
   - **HTML 标签:** `<select>`
   - **锁定状态:** `disabled: true` + `pointer-events: none` + `opacity: 0.6`
   - **样式:** 同文本输入框
   - **交互:** 锁定时无法展开选项

3. **文本区域 (Textarea)**
   - **HTML 标签:** `<textarea>`
   - **锁定状态:** `disabled: true` + `pointer-events: none` + `opacity: 0.6`
   - **样式:** 同文本输入框
   - **交互:** 锁定时无法编辑，但可滚动浏览（通过容器滚动）

4. **按钮组 (Button Group)**
   - **修改类按钮 (Modify Buttons):**
     - `APPLY 应用同步` - 应用配置更改
     - `SAVE & RUN 立即分析` - 保存并立即运行分析
     - **锁定状态:** `disabled: true`（完全禁用）
     - **样式:** 背景色变灰，文字变浅，鼠标指针变为 `not-allowed`
   - **浏览/加载类按钮 (Browse/Load Buttons):**
     - `读取配置` - 从服务器读取当前配置
     - `加载默认` - 加载默认配置
     - `读取方案` - 加载已保存的方案
     - `保存方案` - 保存当前配置为方案
     - `数据主题` - 切换数据主题
     - `登录` - 用户登录
     - **锁定状态:** 保持可用（`disabled: false`）
     - **样式:** 正常样式，鼠标指针为 `pointer`

5. **数字导航按钮 (Module Navigation Buttons)**
   - **位置:** 右侧配置框顶部，显示 1-11 的数字按钮
   - **功能:** 快速定位到对应的配置模块
   - **锁定状态:** 保持可用（`disabled: false`）
   - **样式:** 
     - 可编辑模块：蓝色背景 (`bg-blue-100`)，蓝色文字 (`text-blue-700`)
     - 只读模块：灰色背景 (`bg-gray-100`)，灰色文字 (`text-gray-500`)
   - **交互:** 点击按钮可快速跳转到对应模块，在锁定状态下仍可使用

#### 顶部导航栏 / Top Navigation Bar
- **品牌标题 (Brand Title):** `AiYX Data Radar`
  - **样式:** 文字可复制，无超链接
  - **说明:** 移除了指向 GitHub 的超链接，用户可直接选中并复制标题文字
  - **Note:** Removed hyperlink to GitHub, allowing users to select and copy the title text directly

#### 配置框滚动要求 / Config Panel Scrolling Requirements
- **容器滚动 (Container Scrolling):** 右侧配置框容器支持垂直滚动
- **滚动条样式 (Scrollbar Style):** 同编辑框
- **滚动触发条件 (Scroll Trigger):** 当配置项内容超过容器高度时自动显示滚动条
- **滚动平滑性 (Smooth Scrolling):** `scroll-behavior: smooth`（可选）
- **指针事件 (Pointer Events):** 容器级 `pointer-events: auto`，允许滚动
- **元素级禁用 (Element-level Disable):** 不使用容器级 `pointer-events: none`，改为元素级禁用

#### 配置框同步机制 / Config Panel Sync Mechanism
```javascript
// 配置项变更同步 / Config Item Change Sync
function syncConfigChange(elementId, configKey) {
  const element = document.getElementById(elementId);
  
  element.addEventListener('change', () => {
    // 更新配置对象 / Update config object
    config[configKey] = element.value;
    
    // 触发编辑器更新 / Trigger editor update
    updateEditorContent();
  });
}

// 编辑器内容变更同步 / Editor Content Change Sync
function syncEditorChange(editorId, configKey) {
  const editor = document.getElementById(editorId);
  
  editor.addEventListener('input', () => {
    // 解析编辑器内容 / Parse editor content
    const content = editor.value;
    
    // 更新配置对象 / Update config object
    config[configKey] = content;
    
    // 更新右侧配置框 / Update right config panel
    updateConfigPanel();
  });
}
```

### 3.3.4 锁定编辑功能详细要求 / Lock Edit Mode Detailed Requirements

#### 锁定状态定义 / Lock State Definition
- **默认状态:** 系统启动时默认为锁定状态（`isLocked: true`）
- **状态切换:** 通过"锁定编辑"按钮切换锁定/解锁状态
- **状态指示:** 按钮显示当前状态（锁定时显示"🔒 锁定编辑"，解锁时显示"🔓 解锁编辑"）

#### 锁定状态下的元素行为 / Element Behavior in Locked State

**1. 修改类按钮 (Modify Buttons) - 完全禁用**
```javascript
// 禁用修改按钮 / Disable modify buttons
const modifyButtons = [
  'apply-btn',      // APPLY 应用同步
  'save-run-btn'    // SAVE & RUN 立即分析
];

modifyButtons.forEach(btnId => {
  const btn = document.getElementById(btnId);
  btn.disabled = true;
  btn.style.opacity = '0.5';
  btn.style.cursor = 'not-allowed';
  btn.style.backgroundColor = '#ccc';
});
```

**2. 浏览/加载类按钮 (Browse/Load Buttons) - 保持可用**
```javascript
// 保持浏览按钮可用 / Keep browse buttons enabled
const browseButtons = [
  'read-config-btn',    // 读取配置
  'load-default-btn',   // 加载默认
  'load-profile-btn',   // 读取方案
  'save-profile-btn',   // 保存方案
  'theme-btn',          // 数据主题
  'login-btn'           // 登录
];

browseButtons.forEach(btnId => {
  const btn = document.getElementById(btnId);
  btn.disabled = false;
  btn.style.opacity = '1';
  btn.style.cursor = 'pointer';
});
```

**2.1 数字导航按钮 (Module Navigation Buttons) - 保持可用**
```javascript
// 保持数字导航按钮可用 / Keep module navigation buttons enabled
const navBtns = document.querySelectorAll('.module-nav-btn');
navBtns.forEach(btn => {
  btn.disabled = false;
  btn.style.pointerEvents = 'auto';
  btn.style.opacity = '1';
});
```
- **说明:** 右侧配置面板顶部的数字导航按钮（1-11）在锁定状态下保持可用，允许用户快速定位到不同的配置模块。
- **Note:** The module navigation buttons (1-11) at the top of the right config panel remain enabled in locked state, allowing users to quickly navigate to different config modules.

**3. 输入元素 (Input Elements) - 元素级禁用**
```javascript
// 禁用所有输入元素 / Disable all input elements
const inputElements = document.querySelectorAll(
  'input, select, textarea, button, [role="button"], [onclick]'
);

inputElements.forEach(elem => {
  // 排除浏览按钮 / Exclude browse buttons
  if (!browseButtons.includes(elem.id)) {
    elem.disabled = true;
    elem.style.pointerEvents = 'none';
    elem.style.opacity = '0.6';
    elem.style.backgroundColor = '#f5f5f5';
  }
});
```

**4. 编辑框 (Editors) - 只读模式**
```javascript
// 设置编辑框为只读 / Set editors to read-only
const editors = [
  'yaml-editor',
  'frequency-editor',
  'timeline-editor',
  'analysis_prompt-editor',
  'translation_prompt-editor'
];

editors.forEach(editorId => {
  const editor = document.getElementById(editorId);
  editor.readOnly = true;
  editor.style.pointerEvents = 'auto';  // 允许滚动和选择
  editor.style.backgroundColor = '#f5f5f5';
  editor.style.opacity = '0.8';
});
```

#### 解锁状态下的元素行为 / Element Behavior in Unlocked State
- **所有按钮:** 恢复正常状态（`disabled: false`）
- **所有输入元素:** 恢复可交互状态（`disabled: false`, `pointer-events: auto`, `opacity: 1`）
- **所有编辑框:** 恢复编辑模式（`readOnly: false`, `opacity: 1`）
- **背景色:** 恢复原始背景色

#### 锁定状态切换函数 / Lock State Toggle Function
```javascript
// 应用锁定状态 / Apply lock state
function applyLockState(isLocked) {
  const modifyButtons = ['apply-btn', 'save-run-btn'];
  const browseButtons = ['read-config-btn', 'load-default-btn', 'load-profile-btn', 'save-profile-btn', 'theme-btn', 'login-btn'];
  const editors = ['yaml-editor', 'frequency-editor', 'timeline-editor', 'analysis_prompt-editor', 'translation_prompt-editor'];
  
  if (isLocked) {
    // 禁用修改按钮 / Disable modify buttons
    modifyButtons.forEach(btnId => {
      const btn = document.getElementById(btnId);
      btn.disabled = true;
      btn.style.opacity = '0.5';
      btn.style.cursor = 'not-allowed';
    });
    
    // 禁用输入元素 / Disable input elements
    document.querySelectorAll('input, select, textarea').forEach(elem => {
      elem.disabled = true;
      elem.style.pointerEvents = 'none';
      elem.style.opacity = '0.6';
    });
    
    // 设置编辑框为只读 / Set editors to read-only
    editors.forEach(editorId => {
      const editor = document.getElementById(editorId);
      editor.readOnly = true;
      editor.style.pointerEvents = 'auto';
      editor.style.backgroundColor = '#f5f5f5';
    });
  } else {
    // 恢复修改按钮 / Restore modify buttons
    modifyButtons.forEach(btnId => {
      const btn = document.getElementById(btnId);
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.style.cursor = 'pointer';
    });
    
    // 恢复输入元素 / Restore input elements
    document.querySelectorAll('input, select, textarea').forEach(elem => {
      elem.disabled = false;
      elem.style.pointerEvents = 'auto';
      elem.style.opacity = '1';
    });
    
    // 恢复编辑框 / Restore editors
    editors.forEach(editorId => {
      const editor = document.getElementById(editorId);
      editor.readOnly = false;
      editor.style.backgroundColor = '#fff';
    });
  }
}

// 切换全局锁定 / Toggle global lock
function toggleGlobalLock() {
  isLocked = !isLocked;
  applyLockState(isLocked);
  
  // 更新按钮文本 / Update button text
  const lockBtn = document.getElementById('lock-btn');
  lockBtn.textContent = isLocked ? '🔒 锁定编辑' : '🔓 解锁编辑';
}
```

### 3.3.5 方案管理功能详细要求 / Profile Management Detailed Requirements

#### 保存方案流程 / Save Profile Flow
1. **打开保存对话框 (Open Save Dialog)**
   - 点击"保存方案"按钮 → 调用 `openSaveProfileModal()`
   - 显示模态框，加载已保存方案列表

2. **方案列表显示 (Display Profile List)**
   - 从服务器获取 `/api/profiles/list`
   - 显示最多 5 个最近保存的方案
   - 每个方案显示：序号、名称、修改时间、文件大小
   - 支持点击选择方案进行覆盖

3. **保存选项 (Save Options)**
   - **选项 A:** 点击现有方案 → 弹出确认对话框 → 确认后覆盖
   - **选项 B:** 输入自定义名称 → 点击"确认保存" → 保存为新方案
   - **选项 C:** 留空名称 → 点击"确认保存" → 自动生成时间戳名称（格式：`YYYYMMDD_HHMMSS`）

4. **确认对话框 (Confirmation Dialog)**
   - 显示要覆盖的方案名称
   - 显示原方案的修改时间
   - 提供"确认覆盖"和"取消"两个按钮

5. **保存到服务器 (Save to Server)**
   - 调用 `confirmSaveProfileToBackend()`
   - 发送 POST 请求到 `/api/profiles/save`
   - 请求体包含：方案名称、所有配置文件内容（JSON 格式）
   - 服务器返回保存结果和新方案 ID

#### 加载方案流程 / Load Profile Flow
1. **打开加载对话框 (Open Load Dialog)**
   - 点击"读取方案"按钮 → 调用 `openLoadProfileModal()`
   - 显示模态框，加载已保存方案列表

2. **方案列表显示 (Display Profile List)**
   - 从服务器获取 `/api/profiles/list`
   - 显示所有已保存方案
   - 每个方案显示：序号、名称、修改时间、文件大小

3. **选择加载 (Select & Load)**
   - 点击方案 → 调用 `loadProfileFromBackend(profileId)`
   - 发送 GET 请求到 `/api/profiles/load/{profileId}`
   - 服务器返回方案内容（JSON 格式）

4. **应用方案 (Apply Profile)**
   - 解析返回的 JSON 数据
   - 更新所有编辑框内容
   - 更新右侧配置框
   - 显示"方案加载成功"提示

#### 方案数据结构 / Profile Data Structure
```json
{
  "id": "profile_20260419_143022",
  "name": "生产环境配置_v1.2",
  "created_at": "2026-04-19 14:30:22",
  "updated_at": "2026-04-19 14:30:22",
  "size": "2.5 KB",
  "configs": {
    "yaml": "# YAML 配置内容...",
    "frequency": "# 频率配置内容...",
    "timeline": "# 时间线配置内容...",
    "analysis_prompt": "# 分析提示词内容...",
    "translation_prompt": "# 翻译提示词内容..."
  }
}
```

#### 方案管理 API 端点 / Profile Management API Endpoints
- **获取方案列表:** `GET /api/profiles/list` → 返回最近 5 个方案
- **加载方案:** `GET /api/profiles/load/{profileId}` → 返回完整方案数据
- **保存方案:** `POST /api/profiles/save` → 保存新方案或覆盖现有方案
- **删除方案:** `DELETE /api/profiles/{profileId}` → 删除指定方案

### 3.3.6 配置文件独立性要求 / Config File Independence Requirements

#### 配置文件隔离 / Config File Isolation
- **YAML 配置:** 独立编辑和保存，不影响其他配置文件
- **频率配置:** 独立编辑和保存，不影响其他配置文件
- **时间线配置:** 独立编辑和保存，不影响其他配置文件
- **AI 提示词:** 分析提示词和翻译提示词独立编辑和保存

#### 配置文件同步机制 / Config File Sync Mechanism
- **单向同步:** 编辑框 → 配置对象 → 右侧配置框
- **双向同步:** 右侧配置框 → 配置对象 → 编辑框（可选）
- **冲突处理:** 当编辑框和右侧配置框内容不一致时，以编辑框为准

#### 配置文件持久化 / Config File Persistence
- **本地存储:** 使用 `localStorage` 缓存当前配置（可选）
- **服务器存储:** 通过 API 保存到服务器 `profiles/` 目录
- **自动备份:** 每次保存时自动备份前一个版本

### 3.3.7 UI 样式与交互细节 / UI Styling & Interaction Details

#### 颜色方案 / Color Scheme
- **主色:** `#6366f1`（靛蓝色）
- **辅助色:** `#8b5cf6`（紫色）
- **成功色:** `#10b981`（绿色）
- **警告色:** `#f59e0b`（橙色）
- **错误色:** `#ef4444`（红色）
- **禁用色:** `#d1d5db`（灰色）
- **背景色:** `#ffffff`（白色）
- **文字色:** `#1f2937`（深灰色）

#### 字体与排版 / Typography
- **字体族:** `'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`
- **正文字号:** `14px`
- **标题字号:** `16px`
- **小字号:** `12px`
- **行高:** `1.5`

#### 间距与布局 / Spacing & Layout
- **内边距 (Padding):** `16px`（容器）、`8px`（元素）
- **外边距 (Margin):** `8px`（元素间）、`16px`（容器间）
- **边框圆角 (Border Radius):** `4px`（输入框）、`8px`（按钮）
- **边框宽度 (Border Width):** `1px`

#### 交互反馈 / Interaction Feedback
- **悬停效果 (Hover):** 背景色变浅，阴影增加
- **焦点效果 (Focus):** 边框变色，阴影增加
- **点击效果 (Active):** 背景色变深，阴影减少
- **禁用效果 (Disabled):** 背景色变灰，文字变浅，鼠标指针变为 `not-allowed`

#### 动画与过渡 / Animation & Transition
- **过渡时间 (Transition Duration):** `0.3s`
- **过渡函数 (Transition Timing):** `ease-in-out`
- **模态框动画:** 淡入淡出（`opacity: 0 → 1`）
- **按钮动画:** 背景色平滑过渡

### 3.3.8 AI 模型查询功能详细要求 / AI Model Query Feature Detailed Requirements

#### 功能概述 / Feature Overview
在 AI 模型配置部分添加"🔍 查询模型"按钮，支持：
1. **连接测试 (Connection Test):** 验证 API 连接和认证信息
2. **模型列表获取 (Model List Fetching):** 从 AI 服务商获取可用模型列表
3. **自动配置填充 (Auto Config Population):** 根据选择的模型自动填充配置参数

#### 模型配置规则映射 / Model Configuration Rules Mapping

支持的 AI 服务商及其配置规则：

```javascript
const modelConfigRules = {
  'SiliconFlow': {
    baseUrl: 'https://api.siliconflow.cn/v1',
    modelPrefix: 'Pro/',
    supportedModels: ['deepseek-ai/deepseek-v3', 'Qwen/Qwen2.5-72B-Instruct', 'meta-llama/Llama-3.1-405B-Instruct'],
    defaultTemperature: 1,
    defaultMaxTokens: 4096
  },
  'OpenAI': {
    baseUrl: 'https://api.openai.com/v1',
    modelPrefix: '',
    supportedModels: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
    defaultTemperature: 0.7,
    defaultMaxTokens: 2048
  },
  'DeepSeek': {
    baseUrl: 'https://api.deepseek.com/v1',
    modelPrefix: 'deepseek-ai/',
    supportedModels: ['deepseek-v3', 'deepseek-v2.5', 'deepseek-v2'],
    defaultTemperature: 1,
    defaultMaxTokens: 4096
  },
  'Zhipu': {
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    modelPrefix: '',
    supportedModels: ['glm-4', 'glm-3-turbo'],
    defaultTemperature: 0.95,
    defaultMaxTokens: 2048
  }
};
```

#### 查询流程 / Query Workflow

**步骤 1: 打开查询模态框 (Open Query Modal)**
```javascript
function openModelQueryModal() {
  // 显示模态框
  const modal = document.getElementById('model-query-modal');
  modal.style.display = 'flex';
  
  // 初始化提供商选择
  const providerSelect = document.getElementById('provider-select');
  providerSelect.value = 'SiliconFlow'; // 默认选择
}
```

**步骤 2: 测试连接 (Test Connection)**
```javascript
async function testAIConnection() {
  const provider = document.getElementById('provider-select').value;
  const apiKey = document.getElementById('api-key-input').value;
  
  // 调用后端 API 测试连接
  const response = await fetch('/api/test-ai-connection', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, apiKey })
  });
  
  // 显示测试结果
  const result = await response.json();
  if (result.success) {
    showNotification('✅ 连接成功', 'success');
  } else {
    showNotification('❌ 连接失败: ' + result.error, 'error');
  }
}
```

**步骤 3: 获取模型列表 (Fetch Model List)**
```javascript
async function fetchAvailableModels() {
  const provider = document.getElementById('provider-select').value;
  const apiKey = document.getElementById('api-key-input').value;
  
  // 调用后端 API 获取模型列表
  const response = await fetch('/api/get-available-models', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, apiKey })
  });
  
  const result = await response.json();
  
  // 填充模型选择下拉框
  const modelSelect = document.getElementById('model-select');
  modelSelect.innerHTML = '';
  result.models.forEach(model => {
    const option = document.createElement('option');
    option.value = model;
    option.textContent = model;
    modelSelect.appendChild(option);
  });
}
```

**步骤 4: 应用配置 (Apply Configuration)**
```javascript
function applyModelConfig() {
  const provider = document.getElementById('provider-select').value;
  const selectedModel = document.getElementById('model-select').value;
  const apiKey = document.getElementById('api-key-input').value;
  
  // 根据规则映射获取配置参数
  const rules = modelConfigRules[provider];
  
  // 更新配置对象
  config.ai_model = {
    provider: provider,
    model: selectedModel,
    api_key: apiKey,
    base_url: rules.baseUrl,
    temperature: rules.defaultTemperature,
    max_tokens: rules.defaultMaxTokens
  };
  
  // 更新配置面板显示
  updateConfigPanel();
  
  // 关闭模态框
  closeModelQueryModal();
  
  showNotification('✅ 配置已应用', 'success');
}
```

#### 模态框 UI 结构 / Modal UI Structure

```html
<div id="model-query-modal" class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h3>🔍 AI 模型查询与配置</h3>
      <button class="close-btn" onclick="closeModelQueryModal()">×</button>
    </div>
    
    <div class="modal-body">
      <!-- 提供商选择 -->
      <div class="form-group">
        <label>AI 服务商 / AI Provider:</label>
        <select id="provider-select">
          <option value="SiliconFlow">SiliconFlow</option>
          <option value="OpenAI">OpenAI</option>
          <option value="DeepSeek">DeepSeek</option>
          <option value="Zhipu">Zhipu</option>
        </select>
      </div>
      
      <!-- API Key 输入 -->
      <div class="form-group">
        <label>API Key:</label>
        <input type="password" id="api-key-input" placeholder="输入 API Key">
      </div>
      
      <!-- 连接测试按钮 -->
      <button class="btn btn-secondary" onclick="testAIConnection()">
        🧪 测试连接
      </button>
      
      <!-- 获取模型列表按钮 -->
      <button class="btn btn-secondary" onclick="fetchAvailableModels()">
        📋 获取模型列表
      </button>
      
      <!-- 模型选择 -->
      <div class="form-group">
        <label>选择模型 / Select Model:</label>
        <select id="model-select"></select>
      </div>
    </div>
    
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModelQueryModal()">取消</button>
      <button class="btn btn-primary" onclick="applyModelConfig()">应用配置</button>
    </div>
  </div>
</div>
```

#### 后端 API 端点 / Backend API Endpoints

**1. 测试连接 (Test Connection)**
- **端点:** `POST /api/test-ai-connection`
- **请求体:** `{ provider: string, apiKey: string }`
- **响应:** `{ success: boolean, error?: string }`

**2. 获取模型列表 (Get Available Models)**
- **端点:** `POST /api/get-available-models`
- **请求体:** `{ provider: string, apiKey: string }`
- **响应:** `{ models: string[], error?: string }`

**3. 应用配置 (Apply Configuration)**
- **端点:** `POST /api/apply-model-config`
- **请求体:** `{ provider: string, model: string, apiKey: string }`
- **响应:** `{ success: boolean, config: object }`

#### 模型查询弹出框优化 / Model Query Modal Enhancements

**功能需求 (Feature Requirements)**
1. **搜索过滤功能 (Search Filtering)**: 在模型列表上方添加搜索框，支持实时过滤模型名称。
2. **可调整大小 (Resizable)**: 弹出框支持通过右下角拖拽调整大小。
3. **增强拖拽区域 (Enhanced Drag Area)**: 扩大右下角拖拽区域的可视范围，提升用户体验。

**实现细节 / Implementation Details**

**1. 搜索框实现 (Search Box Implementation)**
- **位置:** 模型列表上方，"步骤2:选择模型"标题下方
- **HTML 结构** (`/TrendRadar/output/config_editor/assets/script.js` 第 6377-6388 行):
  ```html
  <div class="mb-4">
      <input type="text" id="modelSearchInput" 
             placeholder="🔍 搜索模型..." 
             class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
             oninput="filterModels()">
  </div>
  ```
- **过滤逻辑** (第 6540-6555 行):
  ```javascript
  window.filterModels = function() {
      const searchInput = document.getElementById('modelSearchInput');
      const searchTerm = searchInput.value.toLowerCase();
      const modelButtons = document.querySelectorAll('#model-list button');
      
      modelButtons.forEach(button => {
          const modelName = button.querySelector('.font-medium').textContent.toLowerCase();
          if (modelName.includes(searchTerm)) {
              button.style.display = '';
          } else {
              button.style.display = 'none';
          }
      });
  };
  ```
- **特性:** 实时搜索，不区分大小写，支持模糊匹配

**2. 可调整大小实现 (Resizable Implementation)**
- **CSS 属性** (`/TrendRadar/output/config_editor/assets/script.js` 第 6371 行):
  ```html
  <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-96 overflow-y-auto" 
       style="resize: both; overflow: auto; min-width: 400px; min-height: 300px;">
  ```
- **约束参数:**
  - `resize: both` - 允许水平和垂直方向调整
  - `min-width: 400px` - 最小宽度限制
  - `min-height: 300px` - 最小高度限制
  - `overflow: auto` - 内容溢出时显示滚动条

**3. 拖拽区域可视化 (Drag Area Visualization)**
- **CSS 样式** (`/TrendRadar/output/config_editor/assets/style.css` 第 1224+ 行):
  ```css
  /* 模型查询弹出框拖拽区域增强 */
  #modelQueryModal .bg-white {
      position: relative;
  }
  
  #modelQueryModal .bg-white::after {
      content: '';
      position: absolute;
      right: 0;
      bottom: 0;
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, transparent 50%, rgba(59, 130, 246, 0.2) 50%);
      cursor: nwse-resize;
      pointer-events: none;
  }
  
  #modelQueryModal .bg-white:hover::after {
      background: linear-gradient(135deg, transparent 50%, rgba(59, 130, 246, 0.4) 50%);
  }
  ```
- **设计说明:**
  - 使用 `::after` 伪元素创建 40px × 40px 的可视拖拽区域
  - 渐变背景提示用户可拖拽位置
  - hover 效果增强交互反馈
  - `pointer-events: none` 确保不干扰原生 resize 功能

**用户体验改进 / UX Improvements**
1. **搜索效率:** 当模型列表较长时（如 SiliconFlow 提供 50+ 模型），搜索框可快速定位目标模型。
2. **灵活布局:** 用户可根据屏幕尺寸和个人偏好调整弹出框大小，适应不同的工作场景。
3. **视觉引导:** 右下角的渐变三角形清晰提示拖拽位置，降低操作门槛。

---

## 4. 效果演示 / Effects & UI
- **Dashboard:** 提供沉浸式阅读体验，并将配置入口全局化。
- **Popup:** 解决了以往需要切换网址才能配置的痛点，实现了“边看报告边调整配置”的丝滑体验。
- **Dashboard:** Provides an immersive reading experience with centralized config access.
- **Popup:** Solves the pain point of switching URLs for config, enabling a smooth "read and adjust" workflow.
