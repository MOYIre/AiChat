#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天功能模块 - 独立版本

使用方法:
    from chat_share import ChatBot, get_system_prompt_by_mode

    # 创建聊天机器人
    bot = ChatBot()

    # 同步聊天
    response = bot.chat("你好", user_id="user_123")

    # 异步聊天
    bot.chat_async("你好", user_id="user_123", callback=on_response)

    # 切换模式
    bot.set_mode("user_123", "coc")
"""

from .chat_prompts import (
    SYSTEM_PROMPT_CHAT,
    SYSTEM_PROMPT_ADMIN,
    SYSTEM_PROMPT_COC,
    SYSTEM_PROMPT_DND,
    SYSTEM_PROMPT_THINK,
    get_system_prompt_by_mode
)
from .chat_executor import ChatExecutor, chat_executor
from .chat_history import ChatHistory
from .chat_modes import ChatModeManager, get_available_modes, get_mode_description
from .chat_config import setup
from .ws_client import WSClient


class ChatBot:
    """聊天机器人（便捷封装）"""

    def __init__(self, history_dir: str = None):
        """
        初始化聊天机器人

        Args:
            history_dir: 对话历史存储目录（可选）
        """
        self.executor = ChatExecutor()
        self.history = ChatHistory(history_dir)
        self.modes = ChatModeManager()

    def chat(self, message: str, user_id: str = "default", mode: str = None) -> str:
        """
        同步聊天

        Args:
            message: 用户消息
            user_id: 用户标识
            mode: 指定模式（可选，不指定则使用用户当前模式）

        Returns:
            AI回复
        """
        # 获取模式
        if mode is None:
            mode = self.modes.get_mode(user_id)

        # 构建提示
        system_prompt = get_system_prompt_by_mode(mode)
        history = self.history.get_history(user_id)

        if history:
            full_prompt = f"{system_prompt}\n\n【对话历史】\n{history}\n\n【用户消息】\n{message}"
        else:
            full_prompt = f"{system_prompt}\n\n【用户消息】\n{message}"

        # 执行
        response = self.executor.execute_chat(full_prompt, hash(user_id))

        # 保存历史
        if response:
            self.history.save_history(user_id, f"用户: {message}\nAI: {response}")

        return response

    def chat_async(self, message: str, user_id: str, callback, mode: str = None):
        """
        异步聊天

        Args:
            message: 用户消息
            user_id: 用户标识
            callback: 回调函数 callback(response, user_id)
            mode: 指定模式（可选）
        """
        def on_response(response, _):
            if response:
                self.history.save_history(user_id, f"用户: {message}\nAI: {response}")
            callback(response, user_id)

        # 获取模式
        if mode is None:
            mode = self.modes.get_mode(user_id)

        # 构建提示
        system_prompt = get_system_prompt_by_mode(mode)
        history = self.history.get_history(user_id)

        if history:
            full_prompt = f"{system_prompt}\n\n【对话历史】\n{history}\n\n【用户消息】\n{message}"
        else:
            full_prompt = f"{system_prompt}\n\n【用户消息】\n{message}"

        self.executor.execute_chat_async(full_prompt, hash(user_id), on_response)

    def set_mode(self, user_id: str, mode: str) -> bool:
        """设置用户模式"""
        return self.modes.set_mode(user_id, mode)

    def get_mode(self, user_id: str) -> str:
        """获取用户模式"""
        return self.modes.get_mode(user_id)

    def clear_history(self, user_id: str):
        """清除用户对话历史"""
        self.history.clear_history(user_id)


__all__ = [
    # 核心类
    'ChatBot',
    'ChatExecutor',
    'ChatHistory',
    'ChatModeManager',
    'WSClient',  # WebSocket客户端

    # 提示词
    'SYSTEM_PROMPT_CHAT',
    'SYSTEM_PROMPT_ADMIN',
    'SYSTEM_PROMPT_COC',
    'SYSTEM_PROMPT_DND',
    'SYSTEM_PROMPT_THINK',
    'get_system_prompt_by_mode',

    # 模式
    'get_available_modes',
    'get_mode_description',

    # 配置
    'setup',
]
