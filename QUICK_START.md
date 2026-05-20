# 🚀 快速启动检查清单

## ✅ 环境变量配置完成！

你的项目已经完全配置为使用环境变量，所有敏感信息已从代码中移除。现在可以安全地部署到服务器！

---

## 📋 本地开发快速开始（3步）

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 2️⃣ 确保 .env 文件存在
```bash
# .env 文件应该已自动创建，验证它：
cat .env

# 如果不存在，复制模板并编辑：
cp .env.example .env
```

### 3️⃣ 启动应用
```bash
python app.py
```

访问 http://localhost:5000 🎉

---

## 🖥️ 宝塔服务器部署快速开始（8步）

### 1️⃣ 检查前置条件
```bash
# ☐ 宝塔面板已安装
# ☐ Python 3.8+ 可用
# ☐ MongoDB 已安装并运行
# ☐ Nginx 已安装
```

### 2️⃣ 上传代码
```bash
# 通过 Git 克隆或手动上传到：
# /www/wwwroot/www.thestationagentheart.co
git clone <your-repo> /www/wwwroot/www.thestationagentheart.co
cd /www/wwwroot/www.thestationagentheart.co
```

### 3️⃣ 创建并配置 .env（⭐ 关键步骤）
```bash
cp .env.example .env
vim .env

# 确保修改以下关键项：
# - SECRET_KEY: 强随机值（至少 32 字符）
# - MONGO_URI: 你的 MongoDB 连接地址
# - MAIL_USERNAME/PASSWORD: 邮箱凭证
```

### 4️⃣ 创建虚拟环境并安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5️⃣ 验证环境变量
```bash
python3 verify_env.py

# 输出应该显示所有配置项都已正确加载：
# ✓ MONGO_URI = mongodb://...
# ✓ SECRET_KEY = ****...
# 等
```

### 6️⃣ 配置后台服务（Systemd）
```bash
# 方式 A：使用 systemd（推荐）
sudo cp deploy/the-station-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start the-station-agent
sudo systemctl enable the-station-agent

# 或者方式 B：使用自动化脚本
bash deploy.sh
```

### 7️⃣ 配置 Nginx 反向代理
```bash
# 使用宝塔面板：
# 1. 网站 -> 选中站点 -> 反向代理
# 2. 源站 URL: http://127.0.0.1:8000
# 3. 启用缓存、Gzip 等（可选）

# 或手动配置：
sudo cp deploy/nginx.conf /etc/nginx/sites-available/the-station-agent
sudo ln -s /etc/nginx/sites-available/the-station-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8️⃣ 验证部署
```bash
# 检查应用是否运行
systemctl status the-station-agent

# 测试应用
curl http://127.0.0.1:8000/

# 测试反向代理
curl http://www.thestationagentheart.co/

# 查看日志
journalctl -u the-station-agent -f
```

---

## 🔒 安全检查清单

部署前必须检查：

```
部署生产环境时：
☐ SECRET_KEY 已更改为强随机值（不是默认值）
☐ FLASK_ENV=production 且 FLASK_DEBUG=0
☐ MONGO_URI 指向正确的数据库（有用户名密码）
☐ 邮件配置已验证（发送测试邮件）
☐ .env 文件不在 git 版本控制中
☐ HTTPS/SSL 已启用
☐ MongoDB 已设置认证

可选但推荐：
☐ 定期备份 MongoDB 数据
☐ 配置日志收集
☐ 配置性能监控
☐ 设置告警通知
```

---

## 📁 重要文件说明

| 文件/目录 | 说明 | Git | 部署 |
|----------|------|-----|------|
| `.env` | 实际配置（敏感） | ❌ 不提交 | ✅ 必需 |
| `.env.example` | 配置模板 | ✅ 提交 | 参考 |
| `app.py` | Flask 主程序 | ✅ 提交 | ✅ 必需 |
| `requirements.txt` | 依赖列表 | ✅ 提交 | ✅ 必需 |
| `deploy/` | 部署脚本 | ✅ 提交 | 参考 |
| `ENV_SETUP.md` | 环境配置指南 | ✅ 提交 | 参考 |
| `DEPLOYMENT_BAOTA.md` | 部署指南 | ✅ 提交 | 参考 |

---

## 🆘 常见问题快速解决

### 问题：502 Bad Gateway

```bash
# 1. 检查应用是否运行
systemctl status the-station-agent

# 2. 检查错误日志
journalctl -u the-station-agent -n 50

# 3. 检查 Gunicorn 端口
netstat -tlnp | grep 8000

# 4. 测试本地连接
curl http://127.0.0.1:8000/
```

### 问题：no package.json found

```bash
# 已自动解决 - 项目包含最小化的 package.json
# 如果仍然出现此错误，检查部署脚本是否在错误的目录运行
```

### 问题：MongoDB 连接失败

```bash
# 1. 检查 MongoDB 是否运行
systemctl status mongod

# 2. 验证连接字符串
grep MONGO_URI .env

# 3. 测试连接
mongo "your-mongo-uri"
```

### 问题：邮件发送失败

```bash
# 1. 检查邮件配置
grep MAIL_ .env

# 2. 验证 SMTP 凭证是否正确
# 3. 查看应用日志中的邮件错误
journalctl -u the-station-agent | grep -i mail
```

---

## 📚 详细文档

需要更多细节？查看这些文档：

- **本地开发** → `ENV_SETUP.md`
- **宝塔部署** → `DEPLOYMENT_BAOTA.md`
- **完成总结** → `SECURITY_COMPLETION.md`
- **故障排查** → `DEPLOYMENT_BAOTA.md` 中的"常见问题排查"部分

---

## 🎯 下一步

1. ✅ 查看 `.env.example` 了解所有配置项
2. ✅ 编辑 `.env` 填入你的实际值
3. ✅ 运行 `python3 verify_env.py` 验证配置
4. ✅ 按照上面的 8 步部署到宝塔
5. ✅ 测试应用是否正常运行

---

## 💡 提示

- **安全第一**：永远不要在代码中硬编码敏感信息
- **环境隔离**：本地、测试、生产环境分别使用不同的 `.env` 文件
- **定期审计**：定期检查日志和依赖更新
- **备份重要**：定期备份 MongoDB 数据和配置

---

**开始部署吧！祝你好运！** 🚀

有问题？查看文档或查看日志：
```bash
journalctl -u the-station-agent -f
tail -f /var/log/nginx/error.log
```

