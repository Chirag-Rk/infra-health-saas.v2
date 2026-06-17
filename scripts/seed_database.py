"""
Database Seed Script
====================
Populates the Urban Infrastructure Portal with realistic sample data
for a fictional city (Metropolis City, lat/lon centered around 40.7, -74.0).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta, datetime
import random
from app.database import SessionLocal, init_db
from app.models.asset_model import InfrastructureAsset
from app.models.maintenance_model import MaintenanceLog, CitizenReport
from app.models.connection_model import AssetConnection
from app.models.user_model import User
from app.services.health_engine import calculate_health_score

random.seed(42)

CITY_CENTER_LAT = 40.7128
CITY_CENTER_LON = -74.0060

ASSET_CONFIGS = [
    # (name, type, department, lat_offset, lon_offset, year, status)
    ("Main Street Bridge", "bridge", "Public Works", 0.02, 0.01, 1985, "active"),
    ("Harbor Tunnel Road", "road", "Transportation", -0.01, 0.03, 1998, "active"),
    ("North Water Pipeline", "pipeline", "Water Authority", 0.03, -0.02, 2001, "active"),
    ("Central Drainage System", "drainage", "Stormwater Dept", -0.02, -0.01, 1992, "active"),
    ("Downtown Street Lights Cluster", "street_light", "City Electric", 0.005, 0.005, 2015, "active"),
    ("Central Library", "public_facility", "Community Services", 0.01, 0.01, 2005, "active"),
    ("Riverside Bridge", "bridge", "Public Works", 0.04, 0.02, 1972, "active"),
    ("Industrial Zone Road", "road", "Transportation", -0.03, 0.04, 2003, "active"),
    ("South Gas Pipeline", "pipeline", "Gas Authority", -0.04, -0.03, 1995, "active"),
    ("West Side Drain Network", "drainage", "Stormwater Dept", 0.03, -0.04, 2008, "active"),
    ("Park Avenue Lights", "street_light", "City Electric", 0.015, 0.015, 2018, "active"),
    ("City Hospital", "public_facility", "Health Dept", -0.015, 0.02, 2010, "active"),
    ("Old Mill Bridge", "bridge", "Public Works", -0.05, -0.02, 1965, "under_maintenance"),
    ("Eastern Bypass Road", "road", "Transportation", 0.05, 0.05, 2012, "active"),
    ("Metro Water Main", "pipeline", "Water Authority", 0.01, -0.05, 1988, "active"),
    ("Northside Culvert", "drainage", "Stormwater Dept", -0.06, 0.01, 1978, "active"),
    ("Market District Lights", "street_light", "City Electric", 0.02, 0.025, 2020, "active"),
    ("City Hall", "public_facility", "Administration", 0.008, -0.008, 1990, "active"),
    ("Greenway Pedestrian Bridge", "bridge", "Parks Dept", -0.02, 0.05, 2019, "active"),
    ("Freight Road South", "road", "Transportation", -0.07, -0.05, 1999, "active"),
]

INSPECTORS = ["James Carter", "Maria Rodriguez", "David Kim", "Sarah Thompson", "Robert Chen", "Lisa Patel"]
DAMAGE_NOTES = [
    "Minor surface cracking detected on north face.",
    "Structural supports showing early corrosion.",
    "Significant pothole formation across two lanes.",
    "Drainage blockage causing surface pooling.",
    "Wiring damage in 3 lamp posts, immediate fix applied.",
    "Routine inspection — all systems nominal.",
    "Concrete spalling on underside of deck.",
    "Pipe joint leakage detected in section B.",
    "Tree root intrusion causing pipe deformation.",
    "Steel rebar exposure after erosion, critical repair needed.",
]
MAINTENANCE_ACTIONS = [
    "Patched cracks with epoxy injection.",
    "Replaced corroded bolts and applied rust inhibitor.",
    "Filled potholes with hot-mix asphalt.",
    "Cleared blockage using hydro-jetting equipment.",
    "Replaced faulty lamp posts (3 units).",
    "Standard lubrication and safety inspection.",
    "Applied protective coating to concrete surfaces.",
    "Replaced pipe joint O-rings and resealed.",
    "Root barrier installed and pipe relaid.",
    "Emergency concrete patch and rebar protection applied.",
]
REPORT_TYPES = ["pothole", "crack", "flooding", "outage", "structural"]
REPORT_DESCRIPTIONS = [
    "Large pothole causing vehicle damage on main stretch.",
    "Visible cracks along the railing — safety concern.",
    "Water pooling after light rain, drain appears blocked.",
    "Several street lights non-functional since last week.",
    "Bridge supports look damaged, concrete chunks visible.",
    "Road surface breaking apart near junction.",
    "Flooding near underpass during heavy rain.",
    "Pipe leaking in residential area.",
]


def random_date(start_year: int, end_year: int) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed_users(db):
    users = [
        User(name="Admin User", email="admin@metropolis.gov", role="admin"),
        User(name="Chief Engineer", email="engineer@metropolis.gov", role="engineer"),
        User(name="Field Inspector", email="inspector@metropolis.gov", role="inspector"),
        User(name="Public Viewer", email="viewer@metropolis.gov", role="viewer"),
    ]
    for u in users:
        db.add(u)
    db.commit()
    print(f"  ✓ Seeded {len(users)} users")


def seed_assets(db) -> list:
    assets = []
    for i, (name, atype, dept, dlat, dlon, year, sts) in enumerate(ASSET_CONFIGS):
        lat = round(CITY_CENTER_LAT + dlat + random.uniform(-0.002, 0.002), 6)
        lon = round(CITY_CENTER_LON + dlon + random.uniform(-0.002, 0.002), 6)

        # Randomize last inspection date
        if year < 1990:
            last_insp = random_date(2021, 2023)
        elif year < 2005:
            last_insp = random_date(2022, 2024)
        else:
            last_insp = random_date(2023, 2025)

        asset = InfrastructureAsset(
            asset_name=name,
            asset_type=atype,
            department=dept,
            latitude=lat,
            longitude=lon,
            installation_year=year,
            status=sts,
            last_inspection_date=last_insp,
            health_score=0.0,
            risk_level="healthy"
        )
        db.add(asset)
        assets.append(asset)

    db.commit()
    for a in assets:
        db.refresh(a)
    print(f"  ✓ Seeded {len(assets)} infrastructure assets")
    return assets


def seed_maintenance_logs(db, assets: list):
    total_logs = 0
    for asset in assets:
        num_logs = random.randint(1, 6)
        for _ in range(num_logs):
            log_year_start = asset.installation_year + 2
            log_year_end = 2025
            if log_year_start >= log_year_end:
                log_year_start = log_year_end - 1

            log = MaintenanceLog(
                asset_id=asset.id,
                inspection_date=random_date(log_year_start, log_year_end),
                inspector=random.choice(INSPECTORS),
                condition_notes=random.choice(DAMAGE_NOTES),
                damage_level=round(random.uniform(0.5, 9.5), 1) if asset.installation_year < 2000
                             else round(random.uniform(0.0, 5.0), 1),
                maintenance_action=random.choice(MAINTENANCE_ACTIONS),
            )
            db.add(log)
            total_logs += 1

            # Update last inspection date on asset
            if asset.last_inspection_date is None or log.inspection_date > asset.last_inspection_date:
                asset.last_inspection_date = log.inspection_date

    db.commit()
    print(f"  ✓ Seeded {total_logs} maintenance logs")


def seed_citizen_reports(db, assets: list):
    total_reports = 0
    for asset in random.sample(assets, k=int(len(assets) * 0.7)):
        num_reports = random.randint(0, 4)
        for _ in range(num_reports):
            report = CitizenReport(
                asset_id=asset.id,
                report_type=random.choice(REPORT_TYPES),
                description=random.choice(REPORT_DESCRIPTIONS),
                location=f"Near {asset.asset_name}",
                severity=random.choice(["low", "low", "medium", "high"]),
                timestamp=datetime(
                    random.randint(2022, 2025),
                    random.randint(1, 12),
                    random.randint(1, 28)
                )
            )
            db.add(report)
            total_reports += 1
    db.commit()
    print(f"  ✓ Seeded {total_reports} citizen reports")


def seed_connections(db, assets: list):
    # Define infrastructure dependency connections
    connection_pairs = [
        (0, 1, "structural"),    # Main Street Bridge → Harbor Tunnel Road
        (6, 7, "structural"),    # Riverside Bridge → Industrial Zone Road
        (2, 1, "feeds_into"),    # North Water Pipeline → Harbor Tunnel Road
        (3, 1, "adjacent"),      # Central Drainage → Harbor Tunnel Road
        (3, 7, "adjacent"),      # Central Drainage → Industrial Zone Road
        (8, 7, "feeds_into"),    # South Gas Pipeline → Industrial Zone Road
        (12, 13, "structural"),  # Old Mill Bridge → Eastern Bypass Road
        (14, 13, "feeds_into"),  # Metro Water Main → Eastern Bypass Road
        (15, 13, "adjacent"),    # Northside Culvert → Eastern Bypass Road
        (9, 13, "adjacent"),     # West Side Drain → Eastern Bypass Road
        (0, 5, "adjacent"),      # Main Street Bridge → Central Library
        (11, 1, "adjacent"),     # City Hospital → Harbor Tunnel Road
        (17, 1, "adjacent"),     # City Hall → Harbor Tunnel Road
        (18, 13, "structural"),  # Greenway Bridge → Freight Road
    ]

    total_conn = 0
    for src_idx, dst_idx, ctype in connection_pairs:
        if src_idx < len(assets) and dst_idx < len(assets):
            conn = AssetConnection(
                asset_id=assets[src_idx].id,
                connected_asset_id=assets[dst_idx].id,
                connection_type=ctype
            )
            db.add(conn)
            total_conn += 1

    db.commit()
    print(f"  ✓ Seeded {total_conn} asset connections")


def recalculate_all_health_scores(db, assets: list):
    for asset in assets:
        logs = [l for l in db.query(MaintenanceLog).filter(MaintenanceLog.asset_id == asset.id).all()]
        reports = [r for r in db.query(CitizenReport).filter(CitizenReport.asset_id == asset.id).all()]

        damage_levels = [l.damage_level for l in logs if l.damage_level is not None]
        maintenance_dates = [l.inspection_date for l in logs if l.inspection_date]

        result = calculate_health_score(
            installation_year=asset.installation_year,
            asset_type=asset.asset_type,
            last_inspection_date=asset.last_inspection_date,
            damage_levels=damage_levels,
            citizen_report_count=len(reports),
            maintenance_dates=maintenance_dates
        )
        asset.health_score = result["health_score"]
        asset.risk_level = result["risk_level"]

    db.commit()
    print(f"  ✓ Recalculated health scores for {len(assets)} assets")


def main():
    print("\n Urban Infrastructure Portal - Database Seeder")
    print("=" * 52)
    init_db()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(CitizenReport).delete()
        db.query(MaintenanceLog).delete()
        db.query(AssetConnection).delete()
        db.query(InfrastructureAsset).delete()
        db.query(User).delete()
        db.commit()
        print("  ✓ Cleared existing data")

        seed_users(db)
        assets = seed_assets(db)
        seed_maintenance_logs(db, assets)
        seed_citizen_reports(db, assets)
        seed_connections(db, assets)
        recalculate_all_health_scores(db, assets)

        print("\n Seeding complete!")
        print(f"   Total assets: {len(assets)}")

        healthy = sum(1 for a in assets if a.risk_level == "healthy")
        warning = sum(1 for a in assets if a.risk_level == "warning")
        critical = sum(1 for a in assets if a.risk_level == "critical")
        print(f"   Healthy: {healthy} | Warning: {warning} | Critical: {critical}")
        print("\n   Run the API: uvicorn app.main:app --reload")
        print("   Run the UI:  streamlit run frontend/streamlit_app.py\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
