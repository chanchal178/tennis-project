"""
ETL Pipeline for Tennis Competitor Rankings.
Extracts doubles / singles competitor rankings from Sportradar API,
normalizes competitors and rankings, and loads them with safe upserts and FK order.
"""

import logging
from typing import Tuple, Dict, Any, List
from datetime import datetime
from sqlalchemy import text
from db import engine
from api_client import SportradarTennisAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_rankings_data() -> Tuple[bool, Dict[str, Any], str, bool]:
    """Extracts raw rankings data from Sportradar API or reference dataset."""
    client = SportradarTennisAPI()
    return client.fetch_doubles_rankings()

def transform_rankings(raw_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Transforms raw rankings into Competitors and Competitor_Rankings tables."""
    competitors_dict: Dict[str, Dict[str, Any]] = {}
    rankings_list: List[Dict[str, Any]] = []

    ranking_groups = raw_data.get("rankings", [])
    now_ts = datetime.utcnow()

    for group in ranking_groups:
        ranking_type = group.get("type", "doubles")
        comp_rankings = group.get("competitor_rankings", [])

        for entry in comp_rankings:
            competitor = entry.get("competitor", {})
            comp_id = competitor.get("id")
            comp_name = competitor.get("name")

            if not comp_id or not comp_name:
                continue

            # Upsert into competitors_dict
            if comp_id not in competitors_dict:
                competitors_dict[comp_id] = {
                    "id": comp_id,
                    "name": comp_name,
                    "country": competitor.get("country", "Unknown"),
                    "country_code": competitor.get("country_code", "UNK"),
                    "abbreviation": competitor.get("abbreviation"),
                    "gender": competitor.get("gender", "unspecified")
                }

            # Generate stable primary key for ranking record (e.g. compId_type)
            ranking_id = f"{comp_id}_{ranking_type}"

            rankings_list.append({
                "id": ranking_id,
                "competitor_id": comp_id,
                "rank": int(entry.get("rank", 9999)),
                "movement": int(entry.get("movement", 0)),
                "points": int(entry.get("points", 0)),
                "competitions_played": int(entry.get("competitions_played", 0)),
                "ranking_type": ranking_type,
                "updated_at": now_ts
            })

    return list(competitors_dict.values()), rankings_list

def load_rankings(competitors: List[Dict[str, Any]], rankings: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Loads competitors and rankings into the database idempotently."""
    loaded_competitors = 0
    loaded_rankings = 0

    with engine.begin() as conn:
        # 1. Upsert Competitors
        for comp in competitors:
            existing = conn.execute(
                text("SELECT id FROM Competitors WHERE id = :id"),
                {"id": comp["id"]}
            ).fetchone()

            if existing:
                conn.execute(
                    text("""
                        UPDATE Competitors 
                        SET name = :name, country = :country, country_code = :country_code,
                            abbreviation = :abbreviation, gender = :gender
                        WHERE id = :id
                    """),
                    comp
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO Competitors (id, name, country, country_code, abbreviation, gender)
                        VALUES (:id, :name, :country, :country_code, :abbreviation, :gender)
                    """),
                    comp
                )
            loaded_competitors += 1

        # 2. Upsert Competitor_Rankings
        for rk in rankings:
            existing = conn.execute(
                text("SELECT id FROM Competitor_Rankings WHERE id = :id"),
                {"id": rk["id"]}
            ).fetchone()

            if existing:
                conn.execute(
                    text("""
                        UPDATE Competitor_Rankings 
                        SET rank = :rank, movement = :movement, points = :points,
                            competitions_played = :competitions_played, ranking_type = :ranking_type,
                            updated_at = :updated_at
                        WHERE id = :id
                    """),
                    rk
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO Competitor_Rankings 
                        (id, competitor_id, rank, movement, points, competitions_played, ranking_type, updated_at)
                        VALUES 
                        (:id, :competitor_id, :rank, :movement, :points, :competitions_played, :ranking_type, :updated_at)
                    """),
                    rk
                )
            loaded_rankings += 1

    return loaded_competitors, loaded_rankings

def run_rankings_etl() -> Dict[str, Any]:
    """Main execution function for Rankings ETL."""
    logger.info("Starting Competitor Rankings ETL...")
    success, raw_data, msg, is_live = extract_rankings_data()
    if not success or not raw_data:
        logger.error(f"Failed extracting rankings: {msg}")
        return {"success": False, "message": msg, "competitors_loaded": 0, "rankings_loaded": 0, "is_live": is_live}

    competitors, rankings = transform_rankings(raw_data)
    c_loaded, r_loaded = load_rankings(competitors, rankings)

    logger.info(f"Rankings ETL completed: {c_loaded} competitors, {r_loaded} rankings.")
    return {
        "success": True,
        "message": f"Loaded {c_loaded} competitors and {r_loaded} rankings. ({msg})",
        "competitors_loaded": c_loaded,
        "rankings_loaded": r_loaded,
        "is_live": is_live
    }

if __name__ == "__main__":
    result = run_rankings_etl()
    print(result)
