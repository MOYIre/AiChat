#!/bin/bash
# AI聊天机器人启动脚本

cd "$(dirname "$0")"

# 检查参数
if [ "$1" == "--config" ]; then
    python3 run.py --config
else
    python3 run.py "$@"
fi
