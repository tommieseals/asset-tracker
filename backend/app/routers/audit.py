"Audit log endpoints"
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import AuditLog, User, UserRole
from ..schemas import AuditLogResponse, AuditLogFilter
from ..auth import get_current_user, require_admin_or_auditor

router = APIRouter()

@router.get(/, response_model=List[AuditLogResponse])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_auditor)
):
    "List audit logs with filters (admin/auditor only)"
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get(/entity/entity_type/entity_id, response_model=List[AuditLogResponse])
async def get_entity_audit_trail(
    entity_type: str,
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Get complete audit trail for a specific entity"
    query = (
        select(AuditLog)
        .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.timestamp.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get(/user/user_id, response_model=List[AuditLogResponse])
async def get_user_audit_trail(
    user_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_auditor)
):
    "Get all actions performed by a specific user (admin/auditor only)"
    query = (
        select(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get(/summary)
async def get_audit_summary(
    days: int = Query(default=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_auditor)
):
    "Get audit log summary statistics"
    from sqlalchemy import func
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Count by action
    action_counts = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id))
        .filter(AuditLog.timestamp >= cutoff)
        .group_by(AuditLog.action)
    )
    
    # Count by entity type
    entity_counts = await db.execute(
        select(AuditLog.entity_type, func.count(AuditLog.id))
        .filter(AuditLog.timestamp >= cutoff)
        .group_by(AuditLog.entity_type)
    )
    
    # Most active users
    user_counts = await db.execute(
        select(AuditLog.user_id, func.count(AuditLog.id))
        .filter(AuditLog.timestamp >= cutoff)
        .group_by(AuditLog.user_id)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
    )
    
    return {
        period_days: days,
        actions: dict(action_counts.fetchall()),
        entity_types: dict(entity_counts.fetchall()),
        most_active_users: dict(user_counts.fetchall())
    }
EOF