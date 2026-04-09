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
   - **交互触发 (Trigger):** 页面右下角常驻紫色“⚙️ 可视化配置”悬浮按钮。
   - **窗口特性 (Window Features):** 
     - **可拖拽 (Draggable):** 通过原生 JS 监听标题栏实现自由移动。
     - **可缩放 (Resizable):** 利用原生 CSS `resize: both` 允许用户自由调节窗口大小。
     - **内嵌集成:** 弹窗内嵌可视化 YAML 编辑器，支持实时修改 `config.yaml`。
   - Interaction: Persistent purple "Visual Config" button at bottom-right. Features: Draggable via header, Resizable via CSS, and Embedded YAML editor inside the modal.

### 3.2 实现路径与关键文件 / Key Files & Paths
- **前端主页 (Dashboard Entrance):** `/TrendRadar/output/index.html`
- **编辑器工作区 (Editor Workspace):** `/TrendRadar/output/config_editor/`
- **后端拦截点 (Backend Patch):** `/TrendRadar/trendradar/report/generator.py`
  - *修改点:* 注释掉了 `shutil.copy2` 到 `index.html` 的步骤，防止自定义 Dashboard 被每日生成的新闻覆盖。
  - *Patch Detail:* Commented out `shutil.copy2` to `index.html` to prevent the custom Dashboard from being overwritten by daily news reports.

---

## 4. 效果演示 / Effects & UI
- **Dashboard:** 提供沉浸式阅读体验，并将配置入口全局化。
- **Popup:** 解决了以往需要切换网址才能配置的痛点，实现了“边看报告边调整配置”的丝滑体验。
- **Dashboard:** Provides an immersive reading experience with centralized config access.
- **Popup:** Solves the pain point of switching URLs for config, enabling a smooth "read and adjust" workflow.
