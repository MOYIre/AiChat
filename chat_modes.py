#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天模式管理模块
"""

import threading
from typing import Dict, Optional


# 可用模式
AVAILABLE_MODES = {
    'chat': '日常聊天模式',
    'coc': 'COC跑团模式',
    'dnd': 'DND跑团模式',
    'think': '深度思考模式'
}


def get_available_modes() -> Dict[str, str]:
    """获取所有可用模式"""
    return AVAILABLE_MODES.copy()


def get_mode_description(mode: str) -> str:
    """获取模式描述"""
    return AVAILABLE_MODES.get(mode, '未知模式')


class ChatModeManager:
    """聊天模式管理器"""

    def __init__(self):
        self.lock = threading.Lock()
        self.modes = {}

    def get_mode(self, session_key: str) -> str:
        """获取会话的模式"""
        with self.lock:
            return self.modes.get(session_key, 'chat')

    def set_mode(self, session_key: str, mode: str) -> bool:
        """设置会话的模式"""
        if mode not in AVAILABLE_MODES:
            return False
        with self.lock:
            self.modes[session_key] = mode
        return True

    def reset_mode(self, session_key: str):
        """重置会话模式"""
        with self.lock:
            if session_key in self.modes:
                del self.modes[session_key]
