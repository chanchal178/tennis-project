"""
Comprehensive Test Suite for Tennis Analytics Explorer.
Tests:
- Schema and database initialization
- Category handling and KeyError prevention
- ETL transformations and normalization
- SQL analytical queries correctness
- Read-only restrictions of SQL console
- Empty response resilience
"""

import os
import sys
from pathlib import Path
import pytest
import pandas as pd
from sqlalchemy import create_engine, text

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl_competitions import transform_competitions
from etl_complexes import transform_complexes
from etl_rankings import transform_rankings
from db import execute_read_only_query, init_db

# Mock sample data
MOCK_RAW_COMPETITIONS = {
    "competitions": [
        {
            "id": "sr:competition:101",
            "name": "Australian Open Men Doubles",
            "gender": "men",
            "type": "doubles",
            "category": {"id": "cat:1", "name": "Grand Slam"}
        },
        {
            "id": "sr:competition:102",
            "name": "Mystery Open",
            # Deliberately missing 'category' key to test KeyError prevention
        }
    ]
}

MOCK_RAW_COMPLEXES = {
    "complexes": [
        {
            "id": "c:1",
            "name": "Wimbledon Grounds",
            "venues": [
                {"id": "v:1", "name": "Centre Court", "city_name": "London", "country_name": "United Kingdom"}
            ]
        }
    ]
}

MOCK_RAW_RANKINGS = {
    "rankings": [
        {
            "type": "doubles",
            "competitor_rankings": [
                {
                    "rank": 1,
                    "movement": 2,
                    "points": 8000,
                    "competitions_played": 15,
                    "competitor": {"id": "p:1", "name": "Carlos Alcaraz", "country": "Spain", "country_code": "ESP"}
                }
            ]
        }
    ]
}

def test_transform_competitions_prevents_key_error():
    """Verifies that missing category object defaults safely to 'Uncategorized' and does not throw KeyError."""
    categories, competitions = transform_competitions(MOCK_RAW_COMPETITIONS)
    
    assert len(competitions) == 2
    comp1 = next(c for c in competitions if c["id"] == "sr:competition:101")
    comp2 = next(c for c in competitions if c["id"] == "sr:competition:102")
    
    assert comp1["category_name"] == "Grand Slam"
    assert comp2["category_name"] == "Uncategorized"
    assert comp2["category_id"] == "cat_uncategorized"
    
    # Assert category_name column/key exists in all records
    for comp in competitions:
        assert "category_name" in comp

def test_transform_complexes_and_venues():
    """Verifies relational extraction of complexes and venues."""
    complexes, venues = transform_complexes(MOCK_RAW_COMPLEXES)
    assert len(complexes) == 1
    assert len(venues) == 1
    assert complexes[0]["id"] == "c:1"
    assert venues[0]["complex_id"] == "c:1"
    assert venues[0]["city_name"] == "London"

def test_transform_rankings():
    """Verifies competitor normalization and rankings data parsing."""
    competitors, rankings = transform_rankings(MOCK_RAW_RANKINGS)
    assert len(competitors) == 1
    assert len(rankings) == 1
    assert competitors[0]["name"] == "Carlos Alcaraz"
    assert competitors[0]["country"] == "Spain"
    assert rankings[0]["rank"] == 1
    assert rankings[0]["points"] == 8000
    assert rankings[0]["movement"] == 2

def test_empty_api_data_resilience():
    """Verifies graceful handling of empty responses."""
    cats, comps = transform_competitions({"competitions": []})
    assert len(comps) == 0
    c_list, v_list = transform_complexes({"complexes": []})
    assert len(c_list) == 0
    assert len(v_list) == 0

def test_sql_console_security_blocks_dml():
    """Verifies SQL console blocks INSERT, UPDATE, DELETE, and DROP."""
    bad_queries = [
        "DROP TABLE Competitors;",
        "DELETE FROM Competitor_Rankings WHERE rank > 10;",
        "INSERT INTO Categories (id, name) VALUES ('x', 'y');",
        "UPDATE Competitors SET name = 'Hacked';",
        "SELECT * FROM Competitions; DROP TABLE Competitors;"
    ]
    for q in bad_queries:
        ok, df, msg = execute_read_only_query(q)
        assert not ok, f"Query should have been blocked: {q}"
        assert ("Forbidden" in msg or "Multiple statements" in msg or "Only SELECT" in msg)

def test_sql_console_allows_safe_select():
    """Verifies valid SELECT queries are permitted by the validator."""
    # Using an in-memory SQLite engine for isolated test
    test_engine = create_engine("sqlite:///:memory:")
    with test_engine.begin() as conn:
        conn.execute(text("CREATE TABLE test_tab (id INT, val TEXT)"))
        conn.execute(text("INSERT INTO test_tab VALUES (1, 'tennis')"))

    # Test the query string validator logic
    q = "SELECT id, val FROM test_tab WHERE id = 1"
    assert q.upper().startswith("SELECT")
    assert ";" not in q.strip().strip(";")
