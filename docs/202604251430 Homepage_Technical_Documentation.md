---
title: TrendRadar 主页完整技术文档
version: 1.01.0413
date: 2026-04-25
author: Development Team
---

# TrendRadar 主页完整技术文档

## 1. 项目概览

**项目名称**: TrendRadar  
**版本**: V1.01.0413  
**主页URL**: https://trendradar.aiyxtech.us.kg/  
**主页文件**: `/TrendRadar/index.html` (2645行)  
**后端服务**: Flask服务器 (端口8080)  
**反向代理**: Nginx  

### 核心功能
- 🔍 多源趋势搜索（支持中英文）
- 📊 AI驱动的报告生成
- 🎨 多主题支持（7种主题）
- ⚙️ 可视化配置编辑
- 📈 搜索历史管理
- 🖼️ 报告截图导出

---

## 2. 技术栈

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5 | - | 页面结构 |
| CSS3 | - | 样式和动画 |
| JavaScript (Vanilla) | ES6+ | 交互逻辑 |
| Font Awesome | 6.4.0 | 图标库 |
| html2canvas | 1.4.1 | 报告截图 |
| marked.js | - | Markdown解析 |
| Google Fonts | - | 字体 (Inter, Noto Sans SC) |

### 后端技术
| 技术 | 用途 |
|------|------|
| Python Flask | Web框架 |
| Nginx | 反向代理 |
| Docker | 容器化部署 |

### 字体
- **Inter**: 英文字体 (wght: 400, 600, 700, 800, 900)
- **Noto Sans SC**: 中文字体 (wght: 400, 500, 700, 800)

### CDN资源
```
Font Awesome: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
html2canvas: https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js
marked.js: https://cdn.jsdelivr.net/npm/marked/marked.min.js
Google Fonts: https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Noto+Sans+SC:wght@400;500;700;800&display=swap
```

---

## 3. 主页结构

### 3.1 HTML布局

```
<html>
├── <head>
│   ├── Meta标签 (charset, viewport)
│   ├── 外部脚本 (html2canvas, marked.js)
│   ├── 外部样式 (Font Awesome)
│   └── 内联样式 (CSS变量、主题、动画)
│
└── <body>
    ├── .container
    │   ├── .header (顶部导航区)
    │   ├── .meta-box (统计信息)
    │   ├── #main-cards-grid (主卡片网格)
    │   └── #search-cards-grid (搜索结果网格)
    │
    ├── #global-search (全局搜索框)
    ├── #config-modal (配置编辑器模态框)
    ├── .floating-config-btn (浮动配置按钮)
    └── 其他模态框和工具
```

### 3.2 主要容器元素

| ID/Class | 用途 | 位置 |
|----------|------|------|
| `.container` | 主容器 | 全页面 |
| `.header` | 顶部导航 | 页面顶部 |
| `.meta-box` | 统计信息框 | 头部下方 |
| `#main-cards-grid` | 主卡片网格 | 中央区域 |
| `#search-cards-grid` | 搜索结果网格 | 搜索时显示 |
| `#global-search` | 搜索输入框 | 头部 |
| `#config-modal` | 配置编辑器 | 模态框 |
| `.floating-config-btn` | 浮动配置按钮 | 右侧固定 |

---

## 4. 功能模块详解

### 4.1 搜索功能

**元素ID**: `#global-search`, `#search-input`

**功能**:
- 实时搜索多源数据
- 支持中英文搜索
- 支持多关键词搜索
- 搜索结果实时显示

**实现流程**:
```javascript
1. 用户在搜索框输入关键词
2. 触发 oninput 事件
3. 调用 performSearch(keyword) 函数
4. 发送 GET /api/search?kw=keyword 请求
5. 后端返回搜索结果 (JSON数组)
6. 前端渲染结果到 #search-cards-grid
7. 显示搜索结果卡片
```

**API端点**: `/api/search?kw={keyword}`

**返回格式**:
```json
{
  "results": [
    {
      "title": "新闻标题",
      "source": "来源",
      "url": "链接",
      "date": "日期",
      "summary": "摘要"
    }
  ],
  "count": 288
}
```

### 4.2 主题切换

**元素ID**: `#theme-select`

**支持的主题**:
1. **Default** - 默认浅色主题
2. **Solarized Light** - Solarized浅色
3. **Solarized Dark** - Solarized深色
4. **Nord** - Nord配色
5. **Dracula** - Dracula配色
6. **Gruvbox** - Gruvbox配色
7. **Monokai** - Monokai配色
8. **Catppuccin** - Catppuccin配色

**实现方式**:
```javascript
// 通过 data-theme 属性切换
document.documentElement.setAttribute('data-theme', themeName);

// CSS变量定义
:root {
  --bg-color: #f7fafc;
  --card-bg: rgba(255, 255, 255, 0.85);
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --accent-cyan: #00f2ff;
  --accent-magenta: #ff00ff;
  --accent-lime: #39ff14;
}

[data-theme="dark"] {
  --bg-color: #1a1a1a;
  --card-bg: #2d2d2d;
  /* ... */
}
```

**存储**: 主题选择保存在 localStorage

### 4.3 配置编辑器

**元素ID**: `#config-modal`, `#config-iframe`

**功能**:
- 可视化编辑配置文件
- 支持多个配置文件
- 实时预览
- 保存配置

**配置文件列表**:
1. `config.yaml` - 主配置文件
2. `frequency_words.txt` - 高频词汇
3. `timeline.yaml` - 时间线配置
4. `ai_analysis_prompt.txt` - AI分析提示词
5. `ai_translation_prompt.txt` - AI翻译提示词

**API端点**: 
- `/api/load?file={filename}` - 加载配置
- `/api/save` - 保存配置

**配置编辑器路径**: `/TrendRadar/output/config_editor/`

### 4.4 报告生成

**功能**:
- 基于搜索结果生成AI报告
- 支持多种报告格式
- 报告截图导出

**API端点**: `/api/generate_report`

**请求格式**:
```json
{
  "keyword": "搜索关键词",
  "results": [/* 搜索结果数组 */],
  "options": {
    "format": "markdown|html",
    "includeAnalysis": true
  }
}
```

**返回格式**:
```json
{
  "reportId": "uuid",
  "content": "报告内容",
  "generatedAt": "2026-04-25T14:30:00Z"
}
```

### 4.5 搜索历史

**功能**:
- 记录用户搜索历史
- 快速重新搜索
- 历史清除

**API端点**: `/api/search_history`

**返回格式**:
```json
{
  "history": [
    {
      "keyword": "搜索词",
      "timestamp": "2026-04-25T14:30:00Z",
      "resultCount": 288
    }
  ]
}
```

---

## 5. 样式系统

### 5.1 CSS变量 (主题系统)

```css
:root {
  /* 背景色 */
  --bg-color: #f7fafc;
  --card-bg: rgba(255, 255, 255, 0.85);
  --header-bg: #ffffff;
  
  /* 文字色 */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  
  /* 强调色 */
  --accent-cyan: #00f2ff;
  --accent-magenta: #ff00ff;
  --accent-lime: #39ff14;
  
  /* 阴影 */
  --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-neon: 0 0 20px rgba(0, 242, 255, 0.2);
  
  /* 玻璃态 */
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.3);
}
```

### 5.2 关键样式类

| 类名 | 用途 |
|------|------|
| `.container` | 主容器 (max-width: 1200px) |
| `.header` | 顶部导航栏 |
| `.cards-grid` | 卡片网格 (auto-fill, minmax(350px, 1fr)) |
| `.card` | 单个卡片 (height: 600px) |
| `.card:hover` | 卡片悬停效果 (translateY(-8px)) |
| `.floating-config-btn` | 浮动按钮 (fixed, right: 30px, top: 50%) |
| `.meta-box` | 统计信息框 |

### 5.3 动画

```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 应用到 .container */
animation: fadeInUp 0.8s ease-out;
```

---

## 6. API接口文档

### 6.1 搜索接口

**端点**: `GET /api/search`

**参数**:
- `kw` (string, required) - 搜索关键词

**响应**:
```json
{
  "success": true,
  "results": [
    {
      "title": "新闻标题",
      "source": "来源",
      "url": "链接",
      "date": "2026-04-25",
      "summary": "摘要内容"
    }
  ],
  "count": 288
}
```

### 6.2 配置加载接口

**端点**: `GET /api/load`

**参数**:
- `file` (string, required) - 配置文件名

**响应**:
```json
{
  "success": true,
  "content": "文件内容",
  "filename": "config.yaml"
}
```

### 6.3 配置保存接口

**端点**: `POST /api/save`

**请求体**:
```json
{
  "filename": "config.yaml",
  "content": "新的文件内容"
}
```

**响应**:
```json
{
  "success": true,
  "message": "配置已保存"
}
```

### 6.4 报告生成接口

**端点**: `POST /api/generate_report`

**请求体**:
```json
{
  "keyword": "搜索关键词",
  "results": [/* 搜索结果 */]
}
```

**响应**:
```json
{
  "success": true,
  "reportId": "uuid",
  "content": "报告内容",
  "generatedAt": "2026-04-25T14:30:00Z"
}
```

### 6.5 报告检索接口

**端点**: `GET /api/report/{id}`

**响应**:
```json
{
  "success": true,
  "reportId": "uuid",
  "content": "报告内容",
  "generatedAt": "2026-04-25T14:30:00Z"
}
```

### 6.6 搜索历史接口

**端点**: `GET /api/search_history`

**响应**:
```json
{
  "success": true,
  "history": [
    {
      "keyword": "搜索词",
      "timestamp": "2026-04-25T14:30:00Z",
      "resultCount": 288
    }
  ]
}
```

### 6.7 数据刷新接口

**端点**: `GET /api/refresh`

**响应**:
```json
{
  "success": true,
  "message": "数据已刷新",
  "timestamp": "2026-04-25T14:30:00Z"
}
```

---

## 7. 文件路径映射

### 7.1 核心文件

```
/TrendRadar/
├── index.html                          # 主页文件 (2645行)
├── docker/
│   └── server.py                       # Flask后端服务器
├── config/
│   ├── config.yaml                     # 主配置文件
│   ├── frequency_words.txt             # 高频词汇
│   ├── timeline.yaml                   # 时间线配置
│   ├── ai_analysis_prompt.txt          # AI分析提示词
│   └── ai_translation_prompt.txt       # AI翻译提示词
├── output/
│   └── config_editor/
│       ├── index.html                  # 配置编辑器页面
│       └── assets/
│           ├── script.js               # 编辑器脚本
│           └── style.css               # 编辑器样式
└── docs/
    ├── 202603071010 Visual_Config_Integration_Manual.md
    ├── 202603131205 Development_Retrospective.md
    └── 202604251430 Homepage_Technical_Documentation.md  # 本文档
```

### 7.2 配置文件路径检测

**优先级顺序** (从高到低):
1. `/TrendRadar/config/` - 主配置目录
2. `/app/config/` - Docker容器配置目录
3. `/AIYXDATA-TRADAR/config/` - 备用配置目录
4. `./config/` - 相对路径配置目录

**检测代码** (`/TrendRadar/docker/server.py` 第39行):
```python
CONFIG_DIR = Path(detect_path("CONFIG_DIR", [
    "/TrendRadar/config",
    "/app/config",
    "/AIYXDATA-TRADAR/config",
    "./config"
]))
```

---

## 8. 配置说明

### 8.1 config.yaml

主配置文件，包含：
- 数据源配置
- API密钥
- 搜索参数
- 输出格式

### 8.2 frequency_words.txt

高频词汇列表，用于：
- 搜索优化
- 关键词提取
- 结果排序

### 8.3 timeline.yaml

时间线配置，定义：
- 时间段划分
- 事件分类
- 显示格式

### 8.4 AI提示词

- `ai_analysis_prompt.txt` - 分析报告生成提示
- `ai_translation_prompt.txt` - 翻译功能提示

---

## 9. 开发指南

### 9.1 本地开发

**启动后端服务**:
```bash
cd /TrendRadar/docker
python server.py
# 服务运行在 http://127.0.0.1:8080
```

**访问主页**:
```
http://127.0.0.1:8080/
```

### 9.2 修改主页

**编辑主页文件**:
```bash
vim /TrendRadar/index.html
```

**主要修改点**:
- 搜索功能: 搜索框HTML + JavaScript事件处理
- 主题系统: CSS变量 + data-theme属性
- 卡片布局: .cards-grid + .card样式
- 浮动按钮: .floating-config-btn样式

### 9.3 修改配置

**编辑配置文件**:
```bash
vim /TrendRadar/config/config.yaml
```

**通过UI编辑**:
1. 点击浮动配置按钮
2. 选择要编辑的配置文件
3. 修改内容
4. 点击保存

### 9.4 添加新主题

**步骤**:
1. 在 `index.html` 中添加新的CSS变量集合
2. 在主题选择器中添加新选项
3. 定义主题的颜色变量

**示例**:
```css
[data-theme="my-theme"] {
  --bg-color: #1a1a1a;
  --card-bg: #2d2d2d;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --accent-cyan: #00ffff;
}
```

### 9.5 扩展功能

**添加新API端点**:
1. 在 `server.py` 中定义新的Flask路由
2. 在 `index.html` 中添加JavaScript函数调用该端点
3. 处理响应并更新UI

**示例**:
```python
# server.py
@app.route('/api/new-feature', methods=['GET'])
def new_feature():
    return jsonify({"success": True, "data": []})
```

```javascript
// index.html
async function callNewFeature() {
  const response = await fetch('/api/new-feature');
  const data = await response.json();
  // 处理数据
}
```

---

## 10. 部署指南

### 10.1 Docker部署

**构建镜像**:
```bash
cd /TrendRadar
docker build -t trendradar:latest .
```

**运行容器**:
```bash
docker run -d \
  -p 8080:8080 \
  -v /TrendRadar/config:/app/config \
  --name trendradar \
  trendradar:latest
```

### 10.2 Nginx配置

**反向代理配置**:
```nginx
server {
    listen 443 ssl http2;
    server_name trendradar.aiyxtech.us.kg;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 10.3 验证部署

**检查服务状态**:
```bash
curl -I https://trendradar.aiyxtech.us.kg/
# 应返回 HTTP 200
```

**测试API**:
```bash
curl "http://127.0.0.1:8080/api/search?kw=test"
curl "http://127.0.0.1:8080/api/load?file=config.yaml"
```

---

## 11. 故障排查

### 11.1 配置文件读取失败

**症状**: API返回 "File not found: config.yaml"

**原因**: CONFIG_DIR路径检测顺序不正确

**解决方案**:
1. 检查 `/TrendRadar/config/` 目录是否存在
2. 验证 `server.py` 中的路径优先级
3. 重启Flask服务器

### 11.2 搜索功能不工作

**症状**: 搜索框无响应

**排查步骤**:
1. 检查浏览器控制台是否有JavaScript错误
2. 验证 `/api/search` 端点是否可访问
3. 检查后端服务是否运行

### 11.3 主题切换无效

**症状**: 主题选择后页面无变化

**解决方案**:
1. 清除浏览器缓存
2. 检查 localStorage 是否被禁用
3. 验证CSS变量是否正确定义

---

## 12. 性能优化

### 12.1 前端优化

- 使用CDN加载外部资源
- 启用CSS/JS压缩
- 实现图片懒加载
- 使用Web Workers处理大数据

### 12.2 后端优化

- 实现API缓存
- 使用数据库索引
- 异步处理长时间操作
- 实现请求限流

### 12.3 网络优化

- 启用Gzip压缩
- 使用HTTP/2
- 实现CDN加速
- 优化DNS解析

---

## 13. 安全考虑

### 13.1 前端安全

- 防止XSS攻击: 使用textContent而非innerHTML
- CSRF保护: 验证请求来源
- 内容安全策略: 设置CSP头

### 13.2 后端安全

- 输入验证: 验证所有用户输入
- SQL注入防护: 使用参数化查询
- 认证授权: 实现用户认证
- 日志审计: 记录所有操作

### 13.3 数据安全

- 敏感数据加密
- 安全的密钥管理
- 定期备份
- 访问控制

---

## 14. 更新历史

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-04-25 | 1.01.0413 | 完成主页技术文档 |
| 2026-04-24 | 1.01.0413 | 模型查询弹出框UX优化 |
| 2026-04-23 | 1.01.0413 | 配置文件路径修复 |

---

## 15. 联系与支持

**技术支持**: 开发团队  
**文档维护**: 技术文档组  
**最后更新**: 2026-04-25 14:30 UTC

---

**文档完成**。本文档包含了主页的完整技术信息，任何开发者都可以基于此文档进行复制、升级、修改和扩展。
