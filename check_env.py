#!/usr/bin/env python3
"""
环境检查脚本
检查开发环境是否配置正确
"""

import sys
import subprocess
from pathlib import Path

def check_python():
    """检查 Python 版本"""
    print("✓ Python 版本:", sys.version.split()[0])
    if sys.version_info < (3, 8):
        print("✗ 错误：需要 Python 3.8+")
        return False
    return True

def check_dependencies():
    """检查 Python 依赖"""
    requirements = {
        'flask': 'Flask',
        'pymongo': 'PyMongo',
        'werkzeug': 'Werkzeug'
    }
    
    all_ok = True
    for module, name in requirements.items():
        try:
            __import__(module)
            print(f"✓ {name} 已安装")
        except ImportError:
            print(f"✗ {name} 未安装")
            all_ok = False
    
    return all_ok

def check_mongodb():
    """检查 MongoDB 连接"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("✓ MongoDB 连接成功")
        return True
    except Exception as e:
        print(f"✗ MongoDB 连接失败: {e}")
        print("  提示：请确保 MongoDB 服务正在运行（执行 mongod 命令）")
        return False

def check_templates():
    """检查模板文件"""
    templates = ['home.html', 'login.html', 'sign.html', 'playground.html']
    templates_dir = Path(__file__).parent / 'templates'
    
    all_ok = True
    for template in templates:
        if (templates_dir / template).exists():
            print(f"✓ {template} 存在")
        else:
            print(f"✗ {template} 缺失")
            all_ok = False
    
    return all_ok

def check_static():
    """检查静态文件"""
    static_dirs = ['image', 'music']
    static_path = Path(__file__).parent / 'static'
    
    all_ok = True
    for dir_name in static_dirs:
        if (static_path / dir_name).exists():
            print(f"✓ static/{dir_name} 存在")
        else:
            print(f"⚠ static/{dir_name} 缺失（非必需）")
    
    return all_ok

def main():
    print("=" * 50)
    print("  The Station & Agent - 环境检查")
    print("=" * 50)
    print()
    
    print("【Python 检查】")
    python_ok = check_python()
    print()
    
    print("【依赖检查】")
    deps_ok = check_dependencies()
    print()
    
    print("【MongoDB 检查】")
    mongo_ok = check_mongodb()
    print()
    
    print("【文件结构检查】")
    templates_ok = check_templates()
    print()
    
    print("【静态资源检查】")
    static_ok = check_static()
    print()
    
    print("=" * 50)
    
    if python_ok and deps_ok and mongo_ok and templates_ok:
        print("✓ 所有检查通过！可以启动应用")
        print()
        print("启动命令：python app.py")
        return 0
    else:
        print("✗ 存在问题需要解决")
        if not deps_ok:
            print("\n安装依赖：pip install -r requirements.txt")
        if not mongo_ok:
            print("\n启动 MongoDB：mongod (在新的命令行窗口中)")
        return 1

if __name__ == '__main__':
    sys.exit(main())

