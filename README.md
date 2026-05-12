<div align="center" id="aiyxdata_tradar">

# AIYXDATA-TRADAR

**AI 驱动的全渠道热点情报助手**

[快速开始](#-快速开始) | [核心功能](#-核心功能) | [配置详解](#-配置详解) | [English](README-EN.md)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-部署-2496ED?style=flat-square&logo=docker&logoColor=white)](docker/)
[![AI Powered](https://img.shields.io/badge/AI-LiteLLM-FF6B6B?style=flat-square&logo=openai&logoColor=white)](#-ai-智能分析)

AIYXDATA-TRADAR 是一款专为高效信息流管理设计的开源工具。它能从全球多个主流平台提取实时热点，通过 LiteLLM 集成的 AI 大模型进行深度研判，并精准推送到您的协作工具中。

</div>

---

## 📋 版本历史

### v1.01.0511 (2026-05-11)

**🎉 可视化配置中心增强**
- **AI 模型查询优化**：支持多种 API 响应格式，自动重试 /v1 路径
- **模态框体验改进**：增大尺寸、禁止背景关闭、搜索框固定显示
- **错误处理增强**：详细的错误提示和调试日志

**🔧 后端 API 增强**
- 新增 `/api/ai_refresh` 端点 - 强制刷新 AI 分析
- 改进 `/api/check_ai_connection` - 支持 /v1 路径自动重试
- 增强 `/api/get_ai_models` - 支持多种响应格式（data/models/result/items）
- 新增 `get_latest_ai_report()` 方法 - 获取最新 AI 报告

**📁 关键文件**
- `docker/server.py` (605-724行) - 模型查询 API 实现
- `output/config_editor/assets/script.js` (6574-6734行) - 前端模型查询功能
- `output/config_editor/assets/style.css` (1244-1260行) - 模态框样式
- `docker-compose.yml` - 容器配置（aiyxdata_tradar, 127.0.0.1:8084:8080）

**📖 技术文档**
- `docs/202603071010 Visual_Config_Integration_Manual.md` - 可视化配置集成手册
- `docs/202603131205 Development_Retrospective.md` - 开发回顾文档
- `docs/AI_MODEL_QUERY_FEATURE.md` - AI 模型查询功能文档

---

## 🎯 核心功能

- **🚀 多维热点聚合**：支持微博、知乎、抖音等主流平台榜单实时抓取，告别信息茧房。
- **📰 RSS/Atom 增强**：支持自定义 RSS/Atom 订阅源，将碎片化阅读集中管理。
- **🤖 AI 智能分析**：基于 LiteLLM 适配 100+ AI 提供商（如 OpenAI, DeepSeek, Google Gemini, Anthropic），自动生成趋势研判。
  - **v1.01.0511 新增**：AI 分析内容按【地区/主题】标签自动分段，提升可读性。每个【中国】、【海外】、【AI科技】等标签下的内容独立成段，段落间有明显的视觉分隔，适用于所有输出渠道（HTML、Markdown、飞书、钉钉等）。
- **📢 全程渠道通知**：
  - **通用协作**：Slack, Telegram, Discord (Generic Webhook)
  - **办公套件**：飞书 (Lark), 钉钉, 企业微信
  - **移动通知**：Bark (iOS), ntfy, 邮件 (Email)
- **📅 弹性调度系统**：自研 `timeline.yaml` 调度逻辑，精准控制采集与推送时段。
- **📊 自动化报告**：内置轻量级 Web 服务器，自动生成精美的 HTML 历史分析报告。

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/davidwei07chat/AIYXDATA-TRADAR.git
cd AIYXDATA-TRADAR
```

### 2. 环境初始化
```bash
# 推荐使用 Python 3.10+
pip install -r requirements.txt
```

### 3. 配置核心参数
编辑 `config/config.yaml`，填入您的 API 密钥及通知渠道地址。

### 4. 启动程序
```bash
python -m aiyxdata_tradar
```

---

## 🐳 Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/davidwei07chat/AIYXDATA-TRADAR.git
cd AIYXDATA-TRADAR

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 单容器

```bash
# 构建镜像
docker build -t aiyxdata-tradar .

# 运行容器
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/aiyxdata_tradar:/app/aiyxdata_tradar \
  --name tradar \
  aiyxdata-tradar

# 查看日志
docker logs -f tradar

# 停止容器
docker stop tradar
```

### 配置说明

启动前，请确保配置文件已准备好：
- `config/config.yaml` - 核心配置（API Key、通知渠道等）
- `config/timeline.yaml` - 时间调度配置
- `config/frequency_words.txt` - 关键词配置

Docker Compose 会自动挂载这些配置文件到容器内。

### 容器配置说明

**容器名称**: `aiyxdata_tradar`
**端口映射**: `127.0.0.1:8084:8080`（仅本地访问）
**工作目录**: `/app/docker`

如需外网访问，请配置 Nginx 反向代理：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8084;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 可视化配置中心

访问 `https://your-domain.com/config_editor/` 使用可视化配置界面：

**功能特性**：
- 📝 在线编辑配置文件（config.yaml, timeline.yaml）
- 🔍 AI 模型查询和选择
- ✅ 配置验证和实时预览
- 💾 一键保存和应用配置

**AI 模型查询**：
1. 输入 API Base 和 API Key
2. 点击"测试连接"验证连接
3. 搜索框自动显示，输入关键词过滤模型
4. 点击模型卡片选择并应用到配置

**支持的 API 格式**：
- OpenAI 标准格式（/models, /v1/models）
- 多种响应字段（data, models, result, items）
- 多种 ID 字段（id, model, name, model_id）

**关键文件**：
- `output/config_editor/index.html` - 配置界面入口
- `output/config_editor/assets/script.js` (6574-6734行) - 模型查询功能
- `output/config_editor/assets/style.css` (1244-1260行) - 模态框样式
- `docker/server.py` (605-724行) - 后端 API 实现

---

## 🏗️ 功能架构

### 核心模块

| 模块 | 文件路径 | 功能说明 |
|------|---------|---------|
| **主程序** | `aiyxdata_tradar/` | 热点抓取、AI 分析、通知推送 |
| **Web 服务器** | `docker/server.py` | HTTP API 服务、配置管理 |
| **可视化配置** | `output/config_editor/` | 前端配置界面 |
| **MCP 服务器** | `mcp_server/` | Model Context Protocol 集成 |
| **调度系统** | `config/timeline.yaml` | 时间段调度配置 |

### API 端点

| 端点 | 方法 | 功能 | 文件位置 |
|------|------|------|---------|
| `/api/check_ai_connection` | POST | 测试 AI API 连接 | `docker/server.py:546-603` |
| `/api/get_ai_models` | POST | 获取可用模型列表 | `docker/server.py:605-724` |
| `/api/ai_refresh` | POST | 强制刷新 AI 分析 | `docker/server.py:506-528` |
| `/api/config` | GET/POST | 配置文件管理 | `docker/server.py:400-502` |

### 前端组件

| 组件 | 文件路径 | 功能说明 |
|------|---------|---------|
| **模型查询模态框** | `output/config_editor/assets/script.js:6574-6734` | AI 模型选择界面 |
| **配置编辑器** | `output/config_editor/assets/script.js:1-6573` | YAML 配置编辑 |
| **样式定义** | `output/config_editor/assets/style.css` | UI 样式和主题 |

---

## ⚙️ 配置详解

- **`config/config.yaml`**: 全局核心设置（通知渠道、API Key、采集策略）。
- **`config/timeline.yaml`**: 时间段调度设置（定义推送与分析的时间窗口）。
- **`config/frequency_words.txt`**: 关键词过滤与监控配置。

---

## ⚖️ 开源协议

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

© 2026 AIYXDATA. All rights reserved.
