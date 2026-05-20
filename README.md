# The Station & Agent - 登录和注册系统

这是一个完整的 Flask Web 应用程序，包含用户注册和登录功能，使用 MongoDB 数据库来存储用户信息。

## 项目结构

```
TheStationAgent/
├── app.py                    # Flask 主应用程序
├── requirements.txt          # Python 依赖
├── database/
│   └── README.md            # 数据库配置指南
├── static/
│   ├── image/               # 静态图片资源
│   └── music/               # 音乐文件
└── templates/
    ├── home.html            # 主页面
    ├── login.html           # 登录页面
    ├── sign.html            # 注册页面
    └── playground.html      # 练习页面
```

## 功能特性

✅ **用户注册**
- 验证用户名、邮箱和密码
- 密码加密存储
- 防止重复注册

✅ **用户登录**
- 邮箱和密码验证
- Session 会话管理
- 安全的密码验证

✅ **用户状态**
- 实时显示登录状态
- 用户名显示
- 登出功能

✅ **MongoDB 集成**
- 用户数据持久化
- 作为 database 文件夹中的数据集

## 前置需求

- Python 3.8+
- MongoDB 4.0+
- pip (Python 包管理器)

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd E:\TheStationAgent
pip install -r requirements.txt
```

### 2. 安装和启动 MongoDB

**Windows 用户：**
- 从 [MongoDB 官网](https://www.mongodb.com/try/download/community) 下载 MongoDB Community
- 安装时选择 "Install MongoDB as a Service"
- MongoDB 会自动作为服务在后台运行

**或者手动启动 MongoDB：**
```bash
mongod
```

### 3. 验证 MongoDB 连接

```bash
mongo
# 在 MongoDB Shell 中输入
show databases
# 然后输入 exit 退出
exit
```

## 运行应用

```bash
cd E:\TheStationAgent
python app.py
```

应用会在 `http://localhost:5000` 启动

## 使用说明

### 访问应用

- **主页**：http://localhost:5000/
- **注册页面**：http://localhost:5000/register
- **登录页面**：http://localhost:5000/login
- **Playground**：http://localhost:5000/playground

### 注册新账户

1. 打开注册页面 (http://localhost:5000/register)
2. 填写以下信息：
   - **用户名**：至少 3 个字符
   - **邮箱**：有效的邮箱地址
   - **密码**：至少 6 个字符
   - **确认密码**：与密码相同
3. 点击"注册"按钮

### 登录账户

1. 打开登录页面 (http://localhost:5000/login)
2. 输入注册时的：
   - **邮箱**
   - **密码**
3. 点击"登录"按钮

### 登出

点击导航栏中的"登出"链接即可退出登录

## API 端点

### 认证相关

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | 主页面 |
| GET | `/login` | 登录页面 |
| POST | `/login` | 处理登录请求 |
| GET | `/register` | 注册页面 |
| POST | `/register` | 处理注册请求 |
| GET | `/logout` | 登出并清除会话 |
| GET | `/user-info` | 获取当前用户信息 |

### 其他页面

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/playground` | Playground 页面 |

## 数据库架构

### 用户集合 (users)

```javascript
{
  "_id": ObjectId,           // 唯一标识符
  "username": String,        // 用户名（唯一）
  "email": String,           // 邮箱（唯一）
  "password": String,        // 加密后的密码
  "created_at": DateTime,    // 创建时间
  "updated_at": DateTime     // 更新时间
}
```

## 数据库管理

### 查看用户

```bash
# 打开 MongoDB Shell
mongo

# 切换到应用数据库
use station_agent_db

# 查询所有用户
db.users.find()

# 查询特定用户
db.users.findOne({email: "user@example.com"})

# 查询用户数量
db.users.countDocuments()
```

### 删除用户

```bash
# 删除特定用户
db.users.deleteOne({email: "user@example.com"})

# 删除所有用户
db.users.deleteMany({})
```

## 常见问题

### Q: MongoDB 连接失败怎么办？
A: 
1. 检查 MongoDB 是否运行：`net start MongoDB` (Windows)
2. 验证连接字符串：默认为 `mongodb://localhost:27017/`
3. 检查防火墙设置是否阻止了连接

### Q: 注册时显示"邮箱已被注册"？
A: 
1. 使用不同的邮箱地址
2. 检查数据库中是否存在该邮箱：`db.users.findOne({email: "..."})`
3. 如需重新测试，可以删除该用户：`db.users.deleteOne({email: "..."})`

### Q: 登录失败怎么办？
A:
1. 检查邮箱和密码是否匹配
2. 确认该邮箱已注册
3. 检查浏览器控制台是否有错误信息

### Q: 如何重置密码？
A: 当前版本不支持密码重置。如需重置，请在数据库中删除用户后重新注册。

## 安全建议

⚠️ **生产环境注意事项：**
1. 更改 `app.secret_key` 为强随机密钥
2. 使用环境变量存储敏感信息
3. 配置 HTTPS/SSL
4. 实现 CSRF 保护
5. 添加速率限制和登录尝试限制
6. 定期更新依赖包

## 文件说明

- **app.py**：Flask 应用主文件，包含所有路由和数据库逻辑
- **requirements.txt**：Python 依赖列表
- **templates/*.html**：前端 HTML 模板
- **static/**：静态资源（CSS、JS、图片等）

## 故障排除

### 问题：页面加载缓慢
解决方案：
- 检查互联网连接
- 清除浏览器缓存
- 重启 Flask 服务

### 问题：表单验证错误
解决方案：
- 确保邮箱格式正确
- 确保密码符合要求
- 检查用户名长度

### 问题：MongoDB 错误
解决方案：
- 重启 MongoDB 服务
- 检查数据库连接字符串
- 查看 Flask 应用日志

## 技术栈

- **后端**：Flask 2.3.3
- **数据库**：MongoDB 4.5.0
- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **安全**：Werkzeug（密码哈希）
- **依赖管理**：pip

## 更新和扩展

未来可能的功能：
- 邮箱验证
- 密码重置功能
- 用户资料编辑
- 两步验证
- OAuth 社交登录
- 用户头像上传
- 用户活动日志

## 许可证

MIT 许可证

## 联系方式和支持

如有问题或建议，请提交 Issue 或 Pull Request。

---

**最后更新**：2026 年 5 月 14 日

