from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.node import Node
from app.models.user import User
from app.schemas.node import EnrollmentTokenCreate, EnrollmentTokenRead, NodeRead
from app.security.csrf import require_csrf_token
from app.security.rbac import require_admin
from app.security.session import get_current_user
from app.services.audit_service import write_audit_event
from app.services.node_service import create_enrollment_token, list_nodes

router = APIRouter(tags=["nodes"])


def _node_read(node: Node) -> NodeRead:
    return NodeRead(
        id=node.public_id,
        machine_id=node.machine_id,
        hostname=node.hostname,
        os_name=node.os_name,
        kernel=node.kernel,
        architecture=node.architecture,
        online=node.online,
        last_seen_at=node.last_seen_at,
        created_at=node.created_at,
    )


@router.get("/nodes", response_model=list[NodeRead])
async def nodes(_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [_node_read(node) for node in list_nodes(db)]


@router.post("/enrollment-tokens", response_model=EnrollmentTokenRead)
async def enrollment_token(
    payload: EnrollmentTokenCreate,
    request: Request,
    _csrf=Depends(require_csrf_token),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    token, raw_token = create_enrollment_token(db, created_by_id=user.id, expires_in_hours=payload.expires_in_hours)
    write_audit_event(
        db,
        action="node.enrollment_token.created",
        result="success",
        request=request,
        actor_id=user.id,
        target_type="enrollment_token",
        target_id=token.public_id,
        metadata={"expires_at": token.expires_at.isoformat() if token.expires_at else None},
    )
    db.commit()
    db.refresh(token)
    return EnrollmentTokenRead(id=token.public_id, token=raw_token, expires_at=token.expires_at)
