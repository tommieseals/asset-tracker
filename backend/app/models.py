"SQLAlchemy models for Asset Inventory Tracker"
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = admin
    USER = user
    AUDITOR = auditor

class AssetStatus(str, enum.Enum):
    AVAILABLE = available
    CHECKED_OUT = checked_out
    MAINTENANCE = maintenance
    RETIRED = retired

class AssetCategory(str, enum.Enum):
    LAPTOP = laptop
    MONITOR = monitor
    KEYBOARD = keyboard
    MOUSE = mouse
    HEADSET = headset
    PHONE = phone
    LICENSE = license
    KEY = key
    OTHER = other

class User(Base):
    __tablename__ = users
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    department = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_assets = relationship(Asset, back_populates=assignee, foreign_keys=Asset.assigned_to)
    checkouts = relationship(CheckoutHistory, back_populates=user)
    audit_logs = relationship(AuditLog, back_populates=user)

class Asset(Base):
    __tablename__ = assets
    
    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(Enum(AssetCategory), nullable=False)
    description = Column(Text)
    serial_number = Column(String(100), unique=True)
    manufacturer = Column(String(100))
    model = Column(String(100))
    purchase_date = Column(DateTime)
    purchase_price = Column(String(50))
    warranty_expires = Column(DateTime)
    location = Column(String(255))
    status = Column(Enum(AssetStatus), default=AssetStatus.AVAILABLE)
    assigned_to = Column(Integer, ForeignKey(users.id), nullable=True)
    notes = Column(Text)
    metadata = Column(JSON, default=dict)
    qr_code = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignee = relationship(User, back_populates=assigned_assets, foreign_keys=[assigned_to])
    checkout_history = relationship(CheckoutHistory, back_populates=asset)
    audit_logs = relationship(AuditLog, back_populates=asset)

class CheckoutHistory(Base):
    __tablename__ = checkout_history
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey(assets.id), nullable=False)
    user_id = Column(Integer, ForeignKey(users.id), nullable=False)
    checkout_date = Column(DateTime, default=datetime.utcnow)
    checkin_date = Column(DateTime, nullable=True)
    notes = Column(Text)
    checked_out_by = Column(Integer, ForeignKey(users.id))
    checked_in_by = Column(Integer, ForeignKey(users.id), nullable=True)
    
    # Relationships
    asset = relationship(Asset, back_populates=checkout_history)
    user = relationship(User, back_populates=checkouts, foreign_keys=[user_id])

class AuditLog(Base):
    __tablename__ = audit_logs
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)  # create, update, delete, checkout, checkin
    entity_type = Column(String(50), nullable=False)  # asset, user, etc.
    entity_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey(users.id), nullable=False)
    changes = Column(JSON, default=dict)  # What was changed
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship(User, back_populates=audit_logs)
    asset = relationship(Asset, back_populates=audit_logs, foreign_keys=[entity_id],
                        primaryjoin=and_(AuditLog.entity_id==Asset.id, AuditLog.entity_type==asset))

class SoftwareLicense(Base):
    __tablename__ = software_licenses
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    vendor = Column(String(100))
    license_key = Column(String(500))  # Encrypted in production
    license_type = Column(String(50))  # perpetual, subscription, per-seat
    seats_total = Column(Integer, default=1)
    seats_used = Column(Integer, default=0)
    expires_at = Column(DateTime)
    cost = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
EOF