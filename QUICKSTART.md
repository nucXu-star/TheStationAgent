# ⚡ 快速开始指南

## 3 分钟启动应用

### 步骤 1：安装依赖（1 分钟）

打开 PowerShell，进入项目目录：

```powershell
cd E:\TheStationAgent
pip install -r requirements.txt
```

### 步骤 2：启动 MongoDB（1 分钟）

打开另一个 PowerShell 窗口：

```powershell
mongod
```

如果 MongoDB 已安装为服务，可以检查服务状态：

```powershell
Get-Service MongoDB
```

### 步骤 3：运行应用（1 分钟）

在第一个 PowerShell 中运行：

```powershell
python app.py
```

看到以下输出说明启动成功：
```
✓ MongoDB 连接成功
 * Running on http://localhost:5000
```

## 测试应用

### 1. 打开浏览器

访问：http://localhost:5000

### 2. 注册新账户

1. 点击导航栏中的"注册"
2. 填写信息：
   - 用户名：`testuser`
   - 邮箱：`test@example.com`
   - 密码：`123456`
   - 确认密码：`123456`
3. 点击"注册"按钮

### 3. 登录账户

1. 点击"登出"重置会话（或关闭浏览器重新打开）
2. 点击"登录"
3. 输入邮箱和密码
4. 点击"登录"按钮

### 4. 查看用户状态

登录成功后，导航栏应显示 "欢迎, testuser!"

## 常见问题速查

| 问题 | 解决方案 |
|------|--------|
| MongoDB 连接失败 | 确保 mongod 正在运行 |
| 端口 5000 已被占用 | 修改 app.py 中的 port=5000 为其他端口 |
| "邮箱已被注册" | 使用不同的邮箱地址重试 |
| 登录失败 | 检查邮箱和密码是否正确 |

## 检查数据库中的用户

打开新的 PowerShell 窗口：

```powershell
mongo
use station_agent_db
db.users.find()
```

应该能看到你注册的用户信息。

## 下一步

- 修改 app.py 中的 `app.secret_key` 为更安全的密钥
- 尝试添加更多用户
- 在 `database/README.md` 中查看更多数据库操作
- 在 `README.md` 中查看详细文档

## 需要帮助？

查看项目根目录的 `README.md` 文件获取完整文档。

