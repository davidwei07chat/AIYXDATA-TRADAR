# TrendRadar 微信 OAuth 2.0 + 用户管理系统 - 开发执行文档

**文档版本**: 1.0  
**创建日期**: 2026-04-20  
**最后更新**: 2026-04-20  
**状态**: 待审核

---

## 1. 项目概述

### 1.1 功能目标
为 TrendRadar 添加微信扫码登录功能，实现完整的用户认证、登录记录管理和使用情况统计系统。

### 1.2 核心需求
- ✓ 微信扫码登录（OAuth 2.0）
- ✓ 用户信息管理
- ✓ 登录记录追踪
- ✓ 操作日志记录
- ✓ 管理后台（查看用户、登录记录、使用统计）
- ✓ 最小化对现有功能的影响

### 1.3 系统架构
```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │  前端应用 (HTML/CSS/JS)                           │   │
│  │  - 登录页面 (微信二维码)                          │   │
│  │  - 主应用界面                                    │   │
│  │  - 管理后台 (仅管理员)                           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/HTTPS
┌─────────────────────────────────────────────────────────┐
│              TrendRadar 服务器 (Python)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  HTTP 服务器 (server.py)                         │   │
│  │  - 认证中间件 (Token 验证)                       │   │
│  │  - 微信 OAuth 回调处理                           │   │
│  │  - 现有 API 端点 (带权限检查)                    │   │
│  │  - 管理后台 API                                  │   │
│  │  - 审计日志记录                                  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  主程序 (爬虫、AI分析、通知)                      │   │
│  │  - 内部调用 bypass 认证                          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕ API
┌─────────────────────────────────────────────────────────┐
│                  微信开放平台                             │
│  - OAuth 2.0 认证服务                                   │
└─────────────────────────────────────────────────────────┘
                          ↕ API
┌─────────────────────────────────────────────────────────┐
│                    Supabase                              │
│  - PostgreSQL 数据库                                    │
│  - REST API                                             │
│  - 用户表、登录记录表、操作日志表                        │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 功能需求详解

### 2.1 微信扫码登录流程

**流程图**:
```
1. 用户访问登录页面
   ↓
2. 前端生成微信二维码 (调用微信 JS-SDK)
   ↓
3. 用户扫码授权
   ↓
4. 微信重定向到回调 URL (带 code)
   ↓
5. 后端用 code 换取 access_token
   ↓
6. 后端用 access_token 获取用户信息 (openid, nickname, avatar)
   ↓
7. 后端查询/创建用户记录
   ↓
8. 后端生成 JWT token
   ↓
9. 前端存储 token (localStorage)
   ↓
10. 前端重定向到主应用
```

**关键参数**:
- `client_id`: 微信应用 ID
- `client_secret`: 微信应用密钥
- `redirect_uri`: 回调地址 (e.g., `https://your-domain.com/oauth/callback`)
- `scope`: `snsapi_userinfo` (获取用户信息)

### 2.2 用户管理功能

**用户信息**:
- `user_id`: 唯一标识 (UUID)
- `openid`: 微信 openid
- `unionid`: 微信 unionid (可选)
- `nickname`: 昵称
- `avatar_url`: 头像 URL
- `created_at`: 创建时间
- `last_login_at`: 最后登录时间
- `is_admin`: 是否管理员 (默认 false)
- `status`: 账户状态 (active/inactive/banned)

### 2.3 登录记录管理

**记录内容**:
- `login_id`: 唯一标识
- `user_id`: 用户 ID
- `login_time`: 登录时间
- `ip_address`: IP 地址
- `user_agent`: 用户代理 (浏览器信息)
- `device_type`: 设备类型 (web/mobile)
- `login_status`: 登录状态 (success/failed)
- `failure_reason`: 失败原因 (如果失败)

**查询功能**:
- 按用户查询登录历史
- 按时间范围查询
- 按 IP 地址查询
- 导出登录记录

### 2.4 使用情况统计

**操作日志**:
- `log_id`: 唯一标识
- `user_id`: 用户 ID
- `operation_type`: 操作类型 (load_config/save_config/refresh_data/etc)
- `operation_time`: 操作时间
- `operation_details`: 操作详情 (JSON)
- `status`: 操作状态 (success/failed)
- `error_message`: 错误信息 (如果失败)

**统计指标**:
- 用户活跃度 (日/周/月)
- 操作频率分布
- 功能使用热力图
- 错误率统计

### 2.5 管理后台功能

**仅管理员可访问**:
- 用户列表 (搜索、过滤、分页)
- 用户详情 (登录历史、操作记录)
- 登录记录查询
- 操作日志查询
- 使用统计仪表板
- 用户禁用/启用
- 权限管理

---

## 3. 技术方案

### 3.1 后端架构改造

**新增模块**:
```
/TrendRadar/docker/
├── auth/
│   ├── __init__.py
│   ├── oauth.py          # 微信 OAuth 处理
│   ├── jwt_handler.py    # JWT token 生成/验证
│   ├── middleware.py     # 认证中间件
│   └── permissions.py    # 权限检查
├── models/
│   ├── __init__.py
│   ├── user.py           # 用户模型
│   ├── login_log.py      # 登录记录模型
│   └── operation_log.py  # 操作日志模型
├── services/
│   ├── __init__.py
│   ├── user_service.py   # 用户服务
│   ├── auth_service.py   # 认证服务
│   └── audit_service.py  # 审计服务
├── api/
│   ├── __init__.py
│   ├── auth_routes.py    # 认证路由
│   ├── admin_routes.py   # 管理后台路由
│   └── audit_routes.py   # 审计数据路由
└── server.py             # 改造现有服务器
```

**改造现有 server.py**:
- 添加认证中间件
- 为现有 API 端点添加权限检查
- 添加新的认证路由
- 添加管理后台路由
- 为内部调用设置 bypass 机制

### 3.2 数据库设计 (Supabase PostgreSQL)

**表结构**:

#### users 表
```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  openid VARCHAR(255) UNIQUE NOT NULL,
  unionid VARCHAR(255),
  nickname VARCHAR(255),
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP,
  is_admin BOOLEAN DEFAULT FALSE,
  status VARCHAR(50) DEFAULT 'active',
  metadata JSONB
);

CREATE INDEX idx_users_openid ON users(openid);
CREATE INDEX idx_users_status ON users(status);
```

#### login_logs 表
```sql
CREATE TABLE login_logs (
  login_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(45),
  user_agent TEXT,
  device_type VARCHAR(50),
  login_status VARCHAR(50),
  failure_reason TEXT,
  metadata JSONB
);

CREATE INDEX idx_login_logs_user_id ON login_logs(user_id);
CREATE INDEX idx_login_logs_login_time ON login_logs(login_time);
CREATE INDEX idx_login_logs_ip_address ON login_logs(ip_address);
```

#### operation_logs 表
```sql
CREATE TABLE operation_logs (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id),
  operation_type VARCHAR(100) NOT NULL,
  operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  operation_details JSONB,
  status VARCHAR(50),
  error_message TEXT,
  metadata JSONB
);

CREATE INDEX idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_operation_type ON operation_logs(operation_type);
CREATE INDEX idx_operation_logs_operation_time ON operation_logs(operation_time);
```

### 3.3 API 端点设计

#### 认证相关
```
POST /oauth/login
  - 返回微信二维码 URL

GET /oauth/callback?code=xxx&state=xxx
  - 微信回调处理
  - 返回 JWT token

POST /oauth/logout
  - 登出 (需要 token)

POST /oauth/refresh
  - 刷新 token
```

#### 用户相关
```
GET /api/user/profile
  - 获取当前用户信息 (需要 token)

GET /api/user/login-history
  - 获取登录历史 (需要 token)

GET /api/user/operation-history
  - 获取操作历史 (需要 token)
```

#### 管理后台 (需要 admin token)
```
GET /admin/users
  - 获取用户列表

GET /admin/users/{user_id}
  - 获取用户详情

POST /admin/users/{user_id}/ban
  - 禁用用户

POST /admin/users/{user_id}/unban
  - 启用用户

POST /admin/users/{user_id}/promote
  - 提升为管理员

GET /admin/login-logs
  - 获取登录记录

GET /admin/operation-logs
  - 获取操作日志

GET /admin/statistics
  - 获取统计数据
```

### 3.4 前端改造方案

**新增页面**:
- `/login.html` - 登录页面 (微信二维码)
- `/admin/dashboard.html` - 管理后台首页
- `/admin/users.html` - 用户管理
- `/admin/logs.html` - 日志查询

**改造现有页面**:
- 添加登出按钮
- 添加用户信息显示
- 添加权限检查 (隐藏/禁用无权限功能)

**前端逻辑**:
```javascript
// 存储 token
localStorage.setItem('auth_token', token);

// 发送请求时携带 token
fetch('/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
});

// 处理 401 响应 (token 过期)
if (response.status === 401) {
  localStorage.removeItem('auth_token');
  window.location.href = '/login.html';
}
```

---

## 4. 配置要求

### 4.1 微信开放平台配置

**前置条件**:
- 拥有微信企业认证账号
- 已申请微信开放平台权限

**配置步骤**:
1. 登录 [微信开放平台](https://open.weixin.qq.com/)
2. 创建网站应用
3. 获取 `AppID` 和 `AppSecret`
4. 配置授权回调域名: `your-domain.com`
5. 配置回调 URL: `https://your-domain.com/oauth/callback`

### 4.2 Supabase 配置

**前置条件**:
- 拥有 Supabase 账号

**配置步骤**:
1. 登录 [Supabase](https://supabase.com/)
2. 创建新项目
3. 获取 `Project URL` 和 `API Key`
4. 在 SQL Editor 中执行数据库初始化脚本 (见 3.2)
5. 配置 RLS (Row Level Security) 策略

### 4.3 环境变量设置

**在 `/TrendRadar/config/config.yaml` 中添加**:
```yaml
auth:
  enabled: true
  jwt_secret: "your-secret-key-here"
  jwt_expiry: 86400  # 24 hours
  
wechat:
  app_id: "your-app-id"
  app_secret: "your-app-secret"
  redirect_uri: "https://your-domain.com/oauth/callback"
  
supabase:
  url: "https://your-project.supabase.co"
  api_key: "your-api-key"
  
admin:
  default_admin_openid: "admin-openid-here"  # 初始管理员
```

**或使用环境变量**:
```bash
export WECHAT_APP_ID="your-app-id"
export WECHAT_APP_SECRET="your-app-secret"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_API_KEY="your-api-key"
export JWT_SECRET="your-secret-key"
```

### 4.4 数据库初始化

**执行 SQL 脚本**:
```bash
# 在 Supabase SQL Editor 中执行
psql -h your-project.supabase.co -U postgres -d postgres -f init_database.sql
```

---

## 5. 实现细节

### 5.1 后端改造步骤

#### 第一阶段: 基础认证框架
1. 创建 `auth/` 模块
2. 实现 JWT token 生成/验证
3. 实现认证中间件
4. 改造 `server.py` 集成中间件

#### 第二阶段: 微信 OAuth
1. 实现微信 OAuth 流程
2. 添加 `/oauth/login` 和 `/oauth/callback` 端点
3. 实现用户创建/更新逻辑
4. 添加登录记录

#### 第三阶段: 审计系统
1. 创建 `audit_service.py`
2. 为所有 API 端点添加操作日志记录
3. 实现审计数据查询 API

#### 第四阶段: 管理后台
1. 创建 `admin_routes.py`
2. 实现用户管理 API
3. 实现日志查询 API
4. 实现统计 API

#### 第五阶段: 内部调用 bypass
1. 为爬虫、MCP 服务器添加内部 token
2. 实现 bypass 机制
3. 测试内部调用不受影响

### 5.2 前端改造步骤

#### 第一阶段: 登录页面
1. 创建 `/login.html`
2. 集成微信 JS-SDK
3. 实现二维码扫描逻辑
4. 实现 token 存储

#### 第二阶段: 主应用改造
1. 添加登出按钮
2. 添加用户信息显示
3. 添加 token 验证逻辑
4. 处理 401 响应

#### 第三阶段: 管理后台
1. 创建管理后台页面
2. 实现用户列表查询
3. 实现日志查询
4. 实现统计展示

### 5.3 关键代码片段

#### JWT Token 生成
```python
import jwt
from datetime import datetime, timedelta

def generate_token(user_id, secret_key, expiry=86400):
    payload = {
        'user_id': str(user_id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=expiry)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token, secret_key):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

#### 认证中间件
```python
def auth_middleware(handler_func):
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized')
            return
        
        token = auth_header[7:]
        payload = verify_token(token, JWT_SECRET)
        if not payload:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Invalid token')
            return
        
        self.user_id = payload['user_id']
        return handler_func(self, *args, **kwargs)
    
    return wrapper
```

#### 微信 OAuth 回调
```python
def handle_oauth_callback(code, state):
    # 1. 用 code 换取 access_token
    token_response = requests.post(
        'https://api.weixin.qq.com/sns/oauth2/access_token',
        params={
            'appid': WECHAT_APP_ID,
            'secret': WECHAT_APP_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )
    
    access_token = token_response.json()['access_token']
    openid = token_response.json()['openid']
    
    # 2. 用 access_token 获取用户信息
    user_info_response = requests.get(
        'https://api.weixin.qq.com/sns/userinfo',
        params={
            'access_token': access_token,
            'openid': openid
        }
    )
    
    user_info = user_info_response.json()
    
    # 3. 查询/创建用户
    user = get_or_create_user(
        openid=openid,
        nickname=user_info.get('nickname'),
        avatar_url=user_info.get('headimgurl')
    )
    
    # 4. 记录登录
    log_login(user_id=user['user_id'], ip_address=get_client_ip())
    
    # 5. 生成 JWT token
    token = generate_token(user['user_id'], JWT_SECRET)
    
    return token
```

---

## 6. 部署和测试

### 6.1 本地开发环境搭建

**安装依赖**:
```bash
pip install pyjwt authlib requests supabase-py
```

**配置本地环境**:
```bash
# 创建 .env 文件
cat > /TrendRadar/.env << EOF
WECHAT_APP_ID=your-test-app-id
WECHAT_APP_SECRET=your-test-app-secret
SUPABASE_URL=https://your-test-project.supabase.co
SUPABASE_API_KEY=your-test-api-key
JWT_SECRET=your-test-secret
EOF
```

**启动服务**:
```bash
cd /TrendRadar/docker
python server.py
```

### 6.2 测试用例

#### 单元测试
- JWT token 生成/验证
- 用户创建/查询
- 权限检查
- 日志记录

#### 集成测试
- 完整的微信登录流程
- 登出流程
- 管理后台操作
- 内部调用 bypass

#### 端到端测试
- 用户登录 → 使用应用 → 查看日志
- 管理员查看用户列表和统计
- 权限检查 (非管理员无法访问管理后台)

### 6.3 生产环境部署

**前置条件**:
- 已配置微信开放平台
- 已配置 Supabase
- 已配置 HTTPS 证书

**部署步骤**:
1. 更新 `config.yaml` 中的生产环境配置
2. 初始化数据库
3. 设置第一个管理员用户
4. 启动服务
5. 验证登录流程

### 6.4 监控和日志

**关键指标**:
- 登录成功率
- 平均响应时间
- 错误率
- 活跃用户数

**日志位置**:
- 应用日志: `/TrendRadar/logs/app.log`
- 审计日志: Supabase `operation_logs` 表
- 登录日志: Supabase `login_logs` 表

---

## 7. 风险评估和缓解方案

### 7.1 对现有功能的影响

**风险**: 现有 API 调用需要认证
**缓解方案**:
- 为内部调用 (爬虫、MCP) 设置 bypass token
- 提供迁移指南
- 保持向后兼容性 (可配置认证开关)

**风险**: 性能下降
**缓解方案**:
- 使用 JWT token (无状态，无需数据库查询)
- 缓存用户信息
- 异步记录审计日志

### 7.2 性能影响

**预期影响**:
- 每个请求增加 10-50ms (token 验证)
- 数据库查询增加 (审计日志)

**优化方案**:
- 使用 Redis 缓存 token 验证结果
- 批量写入审计日志
- 定期清理过期日志

### 7.3 安全考虑

**威胁**: Token 泄露
**缓解方案**:
- 使用 HTTPS 传输
- 设置 token 过期时间
- 实现 token 刷新机制

**威胁**: 微信账号被盗
**缓解方案**:
- 记录登录 IP 和设备信息
- 异常登录告警
- 支持账号禁用

**威胁**: SQL 注入
**缓解方案**:
- 使用 ORM 或参数化查询
- 输入验证
- 定期安全审计

---

## 8. 时间表和里程碑

### 8.1 项目阶段

| 阶段 | 任务 | 预计工作量 | 开始日期 | 结束日期 |
|------|------|----------|--------|--------|
| 1 | 基础认证框架 | 2 天 | - | - |
| 2 | 微信 OAuth 集成 | 2 天 | - | - |
| 3 | 审计系统 | 2 天 | - | - |
| 4 | 管理后台 | 2 天 | - | - |
| 5 | 前端改造 | 2 天 | - | - |
| 6 | 测试和优化 | 2 天 | - | - |
| 7 | 文档和部署 | 1 天 | - | - |
| **总计** | | **13 天** | | |

### 8.2 关键节点

- [ ] 微信开放平台配置完成
- [ ] Supabase 项目创建和初始化
- [ ] 本地开发环境搭建
- [ ] 基础认证框架完成
- [ ] 微信登录流程测试通过
- [ ] 管理后台功能完成
- [ ] 全面测试通过
- [ ] 生产环境部署

---

## 9. 验收标准

### 9.1 功能验收

- ✓ 用户可通过微信扫码登录
- ✓ 登录后可访问应用
- ✓ 登出功能正常
- ✓ 管理员可查看用户列表
- ✓ 管理员可查看登录记录
- ✓ 管理员可查看操作日志
- ✓ 管理员可查看统计数据
- ✓ 内部调用不受认证影响

### 9.2 性能验收

- ✓ 登录响应时间 < 2 秒
- ✓ API 响应时间增加 < 50ms
- ✓ 数据库查询时间 < 100ms

### 9.3 安全验收

- ✓ 所有敏感数据使用 HTTPS 传输
- ✓ Token 无法被伪造
- ✓ 权限检查正确实施
- ✓ 审计日志完整记录

---

## 10. 附录

### 10.1 参考资源

- [微信开放平台文档](https://developers.weixin.qq.com/)
- [Supabase 文档](https://supabase.com/docs)
- [JWT 标准](https://tools.ietf.org/html/rfc7519)
- [OAuth 2.0 规范](https://tools.ietf.org/html/rfc6749)

### 10.2 常见问题

**Q: 如何处理微信账号注销?**
A: 在 `users` 表中标记 `status = 'inactive'`，禁止登录。

**Q: 如何迁移现有用户?**
A: 为现有用户生成虚拟 openid，或要求重新登录。

**Q: 如何支持多个微信账号?**
A: 使用 `unionid` 字段关联同一用户的多个微信账号。

### 10.3 后续优化方向

- [ ] 支持其他登录方式 (GitHub, Google)
- [ ] 实现 2FA (双因素认证)
- [ ] 添加用户角色和权限系统
- [ ] 实现审计日志导出功能
- [ ] 添加登录异常告警
- [ ] 实现用户行为分析

---

**文档完成**  
**下一步**: 用户审核文档内容，确认无误后开始实现
