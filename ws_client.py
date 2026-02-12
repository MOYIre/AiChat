#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket客户端示例
用于连接NapCat等QQ机器人框架

使用前请安装: pip install websocket-client
"""

import json
import threading
import websocket
from typing import Callable, Optional


class WSClient:
    """WebSocket客户端"""

    def __init__(
        self,
        ws_url: str,
        token: str = None,
        on_message: Callable[[dict], None] = None,
        on_connect: Callable[[], None] = None,
        on_disconnect: Callable[[], None] = None,
        on_error: Callable[[Exception], None] = None
    ):
        """
        初始化WebSocket客户端

        Args:
            ws_url: WebSocket地址，如 ws://127.0.0.1:3001
            token: 认证Token（可选）
            on_message: 消息回调函数
            on_connect: 连接成功回调
            on_disconnect: 断开连接回调
            on_error: 错误回调
        """
        self.ws_url = ws_url
        self.token = token
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_error = on_error

        self.ws: Optional[websocket.WebSocketApp] = None
        self.connected = False
        self._lock = threading.Lock()
        self._should_stop = False

    def is_connected(self) -> bool:
        """检查是否已连接"""
        with self._lock:
            return self.connected

    def _on_open(self, ws):
        """连接成功"""
        with self._lock:
            self.connected = True
            self.ws = ws
        print("[WS] 已连接")
        if self.on_connect:
            self.on_connect()

    def _on_message(self, ws, message):
        """收到消息"""
        try:
            data = json.loads(message)
            if self.on_message:
                self.on_message(data)
        except json.JSONDecodeError:
            print(f"[WS] 非JSON消息: {message}")

    def _on_error(self, ws, error):
        """连接错误"""
        print(f"[WS] 错误: {error}")
        with self._lock:
            self.connected = False
        if self.on_error:
            self.on_error(error)

    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        print(f"[WS] 已断开: {close_status_code} - {close_msg}")
        with self._lock:
            self.connected = False
            self.ws = None
        if self.on_disconnect:
            self.on_disconnect()

    def send(self, data: dict) -> bool:
        """
        发送消息

        Args:
            data: 要发送的数据字典

        Returns:
            是否发送成功
        """
        if not self.is_connected():
            print("[WS] 未连接，无法发送")
            return False

        try:
            with self._lock:
                if self.ws:
                    self.ws.send(json.dumps(data))
            return True
        except Exception as e:
            print(f"[WS] 发送失败: {e}")
            return False

    def send_private_msg(self, user_id: int, message: str) -> bool:
        """发送私聊消息"""
        return self.send({
            "action": "send_private_msg",
            "params": {
                "user_id": user_id,
                "message": message
            }
        })

    def send_group_msg(self, group_id: int, message: str) -> bool:
        """发送群消息"""
        return self.send({
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": message
            }
        })

    def connect(self, block: bool = True, reconnect_delay: int = 5):
        """
        连接WebSocket

        Args:
            block: 是否阻塞运行（True会一直运行）
            reconnect_delay: 重连延迟（秒）
        """
        # 构建headers
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        while not self._should_stop:
            try:
                print(f"[WS] 正在连接 {self.ws_url}...")

                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    header=headers,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )

                # 阻塞运行
                self.ws.run_forever()

            except Exception as e:
                print(f"[WS] 连接失败: {e}")

            # 重连
            if not self._should_stop:
                print(f"[WS] {reconnect_delay}秒后重连...")
                import time
                time.sleep(reconnect_delay)

    def disconnect(self):
        """断开连接"""
        self._should_stop = True
        with self._lock:
            if self.ws:
                self.ws.close()
            self.connected = False
        print("[WS] 已断开")


# ============ 使用示例 ============

if __name__ == "__main__":
    # 配置（请替换为你的实际配置）
    WS_URL = "ws://127.0.0.1:3001"  # NapCat WebSocket地址
    TOKEN = "your_token_here"        # Token（可选）

    def on_message(data: dict):
        """收到消息回调"""
        if data.get("post_type") == "message":
            msg_type = data.get("message_type")
            user_id = data.get("user_id")
            message = data.get("message", "")
            group_id = data.get("group_id")

            print(f"[消息] {msg_type}: {message}")

    def on_connect():
        """连接成功回调"""
        print("已连接到服务器!")

    # 创建客户端
    client = WSClient(
        ws_url=WS_URL,
        token=TOKEN,
        on_message=on_message,
        on_connect=on_connect
    )

    # 在后台线程运行
    import threading
    ws_thread = threading.Thread(target=client.connect, kwargs={"block": True}, daemon=True)
    ws_thread.start()

    # 主线程可以继续做其他事
    import time
    while True:
        time.sleep(1)
