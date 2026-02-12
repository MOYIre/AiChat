#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话历史管理模块
"""

import os
import threading
from .chat_config import HISTORY_DIR, MAX_HISTORY_LINES


class ChatHistory:
    """对话历史管理器"""

    def __init__(self, history_dir: str = None):
        """
        初始化对话历史管理器

        Args:
            history_dir: 历史文件存储目录
        """
        self.lock = threading.Lock()
        self.history_dir = history_dir or HISTORY_DIR
        os.makedirs(self.history_dir, exist_ok=True)

    def get_history(self, user_key: str) -> str:
        """
        获取用户的对话历史

        Args:
            user_key: 用户标识（如 "user_123"）

        Returns:
            对话历史文本
        """
        history_file = os.path.join(self.history_dir, f"{user_key}.txt")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return ""
        return ""

    def save_history(self, user_key: str, response: str):
        """
        保存对话历史

        Args:
            user_key: 用户标识
            response: AI回复
        """
        history_file = os.path.join(self.history_dir, f"{user_key}.txt")
        with self.lock:
            try:
                # 追加回复
                with open(history_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{response}")

                # 限制历史长度
                with open(history_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if len(lines) > MAX_HISTORY_LINES:
                    with open(history_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines[-MAX_HISTORY_LINES:])
            except Exception as e:
                print(f"保存历史失败: {e}")

    def clear_history(self, user_key: str) -> bool:
        """清除用户的对话历史"""
        history_file = os.path.join(self.history_dir, f"{user_key}.txt")
        with self.lock:
            if os.path.exists(history_file):
                try:
                    os.remove(history_file)
                    return True
                except:
                    return False
        return True

    def get_history_length(self, user_key: str) -> int:
        """获取对话历史的行数"""
        history = self.get_history(user_key)
        return len(history.strip().split('\n')) if history else 0
