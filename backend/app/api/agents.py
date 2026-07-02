from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState

from app.db.session import SessionLocal, get_db
from app.schemas.node import AgentEnrollRequest, AgentEnrollResponse
from app.services.agent_session_service import agent_sessions
from app.services.audit_service import write_audit_event
from app.services.node_service import authenticate_agent, enroll_node, mark_node_offline, mark_node_online

router = APIRouter(tags=["agents"])


@router.post("/agent/enroll", response_model=AgentEnrollResponse)
async def agent_enroll(payload: AgentEnrollRequest, request: Request, db: Session = Depends(get_db)):
    enrolled = enroll_node(
        db,
        enrollment_token=payload.enrollment_token,
        machine_id=payload.machine_id,
        hostname=payload.hostname,
        os_name=payload.os_name,
        kernel=payload.kernel,
        architecture=payload.architecture,
    )
    if not enrolled:
        write_audit_event(
            db,
            action="node.enrollment.failed",
            result="failure",
            request=request,
            metadata={"machine_id": payload.machine_id, "hostname": payload.hostname},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid enrollment token")

    node, agent_token = enrolled
    write_audit_event(
        db,
        action="node.enrolled",
        result="success",
        request=request,
        target_type="node",
        target_id=node.public_id,
        metadata={"machine_id": node.machine_id, "hostname": node.hostname},
    )
    db.commit()
    db.refresh(node)
    return AgentEnrollResponse(node_id=node.public_id, agent_token=agent_token)


@router.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    node = None
    try:
        first_message = await websocket.receive_json()
        if first_message.get("type") != "agent.auth":
            await websocket.close(code=1008, reason="agent.auth required as first message")
            return

        payload = first_message.get("payload") or {}
        node = authenticate_agent(
            db,
            node_public_id=str(payload.get("node_id") or ""),
            agent_token=str(payload.get("agent_token") or ""),
        )
        if not node:
            await websocket.close(code=1008, reason="invalid agent credentials")
            return

        mark_node_online(db, node)
        db.commit()
        agent_sessions.connect(node.id, websocket)
        await websocket.send_json({"type": "agent.auth.ok", "payload": {"node_id": node.public_id}})

        while True:
            message = await websocket.receive_json()
            if message.get("type") == "agent.hello":
                node.last_seen_at = datetime.now(UTC)
                db.commit()
                await websocket.send_json({"type": "agent.hello.ok", "payload": {"node_id": node.public_id}})
            else:
                await websocket.send_json({"type": "agent.error", "payload": {"error": "unknown message type"}})
    except WebSocketDisconnect:
        pass
    finally:
        if node:
            agent_sessions.disconnect(node.id)
            mark_node_offline(db, node.id)
            db.commit()
        db.close()
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
