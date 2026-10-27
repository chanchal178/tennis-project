# Game Analytics: Unlocking Tennis Data with Sportradar API

> **College Project Submission**  
> **Course / Subject:** Database Management Systems & Applied Data Analytics  
> **Topic:** End-to-End Sports Analytics Dashboard using Sportradar Tennis API, Relational SQL Database, and Streamlit.

---

## 📌 Executive Summary & Architecture

The **Tennis Analytics Explorer** is a high-performance sports analytics solution engineered to ingest, model, query, and visualize global tennis tournament data and competitor doubles rankings.

```
+-----------------------------------+
|      Sportradar Tennis v3 API     |
|   (Competitions, Venues, Ranks)   |
+-----------------+-----------------+
                  | (HTTPS / JSON)
                  v
+-----------------+-----------------+
|      Python ETL Pipelines         |
|  - etl_competitions.py            |
|  - etl_complexes.py               |
|  - etl_rankings.py                |
+-----------------+-----------------+
                  | (SQLAlchemy 2.0 ORM)
                  v
+-----------------+-----------------+
| Relational Database (SQL)         |
| PostgreSQL / MySQL / SQLite       |
| 6 Tables + Views + Indexes        |
+-----------------+-----------------+
                  | (SQL Queries / Pandas)
                  v
+-----------------+-----------------+
|   Streamlit Analytics Dashboard   |
| 7 Pages, Plotly Charts, SQL Shell |
+-----------------------------------+
```

---

## 🛠️ Root Causes of Original Errors & Their Fixes

### 1. `ModuleNotFoundError: No module named 'sqlalchemy'`
- **Root Cause:** SQLAlchemy was missing from `requirements.txt` and the virtual environment was either not created or not activated in the Windows terminal before running `python run_etl.py`.
- **Permanent Fix:** Added `SQLAlchemy>=2.0.30` and database connectors (`psycopg2-binary`, `pymysql`, `cryptography`) to `requirements.txt`. Provided the explicit activation command `venv\Scripts\activate` in documentation.

### 2. Database Initialization Errors involving `.env` configuration & `python run_etl.py --init-db`
- **Root Cause:** 
  1. Missing or malformed `DATABASE_URL` in `.env` resulted in `sqlalchemy.exc.ArgumentError`.
  2. Running raw multi-statement DDL scripts with a single `conn.execute()` caused SQL syntax/delimiter errors across MySQL and PostgreSQL.
  3. No pre-flight database connection check existed before executing migrations.
- **Permanent Fix:** 
  1. Updated `config.py` with automatic connection string assembly and a safe fallback to SQLite for zero-setup local runs.
  2. `db.py`'s `init_db()` cleans and splits statements individually while respecting transactions.
  3. Added `python run_etl.py --test-conn` to diagnose connection health before table creation.

### 3. `KeyError: 'category_name'` in Competition Explorer
- **Root Cause:**
  1. In the Sportradar API response, certain competitions lack a nested `"category"` dictionary or have `"category": None`. Accessing `comp['category']['name']` or assuming `'category_name'` exists in raw dictionaries throws a Python `KeyError`.
  2. The database schema stores `category_id` in `Competitions`, while the human-readable name resides in `Categories.name`. When querying `SELECT * FROM Competitions`, the resulting DataFrame lacked a `category_name` column.
- **Permanent Fix:**
  1. In `etl_competitions.py`, category extraction uses `comp.get("category", {})` with fallback to `'Uncategorized'`.
  2. In `app.py` and `schema.sql`, `Competitions` is left-joined with `Categories`:
     ```sql
     SELECT c.*, COALESCE(cat.name, 'Uncategorized') AS category_name
     FROM Competitions c
     LEFT JOIN Categories cat ON c.category_id = cat.id;
     ```
  3. Created database view `v_competitions_expanded` guaranteeing `category_name` is always present.

---

## 🗄️ Relational Database Schema

The database design adheres to 3NF relational standards across 6 core tables:

1. **`Categories`**: `id` (PK), `name`
2. **`Competitions`**: `id` (PK), `name`, `category_id` (FK -> Categories.id), `gender`, `type`, `parent_id`
3. **`Complexes`**: `id` (PK), `name`
4. **`Venues`**: `id` (PK), `name`, `complex_id` (FK -> Complexes.id), `city_name`, `country_name`, `country_code`, `timezone`
5. **`Competitors`**: `id` (PK), `name`, `country`, `country_code`, `abbreviation`, `gender`
6. **`Competitor_Rankings`**: `id` (PK), `competitor_id` (FK -> Competitors.id), `rank`, `movement`, `points`, `competitions_played`, `ranking_type`, `updated_at`

---

## 💻 Local Setup Instructions (Windows / VS Code)

Follow these exact commands in **Command Prompt** or **PowerShell** inside VS Code:

### Step 1: Open Terminal in VS Code
Open VS Code, press ``Ctrl + ` `` to open the terminal, and navigate to the project root:
```cmd
cd tennis_analytics_submission
```

### Step 2: Create and Activate Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```
*(Your terminal prompt will now show `(venv)`)*

### Step 3: Upgrade pip and Install Dependencies
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```cmd
copy .env.example .env
```
Open `.env` in VS Code and set your database connection and Sportradar API key:
```ini
SPORTRADAR_API_KEY=your_actual_sportradar_api_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/tennis_analytics
```
*(Note: If you do not have PostgreSQL installed, set `DATABASE_URL=sqlite:///tennis_analytics.db` for instant zero-server setup).*

### Step 5: Test Connection and Initialize Database
```cmd
python run_etl.py --test-conn
python run_etl.py --init-db
```

### Step 6: Ingest Data via ETL Pipeline
```cmd
python run_etl.py --all
```

### Step 7: Launch the Streamlit Dashboard
```cmd
streamlit run app.py
```
Your default browser will automatically open `http://localhost:8501`.

---

## 🧪 Running Automated Unit Tests

Execute the comprehensive test suite using `pytest`:
```cmd
pytest -v tests/test_tennis_analytics.py
```
All tests verify:
- Safe handling of missing category names (`KeyError` prevention)
- Schema normalization for complexes and venues
- Correct doubles rankings extraction
- Empty response resilience
- Read-only security enforcement of the SQL console (blocking `DROP`, `DELETE`, `INSERT`)

---

## ☁️ Streamlit Community Cloud Deployment

1. Push your repository to **GitHub** (ensure `.env` and `venv/` are in `.gitignore`).
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **New app** and select your GitHub repository and `app.py`.
4. In **Advanced settings**, add your **Secrets**:
   ```toml
   SPORTRADAR_API_KEY = "your_key"
   DATABASE_URL = "postgresql://user:pass@your-cloud-db-host:5432/tennis_analytics"
   ```
5. Click **Deploy!**

---

## 📸 Screenshot Verification Checklist
- [x] **Hero Banner & KPIs:** Competitors, Competitions, Venues, Countries, Max Points
- [x] **Competition Explorer:** Tournament table with Category and Gender filters
- [x] **Venues & Complexes:** Relational courts table and Venues per Complex bar chart
- [x] **Competitor Search:** Search input by name and expandable stat cards
- [x] **Country Analysis:** Top countries bar charts and summary table
- [x] **Leaderboards:** Podium 1-2-3 cards, sortable table, and CSV download
- [x] **SQL Query Console:** Predefined queries dropdown, safe editor, and result table
