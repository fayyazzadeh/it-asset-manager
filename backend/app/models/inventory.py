from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Hardware(Base):
    __tablename__ = "hardware"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    system_family: Mapped[str | None] = mapped_column(String(150))
    chassis_type: Mapped[str | None] = mapped_column(String(80))
    motherboard_vendor: Mapped[str | None] = mapped_column(String(150))
    motherboard_model: Mapped[str | None] = mapped_column(String(150))
    motherboard_serial: Mapped[str | None] = mapped_column(String(255))
    bios_vendor: Mapped[str | None] = mapped_column(String(150))
    bios_version: Mapped[str | None] = mapped_column(String(150))
    bios_date: Mapped[str | None] = mapped_column(String(50))
    total_ram_bytes: Mapped[int | None] = mapped_column(BigInteger)
    gpu_summary: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class HardwareProcessor(Base):
    __tablename__ = "hardware_processors"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hardware_id: Mapped[int] = mapped_column(ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False)
    socket: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(150))
    architecture: Mapped[str | None] = mapped_column(String(80))
    physical_cores: Mapped[int | None] = mapped_column(Integer)
    logical_cores: Mapped[int | None] = mapped_column(Integer)
    base_frequency_mhz: Mapped[int | None] = mapped_column(Integer)
    max_frequency_mhz: Mapped[int | None] = mapped_column(Integer)
    threads: Mapped[int | None] = mapped_column(Integer)
    serial_number: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str | None] = mapped_column(String(40))
    __table_args__ = (UniqueConstraint("hardware_id", "socket"), CheckConstraint("logical_cores IS NULL OR physical_cores IS NULL OR logical_cores >= physical_cores", name="ck_cpu_logical_ge_physical"))


class MemoryModule(Base):
    __tablename__ = "memory_modules"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hardware_id: Mapped[int] = mapped_column(ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False)
    slot: Mapped[str] = mapped_column(String(80), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    part_number: Mapped[str | None] = mapped_column(String(150))
    serial_number: Mapped[str | None] = mapped_column(String(255))
    capacity_bytes: Mapped[int | None] = mapped_column(BigInteger)
    memory_type: Mapped[str | None] = mapped_column(String(50))
    speed_mhz: Mapped[int | None] = mapped_column(Integer)
    configured_speed_mhz: Mapped[int | None] = mapped_column(Integer)
    ecc: Mapped[bool | None] = mapped_column(Boolean)
    rank: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str | None] = mapped_column(String(40))
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("hardware_id", "slot"), Index("ix_memory_serial", "serial_number"))


class StorageDevice(Base):
    __tablename__ = "storage_devices"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hardware_id: Mapped[int] = mapped_column(ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False)
    device_name: Mapped[str | None] = mapped_column(String(150))
    device_path: Mapped[str | None] = mapped_column(String(255))
    manufacturer: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    serial_number: Mapped[str | None] = mapped_column(String(255))
    storage_type: Mapped[str | None] = mapped_column(String(50))
    interface_type: Mapped[str | None] = mapped_column(String(50))
    capacity_bytes: Mapped[int | None] = mapped_column(BigInteger)
    firmware_version: Mapped[str | None] = mapped_column(String(100))
    health_status: Mapped[str | None] = mapped_column(String(40))
    smart_supported: Mapped[bool | None] = mapped_column(Boolean)
    smart_status: Mapped[str | None] = mapped_column(String(40))
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (Index("ix_storage_serial", "serial_number"),)


class StoragePartition(Base):
    __tablename__ = "storage_partitions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    storage_device_id: Mapped[int] = mapped_column(ForeignKey("storage_devices.id", ondelete="CASCADE"), nullable=False)
    partition_name: Mapped[str | None] = mapped_column(String(150))
    device_path: Mapped[str | None] = mapped_column(String(255))
    filesystem: Mapped[str | None] = mapped_column(String(80))
    mount_point: Mapped[str | None] = mapped_column(String(255))
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    used_bytes: Mapped[int | None] = mapped_column(BigInteger)
    free_bytes: Mapped[int | None] = mapped_column(BigInteger)
    encrypted: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[str | None] = mapped_column(String(40))
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class HardwareGpu(Base):
    __tablename__ = "hardware_gpus"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hardware_id: Mapped[int] = mapped_column(ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(150))
    model: Mapped[str | None] = mapped_column(String(150))
    vendor: Mapped[str | None] = mapped_column(String(150))
    memory_bytes: Mapped[int | None] = mapped_column(BigInteger)
    driver_version: Mapped[str | None] = mapped_column(String(100))
    device_id: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class OperatingSystem(Base):
    __tablename__ = "operating_systems"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(150))
    version: Mapped[str | None] = mapped_column(String(100))
    edition: Mapped[str | None] = mapped_column(String(100))
    build: Mapped[str | None] = mapped_column(String(100))
    architecture: Mapped[str | None] = mapped_column(String(50))
    kernel: Mapped[str | None] = mapped_column(String(150))
    install_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_boot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hostname: Mapped[str | None] = mapped_column(String(255))
    computer_name: Mapped[str | None] = mapped_column(String(255))
    license_status: Mapped[str | None] = mapped_column(String(50))
    activation_status: Mapped[str | None] = mapped_column(String(50))
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Software(Base):
    __tablename__ = "software"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    homepage: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("name", "publisher"), Index("ix_software_name", "name"))


class AssetSoftware(Base):
    __tablename__ = "asset_software"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    software_id: Mapped[int] = mapped_column(ForeignKey("software.id", ondelete="RESTRICT"), nullable=False)
    version: Mapped[str | None] = mapped_column(String(150))
    edition: Mapped[str | None] = mapped_column(String(100))
    architecture: Mapped[str | None] = mapped_column(String(50))
    install_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    install_location: Mapped[str | None] = mapped_column(String(500))
    uninstall_string: Mapped[str | None] = mapped_column(Text)
    discovery_source: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="INSTALLED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("asset_id", "software_id", "version"), Index("ix_asset_software_asset", "asset_id"))


class ServiceDefinition(Base):
    __tablename__ = "service_definitions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    publisher: Mapped[str | None] = mapped_column(String(200))
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    service_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("platform", "name"),)


class AssetService(Base):
    __tablename__ = "asset_services"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    service_definition_id: Mapped[int | None] = mapped_column(ForeignKey("service_definitions.id", ondelete="RESTRICT"))
    service_name: Mapped[str] = mapped_column(String(150), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(40))
    startup_type: Mapped[str | None] = mapped_column(String(40))
    account: Mapped[str | None] = mapped_column(String(255))
    process_id: Mapped[int | None] = mapped_column(Integer)
    port: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("asset_id", "service_name"), Index("ix_asset_services_status", "status"))


class AssetRelationship(Base):
    __tablename__ = "asset_relationships"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parent_asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    child_asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("parent_asset_id", "child_asset_id", "relationship_type"),)
