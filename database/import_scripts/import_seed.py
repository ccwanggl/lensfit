"""Import seed data from CSV files into the database."""

from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from optibench.db.models import (
    DetectorCatalog,
    LensCatalog,
    Manufacturer,
    init_db,
)


def _seed_csv_files(seed_dir: Path, prefix: str) -> list[Path]:
    """Return all seed CSV files matching prefix (e.g. lenses*.csv)."""
    files = sorted(seed_dir.glob(f"{prefix}*.csv"))
    # Ensure the legacy base files come first if they exist
    base = seed_dir / f"{prefix}.csv"
    if base in files:
        files.remove(base)
        files.insert(0, base)
    return files


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


def _float(value: str) -> float | None:
    """Parse a CSV string to float, returning None for empty values."""
    return float(value) if value else None


def _int(value: str) -> int | None:
    """Parse a CSV string to int, returning None for empty values."""
    return int(value) if value else None


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
                focal_length_mm=_float(row.get("focal_length_mm")),
                focal_length_min=_float(row.get("focal_length_min")),
                focal_length_max=_float(row.get("focal_length_max")),
                max_aperture=_float(row.get("max_aperture")),
                min_aperture=_float(row.get("min_aperture")),
                image_circle_mm=_float(row.get("image_circle_mm")),
                min_working_distance_mm=_float(row.get("min_working_distance_mm")),
                max_working_distance_mm=_float(row.get("max_working_distance_mm")),
                nominal_wd_mm=_float(row.get("nominal_wd_mm")),
                mount_type=row.get("mount_type") or None,
                length_mm=_float(row.get("length_mm")),
                weight_g=_float(row.get("weight_g")),
                price_usd=_float(row.get("price_usd")),
                na=_float(row.get("na")),
                wavelength_min_nm=_int(row.get("wavelength_min_nm")),
                wavelength_max_nm=_int(row.get("wavelength_max_nm")),
                distortion_percent=_float(row.get("distortion_percent")),
                mtf50_lpmm=_float(row.get("mtf50_lpmm")),
                data_source="seed",
                data_quality_score=0.8,
                verified=True,
            )
            session.add(lens)
            count += 1
    session.commit()
    print(f"Imported {count} lenses from {csv_path.name}")
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
                sensor_w_mm=_float(row.get("sensor_w_mm")),
                sensor_h_mm=_float(row.get("sensor_h_mm")),
                sensor_diag_mm=_float(row.get("sensor_diag_mm")),
                resolution_w=_int(row.get("resolution_w")),
                resolution_h=_int(row.get("resolution_h")),
                pixel_size_um=_float(row.get("pixel_size_um")),
                mount_type=row.get("mount_type") or None,
                data_interface=row.get("data_interface") or None,
                max_fps_full=_float(row.get("max_fps_full")),
                price_usd=_float(row.get("price_usd")),
                netd_mk=_float(row.get("netd_mk")),
                spectral_range_min_um=_float(row.get("spectral_range_min_um")),
                spectral_range_max_um=_float(row.get("spectral_range_max_um")),
                data_source="seed",
                data_quality_score=0.8,
                verified=True,
            )
            session.add(det)
            count += 1
    session.commit()
    print(f"Imported {count} detectors from {csv_path.name}")
    return count


def main(db_url: str = "sqlite:///optibench.db") -> None:
    """Import all seed data."""
    # 通过 Alembic 迁移创建/更新 schema，保证与模型一致
    init_db(db_url)

    engine = create_engine(db_url, echo=False)

    base_dir = Path(__file__).parent.parent
    seed_dir = base_dir / "seed_data"

    with Session(engine) as session:
        # Clear all catalog data so seed IDs remain deterministic and imports
        # are reproducible. Compatibility cache is also cleared because it
        # references lens/detector IDs.
        session.execute(text("DELETE FROM compatibility_cache"))
        session.execute(text("DELETE FROM detector_catalog"))
        session.execute(text("DELETE FROM lens_catalog"))
        session.query(Manufacturer).filter(Manufacturer.data_source == "seed").delete()
        session.commit()

        # Reset SQLite auto-increment sequences so IDs start from 1.
        # sqlite_sequence only exists after rows have been inserted, so ignore
        # the error on a fresh database.
        try:
            session.execute(
                text(
                    "DELETE FROM sqlite_sequence WHERE name IN "
                    "('manufacturers', 'lens_catalog', 'detector_catalog', 'compatibility_cache')"
                )
            )
            session.commit()
        except Exception:
            session.rollback()

        # Import in order: manufacturers -> lenses -> detectors
        import_manufacturers(session, seed_dir / "manufacturers.csv")
        for lens_csv in _seed_csv_files(seed_dir, "lenses"):
            import_lenses(session, lens_csv)
        for det_csv in _seed_csv_files(seed_dir, "detectors"):
            import_detectors(session, det_csv)

    print("Seed data import complete.")


if __name__ == "__main__":
    main()
