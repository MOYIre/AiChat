#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天模块配置
请根据实际情况修改配置项
"""

import os

# ============ AI执行器配置 ============

# AI命令超时时间（秒）
AI_COMMAND_TIMEOUT = 60

# 最大工作线程数
MAX_WORKER_THREADS = 10

# AI命令执行的工作目录（可选，某些AI CLI工具需要）
AI_WORK_DIR = None  # 例如: "/path/to/your/project"

# 调试日志路径（可选，设为None则不记录）
DEBUG_LOG_PATH = None  # 例如: "./debug.log"


# ============ 对话历史配置 ============

# 对话历史存储目录
HISTORY_DIR = os.path.join(os.path.dirname(__file__), ".chat_history")

# 最大历史行数（每次对话保留的上下文行数）
MAX_HISTORY_LINES = 5


# ============ 快捷设置函数 ============

def setup(history_dir: str = None, debug_log: str = None, work_dir: str = None):
    """
    快速配置聊天模块

    Args:
        history_dir: 对话历史存储目录
        debug_log: 调试日志路径
        work_dir: AI命令执行目录
    """
    global HISTORY_DIR, DEBUG_LOG_PATH, AI_WORK_DIR

    if history_dir:
        HISTORY_DIR = history_dir
    if debug_log:
        DEBUG_LOG_PATH = debug_log
    if work_dir:
        AI_WORK_DIR = work_dir
