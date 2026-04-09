<div align="center" id="aiyxdata_tradar">

# AIYXDATA-TRADAR

**AI-Powered Omnichannel Hotspot Intelligence Assistant**

[Quick Start](#-quick-start) | [Features](#-features) | [Configuration](#-configuration) | [中文](README.md)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Deploy-2496ED?style=flat-square&logo=docker&logoColor=white)](docker/)
[![AI Powered](https://img.shields.io/badge/AI-LiteLLM-FF6B6B?style=flat-square&logo=openai&logoColor=white)](#-ai-intelligent-analysis)

AIYXDATA-TRADAR is an open-source tool designed for efficient information stream management. it extracts real-time trends from multiple global mainstream platforms, performs deep analysis via LiteLLM-integrated AI models, and pushes precise insights to your collaboration tools.

</div>

---

## 🎯 Features

- **🚀 Multi-platform Aggregation**: Real-time crawling of trending lists from Weibo, Zhihu, Douyin, etc., breaking information silos.
- **📰 RSS/Atom Enhancement**: Support for custom RSS/Atom subscription feeds for centralized management of fragmented reading.
- **🤖 AI Intelligent Analysis**: Integrated with LiteLLM supporting 100+ AI providers (e.g., OpenAI, DeepSeek, Google Gemini, Anthropic) for automatic trend detection.
- **📢 Universal Notifications**:
  - **Collaboration**: Slack, Telegram, Discord (Generic Webhook)
  - **Workplace**: Lark (Feishu), DingTalk, WeChat Work
  - **Mobile**: Bark (iOS), ntfy, Email
- **📅 Flexible Scheduling**: Custom `timeline.yaml` logic for precise control over collection and notification windows.
- **📊 Automated Reports**: Built-in lightweight web server for generating beautiful HTML historical analysis reports.

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/davidwei07chat/AIYXDATA-TRADAR.git
cd AIYXDATA-TRADAR
```

### 2. Initialization
```bash
# Recommended Python 3.10+
pip install -r requirements.txt
```

### 3. Core Configuration
Edit `config/config.yaml` and fill in your API keys and notification channel URLs.

### 4. Run
```bash
python -m aiyxdata_tradar
```

---

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

---

## ⚙️ Configuration

- **`config/config.yaml`**: Global core settings (Channels, API Keys, Crawling strategies).
- **`config/timeline.yaml`**: Scheduling settings (Define time windows for push and analysis).
- **`config/frequency_words.txt`**: Keyword filtering and monitoring configuration.

---

## ⚖️ License

Distributed under the [Apache License 2.0](LICENSE).

© 2026 AIYXDATA. All rights reserved.
