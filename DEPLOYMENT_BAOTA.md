# 宝塔面板部署指南

## 📋 前置环境

- 宝塔面板 v7.7.0+ 
- Python 3.8+ 
- MongoDB 4.0+
- Nginx

## 🚀 部署步骤

### 第一步：准备代码与依赖

```bash
# 1. 在宝塔上创建网站
# 宝塔后台 -> 网站 -> 添加站点
# 域名：www.thestationagentheart.co
# 目录：/www/wwwroot/www.thestationagentheart.co

# 2. 将代码上传到网站根目录（通过 FTP / git clone / 手动上传）
cd /www/wwwroot/www.thestationagentheart.co

# 3. 创建 Python 虚拟环境
python3 -m venv .venv

# 4. 激活虚拟环境
source .venv/bin/activate

# 5. 升级 pip
pip install --upgrade pip

# 6. 安装依赖
pip install -r requirements.txt
```

### 第二步：配置环境变量 ⭐ 关键

```bash
# 1. 根据 .env.example 创建 .env 文件
cp .env.example .env

# 2. 编辑 .env 文件，填入生产环境配置
vim .env
```

`.env` 文件配置示例：

```dotenv
# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-production-secret-key-here  # 使用强随机值

# MongoDB 配置
# 本地 MongoDB：mongodb://localhost:27017/station_agent_db
# 也可使用 MongoDB Atlas：mongodb+srv://user:pass@cluster.mongodb.net/db
MONGO_URI=mongodb://localhost:27017/station_agent_db
DATABASE_NAME=station_agent_db

# 邮件配置
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-smtp-auth-code

# 应用配置
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
```

### 第三步：配置 MongoDB

在宝塔面板中：

```bash
# 1. 安装 MongoDB（如果未安装）
# 宝塔后台 -> 软件商店 -> 搜索 MongoDB -> 安装

# 2. 启动 MongoDB
systemctl start mongod

# 3. 验证连接
python3
>>> from pymongo import MongoClient
>>> client = MongoClient('mongodb://localhost:27017/')
>>> client.admin.command('ping')
{'ok': 1.0}
>>> exit()
```

### 第四步：配置反向代理（宝塔图形界面）

```
1. 进入宝塔后台
2. 网站 -> 选中站点 -> 反向代理
3. 添加反向代理：
   - 代理名称：Flask App
   - 目标 URL：http://127.0.0.1:8000
   - 高级配置：添加自定义 header
```

Nginx 配置直接添加示例见 `deploy/nginx.conf`

### 第五步：配置后台服务运行

**方案 A：使用 systemd 服务（推荐）**

```bash
# 1. 复制 systemd 单元文件
sudo cp deploy/the-station-agent.service /etc/systemd/system/

# 2. 重载 systemd
sudo systemctl daemon-reload

# 3. 启动服务
sudo systemctl start the-station-agent

# 4. 设置开机自启
sudo systemctl enable the-station-agent

# 5. 查看状态
sudo systemctl status the-station-agent

# 6. 查看日志
sudo journalctl -u the-station-agent -f
```

**方案 B：使用宝塔自带服务管理**

```bash
# 1. 宝塔后台 -> 软件商店 -> 搜索"Supervisor"
# 2. 安装 Supervisor
# 3. 创建配置文件 /etc/supervisor/conf.d/the-station-agent.conf

[program:the-station-agent]
directory = /www/wwwroot/www.thestationagentheart.co
command = /www/wwwroot/www.thestationagentheart.co/.venv/bin/gunicorn \
    -w 3 \
    -b 0.0.0.0:8000 \
    app:app
autostart = true
autorestart = true
startsecs = 1
stopwaitsecs = 5
stdout_logfile = /www/logs/supervisor/the-station-agent.log
stderr_logfile = /www/logs/supervisor/the-station-agent.err

# 4. 启动服务
supervisorctl reread
supervisorctl update
supervisorctl start the-station-agent
```

**方案 C：使用守护进程启动**

```bash
# 创建启动脚本：/www/wwwroot/www.thestationagentheart.co/start.sh
#!/bin/bash
cd /www/wwwroot/www.thestationagentheart.co
source .venv/bin/activate
exec gunicorn -w 3 -b 0.0.0.0:8000 app:app

# 赋予执行权限
chmod +x start.sh

# 后台运行（使用 nohup）
nohup ./start.sh > output.log 2>&1 &
```

### 第六步：SSL 安全证书（可选但推荐）

```bash
# 使用宝塔的 Let's Encrypt 集成
# 1. 宝塔后台 -> 网站 -> 选中站点 -> SSL
# 2. 选择"Let's Encrypt"
# 3. 自动申请并配置 HTTPS

# 或手动使用 certbot：
sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d www.thestationagentheart.co -d thestationagentheart.co
```

### 第七步：验证部署

```bash
# 1. 检查应用日志
sudo journalctl -u the-station-agent -f

# 2. 测试应用响应
curl http://127.0.0.1:8000/

# 3. 测试反向代理
curl http://www.thestationagentheart.co/

# 4. 测试 API 端点
curl http://www.thestationagentheart.co/user-info
```

### 第八步：定期维护

```bash
# 查看应用状态
systemctl status the-station-agent

# 查看日志
journalctl -u the-station-agent --no-pager | tail -50

# 重启应用（部署更新后）
systemctl restart the-station-agent

# 监控资源使用
systemctl show the-station-agent

# 查看 MongoDB 连接
mongo
> db.adminCommand('currentOp')
> exit
```

## 🐛 常见问题排查

### 问题 1：502 Bad Gateway

**症状：** 访问网站显示 502 错误

**排查步骤：**

```bash
# 1. 检查 Gunicorn 是否运行
systemctl status the-station-agent
ps aux | grep gunicorn

# 2. 检查 Gunicorn 监听的端口
netstat -tlnp | grep 8000

# 3. 查看 Gunicorn 错误日志
journalctl -u the-station-agent -n 50

# 4. 测试本地连接
curl http://127.0.0.1:8000/

# 5. 检查 Nginx 配置有无错误
nginx -t

# 6. 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

**常见原因及解决方案：**

| 原因 | 解决方案 |
|------|--------|
| Gunicorn 未运行 | `systemctl restart the-station-agent` |
| .env 文件配置错误 | 检查 MONGO_URI、SECRET_KEY 是否正确 |
| MongoDB 连接失败 | `systemctl status mongod` 确保 MongoDB 运行 |
| 端口被占用 | `lsof -i :8000` 查看占用进程 |
| 虚拟环境损坏 | 重新创建：`rm -rf .venv && python3 -m venv .venv` |

### 问题 2：no package.json found

**症状：** 部署日志显示 `[ERR_PNPM_NO_PKG_MANIFEST]`

**原因：** 部署脚本在 Flask 项目中错误地运行了 Node 包管理器

**解决方案：**

```bash
# 已自动解决：项目中包含了最小化的 package.json
# 如果重复出现此错误，检查部署脚本是否在正确的目录运行

# 验证
ls -la package.json .env
```

### 问题 3：MongoDB 连接超时

**症状：** 日志显示 `pymongo.errors.ServerSelectionTimeoutError`

**排查步骤：**

```bash
# 1. 检查 MongoDB 是否运行
systemctl status mongod

# 2. 查看 MongoDB 日志
tail -f /var/log/mongodb/mongod.log

# 3. 测试连接
mongo --eval "db.adminCommand('ping')"

# 4. 检查 .env 中的 MONGO_URI 是否正确
grep MONGO_URI .env

# 5. 检查 MongoDB 绑定 IP（如果是远程）
grep bindIp /etc/mongod.conf
```

### 问题 4：邮件发送失败

**症状：** 用户注册时提示"邮件发送失败"

**排查步骤：**

```bash
# 1. 检查 .env 中的邮件配置
grep MAIL_ .env

# 2. 测试邮件服务连接
python3
>>> import smtplib
>>> smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
>>> smtp.login('your-email@qq.com', 'auth-code')
>>> smtp.send_message(...)
>>> exit()

# 3. 查看 Flask 错误日志
journalctl -u the-station-agent | grep -i mail
```

## 📊 性能优化

### 增加工作进程

编辑 systemd unit（`/etc/systemd/system/the-station-agent.service`）：

```ini
ExecStart=/www/wwwroot/www.thestationagentheart.co/.venv/bin/gunicorn \
    -w 4 \              # 根据 CPU 核心数调整（推荐：核心数 * 2-4）
    -b 127.0.0.1:8000 \
    --worker-class gevent \  # 可选：使用 gevent worker 处理并发
    app:app
```

然后重启：
```bash
systemctl daemon-reload
systemctl restart the-station-agent
```

### Nginx 缓存

在 Nginx 配置中添加：

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### MongoDB 索引优化

```bash
mongo
> use station_agent_db
> db.users.createIndex({ email: 1 }, { unique: true })
> db.posts.createIndex({ created_at: -1 })
> db.posts.createIndex({ author_id: 1 })
> exit
```

## 🔐 安全检查清单

- [ ] `.env` 文件已创建且包含生产值
- [ ] `SECRET_KEY` 是强随机值（≥32字符）
- [ ] HTTPS/SSL 已启用
- [ ] MongoDB 已设置认证（MONGO_URI 包含用户名密码）
- [ ] Flask Debug 模式已禁用（FLASK_DEBUG=0）
- [ ] `.env` 不在 version control 中（已配置 .gitignore）
- [ ] 定期备份 MongoDB 数据
- [ ] 定期更新依赖包（`pip install --upgrade -r requirements.txt`）
- [ ] 查看并处理错误日志

## 📞 获取帮助

- 查看应用日志：`journalctl -u the-station-agent -f`
- 查看 Nginx 日志：`tail -f /var/log/nginx/error.log`
- 运行配置验证：`python3 verify_env.py`
- 查看宝塔文档：[宝塔面板官方文档](https://www.bt.cn/new/index.html)

