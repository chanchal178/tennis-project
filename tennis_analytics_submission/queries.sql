-- ==============================================================================
-- Tennis Analytics: Standard Analytical Queries
-- Explanations provided in plain language for each analytical problem.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 1: Competitions by Category
-- Explanation: Groups all tennis tournaments by their parent category (e.g., ATP, WTA, ITF)
-- and returns the count of tournaments in each category, ordered highest to lowest.
-- ------------------------------------------------------------------------------
SELECT 
    COALESCE(cat.name, 'Uncategorized') AS category_name,
    COUNT(comp.id) AS total_competitions
FROM Competitions comp
LEFT JOIN Categories cat ON comp.category_id = cat.id
GROUP BY cat.name
ORDER BY total_competitions DESC;

-- ------------------------------------------------------------------------------
-- Query 2: Competition Counts by Gender and Type
-- Explanation: Breaks down tennis tournaments by gender classification (Men, Women, Mixed)
-- and competition format (Singles, Doubles), counting tournaments in each subset.
-- ------------------------------------------------------------------------------
SELECT 
    COALESCE(gender, 'Unspecified') AS competition_gender,
    COALESCE(type, 'Standard') AS competition_type,
    COUNT(id) AS competition_count
FROM Competitions
GROUP BY gender, type
ORDER BY competition_count DESC;

-- ------------------------------------------------------------------------------
-- Query 3: Venue Counts per Complex
-- Explanation: Lists all tennis complexes (facilities/parks) and calculates the total
-- number of individual venues or courts registered under each complex.
-- ------------------------------------------------------------------------------
SELECT 
    c.id AS complex_id,
    c.name AS complex_name,
    COUNT(v.id) AS total_venues
FROM Complexes c
LEFT JOIN Venues v ON c.id = v.complex_id
GROUP BY c.id, c.name
ORDER BY total_venues DESC, c.name ASC;

-- ------------------------------------------------------------------------------
-- Query 4: Competitor Counts by Country
-- Explanation: Aggregates tennis competitors based on their representing country
-- to identify which nations have the strongest athlete representation.
-- ------------------------------------------------------------------------------
SELECT 
    COALESCE(country, 'Unknown') AS country_name,
    country_code,
    COUNT(id) AS competitor_count
FROM Competitors
GROUP BY country, country_code
ORDER BY competitor_count DESC;

-- ------------------------------------------------------------------------------
-- Query 5: Top-Ranked Competitors by Points
-- Explanation: Retrieves the top 50 ranked competitors along with their rank, total
-- points, country representation, and ranking movement from the previous update.
-- ------------------------------------------------------------------------------
SELECT 
    r.rank,
    c.name AS competitor_name,
    COALESCE(c.country, 'N/A') AS country,
    c.country_code,
    r.points,
    r.movement,
    r.competitions_played,
    r.ranking_type
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
ORDER BY r.rank ASC
LIMIT 50;

-- ------------------------------------------------------------------------------
-- Query 6: Total Ranking Points by Country
-- Explanation: Sums all ranking points accumulated by competitors of each nation.
-- ------------------------------------------------------------------------------
SELECT 
    COALESCE(c.country, 'Unknown') AS country_name,
    SUM(r.points) AS total_ranking_points,
    COUNT(c.id) AS ranked_players_count
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
GROUP BY c.country
ORDER BY total_ranking_points DESC;

-- ------------------------------------------------------------------------------
-- Query 7: Average Ranking Points by Country (Min 1 Competitor)
-- Explanation: Computes the mean ranking points per competitor for countries,
-- highlighting countries with high-performing athletes on average.
-- ------------------------------------------------------------------------------
SELECT 
    COALESCE(c.country, 'Unknown') AS country_name,
    ROUND(AVG(r.points), 1) AS average_points,
    MAX(r.points) AS peak_points,
    COUNT(c.id) AS competitor_count
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
GROUP BY c.country
HAVING COUNT(c.id) >= 1
ORDER BY average_points DESC;

-- ------------------------------------------------------------------------------
-- Query 8: Ranking Movement Analysis
-- Explanation: Identifies biggest climbers (positive movement) and drops (negative
-- movement) in the rankings, showing athlete momentum.
-- ------------------------------------------------------------------------------
SELECT 
    c.name AS competitor_name,
    c.country,
    r.rank AS current_rank,
    r.movement AS rank_movement,
    r.points,
    CASE 
        WHEN r.movement > 0 THEN 'Climbed'
        WHEN r.movement < 0 THEN 'Dropped'
        ELSE 'Unchanged'
    END AS movement_trend
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
WHERE r.movement != 0
ORDER BY ABS(r.movement) DESC
LIMIT 25;
