/*
 * Mega Board five-league team registry and search
 * - Does not fetch or alter games or official report links.
 * - Explicit per-league teams ensure dropdowns work with empty offseason feeds.
 * - City nicknames/abbreviations are scoped by league to avoid cross-sport leakage.
 * - Exposes a testable browser and Node/CommonJS API.
 */
(function(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.MegaSearch = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function() {
  "use strict";

  // 2026 active franchise names. One record: market | nickname | team code | extra searches.
  // Franchise renames/expansion require explicit updates and regression tests.
  const RAW = {
    NFL: [
      "Arizona|Cardinals|ARI|AZ;Phoenix;PHX",
      "Atlanta|Falcons|ATL|",
      "Baltimore|Ravens|BAL|",
      "Buffalo|Bills|BUF|",
      "Carolina|Panthers|CAR|Charlotte;CLT",
      "Chicago|Bears|CHI|",
      "Cincinnati|Bengals|CIN|",
      "Cleveland|Browns|CLE|",
      "Dallas|Cowboys|DAL|",
      "Denver|Broncos|DEN|",
      "Detroit|Lions|DET|",
      "Green Bay|Packers|GB|",
      "Houston|Texans|HOU|",
      "Indianapolis|Colts|IND|Indy",
      "Jacksonville|Jaguars|JAX|JAC",
      "Kansas City|Chiefs|KC|",
      "Las Vegas|Raiders|LV|",
      "Los Angeles|Chargers|LAC|LA Chargers;SD Chargers",
      "Los Angeles|Rams|LAR|LA Rams",
      "Miami|Dolphins|MIA|",
      "Minnesota|Vikings|MIN|Minneapolis;MSP",
      "New England|Patriots|NE|Boston;BOS;Massachusetts",
      "New Orleans|Saints|NO|NOLA",
      "New York|Giants|NYG|NY Giants;NYC",
      "New York|Jets|NYJ|NY Jets;NYC",
      "Philadelphia|Eagles|PHI|Philly",
      "Pittsburgh|Steelers|PIT|",
      "San Francisco|49ers|SF|Niners;Forty Niners;49ers",
      "Seattle|Seahawks|SEA|",
      "Tampa Bay|Buccaneers|TB|Tampa;Bucs",
      "Tennessee|Titans|TEN|Nashville;BNA",
      "Washington|Commanders|WAS|DC;D.C.;Washington DC"
    ],
    NBA: [
      "Atlanta|Hawks|ATL|",
      "Boston|Celtics|BOS|",
      "Brooklyn|Nets|BKN|New York;NY;NYC;BK",
      "Charlotte|Hornets|CHA|CLT",
      "Chicago|Bulls|CHI|",
      "Cleveland|Cavaliers|CLE|Cavs",
      "Dallas|Mavericks|DAL|Mavs",
      "Denver|Nuggets|DEN|",
      "Detroit|Pistons|DET|",
      "Golden State|Warriors|GSW|San Francisco;SF;Bay Area;Dubs",
      "Houston|Rockets|HOU|",
      "Indiana|Pacers|IND|Indianapolis;Indy",
      "Los Angeles|Clippers|LAC|LA Clippers",
      "Los Angeles|Lakers|LAL|LA Lakers",
      "Memphis|Grizzlies|MEM|",
      "Miami|Heat|MIA|",
      "Milwaukee|Bucks|MIL|",
      "Minnesota|Timberwolves|MIN|Minneapolis;MSP;Wolves",
      "New Orleans|Pelicans|NOP|NO;NOLA",
      "New York|Knicks|NYK|NYC",
      "Oklahoma City|Thunder|OKC|",
      "Orlando|Magic|ORL|",
      "Philadelphia|76ers|PHI|Sixers;Philly",
      "Phoenix|Suns|PHX|PHO",
      "Portland|Trail Blazers|POR|Blazers;PDX;Trailblazers",
      "Sacramento|Kings|SAC|",
      "San Antonio|Spurs|SAS|SA",
      "Toronto|Raptors|TOR|",
      "Utah|Jazz|UTA|Salt Lake City;SLC",
      "Washington|Wizards|WAS|DC;D.C.;Washington DC"
    ],
    WNBA: [
      "Atlanta|Dream|ATL|",
      "Chicago|Sky|CHI|",
      "Connecticut|Sun|CON|Uncasville;CT",
      "Dallas|Wings|DAL|",
      "Golden State|Valkyries|GSV|San Francisco;SF;Bay Area",
      "Indiana|Fever|IND|Indianapolis;Indy",
      "Las Vegas|Aces|LVA|LV",
      "Los Angeles|Sparks|LAS|LA Sparks",
      "Minnesota|Lynx|MIN|Minneapolis;MSP",
      "New York|Liberty|NYL|Brooklyn;BK;BKN;NYC",
      "Phoenix|Mercury|PHX|PHO",
      "Portland|Fire|POR|PDX",
      "Seattle|Storm|SEA|",
      "Toronto|Tempo|TOR|",
      "Washington|Mystics|WAS|DC;D.C.;Washington DC"
    ],
    NHL: [
      "Anaheim|Ducks|ANA|Orange County;OC",
      "Boston|Bruins|BOS|",
      "Buffalo|Sabres|BUF|",
      "Calgary|Flames|CGY|",
      "Carolina|Hurricanes|CAR|Raleigh;RDU;Canes",
      "Chicago|Blackhawks|CHI|",
      "Colorado|Avalanche|COL|Denver;DEN;Avs",
      "Columbus|Blue Jackets|CBJ|",
      "Dallas|Stars|DAL|",
      "Detroit|Red Wings|DET|",
      "Edmonton|Oilers|EDM|",
      "Florida|Panthers|FLA|Sunrise;Miami;MIA",
      "Los Angeles|Kings|LAK|LA Kings",
      "Minnesota|Wild|MIN|St Paul;Saint Paul;Minneapolis;MSP",
      "Montreal|Canadiens|MTL|Habs",
      "Nashville|Predators|NSH|",
      "New Jersey|Devils|NJD|Newark;NJ",
      "New York|Islanders|NYI|Long Island;Elmont;NYC",
      "New York|Rangers|NYR|NYC",
      "Ottawa|Senators|OTT|",
      "Philadelphia|Flyers|PHI|Philly",
      "Pittsburgh|Penguins|PIT|Pens",
      "San Jose|Sharks|SJS|SJ",
      "Seattle|Kraken|SEA|",
      "St Louis|Blues|STL|Saint Louis",
      "Tampa Bay|Lightning|TBL|Tampa;TB;Bolts",
      "Toronto|Maple Leafs|TOR|Leafs",
      "Utah|Mammoth|UTA|Salt Lake City;SLC;Utah Hockey Club",
      "Vancouver|Canucks|VAN|",
      "Vegas|Golden Knights|VGK|Las Vegas;LV",
      "Washington|Capitals|WSH|DC;D.C.;Washington DC;Caps",
      "Winnipeg|Jets|WPG|"
    ],
    MLB: [
      "Arizona|Diamondbacks|ARI|Phoenix;PHX;Dbacks;D-backs",
      "Atlanta|Braves|ATL|",
      "Baltimore|Orioles|BAL|Os",
      "Boston|Red Sox|BOS|",
      "Chicago|Cubs|CHC|",
      "Chicago|White Sox|CWS|CHW",
      "Cincinnati|Reds|CIN|",
      "Cleveland|Guardians|CLE|",
      "Colorado|Rockies|COL|Denver;DEN",
      "Detroit|Tigers|DET|",
      "Houston|Astros|HOU|",
      "Kansas City|Royals|KC|KCR",
      "Los Angeles|Angels|LAA|LA Angels;Anaheim",
      "Los Angeles|Dodgers|LAD|LA Dodgers",
      "Miami|Marlins|MIA|",
      "Milwaukee|Brewers|MIL|",
      "Minnesota|Twins|MIN|Minneapolis;MSP",
      "New York|Mets|NYM|NYC",
      "New York|Yankees|NYY|NYC",
      "Philadelphia|Phillies|PHI|Philly",
      "Pittsburgh|Pirates|PIT|",
      "San Diego|Padres|SD|SDP",
      "San Francisco|Giants|SF|SFG",
      "Seattle|Mariners|SEA|",
      "St Louis|Cardinals|STL|Saint Louis",
      "Tampa Bay|Rays|TB|TBR;Tampa",
      "Texas|Rangers|TEX|Arlington;Dallas;DFW",
      "Toronto|Blue Jays|TOR|Jays",
      "Washington|Nationals|WSH|WAS;DC;D.C.;Washington DC;Nats",
      "|Athletics|ATH|Sacramento;SAC;West Sacramento;Oakland;OAK;As;A's"
    ]
  };

  const CITY_ALIASES = {
    "New York": ["NY", "NYC", "New York City"],
    "Brooklyn": ["BK", "BKN", "NY", "NYC", "New York"],
    "Los Angeles": ["LA", "L.A."],
    "San Francisco": ["SF", "SFO", "Bay Area"],
    "Golden State": ["GS", "SF", "SFO", "San Francisco", "Bay Area"],
    "Washington": ["WAS", "WSH", "DC", "D.C.", "Washington DC"],
    "Las Vegas": ["LV", "Vegas"],
    "Vegas": ["LV", "Las Vegas"],
    "Phoenix": ["PHX", "PHO"],
    "Portland": ["PDX", "POR"],
    "Salt Lake City": ["SLC"],
    "Utah": ["UT", "SLC", "Salt Lake City"],
    "St Louis": ["STL", "Saint Louis", "St. Louis"],
    "Kansas City": ["KC", "KCMO"],
    "Oklahoma City": ["OKC"],
    "New Orleans": ["NO", "NOLA"],
    "San Diego": ["SD", "SDG"],
    "San Jose": ["SJ", "SJS"],
    "Tampa Bay": ["TB", "Tampa", "TPA"],
    "Green Bay": ["GB"],
    "Toronto": ["TOR", "TO"],
    "Atlanta": ["ATL"],
    "Denver": ["DEN"],
    "Chicago": ["CHI"],
    "Philadelphia": ["PHI", "PHL", "Philly"],
    "Detroit": ["DET"],
    "Houston": ["HOU"],
    "Dallas": ["DAL", "DFW"],
    "Cleveland": ["CLE"],
    "Seattle": ["SEA"],
    "Boston": ["BOS"],
    "Indianapolis": ["IND", "Indy"],
    "Minneapolis": ["MSP", "MIN"],
    "Minnesota": ["MN", "MSP", "Minneapolis"],
    "Miami": ["MIA"],
    "Charlotte": ["CLT", "CHA"],
    "Baltimore": ["BAL"],
    "Cincinnati": ["CIN"],
    "Pittsburgh": ["PIT"],
    "Sacramento": ["SAC"],
    "Orlando": ["ORL"],
    "Milwaukee": ["MIL"],
    "Memphis": ["MEM"],
    "Buffalo": ["BUF"],
    "Jacksonville": ["JAX", "JAC"],
    "Nashville": ["NSH", "BNA"],
    "Anaheim": ["ANA"],
    "New Jersey": ["NJ", "NJD", "Newark"],
    "Montreal": ["MTL"],
    "Vancouver": ["VAN"],
    "Calgary": ["CGY"],
    "Edmonton": ["EDM"],
    "Ottawa": ["OTT"],
    "Winnipeg": ["WPG"],
    "Columbus": ["CBJ"],
    "Raleigh": ["RDU"],
    "Arizona": ["AZ", "PHX", "Phoenix"],
    "Colorado": ["CO", "COL", "DEN", "Denver"],
    "Connecticut": ["CT", "Uncasville"],
    "Indiana": ["IN", "IND", "Indianapolis", "Indy"],
    "Carolina": ["CAR", "Charlotte", "Raleigh"],
    "Tennessee": ["TN", "TEN", "Nashville"],
    "Texas": ["TX", "TEX", "Arlington", "DFW"],
    "Florida": ["FL", "FLA", "Sunrise", "Miami"],
    "New England": ["NE", "Boston", "BOS"],
    "Oakland": ["OAK"],
    "West Sacramento": ["SAC", "Sacramento"]
  };

  function norm(value) {
    return String(value == null ? "" : value).normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "").toLowerCase()
      .replace(/&/g, " and ").replace(/[^a-z0-9]+/g, " ").trim()
      .replace(/\s+/g, " ");
  }
  function compact(value) { return norm(value).replace(/\s+/g, ""); }
  function terms(value) {
    return [norm(value), compact(value)].filter(Boolean);
  }
  const LEAGUES = Object.keys(RAW);
  const TEAMS = {};
  for (const league of LEAGUES) {
    TEAMS[league] = RAW[league].map((line, index) => {
      const [city, nickname, abbreviation, aliases] = line.split("|");
      const name = [city, nickname].filter(Boolean).join(" ");
      const list = [name, nickname, abbreviation, city,
        ...(CITY_ALIASES[city] || []), ...(aliases ? aliases.split(";") : [])];
      // Include short canonical names in addition to explicitly listed aliases.
      const match = new Set(list.flatMap(terms));
      return Object.freeze({ id: league + ":" + index, league, name,
        city, nickname, abbreviation, aliases: match });
    });
  }

  function getTeams(league = "all") {
    const leagues = !league || league.toLowerCase() === "all" ? LEAGUES : [league.toUpperCase()];
    const names = new Set(leagues.flatMap(l => (TEAMS[l] || []).map(t => t.name)));
    return [...names].sort((a,b) => a.localeCompare(b));
  }

  function directMatch(t, query) {
    const n = norm(query), c = compact(query);
    return !!n && (t.aliases.has(n) || t.aliases.has(c));
  }

  function editDistanceUnder(a, b, limit) {
    if (Math.abs(a.length - b.length) > limit) return false;
    let previous = Array.from({ length: b.length + 1 }, (_,i) => i);
    for (let i=1;i<=a.length;i++) {
      const row = [i];
      let min = i;
      for (let j=1;j<=b.length;j++) {
        const cost = a[i-1] === b[j-1] ? 0 : 1;
        row[j] = Math.min(previous[j]+1, row[j-1]+1, previous[j-1]+cost);
        if (row[j] < min) min = row[j];
      }
      if (min > limit) return false;
      previous = row;
    }
    return previous[b.length] <= limit;
  }

  function findTeams(league, query, fuzzy = true) {
    const roster = TEAMS[String(league||"").toUpperCase()] || [];
    const q = norm(query), qc = compact(query);
    if (!qc) return [];
    const exact = roster.filter(t => directMatch(t, q));
    if (exact.length) return exact;
    // Prefix matching for full market/nickname and full team name; do NOT
    // use substring matching on 2-letter cities like LA, NY or SF.
    if (qc.length >= 3) {
      const partial = roster.filter(t => [...t.aliases].some(a => a.length >= qc.length && a.startsWith(qc)));
      if (partial.length) return partial;
    }
    // Typo fallback only when there were no exact/prefix matches, on longer
    // market/team tokens; never fuzzy-match short abbreviations.
    if (fuzzy && qc.length >= 5) {
      const limit = qc.length >= 8 ? 2 : 1;
      return roster.filter(t => [...t.aliases].some(a =>
        a.length >= 5 && a.indexOf(" ") < 0 && editDistanceUnder(qc, a, limit)));
    }
    return [];
  }

  function readGameTeams(league, game) {
    if (!game || typeof game !== "object") return [];
    const direct = [game.away_team, game.home_team].filter(Boolean);
    if (direct.length) return direct.map(String);
    if (league === "NFL" && game.slug) {
      const match = String(game.slug).match(/^(.+)-at-(.+)-\d{4}-(?:reg|post|pre)-\d+/i);
      if (match) return [match[1].replace(/-/g," "),match[2].replace(/-/g," ")];
    }
    const label = String(game.label || "").split(",")[0].replace(/^Watch Replay\s*/i, "").trim();
    const sides = label.split(/\s+(?:@|at|vs\.?|versus)\s+/i);
    return sides.length === 2 ? sides : [];
  }

  function gameTeamIds(league, game) {
    return new Set(readGameTeams(league, game)
      .flatMap(name => findTeams(league, name, false)).map(t => t.id));
  }

  function matchesSelectedTeam(league, game, selected) {
    if (!selected || selected === "all") return true;
    const teamIds = new Set(findTeams(league, selected, false).map(t => t.id));
    if (!teamIds.size) return readGameTeams(league, game).some(t => compact(t) === compact(selected));
    const actual = gameTeamIds(league, game);
    return [...teamIds].some(id => actual.has(id));
  }

  function matchesQuery(league, game, query) {
    const q = norm(query), qc = compact(query);
    if (!q) return true;
    const actual = gameTeamIds(league, game);
    const matchTerm = term => {
      const teams = findTeams(league, term);
      if (teams.length) return teams.some(t => actual.has(t.id));
      // Keep existing direct matchup / date / label searching. Short aliases
      // must never accidentally match fragments of unrelated team names.
      const text = norm([game?.label, game?.date, game?.slug,
        ...readGameTeams(league, game)].filter(Boolean).join(" "));
      const part = norm(term);
      return part.length >= 3 && text.includes(part);
    };
    // Both sides must match; e.g. "Denver vs KC" or "Yankees @ Mets".
    const sides = String(query).split(/\s+(?:vs\.?|versus|at)\s+|\s*@\s*/i)
      .map(t => t.trim()).filter(Boolean);
    if (sides.length === 2) return sides.every(matchTerm);
    return matchTerm(q);
  }

  return Object.freeze({
    LEAGUES: Object.freeze(LEAGUES), TEAMS, norm, getTeams, findTeams,
    readGameTeams, gameTeamIds, matchesSelectedTeam, matchesQuery
  });
});
