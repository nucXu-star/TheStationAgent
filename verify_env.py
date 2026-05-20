#!/usr/bin/env python3
"""
环境变量配置验证脚本
用于检查环境变量是否正确加载
"""

import os
import sys
from dotenv import load_dotenv

def check_env_config():
    """检查环境变量配置"""
    print("\n" + "="*60)
    print("🔍 环境变量配置检查")
    print("="*60 + "\n")
    
    # 加载 .env 文件
    load_dotenv()
    
    configs = {
        "Flask 配置": [
            ("FLASK_ENV", "development"),
            ("FLASK_DEBUG", "0"),
            ("SECRET_KEY", "dev-secret-key-change-in-production"),
        ],
        "MongoDB 配置": [
            ("MONGO_URI", "mongodb://localhost:27017/"),
            ("DATABASE_NAME", "station_agent_db"),
        ],
        "邮件配置": [
            ("MAIL_SERVER", "smtp.qq.com"),
            ("MAIL_PORT", "465"),
            ("MAIL_USE_SSL", "True"),
            ("MAIL_USERNAME", "1626521893@qq.com"),
            ("MAIL_PASSWORD", "lpcoauuqdwlgecid"),
        ],
        "应用配置": [
            ("FLASK_HOST", "localhost"),
            ("FLASK_PORT", "5000"),
        ],
    }
    
    passed = 0
    failed = 0
    
    for category, env_vars in configs.items():
        print(f"📋 {category}")
        print("-" * 60)
        
        for var_name, default_value in env_vars:
            value = os.getenv(var_name)
            is_default = value is None or value == default_value
            
            if value:
                # 隐藏敏感信息
                if var_name in ["SECRET_KEY", "MAIL_PASSWORD"]:
                    display_value = value[:10] + "***" if len(value) > 10 else "***"
                else:
                    display_value = value
                
                status = "⚠️ (默认值)" if is_default else "✅"
                print(f"  {status} {var_name:20} = {display_value}")
                passed += 1
            else:
                print(f"  ⚠️  {var_name:20} = {default_value} (使用默认值)")
                passed += 1
        
        print()
    
    print("="*60)
    print(f"✅ 检查完成：{passed} 个配置项读取成功")
    print("="*60 + "\n")
    
    # 检查关键配置是否安全
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    if secret_key == 'dev-secret-key-change-in-production':
        print("⚠️  警告：SECRET_KEY 使用的是默认值，生产环境必须修改！\n")
    
    return True

if __name__ == '__main__':
    try:
        check_env_config()
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

