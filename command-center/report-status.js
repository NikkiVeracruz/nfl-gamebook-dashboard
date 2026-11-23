"use strict";
// Display-only status model. Existing league monitors verify official links before
// publishing them; MLB additionally requires its explicit official API marker.
// This module does not make network requests or change archive eligibility.
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.MegaReports = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const required = Object.freeze({
    NFL: [{keys:["pdf_url"], label:"Official gamebook PDF", kind:"PDF"}],
    NBA: [{keys:["pdf_url"], label:"Official gamebook PDF", kind:"PDF"}],
    WNBA: [{keys:["pdf_url"], label:"Official gamebook PDF", kind:"PDF"}],
    NHL: [
      {keys:["gs_url"], label:"Game Summary", kind:"GS"},
      {keys:["es_url"], label:"Event Summary", kind:"ES"}
    ],
    MLB: [
      {keys:["box_url","boxscore_url"], label:"Box score", kind:"box"},
      {keys:["plays_url","play_url","playbyplay_url"], label:"Play-by-play", kind:"plays"}
    ]
  });

  function httpsUrl(raw) {
    try {
      const url = new URL(raw);
      return url.protocol === "https:" ? url : null;
    } catch { return null; }
  }
  function officialVerified(game, league, kind, parsed) {
    if (!parsed) return false;
    const host = parsed.hostname.toLowerCase();
    const path = parsed.pathname;
    if (league === "NFL") {
      return host === "static.www.nfl.com"
        && /^\/image\/upload\/.+\/gamecenter\/.+\.pdf$/i.test(path);
    }
    if (league === "NBA" || league === "WNBA") {
      return host === "statsdmz.nba.com"
        && /^\/pdfs\/\d{8}\/\d{8}_[A-Z0-9]+_book\.pdf$/i.test(path)
        && (!game.date || path.startsWith("/pdfs/" + String(game.date).replace(/-/g,"") + "/"));
    }
    if (league === "NHL") {
      const id = String(game.id || "");
      if (!/^\d{10}$/.test(id) || host !== "www.nhl.com") return false;
      const year = Number(id.slice(0,4));
      const expected = "/scores/htmlreports/" + year + (year+1) + "/" + kind + id.slice(4) + ".HTM";
      return path.toUpperCase() === expected.toUpperCase();
    }
    if (league === "MLB") {
      const id = String(game.id || "");
      return game.link_verification === "verified_api" && /^\d+$/.test(id)
        && host === "www.mlb.com"
        && path === "/gameday/" + id + (kind === "box" ? "/box-score" : "/play-by-play");
    }
    return false;
  }
  function assess(game, league) {
    const specs = required[league] || [];
    const docs = specs.map(spec => {
      const link = spec.keys.map(key => httpsUrl(game?.[key])).find(Boolean) || null;
      const verified = officialVerified(game || {}, league, spec.kind, link);
      return {label:spec.label, url:link?.href || null, verified,
        state:!link ? "Awaiting" : verified ? "Verified" : "Verification pending"};
    });
    const total = docs.length;
    const available = docs.filter(doc => doc.url).length;
    const verified = docs.filter(doc => doc.verified).length;
    const category = !available ? "waiting"
      : verified === total && total > 0 ? "verified"
      : verified > 0 && verified < total ? "partial"
      : "pending";
    let label;
    if (category === "verified") label = "All required reports verified — " + verified + " of " + total;
    else if (category === "partial") label = "Partial reports — " + verified + " of " + total + " available";
    else if (category === "pending") label = "Verification pending — " + available + " of " + total + " links found";
    else label = total === 1 ? "Awaiting official gamebook" : "Awaiting reports";
    return {category, label, docs, total, available, verified};
  }
  return {assess, required};
});
