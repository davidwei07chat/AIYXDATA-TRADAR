# TrendRadar 深度技术分析报告

**文档创建时间**: 2026-04-09  
**分析版本**: v6.0.0  
**文档类型**: 技术架构与功能分析

---

## 📊 一、项目定位与核心价值

**TrendRadar** 是一个**智能热点新闻聚合与分析工具**，其核心价值在于：

- **信息过滤**：从海量新闻中筛选用户真正关心的内容
- **智能分析**：利用 AI 深度解读热点趋势和舆情态势
- **多渠道推送**：支持 9+ 种通知渠道的自动化推送
- **轻量部署**：30秒即可完成部署，支持 GitHub Actions、Docker、本地运行

---

## 🏗️ 二、技术架构深度剖析

### 2.1 整体架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    调度系统 (Scheduler)                   │
│         timeline.yaml 定义时间段 → 触发不同任务          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ 数据抓取 │  │ AI 分析  │  │ 推送通知 │
   └────┬────┘  └────┬────┘  └────┬────┘
        │            │            │
        ▼            ▼            ▼
   ┌──────────────────────────────────┐
   │      存储层 (Storage Layer)       │
   │  SQLite + 本地文件 / S3 云存储    │
   └──────────────────────────────────┘
```

### 2.2 核心模块技术实现

#### 1. 数据抓取模块 (Crawler)

**文件位置**: `aiyxdata_tradar/crawler/fetcher.py`

**技术栈**:
- `requests` - HTTP 请求库
- 自定义重试机制（指数退避）
- 代理支持

**数据源**:
- **热榜平台**: 通过 [NewsNow API](https://github.com/ourongxing/newsnow) 获取 10+ 平台热榜
  - 微博、知乎、百度、抖音、B站、今日头条等
  - API 地址: `https://newsnow.busiyi.world/api/s`
- **RSS 订阅**: 使用 `feedparser` 解析 RSS/Atom 源

**关键技术特性**:
```python
# 智能重试机制
- 最大重试次数: 2 次
- 随机延迟: 3-5 秒基础 + 指数增长
- 请求间隔: 50-120ms（防止被封）

# 数据去重
- 同一标题多次出现时合并排名
- 保留所有排名历史用于趋势分析

# 容错处理
- 跳过无效标题（None、float、空字符串）
- 单个平台失败不影响其他平台
```

#### 2. AI 分析模块 (AI Analyzer)

**文件位置**: `aiyxdata_tradar/ai/analyzer.py`

**技术栈**:
- **LiteLLM** - 统一 AI 接口层
- 支持 100+ AI 提供商（OpenAI、Claude、Gemini、DeepSeek 等）

**核心分析维度**:
```python
1. 核心热点与舆情态势 (core_trends)
2. 舆论风向与争议 (sentiment_controversy)
3. 异动与弱信号 (signals)
4. RSS 深度洞察 (rss_insights)
5. 研判与策略建议 (outlook_strategy)
6. 独立源概括 (standalone_summaries)
```

**技术亮点**:

**Prompt 工程 2.0**:
- 格式规则从 JSON 中提取到独立规范区
- 所有 JSON 字段声明为可选（提升容错性）
- 移除 Markdown 格式要求（减少输出不一致）

**配置示例**:
```yaml
ai:
  model: "deepseek/deepseek-chat"  # 格式: provider/model_name
  api_key: "sk-xxx"
  api_base: "https://api.deepseek.com"  # 可选
  timeout: 120
  max_tokens: 5000
  num_retries: 3  # 自动重试
  fallback_models:  # 降级模型
    - "openai/gpt-4o-mini"
```

**分析流程**:
```python
1. 数据准备
   - 限制分析数量（默认 50 条，防止 Token 超限）
   - 包含排名时间线（可选）
   - 合并热榜 + RSS 数据

2. Prompt 构建
   [system] 角色定义 + 输出格式规范
   [user] 新闻内容 + 分析维度要求

3. LiteLLM 调用
   - 自动重试（num_retries）
   - 降级模型（fallback_models）
   - 超时控制（timeout）

4. 结果解析
   - JSON 格式提取
   - 容错处理（缺失字段填充默认值）
   - 嵌入 HTML 报告
```

#### 3. 存储管理模块 (Storage Manager)

**文件位置**: `aiyxdata_tradar/storage/manager.py`

**多后端架构**:

```python
┌─ LocalStorageBackend (本地存储)
│   ├─ news.db (SQLite 数据库)
│   ├─ YYYY-MM-DD.txt (纯文本快照)
│   └─ YYYY-MM-DD.html (可视化报告)
│
└─ RemoteStorageBackend (远程存储)
    ├─ S3 兼容协议
    ├─ 支持 Cloudflare R2、阿里云 OSS、腾讯云 COS
    ├─ 自动同步到云端
    └─ 支持从远程拉取历史数据
```

**智能选择逻辑**:
```python
if backend_type == "auto":
    if is_github_actions() and has_remote_config():
        return "remote"  # GitHub Actions + 远程配置 → 云存储
    else:
        return "local"   # 其他情况 → 本地存储
```

**数据保留策略**:
```yaml
storage:
  local_retention_days: 30   # 本地保留 30 天
  remote_retention_days: 90  # 远程保留 90 天
  pull_enabled: true         # 启动时自动拉取
  pull_days: 7               # 拉取最近 7 天数据
```

#### 4. 调度系统 (Scheduler)

**配置文件**: `config/timeline.yaml` (v2.0.0)

**5 种预设模板**:

| 模板 | 说明 | 适用场景 |
|------|------|---------|
| `always_on` | 24/7 全天候推送 | 实时监控 |
| `morning_evening` | 早晚汇总（推荐） | 日常使用 |
| `office_hours` | 工作日三段式 | 上班族 |
| `night_owl` | 深夜汇总 | 夜猫子 |
| `custom` | 完全自定义 | 高级用户 |

**时间段配置示例**:
```yaml
day_plans:
  weekday:
    - start: "09:00"
      end: "18:00"
      push: true              # 推送开关
      analysis: true          # AI 分析开关
      report_mode: "incremental"  # 报告模式
      once_per_period: true   # 时间段内只推送一次
```

**调度逻辑**:
```python
1. 每次运行时读取当前时间（app.timezone）
2. 匹配当前时间所属时间段
3. 根据时间段配置决定：
   - 是否推送（push）
   - 是否 AI 分析（analysis）
   - 使用什么报告模式（report_mode）
4. 时间段去重（once_per_period）
```

**可视化编辑器**:
- Web 界面实时预览 7×24 时间线
- 拖拽式配置，自动同步到 YAML
- 预设模板一键切换

#### 5. 通知推送模块 (Notification)

**文件位置**: `aiyxdata_tradar/notification/`

**支持 9+ 渠道**:

| 渠道 | 配置项 | 多账号支持 |
|------|--------|-----------|
| 飞书 | webhook_url | ✅ |
| 钉钉 | webhook_url | ✅ |
| 企业微信 | webhook_url | ✅ |
| Telegram | bot_token + chat_id | ✅ |
| Email | from + password + to | ✅ |
| ntfy | server_url + topic | ✅ |
| Bark | url | ✅ |
| Slack | webhook_url | ✅ |
| Generic Webhook | webhook_url + payload_template | ✅ |

**多账号配置**:
```yaml
notification:
  channels:
    feishu:
      webhook_url: "url1;url2;url3"  # 分号分隔
    telegram:
      bot_token: "token1;token2"
      chat_id: "chat1;chat2"  # 配对配置数量必须一致
```

**智能分割**:
- 根据各渠道字节限制自动分割长消息
- 飞书 30KB、钉钉 20KB、企业微信 20KB
- 保持 Markdown 格式完整性

**格式适配**:
```python
# Markdown 自动转换为各平台原生格式
- 飞书: 富文本卡片
- 钉钉: Markdown
- 企业微信: Markdown / Text
- Telegram: HTML
- Email: HTML
```

#### 6. MCP Server (Model Context Protocol)

**文件位置**: `mcp_server/server.py`

**技术栈**:
- **FastMCP 2.0** - 生产级 MCP 框架
- 支持 stdio 和 HTTP 两种传输模式

**核心工具分类**:

**数据查询工具**:
```python
- get_latest_news()        # 获取最新热点
- search_news()            # 关键词搜索
- get_news_by_date()       # 按日期查询
- get_rss_feeds_status()   # RSS 源状态
```

**分析工具**:
```python
- analyze_sentiment()      # 情感分析
- analyze_trend()          # 趋势分析
- compare_platforms()      # 平台对比
- get_keyword_stats()      # 关键词统计
```

**文章阅读工具**:
```python
- read_article(url)        # 单篇文章（Jina AI Reader）
- read_articles_batch()    # 批量读取（最多 5 篇）
```

**推送工具**:
```python
- push_to_channels()       # 推送 AI 消息到所有渠道
- get_channel_format_guide()  # 获取渠道格式指南
```

**应用场景**:
- Claude Desktop 集成
- VS Code 扩展
- 自定义 AI 应用

**使用示例**:
```python
# 1. 用户问："分析 AI 本周的情感倾向"
# 2. AI 调用 resolve_date_range("本周")
#    → {"date_range": {"start": "2026-04-07", "end": "2026-04-13"}}
# 3. AI 调用 analyze_sentiment(topic="ai", date_range=...)
#    → 返回情感分析结果
```

---

## 🔧 三、关键技术原理

### 3.1 关键词匹配与频率统计

**配置文件**: `config/frequency_words.txt`

```
[AI 技术]
人工智能, ChatGPT, GPT, Claude, AI

[科技公司]
苹果, 特斯拉, 微软, 谷歌
```

**匹配逻辑**:
```python
1. 遍历所有新闻标题
2. 检查是否包含关键词（支持正则）
3. 统计每个关键词出现次数和排名
4. 按关键词或平台分组展示
```

**排序策略**:
```yaml
report:
  sort_by_position_first: false  # false: 按匹配数排序
                                 # true: 按配置文件顺序
```

### 3.2 增量检测机制

**SQLite 数据库结构**:
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    platform TEXT NOT NULL,
    rank INTEGER,
    url TEXT,
    timestamp TEXT,
    crawl_time TEXT,
    UNIQUE(title, platform, crawl_time)
);
```

**增量检测流程**:
```python
1. 查询数据库中已存在的新闻
2. 对比当前抓取的新闻
3. 标记新增项（new_items）
4. 根据报告模式决定推送内容：
   - daily: 当日所有 + 新增区域
   - current: 当前榜单 + 新增区域
   - incremental: 仅新增
```

### 3.3 AI 分析流程

**数据准备**:
```python
# 限制分析数量（防止 Token 超限）
max_news = 50  # 默认值

# 包含排名时间线（可选）
include_rank_timeline = True  # 用于趋势分析

# 合并热榜 + RSS 数据
news_content = format_hotlist_news(stats)
rss_content = format_rss_news(rss_stats)
```

**Prompt 构建**:
```python
# 使用安全的字符串替换
user_prompt = template.replace("{report_mode}", mode)
user_prompt = user_prompt.replace("{current_time}", time)
user_prompt = user_prompt.replace("{news_count}", str(count))
```

**LiteLLM 调用**:
```python
response = litellm.completion(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    timeout=timeout,
    max_tokens=max_tokens,
    num_retries=num_retries,
    fallback_models=fallback_models
)
```

**结果解析**:
```python
# JSON 格式提取
data = json.loads(response.choices[0].message.content)

# 容错处理
result = AIAnalysisResult(
    core_trends=data.get("core_trends", ""),
    sentiment_controversy=data.get("sentiment_controversy", ""),
    # ... 缺失字段填充默认值
)
```

### 3.4 时间调度原理

**配置加载**:
```python
# 读取 timeline.yaml
timeline_config = load_yaml("config/timeline.yaml")
preset = config.get("schedule", {}).get("preset", "always_on")

# 获取预设配置
preset_config = timeline_config["presets"][preset]
```

**时间匹配**:
```python
# 获取当前时间（时区感知）
current_time = datetime.now(pytz.timezone(app_timezone))
weekday = current_time.strftime("%A").lower()

# 匹配时间段
for period in day_plans[weekday]:
    if period["start"] <= current_time.time() <= period["end"]:
        return period  # 返回当前时间段配置
```

**去重机制**:
```python
# once_per_period: true 时
last_push_key = f"{date}_{period_start}_{period_end}"
if last_push_key in pushed_periods:
    return  # 已推送过，跳过
pushed_periods.add(last_push_key)
```

---

## 🎯 四、应用场景分析

### 4.1 个人用户场景

**信息过滤**:
- 只关注 AI、科技、金融等特定领域
- 配置关键词组，自动筛选相关新闻

**避免信息过载**:
- 增量模式只推送新增内容
- 时间段控制推送频率

**多设备同步**:
- 通过 Telegram/Email 随时查看
- 支持移动端推送（Bark、ntfy）

### 4.2 企业/团队场景

**舆情监控**:
- 实时追踪品牌/产品相关热点
- AI 分析舆论风向和争议

**竞品分析**:
- 监控竞争对手动态
- 对比不同平台的热度

**行业洞察**:
- AI 分析行业趋势和风险信号
- 生成每日/每周行业报告

**内部推送**:
- 通过企业微信/飞书推送到团队群
- 支持多账号配置（不同部门不同群）

### 4.3 开发者场景

**MCP Server**:
- 作为 AI 助手的数据源
- Claude Desktop 原生集成

**API 集成**:
- 通过 MCP 工具查询历史数据
- 支持自定义查询条件

**二次开发**:
- 基于 TrendRadar 构建定制化应用
- 模块化架构易于扩展

### 4.4 研究/媒体场景

**热点追踪**:
- 快速发现新兴话题
- 追踪话题演变趋势

**情感分析**:
- 了解公众对事件的态度
- 识别争议性话题

**数据归档**:
- 长期存储新闻数据用于研究
- 支持远程云存储（S3）

---

## 💡 五、技术优势与创新点

### 5.1 架构优势

✅ **模块化设计**
- 爬虫、分析、存储、推送完全解耦
- 单一职责原则，易于维护和测试

✅ **多后端支持**
- 本地/云端存储自动切换
- 适应不同部署环境

✅ **可扩展性**
- 轻松添加新平台（修改 config.yaml）
- 轻松添加新通知渠道（实现统一接口）

### 5.2 AI 集成创新

✅ **LiteLLM 统一接口**
- 一套代码支持 100+ 模型
- 无需为每个提供商编写适配代码

✅ **Prompt 工程 2.0**
- 格式规则独立化，提升输出稳定性
- 所有字段可选，提升容错性

✅ **MCP 协议支持**
- AI 助手原生集成
- 标准化工具接口

### 5.3 用户体验优化

✅ **30 秒部署**
- Fork → 配置 Secrets → 自动运行
- GitHub Actions 免费额度足够使用

✅ **可视化编辑器**
- Web 界面配置，无需手写 YAML
- 实时预览时间线

✅ **多语言翻译**
- AI 自动翻译推送内容
- 支持任意目标语言

### 5.4 工程实践亮点

✅ **容错设计**
- 网络失败自动重试
- AI 输出格式容错
- 单个平台失败不影响其他平台

✅ **性能优化**
- 批量翻译减少 API 调用
- SQLite 索引优化查询
- 智能缓存（NewsNow API 缓存）

✅ **安全性**
- GitHub Secrets 管理敏感信息
- Webhook URL 不暴露在代码中
- 多账号限制（防止滥用）

---

## 📚 六、技术栈总结

| 层级 | 技术选型 | 版本要求 | 作用 |
|------|---------|---------|------|
| **语言** | Python | 3.10+ | 主开发语言 |
| **HTTP 请求** | requests | 2.32.5+ | 数据抓取 |
| **RSS 解析** | feedparser | 6.0.0+ | RSS 源解析 |
| **AI 接口** | LiteLLM | 1.57.0+ | 统一 AI 模型调用 |
| **MCP 框架** | FastMCP | 2.12.0+ | AI 助手集成 |
| **数据库** | SQLite | 内置 | 本地数据存储 |
| **云存储** | boto3 | 1.35.0+ | S3 协议支持 |
| **时区处理** | pytz | 2025.2+ | 时间调度 |
| **配置管理** | PyYAML | 6.0.3+ | YAML 配置解析 |
| **重试机制** | tenacity | 8.5.0 | 自动重试 |
| **WebSocket** | websockets | 13.0+ | MCP 传输 |
| **部署** | GitHub Actions / Docker | - | 自动化运行 |

---

## 🔍 七、为什么它能实现这些功能？

### 7.1 数据聚合能力

**依赖 NewsNow API**:
- 复用成熟的多平台数据源
- 无需自己维护爬虫（避免反爬虫问题）
- API 提供缓存机制（减轻服务器压力）

**RSS 标准协议**:
- 兼容所有支持 RSS/Atom 的网站
- `feedparser` 库自动处理各种格式差异

**去重算法**:
- 基于标题相似度合并重复新闻
- 保留所有排名历史用于趋势分析

### 7.2 智能分析能力

**LiteLLM 抽象层**:
- 屏蔽不同 AI 提供商的 API 差异
- 统一的错误处理和重试机制

**结构化 Prompt**:
- 强制 AI 输出 JSON 格式
- 提供明确的分析维度和字数限制

**上下文注入**:
- 提供排名、时间线等结构化数据
- AI 可以进行趋势分析和异动检测

### 7.3 自动化推送能力

**Webhook 机制**:
- 各平台提供的标准推送接口
- HTTP POST 请求即可完成推送

**调度系统**:
- 基于时间段的条件触发
- 支持复杂的时间规则（工作日/周末、跨午夜）

**GitHub Actions**:
- 免费的定时任务执行环境
- 每月 2000 分钟免费额度

### 7.4 轻量部署能力

**无状态设计**:
- 每次运行独立，无需常驻进程
- 适合 Serverless 架构

**配置驱动**:
- 所有行为通过 YAML 控制
- 无需修改代码即可定制

**容器化**:
- Docker 封装所有依赖
- 一键启动，跨平台运行

---

## 🚀 八、潜在应用扩展

### 8.1 企业舆情监控系统
- 监控品牌关键词
- 自动生成舆情报告
- 预警负面信息

### 8.2 投资决策辅助
- 追踪财经热点
- AI 分析市场情绪
- 识别投资机会和风险

### 8.3 内容创作灵感库
- 自动收集热点话题
- 辅助选题和创作
- 追踪话题热度变化

### 8.4 学术研究工具
- 长期归档新闻数据
- 支持趋势研究
- 提供结构化数据导出

### 8.5 个性化新闻推荐
- 基于用户兴趣标签
- 智能推送相关内容
- 学习用户偏好

---

## 📊 九、性能与限制

### 9.1 性能指标

**数据抓取**:
- 单平台抓取时间: 1-3 秒
- 10 个平台总耗时: 约 30 秒
- 支持并发抓取（可优化）

**AI 分析**:
- 分析 50 条新闻: 10-30 秒（取决于模型）
- Token 消耗: 约 2000-5000 tokens
- 成本: DeepSeek 约 ¥0.01/次

**存储**:
- SQLite 数据库: 每天约 1-2 MB
- 本地文件: 每天约 500 KB
- 远程存储: 支持自动清理

### 9.2 限制与注意事项

**API 依赖**:
- 依赖 NewsNow API 稳定性
- API 限流可能影响抓取

**GitHub Actions 限制**:
- 每月 2000 分钟免费额度
- 单次运行最长 6 小时
- 建议控制抓取频率

**AI 成本**:
- 频繁分析会产生 API 费用
- 建议使用便宜的模型（DeepSeek、Gemini Flash）

**通知渠道限制**:
- 各渠道有消息长度限制
- 频繁推送可能被限流

---

## 🎓 十、总结

TrendRadar 是一个**工程实践优秀、架构设计合理、用户体验友好**的开源项目。

### 核心优势

1. **模块化架构** - 高可扩展性，易于维护
2. **AI 技术** - 智能分析能力，提供深度洞察
3. **自动化调度** - 降低使用门槛，适合各种场景
4. **多渠道推送** - 覆盖各种使用场景
5. **轻量部署** - 30 秒即可上手

### 技术亮点

- **LiteLLM 统一接口** - 支持 100+ AI 模型
- **MCP 协议支持** - AI 助手原生集成
- **多后端存储** - 本地/云端自动切换
- **可视化编辑器** - 降低配置门槛
- **容错设计** - 提升系统稳定性

### 适用场景

- 个人信息过滤
- 企业舆情监控
- 投资决策辅助
- 内容创作灵感
- 学术研究工具

TrendRadar 成功解决了**信息过载时代的个性化新闻聚合**问题，是一个值得学习和借鉴的技术方案。

---

**文档维护**: 本文档基于 TrendRadar v6.0.0 版本分析，后续版本可能有所变化。  
**参考资料**: 
- [TrendRadar GitHub](https://github.com/AIYXDATA/TrendRadar)
- [NewsNow API](https://github.com/ourongxing/newsnow)
- [LiteLLM 文档](https://docs.litellm.ai/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
