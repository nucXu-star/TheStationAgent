#!/bin/bash
# 宝塔部署脚本
# 将此脚本放在项目根目录或由宝塔钩子调用
# 功能：自动安装依赖、配置环境变量、启动应用

set -e  # 遇到错误立即退出

echo "🚀 开始部署 The Station Agent..."

# 配置
PROJECT_DIR="/www/wwwroot/www.thestationagentheart.co"  # 替换为你的项目目录
VENV_PATH="${PROJECT_DIR}/.venv"
PYTHON_CMD="python3"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo_info() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 步骤 1: 进入项目目录
echo_info "进入项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR" || exit 1

# 步骤 2: 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_PATH" ]; then
    echo_warn "虚拟环境不存在，创建中..."
    $PYTHON_CMD -m venv "$VENV_PATH"
    echo_info "虚拟环境创建成功"
else
    echo_info "虚拟环境已存在"
fi

# 步骤 3: 激活虚拟环境
echo_info "激活虚拟环境"
source "${VENV_PATH}/bin/activate"

# 步骤 4: 升级 pip
echo_warn "升级 pip..."
pip install --upgrade pip -q

# 步骤 5: 安装依赖
echo_warn "安装 Python 依赖..."
pip install -r requirements.txt -q
echo_info "依赖安装完成"

# 步骤 6: 检查 .env 文件
if [ ! -f ".env" ]; then
    echo_error ".env 文件不存在！"
    echo_warn "请根据 .env.example 创建 .env 文件，内容示例："
    cat .env.example
    exit 1
else
    echo_info ".env 文件已存在"
fi

# 步骤 7: 验证环境变量
echo_warn "验证环境变量配置..."
$PYTHON_CMD verify_env.py

# 步骤 8: 启动应用（推荐使用 gunicorn + systemd 管理）
echo_warn "部署说明："
echo "  1. 后台启动（使用 gunicorn）"
echo "     gunicorn -w 3 -b 0.0.0.0:8000 app:app"
echo ""
echo "  2. 使用 systemd 管理（推荐）"
echo "     sudo cp deploy/the-station-agent.service /etc/systemd/system/"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl start the-station-agent"
echo "     sudo systemctl enable the-station-agent"
echo ""
echo "  3. 在宝塔面板配置反向代理"
echo "     源站: 127.0.0.1:8000"
echo ""

echo_info "部署准备完成！✨"

