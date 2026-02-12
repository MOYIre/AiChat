#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天执行器模块
负责执行AI命令和处理响应

使用方法：
1. 默认调用 iFlow CLI（需要安装）
2. 可自定义 AI 执行器
"""

import subprocess
import re
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Callable, Optional

from .chat_config import (
    AI_COMMAND_TIMEOUT,
    MAX_WORKER_THREADS,
    AI_WORK_DIR,
    DEBUG_LOG_PATH
)

# 过滤正则
EXECUTION_INFO_PATTERN = re.compile(r'<Execution Info>.*?</Execution Info>', re.DOTALL)


class ChatExecutor:
    """聊天执行器"""

    def __init__(self):
        """初始化聊天执行器"""
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)
        self.timeout = AI_COMMAND_TIMEOUT
        self.work_dir = AI_WORK_DIR

        # 错误时的友好提示
        self.friendly_responses = [
            "抱歉，我有些迷糊，能再说一遍吗？",
            "嗯... 刚才好像走神了，能重复一下吗？",
            "我没太明白，换种说法试试？",
            "抱歉，我没听清楚，能再说一次吗？",
            "这个问题有点复杂，我需要想想...",
        ]

    def _log_error(self, error_type: str, error_msg: str, user_id: int, prompt: str):
        """记录错误日志"""
        if not DEBUG_LOG_PATH:
            return
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [ERROR] Type: {error_type}, User: {user_id}\n")
                f.write(f"Prompt: {prompt[:200]}...\n")
                f.write(f"Error: {error_msg}\n")
                f.write("-" * 40 + "\n")
        except:
            pass

    def _call_ai(self, prompt: str) -> str:
        """
        调用AI命令（可自定义替换）

        默认使用 iFlow CLI，可根据需要修改为其他AI接口

        Args:
            prompt: 完整的聊天提示

        Returns:
            AI响应文本
        """
        # 方式1: 使用 iFlow CLI（默认）
        result = subprocess.run(
            ['iflow', '-p', prompt],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            cwd=self.work_dir
        )

        # 方式2: 使用其他CLI工具（示例）
        # result = subprocess.run(
        #     ['your-ai-cli', '--prompt', prompt],
        #     capture_output=True,
        #     text=True,
        #     timeout=self.timeout
        # )

        # 方式3: 调用API（示例）
        # import requests
        # response = requests.post(
        #     "https://api.example.com/chat",
        #     json={"prompt": prompt},
        #     timeout=self.timeout
        # )
        # return response.json()["text"]

        return result.stdout.strip()

    def execute_chat(self, prompt: str, user_id: int = 0) -> str:
        """
        执行聊天命令

        Args:
            prompt: 完整的聊天提示（包含系统提示和对话历史）
            user_id: 用户ID（用于日志记录）

        Returns:
            AI响应
        """
        try:
            output = self._call_ai(prompt)

            # 过滤Execution Info
            output = EXECUTION_INFO_PATTERN.sub('', output).strip()

            # 过滤OAuth2令牌刷新消息等
            oauth2_pattern = re.compile(r'OAuth2 令牌刷新成功', re.IGNORECASE)
            output = oauth2_pattern.sub('', output).strip()

            # 检查错误
            error_keywords = ['error', '错误', 'failed', '失败', 'exception', '异常']
            if any(kw in output.lower() for kw in error_keywords):
                self._log_error("OUTPUT_ERROR", output, user_id, prompt)
                return self.friendly_responses[0]

            if not output:
                self._log_error("EMPTY_OUTPUT", "No output", user_id, prompt)
                return self.friendly_responses[1]

            if len(output) < 5:
                self._log_error("SHORT_OUTPUT", output, user_id, prompt)
                return self.friendly_responses[2]

            return output

        except subprocess.TimeoutExpired:
            self._log_error("TIMEOUT", "Command timeout", user_id, prompt)
            return self.friendly_responses[3]
        except FileNotFoundError:
            self._log_error("NOT_FOUND", "AI CLI not found", user_id, prompt)
            return "AI命令未安装，请检查配置。"
        except Exception as e:
            self._log_error("EXCEPTION", str(e), user_id, prompt)
            return self.friendly_responses[0]

    def execute_chat_async(self, prompt: str, user_id: int, callback: Callable[[str, int], None]):
        """
        异步执行聊天命令

        Args:
            prompt: 完整的聊天提示
            user_id: 用户ID
            callback: 回调函数，接收(result, user_id)
        """
        future = self.executor.submit(self.execute_chat, prompt, user_id)
        try:
            result = future.result(timeout=self.timeout)
            callback(result, user_id)
        except FutureTimeoutError:
            callback("处理超时，请稍后再试。", user_id)
        except Exception as e:
            callback("抱歉，出了点问题，请重试。", user_id)

    def shutdown(self):
        """关闭执行器"""
        self.executor.shutdown(wait=False)


# 全局实例
chat_executor = ChatExecutor()
