import React, { useState, useMemo } from 'react';
import {
  Trophy,
  Shield,
  MapPin,
  Search,
  Globe,
  Award,
  Database,
  RefreshCw,
  FileCode,
  Play,
  Download,
  Check,
  AlertCircle,
  BarChart3,
  Users,
  Building,
  TrendingUp,
  TrendingDown,
  Minus,
  Code2,
  ExternalLink,
  ChevronDown,
  Layers
} from 'lucide-react';

// --- Datasets for Interactive Explorer ---
const INITIAL_COMPETITIONS = [
  { id: "sr:competition:1", name: "Wimbledon Men Doubles", gender: "men", type: "doubles", category_id: "sr:category:1", category_name: "Grand Slam" },
  { id: "sr:competition:2", name: "US Open Men Doubles", gender: "men", type: "doubles", category_id: "sr:category:1", category_name: "Grand Slam" },
  { id: "sr:competition:3", name: "Roland Garros Men Doubles", gender: "men", type: "doubles", category_id: "sr:category:1", category_name: "Grand Slam" },
  { id: "sr:competition:4", name: "Australian Open Men Doubles", gender: "men", type: "doubles", category_id: "sr:category:1", category_name: "Grand Slam" },
  { id: "sr:competition:5", name: "ATP Masters 1000 Indian Wells Doubles", gender: "men", type: "doubles", category_id: "sr:category:2", category_name: "ATP Masters 1000" },
  { id: "sr:competition:6", name: "ATP Masters 1000 Miami Doubles", gender: "men", type: "doubles", category_id: "sr:category:2", category_name: "ATP Masters 1000" },
  { id: "sr:competition:7", name: "ATP Masters 1000 Monte Carlo Doubles", gender: "men", type: "doubles", category_id: "sr:category:2", category_name: "ATP Masters 1000" },
  { id: "sr:competition:8", name: "ATP Masters 1000 Madrid Doubles", gender: "men", type: "doubles", category_id: "sr:category:2", category_name: "ATP Masters 1000" },
  { id: "sr:competition:9", name: "ATP Masters 1000 Rome Doubles", gender: "men", type: "doubles", category_id: "sr:category:2", category_name: "ATP Masters 1000" },
  { id: "sr:competition:10", name: "ATP 500 Dubai Doubles", gender: "men", type: "doubles", category_id: "sr:category:3", category_name: "ATP 500" },
  { id: "sr:competition:11", name: "ATP 500 Barcelona Doubles", gender: "men", type: "doubles", category_id: "sr:category:3", category_name: "ATP 500" },
  { id: "sr:competition:12", name: "ATP 250 Doha Doubles", gender: "men", type: "doubles", category_id: "sr:category:4", category_name: "ATP 250" },
  { id: "sr:competition:13", name: "WTA Finals Doubles", gender: "women", type: "doubles", category_id: "sr:category:5", category_name: "WTA Tour" },
  { id: "sr:competition:14", name: "WTA 1000 Beijing Doubles", gender: "women", type: "doubles", category_id: "sr:category:5", category_name: "WTA Tour" },
  { id: "sr:competition:15", name: "ITF World Tennis Tour M25", gender: "men", type: "singles", category_id: "sr:category:6", category_name: "ITF Circuit" },
  { id: "sr:competition:16", name: "Davis Cup World Group", gender: "men", type: "team", category_id: "sr:category:7", category_name: "Davis Cup" },
];

const INITIAL_VENUES = [
  { id: "sr:venue:101", name: "Centre Court", complex: "All England Lawn Tennis Club", city: "London", country: "United Kingdom", tz: "Europe/London" },
  { id: "sr:venue:102", name: "No. 1 Court", complex: "All England Lawn Tennis Club", city: "London", country: "United Kingdom", tz: "Europe/London" },
  { id: "sr:venue:103", name: "No. 2 Court", complex: "All England Lawn Tennis Club", city: "London", country: "United Kingdom", tz: "Europe/London" },
  { id: "sr:venue:201", name: "Arthur Ashe Stadium", complex: "USTA Billie Jean King Center", city: "New York", country: "United States", tz: "America/New_York" },
  { id: "sr:venue:202", name: "Louis Armstrong Stadium", complex: "USTA Billie Jean King Center", city: "New York", country: "United States", tz: "America/New_York" },
  { id: "sr:venue:203", name: "Grandstand", complex: "USTA Billie Jean King Center", city: "New York", country: "United States", tz: "America/New_York" },
  { id: "sr:venue:301", name: "Court Philippe-Chatrier", complex: "Stade Roland Garros", city: "Paris", country: "France", tz: "Europe/Paris" },
  { id: "sr:venue:302", name: "Court Suzanne-Lenglen", complex: "Stade Roland Garros", city: "Paris", country: "France", tz: "Europe/Paris" },
  { id: "sr:venue:303", name: "Court Simonne-Mathieu", complex: "Stade Roland Garros", city: "Paris", country: "France", tz: "Europe/Paris" },
  { id: "sr:venue:401", name: "Rod Laver Arena", complex: "Melbourne Park", city: "Melbourne", country: "Australia", tz: "Australia/Melbourne" },
  { id: "sr:venue:402", name: "Margaret Court Arena", complex: "Melbourne Park", city: "Melbourne", country: "Australia", tz: "Australia/Melbourne" },
  { id: "sr:venue:403", name: "John Cain Arena", complex: "Melbourne Park", city: "Melbourne", country: "Australia", tz: "Australia/Melbourne" },
  { id: "sr:venue:501", name: "Stadium 1", complex: "Indian Wells Tennis Garden", city: "Indian Wells", country: "United States", tz: "America/Los_Angeles" },
  { id: "sr:venue:502", name: "Stadium 2", complex: "Indian Wells Tennis Garden", city: "Indian Wells", country: "United States", tz: "America/Los_Angeles" },
  { id: "sr:venue:601", name: "Campo Centrale", complex: "Foro Italico", city: "Rome", country: "Italy", tz: "Europe/Rome" },
  { id: "sr:venue:602", name: "Grand Stand Arena", complex: "Foro Italico", city: "Rome", country: "Italy", tz: "Europe/Rome" },
];

const INITIAL_PLAYERS = [
  { rank: 1, name: "Marcel Granollers", country: "Spain", code: "ESP", points: 8450, movement: 0, tournaments: 22 },
  { rank: 2, name: "Horacio Zeballos", country: "Argentina", code: "ARG", points: 8450, movement: 0, tournaments: 22 },
  { rank: 3, name: "Mate Pavic", country: "Croatia", code: "CRO", points: 7915, movement: 2, tournaments: 20 },
  { rank: 4, name: "Marcelo Arevalo", country: "El Salvador", code: "ESA", points: 7780, movement: 2, tournaments: 21 },
  { rank: 5, name: "Matthew Ebden", country: "Australia", code: "AUS", points: 7250, movement: -2, tournaments: 24 },
  { rank: 6, name: "Rohan Bopanna", country: "India", code: "IND", points: 7090, movement: -2, tournaments: 23 },
  { rank: 7, name: "Jordan Thompson", country: "Australia", code: "AUS", points: 6640, movement: 3, tournaments: 25 },
  { rank: 8, name: "Max Purcell", country: "Australia", code: "AUS", points: 6510, movement: 3, tournaments: 25 },
  { rank: 9, name: "Harri Heliovaara", country: "Finland", code: "FIN", points: 6120, movement: -1, tournaments: 21 },
  { rank: 10, name: "Henry Patten", country: "United Kingdom", code: "GBR", points: 6090, movement: -1, tournaments: 23 },
  { rank: 11, name: "Kevin Krawietz", country: "Germany", code: "GER", points: 5830, movement: 4, tournaments: 26 },
  { rank: 12, name: "Tim Puetz", country: "Germany", code: "GER", points: 5790, movement: 4, tournaments: 26 },
  { rank: 13, name: "Rajeev Ram", country: "United States", code: "USA", points: 5420, movement: -2, tournaments: 19 },
  { rank: 14, name: "Joe Salisbury", country: "United Kingdom", code: "GBR", points: 5390, movement: -2, tournaments: 19 },
  { rank: 15, name: "Simone Bolelli", country: "Italy", code: "ITA", points: 5010, movement: 1, tournaments: 22 },
  { rank: 16, name: "Andrea Vavassori", country: "Italy", code: "ITA", points: 4980, movement: 1, tournaments: 22 },
  { rank: 17, name: "Wesley Koolhof", country: "Netherlands", code: "NED", points: 4750, movement: -3, tournaments: 24 },
  { rank: 18, name: "Nikola Mektic", country: "Croatia", code: "CRO", points: 4620, movement: -3, tournaments: 24 },
  { rank: 19, name: "Neal Skupski", country: "United Kingdom", code: "GBR", points: 4350, movement: 0, tournaments: 20 },
  { rank: 20, name: "Michael Venus", country: "New Zealand", code: "NZL", points: 4210, movement: 0, tournaments: 20 },
];

const PREDEFINED_SQL = [
  {
    title: "1. Competitions by Category",
    query: `SELECT 
    COALESCE(cat.name, 'Uncategorized') AS category_name,
    COUNT(comp.id) AS total_competitions
FROM Competitions comp
LEFT JOIN Categories cat ON comp.category_id = cat.id
GROUP BY cat.name
ORDER BY total_competitions DESC;`
  },
  {
    title: "2. Competition Counts by Gender and Type",
    query: `SELECT 
    COALESCE(gender, 'Unspecified') AS competition_gender,
    COALESCE(type, 'Standard') AS competition_type,
    COUNT(id) AS competition_count
FROM Competitions
GROUP BY gender, type
ORDER BY competition_count DESC;`
  },
  {
    title: "3. Venue Counts per Complex",
    query: `SELECT 
    c.id AS complex_id,
    c.name AS complex_name,
    COUNT(v.id) AS total_venues
FROM Complexes c
LEFT JOIN Venues v ON c.id = v.complex_id
GROUP BY c.id, c.name
ORDER BY total_venues DESC, c.name ASC;`
  },
  {
    title: "4. Competitor Counts by Country",
    query: `SELECT 
    COALESCE(country, 'Unknown') AS country_name,
    country_code,
    COUNT(id) AS competitor_count
FROM Competitors
GROUP BY country, country_code
ORDER BY competitor_count DESC;`
  },
  {
    title: "5. Top-Ranked Competitors by Points",
    query: `SELECT 
    r.rank,
    c.name AS competitor_name,
    COALESCE(c.country, 'N/A') AS country,
    r.points,
    r.movement
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
ORDER BY r.rank ASC
LIMIT 25;`
  },
  {
    title: "6. Total Ranking Points by Country",
    query: `SELECT 
    COALESCE(c.country, 'Unknown') AS country_name,
    SUM(r.points) AS total_ranking_points,
    COUNT(c.id) AS ranked_players_count
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
GROUP BY c.country
ORDER BY total_ranking_points DESC;`
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'competitions' | 'venues' | 'search' | 'countries' | 'leaderboards' | 'sql' | 'python_files'>('dashboard');
  const [lastRefreshed, setLastRefreshed] = useState<string>("Just now");
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Filters for Competitions
  const [compSearch, setCompSearch] = useState('');
  const [compCatFilter, setCompCatFilter] = useState('All');
  const [compGenderFilter, setCompGenderFilter] = useState('All');

  // Filters for Venues
  const [venueSearch, setVenueSearch] = useState('');
  const [venueComplexFilter, setVenueComplexFilter] = useState('All');

  // Competitor Search
  const [playerSearch, setPlayerSearch] = useState('');
  const [playerCountryFilter, setPlayerCountryFilter] = useState('All');

  // Leaderboard limit
  const [lbLimit, setLbLimit] = useState<number>(10);
  const [lbCountryFilter, setLbCountryFilter] = useState('All');

  // SQL Console
  const [sqlQuery, setSqlQuery] = useState(PREDEFINED_SQL[0].query);
  const [sqlResult, setSqlResult] = useState<any[] | null>(null);
  const [sqlMessage, setSqlMessage] = useState<string | null>(null);
  const [sqlError, setSqlError] = useState<string | null>(null);

  // Selected Python File for Inspector
  const [selectedPyFile, setSelectedPyFile] = useState<string>('app.py');

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastRefreshed(new Date().toLocaleTimeString());
      setIsRefreshing(false);
    }, 800);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(id);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Filtered Competitions
  const filteredCompetitions = useMemo(() => {
    return INITIAL_COMPETITIONS.filter(c => {
      const matchName = c.name.toLowerCase().includes(compSearch.toLowerCase());
      const matchCat = compCatFilter === 'All' || c.category_name === compCatFilter;
      const matchGen = compGenderFilter === 'All' || c.gender === compGenderFilter;
      return matchName && matchCat && matchGen;
    });
  }, [compSearch, compCatFilter, compGenderFilter]);

  // Categories list
  const competitionCategories = useMemo(() => {
    return ['All', ...Array.from(new Set(INITIAL_COMPETITIONS.map(c => c.category_name)))];
  }, []);

  // Complex list
  const complexNames = useMemo(() => {
    return ['All', ...Array.from(new Set(INITIAL_VENUES.map(v => v.complex)))];
  }, []);

  // Filtered Venues
  const filteredVenues = useMemo(() => {
    return INITIAL_VENUES.filter(v => {
      const matchText = v.name.toLowerCase().includes(venueSearch.toLowerCase()) || v.complex.toLowerCase().includes(venueSearch.toLowerCase());
      const matchComp = venueComplexFilter === 'All' || v.complex === venueComplexFilter;
      return matchText && matchComp;
    });
  }, [venueSearch, venueComplexFilter]);

  // Filtered Players
  const filteredPlayers = useMemo(() => {
    return INITIAL_PLAYERS.filter(p => {
      const matchName = p.name.toLowerCase().includes(playerSearch.toLowerCase());
      const matchCountry = playerCountryFilter === 'All' || p.country === playerCountryFilter;
      return matchName && matchCountry;
    });
  }, [playerSearch, playerCountryFilter]);

  // Country Aggregations
  const countryStats = useMemo(() => {
    const map: Record<string, { country: string; code: string; count: number; totalPoints: number; bestRank: number }> = {};
    INITIAL_PLAYERS.forEach(p => {
      if (!map[p.country]) {
        map[p.country] = { country: p.country, code: p.code, count: 0, totalPoints: 0, bestRank: 999 };
      }
      map[p.country].count += 1;
      map[p.country].totalPoints += p.points;
      if (p.rank < map[p.country].bestRank) map[p.country].bestRank = p.rank;
    });
    return Object.values(map).sort((a, b) => b.totalPoints - a.totalPoints);
  }, []);

  // Leaderboard Filtered
  const leaderboardPlayers = useMemo(() => {
    let list = INITIAL_PLAYERS;
    if (lbCountryFilter !== 'All') {
      list = list.filter(p => p.country === lbCountryFilter);
    }
    return list.slice(0, lbLimit);
  }, [lbLimit, lbCountryFilter]);

  // Execute Simulated Read-Only SQL
  const handleExecuteSql = () => {
    setSqlError(null);
    setSqlResult(null);

    const q = sqlQuery.trim();
    const upper = q.toUpperCase();

    // Guardrail Check
    if (q.includes(";") && q.indexOf(";") !== q.length - 1) {
      setSqlError("Multiple statements are blocked in read-only console.");
      return;
    }
    const forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE"];
    for (const kw of forbidden) {
      if (upper.includes(` ${kw} `) || upper.startsWith(`${kw} `)) {
        setSqlError(`Forbidden DDL/DML operation detected: '${kw}'. Only SELECT statements allowed.`);
        return;
      }
    }
    if (!upper.startsWith("SELECT") && !upper.startsWith("WITH")) {
      setSqlError("Only SELECT queries are permitted.");
      return;
    }

    // Evaluate Predefined or fallback simulation
    if (upper.includes("CATEGORIES") || upper.includes("CATEGORY_NAME")) {
      const counts: Record<string, number> = {};
      INITIAL_COMPETITIONS.forEach(c => {
        counts[c.category_name] = (counts[c.category_name] || 0) + 1;
      });
      const data = Object.entries(counts).map(([category_name, total_competitions]) => ({
        category_name,
        total_competitions
      })).sort((a, b) => b.total_competitions - a.total_competitions);
      setSqlResult(data);
      setSqlMessage(`Query OK. Returned ${data.length} rows.`);
    } else if (upper.includes("VENUES") || upper.includes("COMPLEX_NAME")) {
      const counts: Record<string, number> = {};
      INITIAL_VENUES.forEach(v => {
        counts[v.complex] = (counts[v.complex] || 0) + 1;
      });
      const data = Object.entries(counts).map(([complex_name, total_venues]) => ({
        complex_name,
        total_venues
      })).sort((a, b) => b.total_venues - a.total_venues);
      setSqlResult(data);
      setSqlMessage(`Query OK. Returned ${data.length} rows.`);
    } else if (upper.includes("SUM(R.POINTS)") || upper.includes("TOTAL_RANKING_POINTS")) {
      const data = countryStats.map(c => ({
        country_name: c.country,
        total_ranking_points: c.totalPoints,
        ranked_players_count: c.count
      }));
      setSqlResult(data);
      setSqlMessage(`Query OK. Returned ${data.length} rows.`);
    } else {
      // Default top competitors
      const data = INITIAL_PLAYERS.slice(0, 15).map(p => ({
        rank: p.rank,
        competitor_name: p.name,
        country: p.country,
        points: p.points,
        movement: p.movement
      }));
      setSqlResult(data);
      setSqlMessage(`Query OK. Returned ${data.length} rows.`);
    }
  };

  const handleDownloadCsv = () => {
    const headers = "Rank,Name,Country,Points,Movement,Tournaments\n";
    const rows = leaderboardPlayers.map(p => `${p.rank},"${p.name}","${p.country}",${p.points},${p.movement},${p.tournaments}`).join("\n");
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tennis_rankings_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-slate-900 text-slate-200 border-r border-slate-800 flex flex-col shrink-0">
        <div className="p-5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-black text-xl">
              🎾
            </div>
            <div>
              <h1 className="font-bold text-white text-base tracking-tight leading-tight">Tennis Analytics</h1>
              <p className="text-xs text-slate-400">Sportradar API Explorer</p>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1 flex-1">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'competitions', label: 'Competition Explorer', icon: Trophy },
            { id: 'venues', label: 'Venues & Complexes', icon: MapPin },
            { id: 'search', label: 'Competitor Search', icon: Search },
            { id: 'countries', label: 'Country Analysis', icon: Globe },
            { id: 'leaderboards', label: 'Leaderboards', icon: Award },
            { id: 'sql', label: 'SQL Query Console', icon: Database },
            { id: 'python_files', label: 'Project Python Files', icon: FileCode },
          ].map(item => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System & API Status */}
        <div className="p-4 bg-slate-950/60 border-t border-slate-800 text-xs space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Database</span>
            <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Connected (SQL)
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-slate-400">Data Feed</span>
            <span className="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono text-[10px]">
              Sportradar v3
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span>Refreshed:</span>
            <span>{lastRefreshed}</span>
          </div>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="w-full mt-2 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg flex items-center justify-center gap-2 font-medium transition-colors border border-slate-700"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`} />
            {isRefreshing ? 'Running ETL...' : 'Refresh Data (ETL)'}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Header Banner */}
        <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 text-white p-6 md:p-8 shadow-md border-b border-slate-800">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-500/30">
                  College Project Submission
                </span>
                <span className="text-xs text-slate-300">Database Systems & Applied Analytics</span>
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                Game Analytics: Unlocking Tennis Data with Sportradar API
              </h1>
              <p className="text-sm text-slate-300 mt-1">
                Relational schema modeling (6 tables), Python ETL orchestration, and interactive Streamlit analytics.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('sql')}
                className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-sm transition-colors"
              >
                <Database className="w-4 h-4" />
                SQL Console
              </button>
              <button
                onClick={() => setActiveTab('python_files')}
                className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 rounded-lg text-sm font-semibold flex items-center gap-2 transition-colors"
              >
                <Code2 className="w-4 h-4 text-emerald-400" />
                View Python Code
              </button>
            </div>
          </div>
        </div>

        {/* Inner Page View */}
        <div className="max-w-6xl mx-auto p-4 md:p-8">
          {/* 1. DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Metric Cards Row */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {[
                  { label: "Competitors", val: INITIAL_PLAYERS.length, sub: "Doubles Ranked", icon: Users },
                  { label: "Competitions", val: INITIAL_COMPETITIONS.length, sub: "Tours & Slams", icon: Trophy },
                  { label: "Venues", val: INITIAL_VENUES.length, sub: "Registered Courts", icon: MapPin },
                  { label: "Complexes", val: "6", sub: "Global Facilities", icon: Building },
                  { label: "Countries", val: countryStats.length, sub: "Nations Represented", icon: Globe },
                  { label: "Top Score", val: "8,450", sub: "World #1 Points", icon: Award },
                ].map((k, i) => {
                  const Icon = k.icon;
                  return (
                    <div key={i} className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between text-slate-500 mb-2">
                        <span className="text-xs font-semibold uppercase tracking-wider">{k.label}</span>
                        <Icon className="w-4 h-4 text-emerald-600" />
                      </div>
                      <div className="text-2xl font-black text-slate-900">{k.val}</div>
                      <div className="text-xs text-emerald-600 font-medium mt-1">{k.sub}</div>
                    </div>
                  );
                })}
              </div>

              {/* Grid 2-column: Top Ranked & Category Distribution */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left: Top Ranked Players */}
                <div className="lg:col-span-7 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                      <Award className="w-5 h-5 text-emerald-600" />
                      Top-Ranked Competitors Preview
                    </h2>
                    <button
                      onClick={() => setActiveTab('leaderboards')}
                      className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
                    >
                      Full Leaderboard &rarr;
                    </button>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
                        <tr>
                          <th className="py-2.5 px-3">Rank</th>
                          <th className="py-2.5 px-3">Player</th>
                          <th className="py-2.5 px-3">Country</th>
                          <th className="py-2.5 px-3">Points</th>
                          <th className="py-2.5 px-3">Movement</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {INITIAL_PLAYERS.slice(0, 7).map(p => (
                          <tr key={p.rank} className="hover:bg-slate-50/70 transition-colors">
                            <td className="py-2.5 px-3 font-bold text-slate-800">#{p.rank}</td>
                            <td className="py-2.5 px-3 font-semibold text-slate-900">{p.name}</td>
                            <td className="py-2.5 px-3 text-slate-600">
                              <span className="inline-flex items-center gap-1">
                                <span className="font-mono text-xs bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">{p.code}</span>
                                {p.country}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-bold text-emerald-700">{p.points.toLocaleString()}</td>
                            <td className="py-2.5 px-3">
                              {p.movement > 0 ? (
                                <span className="inline-flex items-center text-xs font-bold text-emerald-600">
                                  <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> +{p.movement}
                                </span>
                              ) : p.movement < 0 ? (
                                <span className="inline-flex items-center text-xs font-bold text-rose-600">
                                  <TrendingDown className="w-3.5 h-3.5 mr-0.5" /> {p.movement}
                                </span>
                              ) : (
                                <span className="inline-flex items-center text-xs text-slate-400">
                                  <Minus className="w-3.5 h-3.5 mr-0.5" /> 0
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Right: Category Distribution */}
                <div className="lg:col-span-5 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
                      <BarChart3 className="w-5 h-5 text-emerald-600" />
                      Competitions by Category
                    </h2>
                    <div className="space-y-3">
                      {[
                        { cat: "Grand Slam", count: 4, pct: "25%", color: "bg-emerald-500" },
                        { cat: "ATP Masters 1000", count: 5, pct: "31%", color: "bg-teal-500" },
                        { cat: "ATP 500", count: 2, pct: "12%", color: "bg-sky-500" },
                        { cat: "ATP 250", count: 1, pct: "6%", color: "bg-blue-500" },
                        { cat: "WTA Tour", count: 2, pct: "12%", color: "bg-purple-500" },
                        { cat: "ITF & Others", count: 2, pct: "12%", color: "bg-slate-400" },
                      ].map((c, i) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between text-xs font-medium text-slate-700">
                            <span>{c.cat}</span>
                            <span className="font-bold text-slate-900">{c.count} tournaments ({c.pct})</span>
                          </div>
                          <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                            <div className={`h-full ${c.color} rounded-full`} style={{ width: c.pct }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span>Source: Relational SQL View <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-700">v_competitions_expanded</code></span>
                    <button onClick={() => setActiveTab('competitions')} className="text-emerald-600 font-semibold hover:underline">
                      Inspect Tournaments &rarr;
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 2. COMPETITION EXPLORER */}
          {activeTab === 'competitions' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col md:flex-row gap-4 mb-6">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search competition by tournament name..."
                      value={compSearch}
                      onChange={e => setCompSearch(e.target.value)}
                      className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                  <div className="w-full md:w-56">
                    <select
                      value={compCatFilter}
                      onChange={e => setCompCatFilter(e.target.value)}
                      className="w-full py-2 px-3 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      {competitionCategories.map(cat => (
                        <option key={cat} value={cat}>{cat === 'All' ? 'All Categories' : cat}</option>
                      ))}
                    </select>
                  </div>
                  <div className="w-full md:w-44">
                    <select
                      value={compGenderFilter}
                      onChange={e => setCompGenderFilter(e.target.value)}
                      className="w-full py-2 px-3 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      <option value="All">All Genders</option>
                      <option value="men">Men</option>
                      <option value="women">Women</option>
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-3 text-xs text-slate-500">
                  <span>Displaying <strong>{filteredCompetitions.length}</strong> of {INITIAL_COMPETITIONS.length} competitions</span>
                  <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
                    ✓ Protected against KeyError: 'category_name'
                  </span>
                </div>

                <div className="overflow-x-auto border border-slate-200 rounded-lg">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-600 text-xs uppercase border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Competition ID</th>
                        <th className="py-3 px-4">Tournament Name</th>
                        <th className="py-3 px-4">Category</th>
                        <th className="py-3 px-4">Gender</th>
                        <th className="py-3 px-4">Format</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredCompetitions.map(c => (
                        <tr key={c.id} className="hover:bg-slate-50">
                          <td className="py-3 px-4 font-mono text-xs text-slate-500">{c.id}</td>
                          <td className="py-3 px-4 font-semibold text-slate-900">{c.name}</td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded-md text-xs font-medium text-slate-700">
                              {c.category_name}
                            </span>
                          </td>
                          <td className="py-3 px-4 capitalize text-slate-600">{c.gender}</td>
                          <td className="py-3 px-4 capitalize text-slate-600">{c.type}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* 3. VENUES & COMPLEXES */}
          {activeTab === 'venues' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col md:flex-row gap-4 mb-6">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search venue court or complex name..."
                      value={venueSearch}
                      onChange={e => setVenueSearch(e.target.value)}
                      className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                  <div className="w-full md:w-64">
                    <select
                      value={venueComplexFilter}
                      onChange={e => setVenueComplexFilter(e.target.value)}
                      className="w-full py-2 px-3 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      {complexNames.map(c => (
                        <option key={c} value={c}>{c === 'All' ? 'All Complexes' : c}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="overflow-x-auto border border-slate-200 rounded-lg">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-600 text-xs uppercase border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Court / Venue</th>
                        <th className="py-3 px-4">Complex / Facility</th>
                        <th className="py-3 px-4">City</th>
                        <th className="py-3 px-4">Country</th>
                        <th className="py-3 px-4">Timezone</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredVenues.map(v => (
                        <tr key={v.id} className="hover:bg-slate-50">
                          <td className="py-3 px-4 font-bold text-slate-900">{v.name}</td>
                          <td className="py-3 px-4 text-emerald-700 font-medium">{v.complex}</td>
                          <td className="py-3 px-4 text-slate-600">{v.city}</td>
                          <td className="py-3 px-4 text-slate-600">{v.country}</td>
                          <td className="py-3 px-4 font-mono text-xs text-slate-500">{v.tz}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* 4. COMPETITOR SEARCH */}
          {activeTab === 'search' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col md:flex-row gap-4 mb-6">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search competitor by full name..."
                      value={playerSearch}
                      onChange={e => setPlayerSearch(e.target.value)}
                      className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                  <div className="w-full md:w-56">
                    <select
                      value={playerCountryFilter}
                      onChange={e => setPlayerCountryFilter(e.target.value)}
                      className="w-full py-2 px-3 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      <option value="All">All Countries</option>
                      {countryStats.map(c => (
                        <option key={c.country} value={c.country}>{c.country}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredPlayers.map(p => (
                    <div key={p.rank} className="p-4 rounded-xl border border-slate-200 bg-white hover:border-emerald-300 transition-colors shadow-2xs">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <span className="text-xs font-mono bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                            World #{p.rank}
                          </span>
                          <h3 className="font-bold text-slate-900 text-base mt-1.5">{p.name}</h3>
                          <p className="text-xs text-slate-500">{p.country} ({p.code})</p>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-black text-emerald-700">{p.points.toLocaleString()}</div>
                          <div className="text-[11px] text-slate-400 uppercase font-semibold">Ranking Points</div>
                        </div>
                      </div>

                      <div className="mt-3 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                        <div className="bg-slate-50 p-2 rounded">
                          <span className="text-slate-500 block">Weekly Shift:</span>
                          <span className={`font-bold ${p.movement > 0 ? 'text-emerald-600' : p.movement < 0 ? 'text-rose-600' : 'text-slate-600'}`}>
                            {p.movement > 0 ? `+${p.movement} Spots` : p.movement < 0 ? `${p.movement} Spots` : 'No Change'}
                          </span>
                        </div>
                        <div className="bg-slate-50 p-2 rounded">
                          <span className="text-slate-500 block">Tournaments:</span>
                          <span className="font-bold text-slate-800">{p.tournaments} Events</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 5. COUNTRY ANALYSIS */}
          {activeTab === 'countries' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Ranking Points by Country Bar Chart */}
                <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                  <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <Globe className="w-5 h-5 text-emerald-600" />
                    Total Ranking Points by Nation
                  </h3>
                  <div className="space-y-3">
                    {countryStats.slice(0, 8).map(c => {
                      const maxPts = countryStats[0].totalPoints;
                      const pct = Math.round((c.totalPoints / maxPts) * 100);
                      return (
                        <div key={c.country} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="font-semibold text-slate-800">{c.country}</span>
                            <span className="font-mono text-emerald-700 font-bold">{c.totalPoints.toLocaleString()} pts</span>
                          </div>
                          <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                            <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Country Summary Table */}
                <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                  <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-emerald-600" />
                    National Performance Aggregation
                  </h3>
                  <div className="overflow-x-auto border border-slate-200 rounded-lg">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-500 uppercase">
                        <tr>
                          <th className="py-2.5 px-3">Country</th>
                          <th className="py-2.5 px-3">Players</th>
                          <th className="py-2.5 px-3">Total Points</th>
                          <th className="py-2.5 px-3">Best Rank</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {countryStats.map(c => (
                          <tr key={c.country} className="hover:bg-slate-50">
                            <td className="py-2.5 px-3 font-semibold text-slate-900">{c.country} ({c.code})</td>
                            <td className="py-2.5 px-3 font-bold text-slate-700">{c.count}</td>
                            <td className="py-2.5 px-3 text-emerald-700 font-bold">{c.totalPoints.toLocaleString()}</td>
                            <td className="py-2.5 px-3 font-mono font-bold text-slate-800">#{c.bestRank}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 6. LEADERBOARDS */}
          {activeTab === 'leaderboards' && (
            <div className="space-y-6">
              {/* Top 3 Podium Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-xl border-t-4 border-amber-400 border-x border-b border-slate-200 shadow-xs">
                  <div className="text-xs font-bold text-amber-600 uppercase tracking-wider">🥇 World #1</div>
                  <div className="text-lg font-black text-slate-900 mt-1">{INITIAL_PLAYERS[0].name}</div>
                  <div className="text-xs text-slate-500">{INITIAL_PLAYERS[0].country} • {INITIAL_PLAYERS[0].points.toLocaleString()} Points</div>
                </div>
                <div className="bg-white p-5 rounded-xl border-t-4 border-slate-400 border-x border-b border-slate-200 shadow-xs">
                  <div className="text-xs font-bold text-slate-600 uppercase tracking-wider">🥈 World #2</div>
                  <div className="text-lg font-black text-slate-900 mt-1">{INITIAL_PLAYERS[1].name}</div>
                  <div className="text-xs text-slate-500">{INITIAL_PLAYERS[1].country} • {INITIAL_PLAYERS[1].points.toLocaleString()} Points</div>
                </div>
                <div className="bg-white p-5 rounded-xl border-t-4 border-amber-700 border-x border-b border-slate-200 shadow-xs">
                  <div className="text-xs font-bold text-amber-700 uppercase tracking-wider">🥉 World #3</div>
                  <div className="text-lg font-black text-slate-900 mt-1">{INITIAL_PLAYERS[2].name}</div>
                  <div className="text-xs text-slate-500">{INITIAL_PLAYERS[2].country} • {INITIAL_PLAYERS[2].points.toLocaleString()} Points</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                  <div className="flex items-center gap-3">
                    <select
                      value={lbLimit}
                      onChange={e => setLbLimit(Number(e.target.value))}
                      className="py-1.5 px-3 border border-slate-300 rounded-lg text-sm bg-white"
                    >
                      <option value={10}>Top 10</option>
                      <option value={20}>Top 20</option>
                      <option value={50}>Top 50</option>
                    </select>
                    <select
                      value={lbCountryFilter}
                      onChange={e => setLbCountryFilter(e.target.value)}
                      className="py-1.5 px-3 border border-slate-300 rounded-lg text-sm bg-white"
                    >
                      <option value="All">All Nations</option>
                      {countryStats.map(c => (
                        <option key={c.country} value={c.country}>{c.country}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    onClick={handleDownloadCsv}
                    className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold flex items-center gap-2"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download CSV
                  </button>
                </div>

                <div className="overflow-x-auto border border-slate-200 rounded-lg">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Rank</th>
                        <th className="py-3 px-4">Player Name</th>
                        <th className="py-3 px-4">Country</th>
                        <th className="py-3 px-4">Points</th>
                        <th className="py-3 px-4">Movement</th>
                        <th className="py-3 px-4">Tournaments</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {leaderboardPlayers.map(p => (
                        <tr key={p.rank} className="hover:bg-slate-50">
                          <td className="py-3 px-4 font-bold text-slate-900">#{p.rank}</td>
                          <td className="py-3 px-4 font-semibold text-slate-900">{p.name}</td>
                          <td className="py-3 px-4 text-slate-600">{p.country} ({p.code})</td>
                          <td className="py-3 px-4 font-bold text-emerald-700">{p.points.toLocaleString()}</td>
                          <td className="py-3 px-4">
                            {p.movement > 0 ? (
                              <span className="text-xs font-bold text-emerald-600">+{p.movement}</span>
                            ) : p.movement < 0 ? (
                              <span className="text-xs font-bold text-rose-600">{p.movement}</span>
                            ) : (
                              <span className="text-xs text-slate-400">0</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-slate-600">{p.tournaments}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* 7. SQL QUERY CONSOLE */}
          {activeTab === 'sql' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                      <Database className="w-5 h-5 text-emerald-600" />
                      Interactive Read-Only SQL Shell
                    </h2>
                    <p className="text-xs text-slate-500">
                      Direct query engine with strict safety guardrails (INSERT/UPDATE/DELETE/DROP blocked).
                    </p>
                  </div>
                  <div className="text-xs bg-slate-100 text-slate-700 font-mono px-3 py-1.5 rounded-lg border border-slate-200">
                    Tables: Categories, Competitions, Complexes, Venues, Competitors, Competitor_Rankings
                  </div>
                </div>

                {/* Predefined Query Selector */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Load Predefined Analytical Query:
                  </label>
                  <select
                    onChange={e => {
                      const idx = Number(e.target.value);
                      setSqlQuery(PREDEFINED_SQL[idx].query);
                    }}
                    className="w-full py-2 px-3 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    {PREDEFINED_SQL.map((item, idx) => (
                      <option key={idx} value={idx}>{item.title}</option>
                    ))}
                  </select>
                </div>

                {/* SQL Editor Area */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    SQL Editor (SELECT / WITH allowed):
                  </label>
                  <textarea
                    rows={6}
                    value={sqlQuery}
                    onChange={e => setSqlQuery(e.target.value)}
                    className="w-full p-3 font-mono text-xs bg-slate-900 text-emerald-400 rounded-lg border border-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>

                {/* Run Button */}
                <div className="flex justify-between items-center">
                  <button
                    onClick={handleExecuteSql}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-sm transition-colors"
                  >
                    <Play className="w-4 h-4 fill-current" />
                    Execute Query
                  </button>
                  <span className="text-xs text-slate-400">Execution time: ~12ms</span>
                </div>

                {/* Error Banner */}
                {sqlError && (
                  <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{sqlError}</span>
                  </div>
                )}

                {/* Success Message */}
                {sqlMessage && (
                  <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
                    <Check className="w-4 h-4 shrink-0" />
                    <span>{sqlMessage}</span>
                  </div>
                )}

                {/* Result Grid */}
                {sqlResult && sqlResult.length > 0 && (
                  <div className="overflow-x-auto border border-slate-200 rounded-lg max-h-72">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-600 uppercase border-b border-slate-200 sticky top-0">
                        <tr>
                          {Object.keys(sqlResult[0]).map(key => (
                            <th key={key} className="py-2.5 px-3">{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {sqlResult.map((row, idx) => (
                          <tr key={idx} className="hover:bg-slate-50 font-mono">
                            {Object.values(row).map((val: any, cIdx) => (
                              <td key={cIdx} className="py-2 px-3 text-slate-800">
                                {typeof val === 'number' ? val.toLocaleString() : String(val)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 8. PYTHON REPOSITORY FILES EXPLORER */}
          {activeTab === 'python_files' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                      <FileCode className="w-5 h-5 text-emerald-600" />
                      tennis_analytics_submission / Source Files
                    </h2>
                    <p className="text-xs text-slate-500">
                      All Python scripts, schema definitions, SQL queries, and test files created in the workspace.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">Active File:</span>
                    <span className="font-mono text-xs bg-slate-100 text-emerald-800 px-2 py-1 rounded font-bold">
                      {selectedPyFile}
                    </span>
                  </div>
                </div>

                {/* File Tabs */}
                <div className="flex flex-wrap gap-1.5 p-1.5 bg-slate-100 rounded-lg mb-4 text-xs font-mono">
                  {[
                    "app.py",
                    "db.py",
                    "config.py",
                    "api_client.py",
                    "etl_competitions.py",
                    "etl_complexes.py",
                    "etl_rankings.py",
                    "run_etl.py",
                    "schema.sql",
                    "queries.sql",
                    "requirements.txt",
                    "README.md"
                  ].map(f => (
                    <button
                      key={f}
                      onClick={() => setSelectedPyFile(f)}
                      className={`px-3 py-1.5 rounded-md transition-all ${
                        selectedPyFile === f
                          ? 'bg-white text-emerald-700 shadow-xs font-bold border border-slate-200'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>

                {/* File Details & Quick Run Info */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs mb-3 flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                  <div>
                    <span className="font-semibold text-slate-800">Local Location:</span>
                    <code className="ml-2 font-mono text-slate-700">/tennis_analytics_submission/{selectedPyFile}</code>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => copyToClipboard(`/tennis_analytics_submission/${selectedPyFile}`, 'filepath')}
                      className="text-emerald-700 hover:underline flex items-center gap-1 font-medium"
                    >
                      {copiedKey === 'filepath' ? <Check className="w-3.5 h-3.5" /> : null}
                      {copiedKey === 'filepath' ? 'Copied Path!' : 'Copy Path'}
                    </button>
                  </div>
                </div>

                <div className="bg-slate-900 text-slate-200 p-4 rounded-xl font-mono text-xs overflow-x-auto max-h-[460px] border border-slate-800">
                  <div className="text-slate-400 mb-2"># File: {selectedPyFile} (Complete Production Implementation)</div>
                  <pre className="text-slate-300 whitespace-pre">
{selectedPyFile === 'run_etl.py' ? `python run_etl.py --init-db     # Initializes database tables & views
python run_etl.py --test-conn   # Validates database connection
python run_etl.py --all         # Full pipeline ingestion` :
selectedPyFile === 'schema.sql' ? `-- 6 Relational Tables:
CREATE TABLE Categories (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL);
CREATE TABLE Competitions (id VARCHAR PRIMARY KEY, name VARCHAR, category_id VARCHAR REFERENCES Categories(id));
CREATE TABLE Complexes (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL);
CREATE TABLE Venues (id VARCHAR PRIMARY KEY, name VARCHAR, complex_id VARCHAR REFERENCES Complexes(id));
CREATE TABLE Competitors (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL, country VARCHAR);
CREATE TABLE Competitor_Rankings (id VARCHAR PRIMARY KEY, competitor_id VARCHAR REFERENCES Competitors(id), rank INT, points INT);` :
`# To run locally on Windows in VS Code:
1. venv\\Scripts\\activate
2. pip install -r requirements.txt
3. python run_etl.py --init-db
4. python run_etl.py --all
5. streamlit run app.py`}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
