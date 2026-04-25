# AI 模型查询功能使用指南

## 功能概述

在 TrendRadar 可视化配置编辑器中，AI 模型配置部分新增了一个 **🔍 查询模型** 按钮，用于快速查询和配置 AI 模型。

## 功能特性

### 1. 连接测试
- 验证 API Base 和 API Key 是否有效
- 支持所有 OpenAI 兼容的 API 提供商
- 实时显示连接状态

### 2. 模型列表查询
- 自动获取 API 支持的所有模型列表
- 以网格布局展示，便于浏览
- 支持点击选择

### 3. 自动配置填充
- 选择模型后自动填充模型名称
- 根据模型类型自动应用推荐配置
- 支持的配置项：
  - API Base URL
  - 采样温度 (Temperature)
  - 最大生成 Token 数 (Max Tokens)

### 4. 支持的提供商

| 提供商 | 模型示例 | API Base |
|--------|---------|---------|
| SiliconFlow | deepseek-ai/deepseek-v3 | https://api.siliconflow.cn/v1 |
| OpenAI | gpt-4, gpt-3.5-turbo | https://api.openai.com/v1 |
| DeepSeek | deepseek/deepseek-chat | https://api.deepseek.com/v1 |
| Zhipu (智谱) | zhipu/glm-4, zhipu/glm-4-flash | - |

## 使用步骤

### 步骤 1：打开配置编辑器
访问 `http://localhost:8080/config_editor/` 并导航到 **"8. AI 模型配置"** 模块。

### 步骤 2：填写 API 信息
在右侧配置面板中填写：
- **API Key**: 从 AI 提供商获取的 API 密钥
- **API Base URL**: API 服务的基础 URL（可选，某些提供商有默认值）

### 步骤 3：点击查询按钮
将鼠标悬停在"模型名称"输入框上，点击出现的 **🔍 查询模型** 按钮。

### 步骤 4：测试连接
在弹出的模态框中，点击 **"测试连接"** 按钮验证 API 连接。

### 步骤 5：选择模型
连接成功后，模型列表会自动加载。点击要使用的模型。

### 步骤 6：自动填充
模型名称、API Base（如果需要）、温度和 Max Tokens 会自动填充。

### 步骤 7：保存配置
点击 **"SAVE & RUN 立即分析"** 按钮保存配置。

## 模型配置规则

系统内置了以下模型的推荐配置：

```javascript
{
  'deepseek-ai/deepseek-v3': {
    api_base: 'https://api.siliconflow.cn/v1',
    temperature: 1,
    max_tokens: 10000
  },
  'gpt-4': {
    api_base: 'https://api.openai.com/v1',
    temperature: 1,
    max_tokens: 8000
  },
  'gpt-3.5-turbo': {
    api_base: 'https://api.openai.com/v1',
    temperature: 1,
    max_tokens: 4000
  },
  'zhipu/glm-4': {
    temperature: 1,
    max_tokens: 8000
  },
  'zhipu/glm-4-flash': {
    temperature: 1,
    max_tokens: 8000
  }
}
```

## 常见问题

### Q: 连接测试失败，显示 "401 - Invalid token"
**A:** 这表示 API Key 无效或已过期。请检查：
1. API Key 是否正确复制
2. API Key 是否已过期
3. API Base URL 是否与 API Key 对应的提供商匹配

### Q: 无法获取模型列表
**A:** 可能的原因：
1. API 提供商不支持 `/models` 端点
2. API Key 权限不足
3. 网络连接问题

### Q: 选择模型后配置没有自动填充
**A:** 这是正常的。系统只会自动填充有推荐配置的模型。对于其他模型，您需要手动配置。

### Q: 如何添加新的模型配置规则？
**A:** 编辑 `/TrendRadar/output/config_editor/assets/script.js` 中的 `MODEL_CONFIG_RULES` 对象，添加新的模型配置。

## 技术实现

### 前端函数

- `openModelQueryModal()` - 打开模型查询模态框
- `closeModelQueryModal()` - 关闭模态框
- `testAIConnection()` - 测试 API 连接
- `fetchAvailableModels(apiBase, apiKey)` - 获取模型列表
- `selectModel(modelName)` - 选择模型并自动填充
- `applyModelConfig(modelName)` - 应用模型配置规则

### 后端 API 端点

- `POST /api/check_ai_connection` - 检查 AI 连接
  - 请求体: `{ api_base, api_key, model }`
  - 响应: `{ success, message }`

- `POST /api/get_ai_models` - 获取模型列表
  - 请求体: `{ api_base, api_key }`
  - 响应: `{ success, models: [...] }`

## 文件位置

- **前端脚本**: `/TrendRadar/output/config_editor/assets/script.js`
- **前端样式**: `/TrendRadar/output/config_editor/assets/style.css`
- **后端服务**: `/TrendRadar/docker/server.py`
- **配置文件**: `/TrendRadar/config/config.yaml`

## 更新日志

### v1.0 (2026-04-19)
- ✅ 添加 AI 模型查询功能
- ✅ 支持连接测试
- ✅ 支持模型列表查询
- ✅ 支持自动配置填充
- ✅ 支持多个 AI 提供商

## 相关文档

- [可视化配置编辑器集成技术文档](202603071010%20Visual_Config_Integration_Manual.md)
- [开发复盘文档](202603131205%20Development_Retrospective.md)
