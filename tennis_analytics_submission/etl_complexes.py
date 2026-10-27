"""
ETL Pipeline for Tennis Complexes & Venues.
Extracts tennis complex structures from Sportradar API, normalizes complexes and venues,
and loads them into relational tables with safe foreign keys and idempotent upserts.
"""

import logging
from typing import Tuple, Dict, Any, List
from sqlalchemy import text
from db import engine
from api_client import SportradarTennisAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_complexes_data() -> Tuple[bool, Dict[str, Any], str, bool]:
    """Extracts raw complexes data from Sportradar API or reference dataset."""
    client = SportradarTennisAPI()
    return client.fetch_complexes()

def transform_complexes(raw_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Transforms complexes and nested venues into clean tabular records."""
    complexes: List[Dict[str, Any]] = []
    venues: List[Dict[str, Any]] = []

    raw_complex_list = raw_data.get("complexes", [])
    for comp in raw_complex_list:
        comp_id = comp.get("id")
        comp_name = comp.get("name")
        if not comp_id or not comp_name:
            continue

        complexes.append({
            "id": comp_id,
            "name": comp_name
        })

        raw_venues = comp.get("venues", [])
        for v in raw_venues:
            v_id = v.get("id")
            v_name = v.get("name")
            if not v_id or not v_name:
                continue

            venues.append({
                "id": v_id,
                "name": v_name,
                "complex_id": comp_id,
                "city_name": v.get("city_name") or (v.get("city", {}).get("name") if isinstance(v.get("city"), dict) else None),
                "country_name": v.get("country_name") or (v.get("country", {}).get("name") if isinstance(v.get("country"), dict) else None),
                "country_code": v.get("country_code") or (v.get("country", {}).get("code") if isinstance(v.get("country"), dict) else None),
                "timezone": v.get("timezone")
            })

    return complexes, venues

def load_complexes(complexes: List[Dict[str, Any]], venues: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Loads complexes and venues with safe upserts and FK order."""
    loaded_complexes = 0
    loaded_venues = 0

    with engine.begin() as conn:
        # 1. Upsert Complexes
        for comp in complexes:
            existing = conn.execute(
                text("SELECT id FROM Complexes WHERE id = :id"),
                {"id": comp["id"]}
            ).fetchone()

            if existing:
                conn.execute(
                    text("UPDATE Complexes SET name = :name WHERE id = :id"),
                    comp
                )
            else:
                conn.execute(
                    text("INSERT INTO Complexes (id, name) VALUES (:id, :name)"),
                    comp
                )
            loaded_complexes += 1

        # 2. Upsert Venues
        for venue in venues:
            existing = conn.execute(
                text("SELECT id FROM Venues WHERE id = :id"),
                {"id": venue["id"]}
            ).fetchone()

            if existing:
                conn.execute(
                    text("""
                        UPDATE Venues 
                        SET name = :name, complex_id = :complex_id, city_name = :city_name,
                            country_name = :country_name, country_code = :country_code, timezone = :timezone
                        WHERE id = :id
                    """),
                    venue
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO Venues (id, name, complex_id, city_name, country_name, country_code, timezone)
                        VALUES (:id, :name, :complex_id, :city_name, :country_name, :country_code, :timezone)
                    """),
                    venue
                )
            loaded_venues += 1

    return loaded_complexes, loaded_venues

def run_complexes_etl() -> Dict[str, Any]:
    """Main execution function for Complexes & Venues ETL."""
    logger.info("Starting Complexes & Venues ETL...")
    success, raw_data, msg, is_live = extract_complexes_data()
    if not success or not raw_data:
        logger.error(f"Failed extracting complexes: {msg}")
        return {"success": False, "message": msg, "complexes_loaded": 0, "venues_loaded": 0, "is_live": is_live}

    complexes, venues = transform_complexes(raw_data)
    c_loaded, v_loaded = load_complexes(complexes, venues)

    logger.info(f"Complexes ETL completed: {c_loaded} complexes, {v_loaded} venues.")
    return {
        "success": True,
        "message": f"Loaded {c_loaded} complexes and {v_loaded} venues. ({msg})",
        "complexes_loaded": c_loaded,
        "venues_loaded": v_loaded,
        "is_live": is_live
    }

if __name__ == "__main__":
    result = run_complexes_etl()
    print(result)
