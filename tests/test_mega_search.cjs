"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const search = require("../command-center/search.js");

const totals = {NFL:32, NBA:30, WNBA:15, NHL:32, MLB:30};
const sample = (label, extras={}) => ({label,date:"2026-11-22", ...extras});

test("Every 2026 league has a team directory with zero games", () => {
  for (const [league,count] of Object.entries(totals)) {
    assert.equal(search.TEAMS[league].length, count, league);
    assert.equal(search.getTeams(league).length, count, league);
  }
  assert.ok(search.getTeams("all").length >= 130);
  assert.ok(search.getTeams("WNBA").includes("Portland Fire"));
  assert.ok(search.getTeams("WNBA").includes("Toronto Tempo"));
  assert.ok(search.getTeams("MLB").includes("Athletics"));
  assert.ok(search.getTeams("NHL").includes("Utah Mammoth"));
});

test("City names and common abbreviations resolve teams in every league", () => {
  const checks = [
    ["NFL","DEN","Denver Broncos"],
    ["NFL","NYC","New York Jets"],
    ["NFL","LA","Los Angeles Chargers"],
    ["NBA","Denver","Denver Nuggets"],
    ["NBA","SF","Golden State Warriors"],
    ["NBA","NY","Brooklyn Nets"],
    ["WNBA","SF","Golden State Valkyries"],
    ["WNBA","PDX","Portland Fire"],
    ["WNBA","Toronto","Toronto Tempo"],
    ["WNBA","NYC","New York Liberty"],
    ["NHL","DEN","Colorado Avalanche"],
    ["NHL","SLC","Utah Mammoth"],
    ["NHL","DC","Washington Capitals"],
    ["MLB","Denver","Colorado Rockies"],
    ["MLB","SF","San Francisco Giants"],
    ["MLB","SAC","Athletics"],
    ["MLB","NYC","New York Mets"],
    ["MLB","LAD","Los Angeles Dodgers"],
  ];
  for (const [league,query,expected] of checks) {
    assert.ok(search.findTeams(league,query).some(t => t.name === expected),
      league + " " + query + " -> " + expected);
  }
  assert.deepEqual(search.findTeams("WNBA","LA").map(x=>x.name), ["Los Angeles Sparks"]);
  assert.equal(search.findTeams("NHL","Denver").length, 1);
});

test("Active and archived matchups match market, nickname, abbreviation and typo", () => {
  const game = sample("Denver Nuggets @ Los Angeles Lakers");
  for (const q of ["DEN", "Denver", "Nuggets", "LAL", "LA", "Los Angeles", "Denvar",
                  "Nuggets @ Lakers", "Denver vs Los Angeles"]) {
    assert.equal(search.matchesQuery("NBA",game,q),true,"Match " + q);
  }
  assert.equal(search.matchesQuery("NBA",game,"New York"),false);
  assert.equal(search.matchesQuery("NBA",game,"Denver vs Miami"),false);
  assert.equal(search.matchesQuery("NBA",game,"DEN @ LAL"),true);
});

test("NFL slugs allow search when labels show only scores", () => {
  const game = sample("Watch Replay, Broncos 26, Chiefs 23, Sunday", {
    slug:"broncos-at-chiefs-2026-reg-11"
  });
  assert.deepEqual(search.readGameTeams("NFL",game),["broncos","chiefs"]);
  assert.equal(search.matchesQuery("NFL",game,"Denver"),true);
  assert.equal(search.matchesQuery("NFL",game,"KC"),true);
  assert.equal(search.matchesQuery("NFL",game,"Broncos vs Chiefs"),true);
  assert.equal(search.matchesQuery("NFL",game,"Lakers"),false);
  assert.equal(search.matchesSelectedTeam("NFL",game,"Denver Broncos"),true);
  assert.equal(search.matchesSelectedTeam("NFL",game,"New York Giants"),false);
});

test("Dropdown team selection uses identity, not literal label text", () => {
  const nhl = sample("Avalanche @ Mammoth");
  assert.equal(search.matchesSelectedTeam("NHL",nhl,"Colorado Avalanche"),true);
  assert.equal(search.matchesSelectedTeam("NHL",nhl,"Utah Mammoth"),true);
  assert.equal(search.matchesSelectedTeam("NHL",nhl,"New York Rangers"),false);
  const mlb = sample("Athletics @ Dodgers");
  assert.equal(search.matchesSelectedTeam("MLB",mlb,"Athletics"),true);
  assert.equal(search.matchesSelectedTeam("MLB",mlb,"Los Angeles Dodgers"),true);
  assert.equal(search.matchesQuery("MLB",mlb,"Sacramento"),true);
});

test("Empty WNBA and MLB feeds do not affect team search", () => {
  assert.equal(search.getTeams("WNBA").length,15);
  assert.equal(search.getTeams("MLB").length,30);
  const wnba = sample("Portland Fire @ Toronto Tempo");
  assert.equal(search.matchesQuery("WNBA",wnba,"PDX"),true);
  assert.equal(search.matchesSelectedTeam("WNBA",wnba,"Portland Fire"),true);
  assert.equal(search.matchesQuery("WNBA",wnba,"Toronto"),true);
  assert.equal(search.matchesSelectedTeam("WNBA",wnba,"Atlanta Dream"),false);
});

test("Overlapping city aliases are league scoped and not partial substrings", () => {
  const dallas = sample("Dallas Wings @ Atlanta Dream");
  assert.equal(search.matchesQuery("WNBA",dallas,"LA"),false);
  assert.equal(search.matchesQuery("WNBA",dallas,"NY"),false);
  assert.equal(search.matchesQuery("WNBA",dallas,"ATL"),true);
  assert.deepEqual(search.findTeams("MLB","LA").map(t=>t.name).sort(),
    ["Los Angeles Angels", "Los Angeles Dodgers"]);
  assert.equal(search.matchesQuery("MLB",sample("New York Yankees @ Boston Red Sox"),"NYC"),true);
  assert.equal(search.matchesQuery("NBA",sample("Brooklyn Nets @ New York Knicks"),"NYC"),true);
});

test("NCAA does not appear", () => {
  assert.deepEqual(search.getTeams("NCAA"),[]);
  assert.deepEqual(search.findTeams("NCAA","Denver"),[]);
});

test("Typo search applies to long expressions, not short abbreviations", () => {
  assert.equal(search.findTeams("MLB","Denvar").some(t=>t.name==="Colorado Rockies"),true);
  assert.equal(search.findTeams("MLB","LA").length,2);
  assert.equal(search.findTeams("MLB","B").length,0);
});
