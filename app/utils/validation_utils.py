from typing import Optional
import re


VALID_ASSET_TYPES = {"road", "bridge", "pipeline", "drainage", "street_light", "public_facility"}
VALID_STATUSES = {"active", "inactive", "under_maintenance", "decommissioned"}
VALID_RISK_LEVELS = {"healthy", "warning", "critical"}


def validate_asset_type(asset_type: str) -> bool:
    return asset_type.lower() in VALID_ASSET_TYPES


def validate_status(status: str) -> bool:
    return status.lower() in VALID_STATUSES


def validate_coordinates(lat: float, lon: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lon <= 180


def validate_year(year: int) -> bool:
    return 1800 <= year <= 2100


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(value: str, max_length: int = 200) -> str:
    return value.strip()[:max_length] if value else ""
