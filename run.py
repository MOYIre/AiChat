#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天机器人启动脚本
首次启动会引导配置WebSocket连接
"""

import os
import json
import sys

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "bot_config.json")


def load_config() -> dict:
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_config(config: dict):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def setup_wizard() -> dict:
    """配置向导"""
    print("=" * 50)
    print("  聊天机器人 - 首次配置")
    print("=" * 50)
    print()

    # WebSocket地址
    print("[1/4] 请输入WebSocket地址")
    print("示例: ws://127.0.0.1:3001")
    ws_url = input("地址: ").strip()
    if not ws_url:
        ws_url = "ws://127.0.0.1:3001"
        print(f"使用默认地址: {ws_url}")

    # Token
    print()
    print("[2/4] 请输入Token（可选，直接回车跳过）")
    token = input("Token: ").strip()

    # 管理员QQ
    print()
    print("[3/4] 请输入管理员QQ号（可选，直接回车跳过）")
    admin_qq = input("QQ号: ").strip()

    # 提示词设置
    print()
    print("[4/4] 设置AI角色提示词")
    print("-" * 40)
    print("预设角色:")
    print("  1. 默认助手 - 友好热心的AI助手")
    print("  2. 自定义 - 输入你自己的角色设定")
    print("  3. 跳过 - 使用默认提示词")
    print("-" * 40)

    prompt_choice = input("选择 (1/2/3): ").strip()

    custom_prompt = None
    if prompt_choice == "2":
        print()
        print("请输入角色设定（多行输入，单独一行输入 'END' 结束）:")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        custom_prompt = "\n".join(lines)
        print("✓ 已保存自定义提示词")
    elif prompt_choice == "1":
        print("✓ 使用默认助手提示词")

    config = {
        "ws_url": ws_url,
        "token": token if token else None,
        "admin_qq": int(admin_qq) if admin_qq.isdigit() else None,
        "custom_prompt": custom_prompt
    }

    save_config(config)
    print()
    print("✓ 配置已保存!")
    print()

    return config


def main():
    """主函数"""
    # 加载配置
    config = load_config()

    # 首次运行，进入配置向导
    if not config.get("ws_url"):
        config = setup_wizard()
    else:
        print(f"已加载配置: {config['ws_url']}")

    # 导入模块
    try:
        # 尝试从父目录导入
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from chat_share import ChatBot, WSClient
    except ImportError:
        try:
            # 直接导入（在目录内运行）
            from __init__ import ChatBot
            from ws_client import WSClient
        except ImportError:
            print("错误: 请确保在正确目录运行")
            sys.exit(1)

    # 创建聊天机器人
    bot = ChatBot()

    # 应用自定义提示词
    if config.get("custom_prompt"):
        import chat_prompts
        chat_prompts.SYSTEM_PROMPT_CHAT = config["custom_prompt"]
        print("✓ 已加载自定义提示词")

    # 消息处理函数
    def on_message(data: dict):
        """处理收到的消息"""
        if data.get("post_type") != "message":
            return

        msg_type = data.get("message_type")
        user_id = data.get("user_id")
        message = data.get("message", "")
        group_id = data.get("group_id")

        # 解析文本消息
        if isinstance(message, list):
            text = ''.join([m['data']['text'] for m in message if m['type'] == 'text'])
        else:
            text = str(message)

        text = text.strip()

        # 检查是否是聊天消息（:开头）
        if text.startswith(':') or text.startswith('：'):
            chat_text = text[1:].strip()
            if chat_text:
                print(f"[聊天] {msg_type}: {chat_text}")

                # 调用AI聊天
                user_key = f"user_{user_id}"
                response = bot.chat(chat_text, user_id=user_key)

                # 发送回复
                if msg_type == "group" and group_id:
                    ws.send_group_msg(group_id, response)
                else:
                    ws.send_private_msg(user_id, response)

    def on_connect():
        """连接成功"""
        print("✓ 已连接到WebSocket服务器!")
        print("机器人已启动，等待消息...")
        print("-" * 30)

    def on_disconnect():
        """断开连接"""
        print("! 连接已断开，正在重连...")

    # 创建WebSocket客户端
    ws = WSClient(
        ws_url=config["ws_url"],
        token=config.get("token"),
        on_message=on_message,
        on_connect=on_connect,
        on_disconnect=on_disconnect
    )

    print()
    print("=" * 50)
    print("  启动中...")
    print("=" * 50)
    print()

    # 启动连接（阻塞）
    try:
        ws.connect(block=True)
    except KeyboardInterrupt:
        print("\n正在退出...")
        ws.disconnect()
        print("已退出")


if __name__ == "__main__":
    # 检查是否需要重新配置
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        # 删除旧配置，重新配置
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        print("已清除旧配置，将重新配置")

    main()
