// Offline regression tests of the Mega Board's pure stale-feed warning logic.
// Runs in Node's VM with a fixed clock and no browser/network.
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const html = fs.readFileSync("command-center/index.html", "utf8");
const start = html.indexOf("function staleFeedWarnings(");
const end = html.indexOf("function renderFreshnessWarnings(", start);
assert(start > 0 && end > start, "Pure stale-feed function must be in the Mega Board HTML");
assert(html.includes('id="freshnessWarning"'), "Warning must have a visible display target");
assert(html.includes("setInterval(renderFreshnessWarnings,60000)"), "Warnings must update every minute");
assert(html.includes("renderFreshnessWarnings()}"), "Warnings must update after feed refresh");
// Parse the full inline script so additions cannot accidentally break the dashboard.
const scriptOpen = html.lastIndexOf("<script>");
const scriptClose = html.indexOf("</script>", scriptOpen);
assert(scriptOpen >= 0 && scriptClose > scriptOpen, "Mega Board inline script missing");
new vm.Script(html.slice(scriptOpen + "<script>".length, scriptClose), {filename:"command-center/index.html"});
const config = [
    {id:"NFL", months:[8,9,10,11,12,1,2]},
    {id:"NBA", months:[10,11,12,1,2,3,4,5,6]},
    {id:"WNBA", months:[5,6,7,8,9,10]},
    {id:"NHL", months:[9,10,11,12,1,2,3,4,5,6]},
    {id:"MLB", months:[2,3,4,5,6,7,8,9,10]}
];
let month = 11;
const context = {config, Date, Number, Math, currentMonthET:()=>month};
vm.createContext(context);
vm.runInContext(html.slice(start,end),context);
assert.equal(typeof context.staleFeedWarnings, "function");
const now = Date.parse("2026-11-22T23:00:00Z");
const feed = (minutes, extras={}) => ({updated_at:new Date(now - minutes*60000).toISOString(),games:[], ...extras});
const findWarnings = data => Array.from(context.staleFeedWarnings(data, now));

assert.deepEqual(findWarnings({NFL:feed(59)}),[],"NFL feed under 60 minutes stays clear");
assert.equal(findWarnings({NFL:feed(61)}).length,1,"NFL feed over 60 minutes warned");
assert.deepEqual(findWarnings({NBA:feed(120)}),[],"NBA preserves 3-hour tolerance");
assert.equal(findWarnings({NBA:feed(181)}).length,1,"NBA feed over 3 hours warned");
assert.equal(findWarnings({NFL:{error:true,games:[]}}).length,1,"Unavailable NFL feed is warned");
assert.equal(findWarnings({NFL:{games:[]}}).length,1,"Invalid timestamp is warned");
assert.equal(findWarnings({NFL:feed(-15)}).length,1,"Future timestamps are warned");
assert.deepEqual(findWarnings({MLB:feed(300)}),[],"Offseason league is not flagged");
month=6;
assert.deepEqual(findWarnings({MLB:feed(300,{offseason:true})}),[],"Explicit offseason is not flagged");
assert.equal(findWarnings({MLB:feed(181)}).length,1,"MLB active season is monitored");
console.log("PASS Mega Board freshness: 10 scenarios");
