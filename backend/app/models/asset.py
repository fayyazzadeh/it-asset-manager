from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET, MACADDR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AssetType(Base):
    __tablename__ = "asset_types"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AssetSubtype(Base):
    __tablename__ = "asset_subtypes"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="RESTRICT"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("asset_type_id", "code"),)


class Network(Base):
    __tablename__ = "networks"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    network_address: Mapped[str | None] = mapped_column(INET)
    cidr: Mapped[int] = mapped_column(Integer, nullable=False)
    gateway: Mapped[str | None] = mapped_column(INET)
    network_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (CheckConstraint("cidr >= 0 AND cidr <= 128", name="ck_network_cidr"),)


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    building: Mapped[str | None] = mapped_column(String(100))
    floor: Mapped[str | None] = mapped_column(String(50))
    room: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("name", "building", "floor", "room"),)


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    qr_code: Mapped[str | None] = mapped_column(String(255), unique=True)
    barcode: Mapped[str | None] = mapped_column(String(255), unique=True)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id", ondelete="RESTRICT"), nullable=False)
    asset_subtype_id: Mapped[int | None] = mapped_column(ForeignKey("asset_subtypes.id", ondelete="RESTRICT"))
    network_id: Mapped[int | None] = mapped_column(ForeignKey("networks.id", ondelete="RESTRICT"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(40), default="DISCOVERED", nullable=False)
    computer_name: Mapped[str | None] = mapped_column(String(255))
    hostname: Mapped[str | None] = mapped_column(String(255))
    fqdn: Mapped[str | None] = mapped_column(String(255))
    domain: Mapped[str | None] = mapped_column(String(255))
    manufacturer: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    serial_number: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (
        Index("ix_assets_status", "status"),
        Index("ix_assets_hostname", "hostname"),
        Index("ix_assets_fqdn", "fqdn"),
        Index("ix_assets_serial_number", "serial_number"),
        Index("ix_assets_last_seen", "last_seen"),
    )


class AssetIdentifier(Base):
    __tablename__ = "asset_identifiers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(50), nullable=False)
    identifier_value: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("identifier_type", "identifier_value"),
        Index("ix_asset_identifiers_asset", "asset_id"),
        Index("ix_asset_identifiers_type_value", "identifier_type", "identifier_value"),
    )


class AssetNetworkInterface(Base):
    __tablename__ = "asset_network_interfaces"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    network_id: Mapped[int | None] = mapped_column(ForeignKey("networks.id", ondelete="RESTRICT"))
    interface_name: Mapped[str | None] = mapped_column(String(150))
    mac_address: Mapped[str | None] = mapped_column(MACADDR)
    ip_address: Mapped[str | None] = mapped_column(INET)
    ip_version: Mapped[int | None] = mapped_column(Integer)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    speed: Mapped[int | None] = mapped_column(BigInteger)
    status: Mapped[str | None] = mapped_column(String(40))
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (
        Index("ix_asset_nic_asset", "asset_id"),
        Index("ix_asset_nic_ip", "ip_address"),
        Index("ix_asset_nic_mac", "mac_address"),
        Index("ix_asset_nic_last_seen", "last_seen"),
    )