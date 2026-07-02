import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enrollment import AgentCredential, EnrollmentToken
from app.models.node import Node
from app.security.tokens import generate_token, hash_token


def new_public_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def create_enrollment_token(db: Session, *, created_by_id: uuid.UUID, expires_in_hours: int | None) -> tuple[EnrollmentToken, str]:
    raw_token = generate_token()
    token = EnrollmentToken(
        public_id=new_public_id("enroll"),
        token_hash=hash_token(raw_token),
        created_by_id=created_by_id,
        expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours) if expires_in_hours else None,
    )
    db.add(token)
    db.flush()
    return token, raw_token


def list_nodes(db: Session) -> list[Node]:
    return list(db.scalars(select(Node).order_by(Node.created_at.desc(), Node.hostname.asc())).all())


def enroll_node(
    db: Session,
    *,
    enrollment_token: str,
    machine_id: str,
    hostname: str,
    os_name: str | None,
    kernel: str | None,
    architecture: str | None,
) -> tuple[Node, str] | None:
    now = datetime.now(UTC)
    token = db.scalar(select(EnrollmentToken).where(EnrollmentToken.token_hash == hash_token(enrollment_token)))
    if not token or token.used_at or (token.expires_at and token.expires_at <= now):
        return None

    node = db.scalar(select(Node).where(Node.machine_id == machine_id))
    if node:
        node.hostname = hostname
        node.os_name = os_name
        node.kernel = kernel
        node.architecture = architecture
    else:
        node = Node(
            public_id=new_public_id("node"),
            machine_id=machine_id,
            hostname=hostname,
            os_name=os_name,
            kernel=kernel,
            architecture=architecture,
        )
        db.add(node)
        db.flush()

    raw_agent_token = generate_token()
    db.add(AgentCredential(node_id=node.id, token_hash=hash_token(raw_agent_token)))
    token.used_at = now
    db.flush()
    return node, raw_agent_token


def authenticate_agent(db: Session, *, node_public_id: str, agent_token: str) -> Node | None:
    credential = db.scalar(select(AgentCredential).where(AgentCredential.token_hash == hash_token(agent_token)))
    if not credential or credential.revoked_at:
        return None

    node = db.get(Node, credential.node_id)
    if not node or node.public_id != node_public_id:
        return None
    return node


def mark_node_online(db: Session, node: Node) -> None:
    node.online = True
    node.last_seen_at = datetime.now(UTC)


def mark_node_offline(db: Session, node_id: uuid.UUID) -> None:
    node = db.get(Node, node_id)
    if node:
        node.online = False
        node.last_seen_at = datetime.now(UTC)
