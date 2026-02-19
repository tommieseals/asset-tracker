"Pydantic schemas for request/response validation"
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import UserRole, AssetStatus, AssetCategory

# ============== User Schemas ==============
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    full_name: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = bearer

class TokenRefresh(BaseModel):
    refresh_token: str

# ============== Asset Schemas ==============
class AssetBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: AssetCategory
    description: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[str] = None
    warranty_expires: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AssetCreate(AssetBase):
    asset_tag: Optional[str] = None  # Auto-generated if not provided

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[AssetCategory] = None
    description: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    status: Optional[AssetStatus] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AssetResponse(AssetBase):
    id: int
    asset_tag: str
    status: AssetStatus
    assigned_to: Optional[int] = None
    assignee: Optional[UserResponse] = None
    qr_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AssetCheckout(BaseModel):
    user_id: int
    notes: Optional[str] = None

class AssetCheckin(BaseModel):
    notes: Optional[str] = None

# ============== Audit Log Schemas ==============
class AuditLogResponse(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int
    user_id: int
    changes: Dict[str, Any]
    ip_address: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AuditLogFilter(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    user_id: Optional[int] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# ============== Search Schemas ==============
class SearchQuery(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    category: Optional[AssetCategory] = None
    status: Optional[AssetStatus] = None
    limit: int = Field(default=20, le=100)

class AISearchQuery(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    
class SearchResult(BaseModel):
    assets: List[AssetResponse]
    total: int
    query_interpretation: Optional[str] = None

# ============== Export Schemas ==============
class ExportRequest(BaseModel):
    format: str = Field(default=csv, pattern=^(csv|xlsx)$)
    category: Optional[AssetCategory] = None
    status: Optional[AssetStatus] = None

# ============== Stats/Dashboard ==============
class DashboardStats(BaseModel):
    total_assets: int
    available_assets: int
    checked_out_assets: int
    maintenance_assets: int
    retired_assets: int
    assets_by_category: Dict[str, int]
    recent_activity: List[AuditLogResponse]
EOF