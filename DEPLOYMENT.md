# AIYXDATA-TRADAR 部署指南

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 或 Python 3.10+ (本地部署)

## 快速部署

### 方式 1: Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/davidwei07chat/AIYXDATA-TRADAR.git
cd AIYXDATA-TRADAR

# 2. 配置文件准备
# 编辑以下文件，填入您的配置：
# - config/config.yaml (API Key、通知渠道)
# - config/timeline.yaml (时间调度)
# - config/frequency_words.txt (关键词配置)

# 3. 启动服务
docker-compose up -d

# 4. 验证服务
docker-compose ps
docker-compose logs -f trendradar
```

### 方式 2: Docker 单容器

```bash
# 构建镜像
docker build -t aiyxdata-tradar:latest .

# 运行容器
docker run -d \
  --name tradar \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/aiyxdata_tradar:/app/aiyxdata_tradar \
  aiyxdata-tradar:latest

# 查看日志
docker logs -f tradar
```

### 方式 3: 本地 Python 环境

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置文件准备
# 编辑 config/config.yaml 等配置文件

# 3. 启动程序
python -m aiyxdata_tradar
```

## 配置文件说明

### config/config.yaml

核心配置文件，包含：
- **API 密钥**：LiteLLM、各平台爬虫 API
- **通知渠道**：Slack、Telegram、飞书等
- **采集策略**：爬虫超时、重试次数等

示例：
```yaml
litellm:
  api_key: "your-api-key"
  model: "gpt-4"

notifications:
  slack:
    webhook_url: "https://hooks.slack.com/..."
  telegram:
    bot_token: "your-bot-token"
    chat_id: "your-chat-id"
```

### config/timeline.yaml

时间调度配置，定义：
- 采集时间段
- 推送时间段
- 分析时间段

### config/frequency_words.txt

关键词过滤配置，格式：
```
[GLOBAL_FILTER]
keyword1
keyword2

[WORD_GROUPS]
group_name:
  - keyword1
  - keyword2
```

## 常见问题

### Q: 如何查看日志？

```bash
# Docker Compose
docker-compose logs -f trendradar

# Docker 单容器
docker logs -f tradar

# 本地运行
# 日志输出到控制台
```

### Q: 如何更新配置？

```bash
# Docker Compose
# 编辑配置文件后，重启服务
docker-compose restart trendradar

# Docker 单容器
# 编辑配置文件后，重启容器
docker restart tradar
```

### Q: 如何停止服务？

```bash
# Docker Compose
docker-compose down

# Docker 单容器
docker stop tradar
docker rm tradar
```

### Q: 如何查看 Web 报告？

启动后访问 `http://localhost:8080` 查看历史分析报告。

## 故障排查

### 容器无法启动

1. 检查配置文件是否存在：
   ```bash
   ls -la config/
   ```

2. 查看错误日志：
   ```bash
   docker-compose logs trendradar
   ```

3. 检查端口是否被占用：
   ```bash
   lsof -i :8080
   ```

### 爬虫无法获取数据

1. 检查网络连接
2. 验证 API 密钥是否正确
3. 查看应用日志中的错误信息

### 通知无法发送

1. 验证通知渠道配置（Webhook URL、Token 等）
2. 检查网络连接
3. 查看应用日志中的错误信息

## 性能优化

### 内存优化

编辑 `docker-compose.yml`，添加内存限制：
```yaml
services:
  trendradar:
    mem_limit: 512m
    memswap_limit: 1g
```

### CPU 优化

编辑 `docker-compose.yml`，添加 CPU 限制：
```yaml
services:
  trendradar:
    cpus: '1.0'
    cpu_shares: 1024
```

## 生产部署建议

1. **使用反向代理**：Nginx/Caddy 处理 HTTPS
2. **持久化存储**：使用 Docker Volume 或挂载本地目录
3. **日志管理**：配置日志轮转，防止磁盘满
4. **监控告警**：集成 Prometheus/Grafana 监控
5. **备份策略**：定期备份配置和数据文件

## 支持

如有问题，请提交 Issue：https://github.com/davidwei07chat/AIYXDATA-TRADAR/issues
