"Asset management endpoints"
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid
import io
import csv
from ..database import get_db
from ..models import Asset, User, AssetStatus, AssetCategory, CheckoutHistory, AuditLog
from ..schemas import (
    AssetCreate, AssetUpdate, AssetResponse, AssetCheckout, 
    AssetCheckin, DashboardStats, ExportRequest
)
from ..auth import get_current_user, require_admin

router = APIRouter()

def generate_asset_tag() -> str:
    "Generate unique asset tag"
    return fAST-uuid.uuid4().hex[:8].upper()

async def log_audit(
    db: AsyncSession, 
    action: str, 
    entity_type: str, 
    entity_id: int, 
    user_id: int, 
    changes: dict,
    request: Optional[Request] = None
):
    "Create audit log entry"
    audit = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        changes=changes,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get(user-agent) if request else None
    )
    db.add(audit)

@router.get(/dashboard, response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Get dashboard statistics"
    # Total counts by status
    status_counts = {}
    for status in AssetStatus:
        result = await db.execute(
            select(func.count(Asset.id)).filter(Asset.status == status)
        )
        status_counts[status.value] = result.scalar()
    
    # Count by category
    category_counts = {}
    for category in AssetCategory:
        result = await db.execute(
            select(func.count(Asset.id)).filter(Asset.category == category)
        )
        count = result.scalar()
        if count > 0:
            category_counts[category.value] = count
    
    # Recent activity
    result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.entity_type == asset)
        .order_by(AuditLog.timestamp.desc())
        .limit(10)
    )
    recent = result.scalars().all()
    
    total = sum(status_counts.values())
    
    return DashboardStats(
        total_assets=total,
        available_assets=status_counts.get(available, 0),
        checked_out_assets=status_counts.get(checked_out, 0),
        maintenance_assets=status_counts.get(maintenance, 0),
        retired_assets=status_counts.get(retired, 0),
        assets_by_category=category_counts,
        recent_activity=recent
    )

@router.post(/, response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Create a new asset"
    asset_tag = asset_data.asset_tag or generate_asset_tag()
    
    # Check for duplicate serial number
    if asset_data.serial_number:
        result = await db.execute(
            select(Asset).filter(Asset.serial_number == asset_data.serial_number)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=Serial number already exists)
    
    asset = Asset(
        asset_tag=asset_tag,
        **asset_data.model_dump(exclude={asset_tag})
    )
    db.add(asset)
    await db.flush()
    
    await log_audit(db, create, asset, asset.id, current_user.id, 
                    {asset_tag: asset_tag, name: asset.name}, request)
    
    await db.commit()
    await db.refresh(asset)
    return asset

@router.get(/, response_model=List[AssetResponse])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    category: Optional[AssetCategory] = None,
    status: Optional[AssetStatus] = None,
    assigned_to: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "List assets with optional filters"
    query = select(Asset).options(selectinload(Asset.assignee))
    
    if category:
        query = query.filter(Asset.category == category)
    if status:
        query = query.filter(Asset.status == status)
    if assigned_to:
        query = query.filter(Asset.assigned_to == assigned_to)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get(/asset_id, response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Get asset by ID"
    result = await db.execute(
        select(Asset).options(selectinload(Asset.assignee)).filter(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=Asset not found)
    return asset

@router.get(/tag/asset_tag, response_model=AssetResponse)
async def get_asset_by_tag(
    asset_tag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Get asset by asset tag (for QR code scanning)"
    result = await db.execute(
        select(Asset).options(selectinload(Asset.assignee)).filter(Asset.asset_tag == asset_tag)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=Asset not found)
    return asset

@router.patch(/asset_id, response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Update asset"
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=Asset not found)
    
    update_data = asset_update.model_dump(exclude_unset=True)
    old_values = {k: getattr(asset, k) for k in update_data}
    
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    await log_audit(db, update, asset, asset.id, current_user.id,
                    {old: old_values, new: update_data}, request)
    
    await db.commit()
    await db.refresh(asset)
    return asset

@router.post(/asset_id/checkout, response_model=AssetResponse)
async def checkout_asset(
    asset_id: int,
    checkout_data: AssetCheckout,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Check out asset to a user"
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=Asset not found)
    
    if asset.status != AssetStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail=fAsset is not available (status: asset.status))
    
    # Verify user exists
    user_result = await db.execute(select(User).filter(User.id == checkout_data.user_id))
    target_user = user_result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail=Target user not found)
    
    # Update asset
    asset.status = AssetStatus.CHECKED_OUT
    asset.assigned_to = checkout_data.user_id
    
    # Create checkout history
    history = CheckoutHistory(
        asset_id=asset.id,
        user_id=checkout_data.user_id,
        notes=checkout_data.notes,
        checked_out_by=current_user.id
    )
    db.add(history)
    
    await log_audit(db, checkout, asset, asset.id, current_user.id,
                    {user_id: checkout_data.user_id, notes: checkout_data.notes}, request)
    
    await db.commit()
    await db.refresh(asset)
    return asset

@router.post(/asset_id/checkin, response_model=AssetResponse)
async def checkin_asset(
    asset_id: int,
    checkin_data: AssetCheckin,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Check in asset"
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=Asset not found)
    
    if asset.status != AssetStatus.CHECKED_OUT:
        raise HTTPException(status_code=400, detail=Asset is not checked out)
    
    # Update latest checkout history
    history_result = await db.execute(
        select(CheckoutHistory)
        .filter(CheckoutHistory.asset_id == asset.id, CheckoutHistory.checkin_date == None)
        .order_by(CheckoutHistory.checkout_date.desc())
    )
    history = history_result.scalar_one_or_none()
    if history:
        history.checkin_date = datetime.utcnow()
        history.checked_in_by = current_user.id
        history.notes = (history.notes or ") + f | Check-in:  or }"
    
    old_assignee = asset.assigned_to
    asset.status = AssetStatus.AVAILABLE
    asset.assigned_to = None
    
    await log_audit(db, "checkin", "asset", asset.id, current_user.id,
                    {"previous_assignee": old_assignee, "notes": checkin_data.notes}, request)
    
    await db.commit()
    await db.refresh(asset)
    return asset

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete asset (admin only)"""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    await log_audit(db, "delete", "asset", asset.id, current_user.id,
                    {"asset_tag": asset.asset_tag, "name": asset.name}, request)
    
    await db.delete(asset)
    await db.commit()

@router.get("/{asset_id}/history")
async def get_asset_history(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get checkout history for an asset"""
    result = await db.execute(
        select(CheckoutHistory)
        .filter(CheckoutHistory.asset_id == asset_id)
        .order_by(CheckoutHistory.checkout_date.desc())
    )
    return result.scalars().all()

@router.post("/export")
async def export_assets(
    export_req: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export assets to CSV or Excel"""
    query = select(Asset).options(selectinload(Asset.assignee))
    
    if export_req.category:
        query = query.filter(Asset.category == export_req.category)
    if export_req.status:
        query = query.filter(Asset.status == export_req.status)
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Asset Tag", "Name", "Category", "Status", "Serial Number",
        "Manufacturer", "Model", "Location", "Assigned To", "Created At"
    ])
    
    for asset in assets:
        writer.writerow([
            asset.asset_tag, asset.name, asset.category.value, asset.status.value,
            asset.serial_number or "", asset.manufacturer or "", asset.model or "",
            asset.location or "", asset.assignee.full_name if asset.assignee else "",
            asset.created_at.isoformat()
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=assets_{datetime.now().strftime(%Y%m%d)}.csv"}
    )
EOF"