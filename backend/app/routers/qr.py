"""QR Code generation endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import qrcode
import io
import base64
from ..database import get_db
from ..models import Asset, User
from ..auth import get_current_user

router = APIRouter()

def generate_qr_code(data: str) -> bytes:
    """Generate QR code as PNG bytes"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

@router.get("/{asset_id}")
async def get_asset_qr_code(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate QR code for an asset"""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # QR code contains asset lookup URL
    qr_data = f"asset://{asset.asset_tag}"
    qr_bytes = generate_qr_code(qr_data)
    
    # Cache QR code in database
    if not asset.qr_code:
        asset.qr_code = base64.b64encode(qr_bytes).decode()
        await db.commit()
    
    return Response(content=qr_bytes, media_type="image/png")

@router.get("/tag/{asset_tag}")
async def get_qr_by_tag(
    asset_tag: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate QR code by asset tag"""
    result = await db.execute(select(Asset).filter(Asset.asset_tag == asset_tag))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    qr_data = f"asset://{asset.asset_tag}"
    qr_bytes = generate_qr_code(qr_data)
    
    return Response(content=qr_bytes, media_type="image/png")

@router.get("/batch")
async def get_batch_qr_codes(
    asset_ids: str,  # comma-separated
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate multiple QR codes as base64 JSON"""
    ids = [int(x.strip()) for x in asset_ids.split(",") if x.strip().isdigit()]
    result = await db.execute(select(Asset).filter(Asset.id.in_(ids)))
    assets = result.scalars().all()
    
    qr_codes = []
    for asset in assets:
        qr_data = f"asset://{asset.asset_tag}"
        qr_bytes = generate_qr_code(qr_data)
        qr_codes.append({
            "asset_id": asset.id,
            "asset_tag": asset.asset_tag,
            "name": asset.name,
            "qr_base64": base64.b64encode(qr_bytes).decode()
        })
    
    return {"qr_codes": qr_codes}
