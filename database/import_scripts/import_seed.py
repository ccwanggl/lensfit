"""Import seed data from CSV files into the database."""

from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from lensfit.db.models import (
    Base,
    DetectorCatalog,
    LensCatalog,
    Manufacturer,
)


def import_manufacturers(session: Session, csv_path: Path) -> dict[str, int]:
    """Import manufacturers and return name -> id mapping."""
    name_to_id = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = Manufacturer(
                name=row["name"],
                name_en=row.get("name_en") or None,
                name_cn=row.get("name_cn") or None,
                country=row.get("country") or None,
                website=row.get("website") or None,
                is_verified=bool(int(row.get("is_verified", "0"))),
                data_source="seed",
            )
            session.add(m)
            session.flush()
            name_to_id[row["name"]] = m.id
    session.commit()
    print(f"Imported {len(name_to_id)} manufacturers")
    return name_to_id


def import_lenses(session: Session, csv_path: Path) -> int:
    """Import lens catalog."""
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lens = LensCatalog(
                manufacturer_id=int(row["manufacturer_id"]),
                model=row["model"],
                category=row["category"],
                status=row.get("status", "active"),
                focal_length_mm=float(row["focal_length_mm"]) if row["focal_length_mm"] else None,
                max_aperture=float(row["max_aperture"]) if row["max_aperture"] else None,
                image_circle_mm=float(row["image_circle_mm"]) if row["image_circle_mm"] else None,
                min_working_distance_mm=float(row["min_working_distance_mm"]) if row["min_working_distance_mm"] else None,
                max_working_distance_mm=float(row["max_working_distance_mm"]) if row["max_working_distance_mm"] else None,
                mount_type=row.get("mount_type") or None,
                length_mm=float(row["length_mm"]) if row["length_mm"] else None,
                weight_g=float(row["weight_g"]) if row["weight_g"] else None,
                price_usd=float(row["price_usd"]) if row["price_usd"] else None,
                data_source="seed",
                data_quality_score=0.8,
                verified=True,
            )
            session.add(lens)
            count += 1
    session.commit()
    print(f"Imported {count} lenses")
    return count


def import_detectors(session: Session, csv_path: Path) -> int:
    """Import detector catalog."""
    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            det = DetectorCatalog(
                manufacturer_id=int(row["manufacturer_id"]),
                model=row["model"],
                category=row["category"],
                sensor_format_inch=row.get("sensor_format_inch") or None,
                sensor_w_mm=float(row["sensor_w_mm"]) if row["sensor_w_mm"] else None,
                sensor_h_mm=float(row["sensor_h_mm"]) if row["sensor_h_mm"] else None,
                sensor_diag_mm=float(row["sensor_diag_mm"]) if row["sensor_diag_mm"] else None,
                resolution_w=int(row["resolution_w"]) if row["resolution_w"] else None,
                resolution_h=int(row["resolution_h"]) if row["resolution_h"] else None,
                pixel_size_um=float(row["pixel_size_um"]) if row["pixel_size_um"] else None,
                mount_type=row.get("mount_type") or None,
                data_interface=row.get("data_interface") or None,
                max_fps_full=float(row["max_fps_full"]) if row["max_fps_full"] else None,
                price_usd=float(row["price_usd"]) if row["price_usd"] else None,
                data_source="seed",
                data_quality_score=0.8,
                verified=True,
            )
            session.add(det)
            count += 1
    session.commit()
    print(f"Imported {count} detectors")
    return count


def main(db_url: str = "sqlite:///lensfit.db") -> None:
    """Import all seed data."""
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)

    base_dir = Path(__file__).parent.parent
    seed_dir = base_dir / "seed_data"

    with Session(engine) as session:
        # Clear existing seed data
        session.query(LensCatalog).filter(LensCatalog.data_source == "seed").delete()
        session.query(DetectorCatalog).filter(DetectorCatalog.data_source == "seed").delete()
        session.query(Manufacturer).filter(Manufacturer.data_source == "seed").delete()

        # Reset SQLite auto-increment sequences so IDs start from 1
        session.execute(
            text(
                "DELETE FROM sqlite_sequence WHERE name IN "
                "('manufacturers', 'lens_catalog', 'detector_catalog')"
            )
        )
        session.commit()

        # Import in order: manufacturers -> lenses -> detectors
        import_manufacturers(session, seed_dir / "manufacturers.csv")
        import_lenses(session, seed_dir / "lenses.csv")
        import_detectors(session, seed_dir / "detectors.csv")

    print("Seed data import complete.")


if __name__ == "__main__":
    main()
