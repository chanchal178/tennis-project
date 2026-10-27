"""
ETL Pipeline for Tennis Categories & Competitions.
Extracts competition data from Sportradar API, normalizes categories and competitions,
and safely loads them into relational tables without duplication.
Guarantees category_name is always captured or gracefully defaulted.
"""

import logging
from typing import Tuple, Dict, Any, List
from sqlalchemy import text
from db import engine, SessionLocal
from api_client import SportradarTennisAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_competitions_data() -> Tuple[bool, Dict[str, Any], str, bool]:
    """Extracts raw competitions from Sportradar API or bundled reference dataset."""
    client = SportradarTennisAPI()
    return client.fetch_competitions()

def transform_competitions(raw_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Transforms API response into distinct Categories and Competitions records.
    Handles missing categories safely to prevent KeyError: 'category_name'.
    """
    categories_dict: Dict[str, str] = {
        "cat_uncategorized": "Uncategorized"
    }
    competitions: List[Dict[str, Any]] = []

    raw_comps = raw_data.get("competitions", [])
    for comp in raw_comps:
        comp_id = comp.get("id")
        comp_name = comp.get("name")
        if not comp_id or not comp_name:
            continue

        # Safely parse category object (prevents KeyError)
        category_obj = comp.get("category")
        if isinstance(category_obj, dict):
            cat_id = category_obj.get("id") or "cat_uncategorized"
            cat_name = category_obj.get("name") or "Uncategorized"
        else:
            cat_id = "cat_uncategorized"
            cat_name = "Uncategorized"

        categories_dict[cat_id] = cat_name

        competitions.append({
            "id": comp_id,
            "name": comp_name,
            "category_id": cat_id,
            "category_name": cat_name,  # preserved for easy inspection
            "gender": comp.get("gender", "unspecified"),
            "type": comp.get("type", "standard"),
            "parent_id": comp.get("parent_id")
        })

    categories_list = [{"id": cid, "name": cname} for cid, cname in categories_dict.items()]
    return categories_list, competitions

def load_competitions(categories: List[Dict[str, Any]], competitions: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Loads categories and competitions into the database.
    Performs safe upserts so multiple runs do not create duplicate records.
    """
    loaded_cats = 0
    loaded_comps = 0

    with engine.begin() as conn:
        # 1. Upsert Categories first to satisfy Foreign Key constraints
        for cat in categories:
            # Dialect-agnostic safe upsert: check then insert/update
            existing = conn.execute(
                text("SELECT id FROM Categories WHERE id = :id"),
                {"id": cat["id"]}
            ).fetchone()

            if existing:
                conn.execute(
                    text("UPDATE Categories SET name = :name WHERE id = :id"),
                    cat
                )
            else:
                conn.execute(
                    text("INSERT INTO Categories (id, name) VALUES (:id, :name)"),
                    cat
                )
            loaded_cats += 1

        # 2. Upsert Competitions
        for comp in competitions:
            existing = conn.execute(
                text("SELECT id FROM Competitions WHERE id = :id"),
                {"id": comp["id"]}
            ).fetchone()

            comp_params = {
                "id": comp["id"],
                "name": comp["name"],
                "category_id": comp["category_id"],
                "gender": comp.get("gender"),
                "type": comp.get("type"),
                "parent_id": comp.get("parent_id")
            }

            if existing:
                conn.execute(
                    text("""
                        UPDATE Competitions 
                        SET name = :name, category_id = :category_id, gender = :gender, 
                            type = :type, parent_id = :parent_id
                        WHERE id = :id
                    """),
                    comp_params
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO Competitions (id, name, category_id, gender, type, parent_id)
                        VALUES (:id, :name, :category_id, :gender, :type, :parent_id)
                    """),
                    comp_params
                )
            loaded_comps += 1

    return loaded_cats, loaded_comps

def run_competitions_etl() -> Dict[str, Any]:
    """Main execution function for Competitions ETL."""
    logger.info("Starting Competitions ETL...")
    success, raw_data, msg, is_live = extract_competitions_data()
    if not success or not raw_data:
        logger.error(f"Failed extracting competitions: {msg}")
        return {"success": False, "message": msg, "categories_loaded": 0, "competitions_loaded": 0, "is_live": is_live}

    categories, competitions = transform_competitions(raw_data)
    loaded_cats, loaded_comps = load_competitions(categories, competitions)

    logger.info(f"Competitions ETL completed: {loaded_cats} categories, {loaded_comps} competitions.")
    return {
        "success": True,
        "message": f"Loaded {loaded_cats} categories and {loaded_comps} competitions. ({msg})",
        "categories_loaded": loaded_cats,
        "competitions_loaded": loaded_comps,
        "is_live": is_live
    }

if __name__ == "__main__":
    result = run_competitions_etl()
    print(result)
