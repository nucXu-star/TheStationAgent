# 环境变量配置指南

## 概述

为了安全性，所有敏感信息（如 MongoDB 连接凭证、邮件服务凭证、密钥等）都已从代码中移除，转而使用环境变量配置。

## 快速开始

### 1. 创建 `.env` 文件

复制 `.env.example` 并创建 `.env`：

```bash
cp .env.example .env
```

### 2. 编辑 `.env` 文件

根据你的实际部署环境修改以下配置：

```dotenv
# Flask 配置
FLASK_ENV=production          # development 或 production
FLASK_DEBUG=0                 # 1 或 0
SECRET_KEY=your-super-secret-key-change-me  # 生成一个随机强密钥

# MongoDB 数据库配置
MONGO_URI=mongodb://username:password@host:port/database_name
DATABASE_NAME=station_agent_db

# 邮件服务配置
MAIL_SERVER=smtp.qq.com       # 或其他邮件服务商
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-smtp-auth-code

# 应用运行配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 3. 安装 python-dotenv

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python app.py
```

## 环境变量详解

| 变量名 | 说明 | 示例值 | 默认值 | 生产必须 |
|--------|------|--------|--------|----------|
| **FLASK_ENV** | Flask 运行环境 | production/development | development | ✅ |
| **FLASK_DEBUG** | 是否启用 Debug | 0 或 1 | 0 | ✅ |
| **SECRET_KEY** | Flask 会话密钥 | 任意强随机字符串 | dev-secret-key-change-in-production | ✅ |
| **MONGO_URI** | MongoDB 连接 URI | `mongodb://...` | mongodb://localhost:27017/ | ✅ |
| **DATABASE_NAME** | 数据库名 | station_agent_db | station_agent_db | ✅ |
| **MAIL_SERVER** | 邮件服务器 | smtp.qq.com | smtp.qq.com | ✅ |
| **MAIL_PORT** | 邮件端口 | 465 | 465 | ✅ |
| **MAIL_USE_SSL** | 是否使用 SSL | True/False | True | ✅ |
| **MAIL_USERNAME** | 邮箱用户名 | xxx@qq.com | - | ✅ |
| **MAIL_PASSWORD** | 邮箱授权码 | smtp-auth-code | - | ✅ |
| **FLASK_HOST** | 应用绑定 IP | 0.0.0.0 | localhost | ⭕ |
| **FLASK_PORT** | 应用端口 | 5000 | 5000 | ⭕ |

## MongoDB 连接字符串示例

### 本地 MongoDB
```
mongodb://localhost:27017/station_agent_db
```

### 带认证的 MongoDB
```
mongodb://username:password@127.0.0.1:27017/station_agent_db
```

### MongoDB Atlas（云服务）
```
mongodb+srv://username:password@cluster.mongodb.net/station_agent_db?retryWrites=true&w=majority
```

## 生产环境部署

### 在宝塔面板上

1. **在网站根目录创建 `.env` 文件**
   - 路径：`/www/wwwroot/your-domain/.env`
   - ⚠️ **重要**：确保 `.env` 不在 git 版本控制中（已通过 `.gitignore` 配置）

2. **通过宝塔系统变量或 systemd 注入**
   
   如果使用 systemd 服务（推荐）：
   ```ini
   [Service]
   EnvironmentFile=/www/wwwroot/your-domain/.env
   ExecStart=/path/to/.venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 app:app
   ```

3. **重启应用**
   ```bash
   systemctl restart your-app-name
   ```

### 通过环境变量直接注入（Systemd）

方式 1：在 systemd unit 文件中设置环境变量
```ini
[Service]
Environment="SECRET_KEY=your-production-secret-key"
Environment="MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/db"
Environment="FLASK_ENV=production"
```

方式 2：从 .env 文件加载（推荐）
```ini
[Service]
EnvironmentFile=/www/wwwroot/your-domain/.env
```

## 安全最佳实践

| 项目 | 做法 | 理由 |
|------|------|------|
| **`.env` 文件** | ❌ 不提交到 git | 防止敏感信息泄露 |
| **`.env.example`** | ✅ 提交到 git | 帮助开发者快速配置 |
| **SECRET_KEY** | ✅ 使用强随机值 | 增强会话安全 |
| **MAIL_PASSWORD** | ✅ 使用 SMTP 授权码 | 不暴露真实邮箱密码 |
| **MONGO_URI** | ✅ 使用数据库专用账户 | 限制权限范围 |
| **生产环境** | ✅ FLASK_ENV=production | 禁用 debug 模式 |

## 常见问题

### Q: `.env` 文件不存在会怎样？
A: 应用会使用代码中的默认值。对于关键配置（如 MongoDB），如果默认值也不可用，应用会连接失败。

### Q: 如何生成强 SECRET_KEY？
A: 使用 Python：
```python
import secrets
print(secrets.token_hex(32))  # 生成 64 个字符的随机密钥
```

### Q: 部署到宝塔后 `.env` 找不到？
A: 确保：
1. `.env` 文件在项目根目录
2. 文件权限允许读取（通常 644）
3. systemd service 使用 `EnvironmentFile=/path/to/.env`
4. 重启应用使配置生效

### Q: 如何验证环境变量是否正确加载？
A: 在应用启动日志中查看：
```
✓ MongoDB 连接成功  # 说明 MONGO_URI 正确
```
或在 Flask shell 中测试：
```python
python
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> print(os.getenv('MONGO_URI'))
```

## 提交清单

部署前检查：
- [ ] `.env` 已创建，包含所有生产值
- [ ] `SECRET_KEY` 是强随机值
- [ ] `MONGO_URI` 指向正确的数据库
- [ ] 邮件配置已验证（发送测试邮件）
- [ ] `FLASK_ENV=production` 且 `FLASK_DEBUG=0`
- [ ] `.env` 在 `.gitignore` 中（不会提交）
- [ ] 依赖已安装：`pip install -r requirements.txt`
- [ ] MongoDB 服务正常运行

## 相关文件

- `.env.example` - 配置模板（可安全提交到 git）
- `.env` - 实际配置（不提交，本地和服务器分别创建）
- `.gitignore` - Git 忽略规则（确保 `.env` 被忽略）
- `requirements.txt` - Python 依赖（包含 python-dotenv）

