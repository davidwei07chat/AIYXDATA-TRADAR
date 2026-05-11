# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.2.0] - 2026-05-11

### Added
- AI 模型查询功能优化，支持多种 API 响应格式
- `/api/ai_refresh` 端点，支持强制刷新 AI 分析
- `get_latest_ai_report()` 方法，获取最新 AI 报告
- 详细的调试日志输出（sys.stderr）
- 模态框体验改进：增大尺寸、禁止背景关闭
- 搜索框固定显示功能

### Changed
- 改进 `/api/check_ai_connection` 端点，支持 /v1 路径自动重试
- 增强 `/api/get_ai_models` 端点，支持多种响应格式（data/models/result/items）
- 优化模型列表高度（max-h-96，可显示6个模型）
- 容器名称标准化为 `aiyxdata_tradar`
- 端口映射改为 `127.0.0.1:8084:8080`（更安全）

### Fixed
- 修复 JSON 解析错误（"Expecting value: line 1 column 1"）
- 修复 HTML 响应被误当作 JSON 处理的问题
- 修复模型列表不显示的问题

### Documentation
- 更新 `docs/202603071010 Visual_Config_Integration_Manual.md`
- 更新 `docs/202603131205 Development_Retrospective.md`
- 新增功能架构说明
- 新增 API 端点文档
- 新增文件路径索引

## [6.1.0] - 2026-03-06

### Added
- AI 分析内容按【地区/主题】标签自动分段，提升可读性

## [6.0.0] - 2026-03-XX

### Added
- 初始版本发布
- 多维热点聚合功能
- RSS/Atom 增强支持
- AI 智能分析
- 全程渠道通知
- 弹性调度系统
- 自动化报告生成
