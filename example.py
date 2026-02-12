#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例
"""

from chat_share import ChatBot, get_available_modes, setup

# 可选：自定义配置
# setup(history_dir="./my_history", debug_log="./debug.log")


def example_sync():
    """同步聊天示例"""
    bot = ChatBot()

    # 普通聊天
    response = bot.chat("你好，介绍一下自己")
    print(f"AI: {response}")

    # 切换到COC模式
    bot.set_mode("user_123", "coc")
    response = bot.chat("开始一场克苏鲁风格的冒险", user_id="user_123")
    print(f"AI: {response}")


def example_async():
    """异步聊天示例"""
    bot = ChatBot()

    def on_response(response, user_id):
        print(f"[{user_id}] AI: {response}")

    # 异步聊天
    bot.chat_async("你好", user_id="user_456", callback=on_response)
    print("消息已发送，等待回复...")


def example_modes():
    """模式管理示例"""
    print("可用模式:")
    for mode, desc in get_available_modes().items():
        print(f"  {mode}: {desc}")

    bot = ChatBot()
    bot.set_mode("test_user", "think")

    response = bot.chat(
        "分析一下人工智能的发展趋势",
        user_id="test_user"
    )
    print(f"AI: {response}")


if __name__ == "__main__":
    print("=" * 40)
    print("聊天模块使用示例")
    print("=" * 40)

    # 运行示例（需要安装 iFlow CLI 或修改 chat_executor.py）
    try:
        example_sync()
    except Exception as e:
        print(f"运行示例出错: {e}")
        print("请确保已安装 AI CLI 工具或修改 chat_executor.py 使用自定义接口")
