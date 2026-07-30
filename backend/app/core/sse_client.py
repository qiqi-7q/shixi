from typing import Dict, List, Optional, Tuple
import asyncio
import time
import json

from app.utils.logger import get_logger

logger = get_logger(__name__, log_filename="sse_manager.log")

class SSEManager:
    """SSE 连接管理器

    特性：
    - 同一 client_id 支持多个连接（浏览器多标签页各自独立队列）
    - 广播时自动检测并清理死连接（队列满 = 消费者已断开）
    - 心跳保活，防止代理/防火墙断空闲连接
    - 连接池统一管理，支持定向推送和全员广播
    """

    def __init__(self):
        # client_id -> [(queue, created_at, filter_devNo), ...]
        self._connections: Dict[str, List[Tuple[asyncio.Queue, float, Optional[str]]]] = {}
        self._lock = asyncio.Lock()

    # ==================== 连接管理 ====================

    async def subscribe(
        self, client_id: str, filter_devNo: Optional[str] = None
    ) -> asyncio.Queue:
        """注册新的 SSE 连接，为该连接创建独立的消息队列

        同一 client_id 多次订阅（多标签页）各自持有独立队列，互不干扰。
        filter_devNo 不为 None 时，该连接只接收匹配设备号的消息。
        """
        q = asyncio.Queue(maxsize=128)
        async with self._lock:
            if client_id not in self._connections:
                self._connections[client_id] = []
            self._connections[client_id].append((q, time.time(), filter_devNo))
        logger.info(
            "SSE 订阅 | client_id=%s | filter_devNo=%s | 该客户端连接数=%d | 总连接数=%d",
            client_id,
            filter_devNo,
            self._client_conn_count(client_id),
            self.connection_count,
        )
        return q

    async def unsubscribe(self, client_id: str, queue: asyncio.Queue):
        """取消订阅，精确移除指定队列（不影响同一 client_id 的其他连接）"""
        async with self._lock:
            if client_id not in self._connections:
                return
            before = len(self._connections[client_id])
            self._connections[client_id] = [
                (q, t, d) for q, t, d in self._connections[client_id] if q is not queue
            ]
            if not self._connections[client_id]:
                del self._connections[client_id]
            after = len(self._connections.get(client_id, []))
        logger.info(
            "SSE 取消订阅 | client_id=%s | 移除前=%d | 移除后=%d | 总连接数=%d",
            client_id,
            before,
            after,
            self.connection_count,
        )

    # ==================== 状态查询 ====================

    @property
    def connection_count(self) -> int:
        """当前总连接数（含同一客户端多标签页）"""
        return sum(len(qs) for qs in self._connections.values())

    @property
    def client_count(self) -> int:
        """去重后的客户端数量"""
        return len(self._connections)

    def get_client_info(self) -> Dict[str, int]:
        """获取各客户端连接数详情"""
        return {cid: len(qs) for cid, qs in self._connections.items()}

    def _client_conn_count(self, client_id: str) -> int:
        if client_id in self._connections:
            return len(self._connections[client_id])
        return 0

    # ==================== 内部方法 ====================

    @staticmethod
    def _build_message(data: dict, event: Optional[str] = None) -> str:
        """构建符合 SSE 规范的消息字符串"""
        parts = []
        if event:
            parts.append(f"event: {event}")
        parts.append(f"data: {json.dumps(data, ensure_ascii=False)}")
        parts.append("")  # 空行表示消息结束
        return "\n".join(parts) + "\n"

    # ==================== 消息推送 ====================

    async def broadcast(self, data: dict, event: Optional[str] = None) -> int:
        """向所有在线客户端广播消息

        对于设置了 filter_devNo 的连接，仅推送匹配设备号的消息。
        消息中 devNo 取自 data["data"]["devNo"]。

        Returns:
            int: 成功推送的队列数
        """
        msg = self._build_message(data, event)
        # 提取消息中的 devNo 用于设备过滤
        msg_devNo = None
        if isinstance(data.get("data"), dict):
            msg_devNo = data["data"].get("devNo")

        dead: List[Tuple[str, asyncio.Queue]] = []
        pushed = 0

        async with self._lock:
            for client_id, queues in list(self._connections.items()):
                for q, _, filter_devNo in queues:
                    # 设备过滤：连接指定了 devNo 时，只推匹配的消息
                    if filter_devNo is not None and filter_devNo != msg_devNo:
                        continue
                    try:
                        q.put_nowait(msg)
                        pushed += 1
                    except asyncio.QueueFull:
                        # 队列满 → 消费者已停止消费（连接断开），标记清理
                        dead.append((client_id, q))

        # 清理死连接
        for client_id, q in dead:
            await self.unsubscribe(client_id, q)
            logger.warning("SSE 清理死连接 | client_id=%s", client_id)

        if dead:
            logger.info(
                "SSE 广播完成 | 推送=%d | 清理死连接=%d | 总连接数=%d",
                pushed,
                len(dead),
                self.connection_count,
            )
        return pushed

    async def send_to_client(
        self, client_id: str, data: dict, event: Optional[str] = None
    ) -> int:
        """向指定 client_id 的所有连接发送消息

        Returns:
            int: 成功推送的队列数
        """
        msg = self._build_message(data, event)
        dead = []
        pushed = 0

        async with self._lock:
            if client_id in self._connections:
                for q, _, _ in self._connections[client_id]:
                    try:
                        q.put_nowait(msg)
                        pushed += 1
                    except asyncio.QueueFull:
                        dead.append((client_id, q))

        for client_id, q in dead:
            await self.unsubscribe(client_id, q)

        return pushed

    # ==================== 定期清理 ====================

    async def cleanup_stale(self, max_idle_seconds: float = 120):
        """清理超过指定时间未活动的连接（心跳超时未响应）

        可在后台定时任务中调用，兜底清理那些因异常未正常 unsubscribe 的队列。
        """
        now = time.time()
        removed = 0
        async with self._lock:
            for client_id in list(self._connections.keys()):
                before = len(self._connections[client_id])
                self._connections[client_id] = [
                    (q, t, d)
                    for q, t, d in self._connections[client_id]
                    if now - t < max_idle_seconds
                ]
                removed += before - len(self._connections[client_id])
                if not self._connections[client_id]:
                    del self._connections[client_id]
        if removed:
            logger.info(
                "SSE 定期清理完成 | 移除=%d | 剩余连接数=%d",
                removed,
                self.connection_count,
            )


# ==================== 全局单例 ====================

sse_mgr = SSEManager()
