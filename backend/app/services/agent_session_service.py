import uuid

from fastapi import WebSocket


class AgentSessionManager:
    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, WebSocket] = {}

    def connect(self, node_id: uuid.UUID, websocket: WebSocket) -> None:
        self._connections[node_id] = websocket

    def disconnect(self, node_id: uuid.UUID) -> None:
        self._connections.pop(node_id, None)

    def is_connected(self, node_id: uuid.UUID) -> bool:
        return node_id in self._connections


agent_sessions = AgentSessionManager()
