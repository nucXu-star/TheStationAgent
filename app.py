from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  # ✨ 新增：用于安全地保存文件名
from bson import ObjectId
import os
import uuid  # ✨ 新增：用于生成唯一文件名
import random
from datetime import datetime
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from dotenv import load_dotenv  # ✨ 新增：加载环境变量

# ✨ 新增：从 .env 文件加载环境变量
load_dotenv()

app = Flask(__name__)
# ✨ 修改：从环境变量读取 SECRET_KEY，提供默认值防止缺失
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# ✨ 修改：从环境变量读取邮件配置
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.qq.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '465'))
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '1626521893@qq.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'lpcoauuqdwlgecid')
mail = Mail(app)

# ✨ 新增：配置文件上传目录和允许的格式
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # 自动创建 uploads 文件夹
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ✨ 修改：从环境变量读取 MongoDB 配置
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'station_agent_db')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[DATABASE_NAME]
    users_collection = db['users']
    posts_collection = db['posts']
    comments_collection = db['comments']  # ✨ 新增：初始化评论集合
    print("✓ MongoDB 连接成功")
except Exception as e:
    print(f"✗ MongoDB 连接失败: {e}")
    db = None
    users_collection = None
    posts_collection = None
    comments_collection = None # ✨ 新增


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if users_collection is None:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500

        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'success': False, 'message': '邮箱和密码不能为空'}), 400

        # 在数据库中查找用户
        user = users_collection.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            if session['role'] == 'admin':
                return jsonify(
                    {'success': True, 'message': '管理员登录成功', 'redirect': url_for('playground_pro')}), 200
            else:
                return jsonify({'success': True, 'message': '登录成功', 'redirect': url_for('playground')}), 200
        else:
            return jsonify({'success': False, 'message': '邮箱或密码错误'}), 401

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users_collection = db['users']
        if users_collection is None:
            return jsonify({'error': '数据库连接失败'}), 500

        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()

        # 验证输入
        if not username or not email or not password or not confirm_password:
            return jsonify({'success': False, 'message': '所有字段都是必需的'}), 400

        if len(username) < 3:
            return jsonify({'success': False, 'message': '用户名至少 3 个字符'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少 6 个字符'}), 400

        if password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400

        if '@' not in email:
            return jsonify({'success': False, 'message': '请输入有效的邮箱地址'}), 400

        # 检查邮箱是否已存在
        if users_collection.find_one({'email': email}):
            return jsonify({'success': False, 'message': '邮箱已被注册'}), 400

            # 检查用户名是否已存在
            # 检查用户名是否已存在
        if users_collection.find_one({'username': username}):
            return jsonify({'success': False, 'message': '用户名已被占用'}), 400

        # 【修改点 1】：直接从 data 里拿前端传过来的验证码
        # 注意：email 在上面已经通过 data.get('email') 拿过了，不要重新覆盖它
        submitted_code = data.get('verify_code', '').strip()

        # 1. 校验验证码
        stored_code = session.get('verify_code')
        stored_email = session.get('verify_email')

        # 【修改点 2】：确保返回的是规范的 JSON 格式，这样前端的 messageDiv 才能正确显示
        if not stored_code or stored_code != submitted_code or stored_email != email:
            return jsonify({'success': False, 'message': '验证码错误或已失效'}), 400

        # 2. 验证通过后，清除 session 中的验证码防止重复使用
        session.pop('verify_code', None)
        session.pop('verify_email', None)

        # 创建新用户
        new_user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            "role": "admin"
        }

        try:
            result = users_collection.insert_one(new_user)
            session['user_id'] = str(result.inserted_id)
            session['email'] = email
            session['username'] = username
            return jsonify({'success': True, 'message': '注册成功', 'redirect': url_for('index')}), 201
        except Exception as e:
            return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

    return render_template('sign.html')


@app.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'success': False, 'message': '邮箱不能为空'})

    # 生成 6 位随机数字验证码
    code = str(random.randint(100000, 999999))

    # 暂存验证码。最简单的方式是存在 session 中。
    # 如果考虑到分布式或更高的可靠性，可以存入 MongoDB，并利用 TTL 索引设置 5 分钟后自动过期。
    session['verify_code'] = code
    session['verify_email'] = email

    # 发送邮件
    try:
        # ✨ 修改：使用环境变量中的邮箱地址
        sender_email = os.getenv('MAIL_USERNAME', '1626521893@qq.com')
        msg = Message("您的注册验证码", sender=sender_email, recipients=[email])
        msg.body = f"欢迎注册 The Station& Agent！您的验证码是：{code}。该验证码在5分钟内有效，请勿泄露给他人。"
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': '邮件发送失败'})
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/user-info')
def user_info():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'email': session.get('email')
        })
    return jsonify({'logged_in': False})


@app.route('/playground')
def playground():
    return render_template('playground.html')


# ==========================================
# ✨ 在线人数统计 API
# ==========================================

@app.route('/api/online-users', methods=['GET'])
def get_online_users():
    """获取实时在线人数（基于心跳机制）"""
    # 如果数据库连接失败，提供一个兜底的假数据防止前端报错
    if db is None:
        return jsonify({'online': 1}), 200

    # 给每个打开网页的浏览器分配一个独一无二的访客 ID，存入 session
    if 'visitor_id' not in session:
        session['visitor_id'] = uuid.uuid4().hex

    visitor_id = session['visitor_id']
    now = datetime.now()

    try:
        # 1. 更新当前访客的最后活跃时间。如果该访客不存在，则插入新记录 (upsert=True)
        db.active_sessions.update_one(
            {'visitor_id': visitor_id},
            {'$set': {'last_seen': now}},
            upsert=True
        )

        # 2. 清理掉不活跃的用户（这里设定：如果 1 分钟内没收到请求，就认为离线了）
        # 因为你的前端是 15 秒请求一次，1 分钟没请求说明网页已经被关掉了
        timeout_threshold = now - timedelta(minutes=1)
        db.active_sessions.delete_many({'last_seen': {'$lt': timeout_threshold}})

        # 3. 统计目前 active_sessions 集合里还有多少条记录，这就是当前在线总人数
        online_count = db.active_sessions.count_documents({})

        return jsonify({'online': online_count})

    except Exception as e:
        print(f"统计在线人数出错: {e}")
        return jsonify({'online': 1}), 500  # 出错时返回默认值
# ==========================================
# ✨ 社区 API 接口
# ==========================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """获取帖子列表，支持分类、排序、关键词搜索和查看'我的'帖子"""
    if posts_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    # 获取前端传来的查询参数
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'hot')
    keyword = request.args.get('keyword', '').strip()
    mine = request.args.get('mine', 'false').lower() == 'true'  # ✨ 新增：是否只看我的

    # 构建基础查询条件
    query = {}
    if category != 'all':
        query['category'] = category

    # ✨ 新增：如果勾选了“我的”，限制 author_id 为当前登录用户
    if mine:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录才能查看您的帖子哦'}), 401
        query['author_id'] = session['user_id']

    # 如果存在关键词，使用正则进行模糊搜索
    if keyword:
        query['$or'] = [
            {'title': {'$regex': keyword, '$options': 'i'}},
            {'content': {'$regex': keyword, '$options': 'i'}}
        ]

    # 构建排序条件
    if sort_by == 'hot':
        sort_order = [('likes', -1), ('created_at', -1)]
    else:
        sort_order = [('created_at', -1)]

    # 从数据库查询
    posts_cursor = posts_collection.find(query).sort(sort_order).limit(50)

    posts = []
    current_user_id = session.get('user_id')  # 获取当前登录用户 ID

    for post in posts_cursor:
        post['_id'] = str(post['_id'])
        post['created_at'] = post['created_at'].strftime("%Y-%m-%d %H:%M")

        # ✨ 新增：判断当前用户是否在 liked_by 列表里
        liked_by = post.get('liked_by', [])
        post['is_liked_by_me'] = (current_user_id in liked_by) if current_user_id else False

        posts.append(post)

    return jsonify({'success': True, 'posts': posts})


@app.route('/api/posts', methods=['POST'])
def create_post():
    """发布新帖子（支持最多9个多媒体文件）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    if posts_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    category = request.form.get('category', '讨论')

    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    # ✨ 新增：处理多个文件上传
    media_list = []
    if 'media' in request.files:
        files = request.files.getlist('media')  # 获取文件列表

        # 限制最多9个文件
        if len(files) > 9:
            return jsonify({'success': False, 'message': '最多只能上传9个文件'}), 400

        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 使用时间戳 + 短UUID 确保多文件瞬间并发时名字也绝对不重复
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)

                media_url = f"/static/uploads/{unique_filename}"
                ext = filename.rsplit('.', 1)[1].lower()

                media_type = 'unknown'
                if ext in {'png', 'jpg', 'jpeg', 'gif'}:
                    media_type = 'image'
                elif ext in {'mp4', 'webm'}:
                    media_type = 'video'
                elif ext in {'mp3', 'wav'}:
                    media_type = 'audio'

                if media_type != 'unknown':
                    media_list.append({
                        'url': media_url,
                        'type': media_type
                    })

    new_post = {
        'title': title,
        'content': content,
        'author_id': session['user_id'],
        'author_name': session['username'],
        'category': category,
        'likes': 0,
        'liked_by': [],
        'views': 0,
        'viewed_by': [],
        'comments_count': 0,
        'created_at': datetime.now(),
        'media': media_list
    }

    try:
        posts_collection.insert_one(new_post)
        return jsonify({'success': True, 'message': '发布成功'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'发布失败: {str(e)}'}), 500


@app.route('/api/comments/<post_id>', methods=['GET'])
def get_comments(post_id):
    """获取指定帖子的所有评论"""
    if comments_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    # 按时间正序排列（旧评论在上，新评论在下）
    comments_cursor = comments_collection.find({'post_id': post_id}).sort('created_at', 1)

    comments = []
    for c in comments_cursor:
        c['_id'] = str(c['_id'])
        c['created_at'] = c['created_at'].strftime("%Y-%m-%d %H:%M")
        comments.append(c)

    return jsonify({'success': True, 'comments': comments})


@app.route('/api/comments', methods=['POST'])
def create_comment():
    """发表新评论"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    if comments_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content', '').strip()

    if not post_id or not content:
        return jsonify({'success': False, 'message': '评论内容不能为空'}), 400

    new_comment = {
        'post_id': post_id,
        'author_id': session['user_id'],
        'author_name': session['username'],
        'content': content,
        'created_at': datetime.now()
    }

    try:
        # 1. 保存评论到 comments 集合
        comments_collection.insert_one(new_comment)
        # 2. 给 posts 集合中对应的帖子 comments_count 数量 +1
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$inc': {'comments_count': 1}}
        )
        return jsonify({'success': True, 'message': '评论成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'评论失败: {str(e)}'}), 500


@app.route('/api/posts/<post_id>/like', methods=['POST'])
def toggle_like(post_id):
    """切换点赞状态 (点赞/取消点赞)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    if posts_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    user_id = session['user_id']

    # 查找帖子
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404

    liked_by = post.get('liked_by', [])

    if user_id in liked_by:
        # 已经点过赞 -> 取消点赞
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {
                '$pull': {'liked_by': user_id},  # 从数组中移除 user_id
                '$inc': {'likes': -1}  # 数量 -1
            }
        )
        return jsonify({'success': True, 'action': 'unliked'})
    else:
        # 没点过赞 -> 添加点赞
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {
                '$addToSet': {'liked_by': user_id},  # 加入数组 (自动去重)
                '$inc': {'likes': 1}  # 数量 +1
            }
        )
        return jsonify({'success': True, 'action': 'liked'})


@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """删除帖子及其关联的评论"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    if posts_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    try:
        # 1. 查找帖子，确认是否存在
        post = posts_collection.find_one({'_id': ObjectId(post_id)})
        if not post:
            return jsonify({'success': False, 'message': '帖子不存在'}), 404
        is_admin = session.get('role') == 'admin'
        # 2. 安全校验：确认当前登录用户是不是帖子的作者
        if post['author_id'] != session['user_id']and not is_admin:
            return jsonify({'success': False, 'message': '无权删除他人的帖子'}), 403

        # 3. 删除帖子
        posts_collection.delete_one({'_id': ObjectId(post_id)})

        # 4. 级联删除：把这个帖子下的所有评论也删掉
        if comments_collection is not None:
            comments_collection.delete_many({'post_id': post_id})

        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@app.route('/api/posts/<post_id>/view', methods=['POST'])
def record_view(post_id):
    """记录帖子浏览量（每个用户只算一次）"""
    # 如果未登录，允许放大看，但不增加实际浏览量统计
    if 'user_id' not in session:
        return jsonify({'success': True, 'incremented': False})

    if posts_collection is None:
        return jsonify({'success': False, 'message': '数据库连接失败'}), 500

    user_id = session['user_id']

    # 查找帖子
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404

    viewed_by = post.get('viewed_by', [])

    # 检查用户是否已经浏览过
    if user_id not in viewed_by:
        # 没浏览过：将 user_id 加入数组，浏览量 +1
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {
                '$addToSet': {'viewed_by': user_id},
                '$inc': {'views': 1}
            }
        )
        return jsonify({'success': True, 'incremented': True})
    else:
        # 已经浏览过：不增加数量
        return jsonify({'success': True, 'incremented': False})


# ==========================================
# ✨ 管理员专属路由与 API
# ==========================================

@app.route('/playground-pro')
def playground_pro():
    # 安全校验：不是管理员直接踢回首页
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('playgroundPRO.html')


@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """管理员获取所有用户列表"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '无权限'}), 403

    # 查找所有用户，但不返回密码字段
    users_cursor = users_collection.find({}, {'password': 0}).sort('created_at', -1)
    users = []
    for u in users_cursor:
        u['_id'] = str(u['_id'])
        if 'created_at' in u:
            u['created_at'] = u['created_at'].strftime("%Y-%m-%d %H:%M")
        users.append(u)
    return jsonify({'success': True, 'users': users})


@app.route('/api/admin/users/<user_id>', methods=['PUT', 'DELETE'])
def manage_user(user_id):
    """管理员修改或删除用户"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '无权限'}), 403

    if request.method == 'DELETE':
        try:
            # 删除用户
            users_collection.delete_one({'_id': ObjectId(user_id)})
            # 可选：连带删除该用户的帖子和评论
            posts_collection.delete_many({'author_id': user_id})
            comments_collection.delete_many({'author_id': user_id})
            return jsonify({'success': True, 'message': '用户及关联数据已删除'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    if request.method == 'PUT':
        try:
            data = request.get_json()
            new_username = data.get('username')
            new_email = data.get('email')
            # 更新用户信息
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'username': new_username, 'email': new_email}}
            )
            return jsonify({'success': True, 'message': '用户信息已更新'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # ✨ 修改：从环境变量读取 host 和 port，便于部署
    flask_host = os.getenv('FLASK_HOST', 'localhost')
    flask_port = int(os.getenv('FLASK_PORT', '5000'))
    flask_debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=flask_debug, host=flask_host, port=flask_port)
