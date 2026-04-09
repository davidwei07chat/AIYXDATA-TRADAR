# Architecture Baseline & Stability Policy / 架构基准与稳定性策略

## Summary / 摘要
This document defines the stable architecture baseline for the TrendRadar project, including Nginx reverse proxy configurations and Docker infrastructure. Any modification to these "anchors" requires explicit justification and user approval.
本文定义了 TrendRadar 项目的稳定架构基准，包括 Nginx 反向代理配置和 Docker 基础设施。对这些“锚点”的任何修改都需要明确的理由和用户批准。

## Project Anchors / 项目锚点

### 1. Nginx Reverse Proxy / Nginx 反向代理
- **Primary Domain / 主域名**: `aiyxdata_tradar.aiyxdatatop.us.ci`
- **Configuration File / 配置文件**: `/etc/nginx/sites-available/aiyxdata_tradar.aiyxdatatop.us.ci.conf`
- **Policy / 策略**:
  - `listen 80` must redirect to `443`.
  - `listen 443 ssl` handles primary traffic.
  - Proxy to `http://127.0.0.1:8080`.
  - SSL certificates located at `/etc/nginx/ssl/werss.crt`.

### 2. Docker Infrastructure / Docker 基础设施
- **Compose Path / Compose 路径**: `/TrendRadar/docker/docker-compose.yml`
- **Main Service / 主服务**: `aiyxdata_tradar`
- **Network / 网络**: `docker_default`
- **Policy / 策略**:
  - Container name must be `aiyxdata_tradar`.
  - Internal/External port mapped to `8080`.
  - Volumes mapped to `../config` and `../output`.

### 3. Change Management / 变更管理
- **Strict Isolation / 严格隔离**: Use `include` statements for adding new proxy routes instead of modifying existing server blocks.
- **Physical Safety / 物理安全**: Protect core files using `chmod` if requested, though logical governance via KI is preferred.
- **Verification / 验证**: Every change to Nginx MUST be preceded by `nginx -t`.

## Version History / 版本历史
- **2026-03-08**: Initial baseline established by Antigravity after fixing web server startup issue.
