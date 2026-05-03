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

## 🎯 核心功能

- **🚀 多维热点聚合**：支持微博、知乎、抖音等主流平台榜单实时抓取，告别信息茧房。
- **📰 RSS/Atom 增强**：支持自定义 RSS/Atom 订阅源，将碎片化阅读集中管理。
- **🤖 AI 智能分析**：基于 LiteLLM 适配 100+ AI 提供商（如 OpenAI, DeepSeek, Google Gemini, Anthropic），自动生成趋势研判。
  - **v6.1.0 新增**：AI 分析内容按【地区/主题】标签自动分段，提升可读性。每个【中国】、【海外】、【AI科技】等标签下的内容独立成段，段落间有明显的视觉分隔，适用于所有输出渠道（HTML、Markdown、飞书、钉钉等）。
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

---

## ⚙️ 配置详解

- **`config/config.yaml`**: 全局核心设置（通知渠道、API Key、采集策略）。
- **`config/timeline.yaml`**: 时间段调度设置（定义推送与分析的时间窗口）。
- **`config/frequency_words.txt`**: 关键词过滤与监控配置。

---

## ⚖️ 开源协议

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

© 2026 AIYXDATA. All rights reserved.
