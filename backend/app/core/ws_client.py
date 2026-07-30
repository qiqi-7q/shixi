import json
import time
from typing import Dict, List, Any
from fastapi import WebSocket
from pydantic import BaseModel

from app.utils.logger import get_logger

logger = get_logger(__name__, log_filename="websocket.log")


# 统一消息协议模型
class WsTextMsg(BaseModel):
    msg_type: str  # text / alert / camera
    data: Any
    timestamp: int


# 视频二进制分隔符
SEPARATOR = b"|||WS_SEP_2026|||"


class WebSocketManager:
    """WebSocket 连接管理器

    负责管理所有活跃的 WebSocket 客户端连接，提供连接建立、消息发送、
    消息接收、连接关闭等核心功能。使用单例模式确保全局唯一。
    """

    def __init__(self):
        # 活跃连接池：key=用户/设备id，value=WebSocket对象
        self.active_connections: Dict[str, WebSocket] = {}

    # ==================== 连接管理 ====================

    async def connect(self, client_id: str, websocket: WebSocket):
        """接受新的 WebSocket 连接并注册到连接池

        Args:
            client_id: 客户端唯一标识
            websocket: WebSocket 连接对象
        """
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info(
                "WebSocket 客户端已接入 | client_id=%s | 在线总数=%d",
                client_id,
                len(self.active_connections),
            )
        except Exception as e:
            logger.error(
                "WebSocket 连接接受失败 | client_id=%s | error=%s", client_id, str(e)
            )
            raise

    def disconnect(self, client_id: str):
        """移除指定的 WebSocket 连接

        Args:
            client_id: 客户端唯一标识
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(
                "WebSocket 客户端已断开 | client_id=%s | 在线总数=%d",
                client_id,
                len(self.active_connections),
            )
        else:
            logger.warning("尝试断开不存在的客户端连接 | client_id=%s", client_id)

    # ==================== 连接状态查询 ====================

    def is_connected(self, client_id: str) -> bool:
        """检查指定客户端是否在线

        Args:
            client_id: 客户端唯一标识

        Returns:
            bool: 客户端是否在线
        """
        return client_id in self.active_connections

    @property
    def connection_count(self) -> int:
        """获取当前在线客户端数量"""
        return len(self.active_connections)

    def get_online_clients(self) -> List[str]:
        """获取所有在线客户端的 ID 列表

        Returns:
            List[str]: 在线客户端 ID 列表
        """
        return list(self.active_connections.keys())

    # ==================== 文本消息发送 ====================

    async def send_text_to_client(self, client_id: str, msg: WsTextMsg) -> bool:
        """向指定客户端发送文本消息

        Args:
            client_id: 目标客户端 ID
            msg: 待发送的消息对象

        Returns:
            bool: 发送是否成功
        """
        if client_id not in self.active_connections:
            logger.warning(
                "发送失败：客户端不在线 | client_id=%s | msg_type=%s",
                client_id,
                msg.msg_type,
            )
            return False

        ws = self.active_connections[client_id]
        try:
            json_str = msg.model_dump_json()
            await ws.send_text(json_str)
            logger.debug(
                "文本消息已发送 | client_id=%s | msg_type=%s", client_id, msg.msg_type
            )
            return True
        except Exception as e:
            logger.error(
                "文本消息发送失败，移除连接 | client_id=%s | msg_type=%s | error=%s",
                client_id,
                msg.msg_type,
                str(e),
            )
            self.disconnect(client_id)
            return False

    async def broadcast_text(self, msg: WsTextMsg) -> Dict[str, Any]:
        """向所有在线客户端广播文本消息

        Args:
            msg: 待广播的消息对象

        Returns:
            Dict: 广播结果，包含 total/success/failed 计数及失败列表
        """
        fail_ids = []
        success_count = 0
        total = len(self.active_connections)

        if total == 0:
            logger.warning("广播文本消息时无在线客户端 | msg_type=%s", msg.msg_type)
            return {"total": 0, "success": 0, "failed": 0, "fail_ids": []}

        for cid, ws in self.active_connections.items():
            try:
                json_str = msg.model_dump_json()
                await ws.send_text(json_str)
                success_count += 1
            except Exception as e:
                logger.error(
                    "广播消息发送失败 | client_id=%s | msg_type=%s | error=%s",
                    cid,
                    msg.msg_type,
                    str(e),
                )
                fail_ids.append(cid)

        # 清理失效连接
        for cid in fail_ids:
            self.disconnect(cid)

        logger.info(
            "文本消息广播完成 | msg_type=%s | total=%d | success=%d | failed=%d",
            msg.msg_type,
            total,
            success_count,
            len(fail_ids),
        )

        return {
            "total": total,
            "success": success_count,
            "failed": len(fail_ids),
            "fail_ids": fail_ids,
        }

    async def broadcast_json(self, msg_type: str, data: Any) -> Dict[str, Any]:
        """向所有在线客户端广播 JSON 消息（便捷方法）

        自动封装 WsTextMsg 并设置时间戳，简化调用方代码。

        Args:
            msg_type: 消息类型标识
            data: 消息数据内容

        Returns:
            Dict: 广播结果，包含 total/success/failed 计数
        """
        msg = WsTextMsg(msg_type=msg_type, data=data, timestamp=int(time.time() * 1000))
        return await self.broadcast_text(msg)

    # ==================== 视频二进制消息发送 ====================

    async def send_video_to_client(
        self, client_id: str, info: dict, video_bytes: bytes
    ) -> bool:
        """向指定客户端发送视频二进制数据包

        Args:
            client_id: 目标客户端 ID
            info: 视频元信息字典
            video_bytes: 视频二进制数据

        Returns:
            bool: 发送是否成功
        """
        if client_id not in self.active_connections:
            logger.warning("发送视频失败：客户端不在线 | client_id=%s", client_id)
            return False

        ws = self.active_connections[client_id]
        try:
            header = json.dumps({"msg_type": "video", "info": info}).encode("utf-8")
            packet = header + SEPARATOR + video_bytes
            await ws.send_bytes(packet)
            logger.debug("视频数据已发送 | client_id=%s", client_id)
            return True
        except Exception as e:
            logger.error(
                "视频数据发送失败，移除连接 | client_id=%s | error=%s",
                client_id,
                str(e),
            )
            self.disconnect(client_id)
            return False

    async def broadcast_video(self, info: dict, video_bytes: bytes) -> Dict[str, Any]:
        """向所有在线客户端广播视频二进制数据

        Args:
            info: 视频元信息字典
            video_bytes: 视频二进制数据

        Returns:
            Dict: 广播结果，包含 total/success/failed 计数
        """
        fail_ids = []
        success_count = 0
        total = len(self.active_connections)

        if total == 0:
            logger.warning("广播视频时无在线客户端")
            return {"total": 0, "success": 0, "failed": 0, "fail_ids": []}

        header = json.dumps({"msg_type": "video", "info": info}).encode("utf-8")
        packet = header + SEPARATOR + video_bytes
        for cid, ws in self.active_connections.items():
            try:
                await ws.send_bytes(packet)
                success_count += 1
            except Exception as e:
                logger.error("广播视频发送失败 | client_id=%s | error=%s", cid, str(e))
                fail_ids.append(cid)

        for cid in fail_ids:
            self.disconnect(cid)

        logger.info(
            "视频广播完成 | total=%d | success=%d | failed=%d",
            total,
            success_count,
            len(fail_ids),
        )

        return {
            "total": total,
            "success": success_count,
            "failed": len(fail_ids),
            "fail_ids": fail_ids,
        }


# 全局单例管理器
ws_manager = WebSocketManager()
