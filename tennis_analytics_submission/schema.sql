-- ==============================================================================
-- Tennis Analytics Relational Database Schema
-- Compatible with PostgreSQL, MySQL, and SQLite
-- ==============================================================================

-- 1. Categories Table
CREATE TABLE IF NOT EXISTS Categories (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- 2. Competitions Table
CREATE TABLE IF NOT EXISTS Competitions (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id VARCHAR(64),
    gender VARCHAR(32),
    type VARCHAR(64),
    parent_id VARCHAR(64),
    FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE SET NULL
);

-- 3. Complexes Table
CREATE TABLE IF NOT EXISTS Complexes (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- 4. Venues Table
CREATE TABLE IF NOT EXISTS Venues (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    complex_id VARCHAR(64),
    city_name VARCHAR(255),
    country_name VARCHAR(255),
    country_code VARCHAR(16),
    timezone VARCHAR(64),
    FOREIGN KEY (complex_id) REFERENCES Complexes(id) ON DELETE SET NULL
);

-- 5. Competitors Table
CREATE TABLE IF NOT EXISTS Competitors (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255),
    country_code VARCHAR(16),
    abbreviation VARCHAR(32),
    gender VARCHAR(32)
);

-- 6. Competitor_Rankings Table
CREATE TABLE IF NOT EXISTS Competitor_Rankings (
    id VARCHAR(128) PRIMARY KEY,
    competitor_id VARCHAR(64) NOT NULL,
    rank INTEGER NOT NULL,
    movement INTEGER DEFAULT 0,
    points INTEGER NOT NULL,
    competitions_played INTEGER DEFAULT 0,
    ranking_type VARCHAR(64) DEFAULT 'doubles',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES Competitors(id) ON DELETE CASCADE
);

-- Indexes for Query Performance & Analytics
CREATE INDEX IF NOT EXISTS idx_comp_category ON Competitions(category_id);
CREATE INDEX IF NOT EXISTS idx_venue_complex ON Venues(complex_id);
CREATE INDEX IF NOT EXISTS idx_competitor_country ON Competitors(country);
CREATE INDEX IF NOT EXISTS idx_ranking_rank ON Competitor_Rankings(rank);
CREATE INDEX IF NOT EXISTS idx_ranking_points ON Competitor_Rankings(points);
CREATE INDEX IF NOT EXISTS idx_ranking_comp ON Competitor_Rankings(competitor_id);

-- Convenient View for Competitions with Category Name (Guarantees category_name is always present!)
CREATE VIEW IF NOT EXISTS v_competitions_expanded AS
SELECT 
    c.id,
    c.name,
    c.category_id,
    COALESCE(cat.name, 'Uncategorized') AS category_name,
    COALESCE(c.gender, 'All') AS gender,
    COALESCE(c.type, 'Standard') AS type,
    c.parent_id
FROM Competitions c
LEFT JOIN Categories cat ON c.category_id = cat.id;
