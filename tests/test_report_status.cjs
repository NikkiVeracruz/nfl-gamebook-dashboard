"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const reports=require("../command-center/report-status.js");

const doc=(kind,id="2026020377") =>
  "https://www.nhl.com/scores/htmlreports/20262027/"+kind+id.slice(4)+".HTM";
const mlb=(id="748123") => ({
  id, status:"Final", box_url:"https://www.mlb.com/gameday/"+id+"/box-score",
  plays_url:"https://www.mlb.com/gameday/"+id+"/play-by-play",
  link_verification:"verified_api"
});

test("all five leagues have only the required official document types",()=>{
  assert.deepEqual(Object.fromEntries(Object.entries(reports.required)
    .map(([league,items])=>[league,items.map(i=>i.label)])),{
      NFL:["Official gamebook PDF"],NBA:["Official gamebook PDF"],
      WNBA:["Official gamebook PDF"],
      NHL:["Game Summary","Event Summary"],
      MLB:["Box score","Play-by-play"]
    });
});

test("NHL: partial Game Summary stays partial, not complete",()=>{
  const partial=reports.assess({id:"2026020377",gs_url:doc("GS")},"NHL");
  assert.equal(partial.category,"partial");
  assert.equal(partial.label,"Partial reports — 1 of 2 available");
  assert.equal(partial.docs[0].state,"Verified");
  assert.equal(partial.docs[1].state,"Awaiting");
  const complete=reports.assess({id:"2026020377",gs_url:doc("GS"),es_url:doc("ES")},"NHL");
  assert.equal(complete.category,"verified");
  assert.equal(complete.label,"All required reports verified — 2 of 2");
  assert.equal(complete.verified,2);
});

test("NHL: no URLs and wrongly associated report IDs are never verified",()=>{
  assert.equal(reports.assess({id:"2026020377"},"NHL").label,"Awaiting reports");
  const wrong=reports.assess({id:"2026020378",gs_url:doc("GS")},"NHL");
  assert.equal(wrong.category,"pending");
  assert.equal(wrong.docs[0].state,"Verification pending");
});

test("MLB: verification needs both links and official API proof",()=>{
  assert.equal(reports.assess(mlb(),"MLB").category,"verified");
  assert.equal(reports.assess({...mlb(),link_verification:undefined},"MLB").category,"pending");
  assert.equal(reports.assess({...mlb(),plays_url:undefined},"MLB").category,"partial");
  assert.equal(reports.assess({...mlb(),plays_url:"https://example.org/played"},"MLB").category,"pending");
  const duplicate={...mlb(),play_url:"https://www.mlb.com/gameday/748123/play-by-play"};
  assert.equal(reports.assess(duplicate,"MLB").docs.length,2);
});

test("NFL: distinguish awaiting gamebook from verified official PDF",()=>{
  const empty=reports.assess({},"NFL");
  assert.equal(empty.category,"waiting");
  assert.equal(empty.label,"Awaiting official gamebook");
  const found=reports.assess({pdf_url:"https://static.www.nfl.com/image/upload/v1795382014/gamecenter/ab999586-4feb-11f1-abca-2c54536568a9.pdf"},"NFL");
  assert.equal(found.category,"verified");
  assert.equal(found.label,"All required reports verified — 1 of 1");
  assert.equal(reports.assess({pdf_url:"https://example.com/fake.pdf"},"NFL").category,"pending");
});

test("NBA and WNBA: accept monitored PDF format; reject guessed/unverified domains",()=>{
  const game={date:"2026-11-22",pdf_url:"https://statsdmz.nba.com/pdfs/20261122/20261122_BOSGSW_book.pdf"};
  assert.equal(reports.assess(game,"NBA").category,"verified");
  assert.equal(reports.assess(game,"WNBA").category,"verified");
  assert.equal(reports.assess({...game,date:"2026-11-23"},"NBA").category,"pending");
  assert.equal(reports.assess({...game,pdf_url:"https://statsdmz.evil.example/pdfs/20261122/20261122_BOSGSW_book.pdf"},"NBA").category,"pending");
  assert.equal(reports.assess({...game,pdf_url:"http://statsdmz.nba.com/test.pdf"},"NBA").category,"waiting");
});

test("Mega Board integrates the status model, counts, filters and existing clocks",()=>{
  const html=fs.readFileSync(path.join(__dirname,"../command-center/index.html"),"utf8");
  for(const text of [
    'src="./report-status.js"',"MegaReports.assess(g,l)",'id="partial"',
    'Complete report sets','Partial reports','Final, awaiting reports',
    '<option value="verified">','<option value="partial">','<option value="pending">',
    '<option value="waiting">','<option value="live">','<option value="scheduled">',
    "report.docs","doc.state",
    "const info=statusFor(g,l);const matchesStatus",
    'setInterval(updateClocks,15000);setInterval(refresh,300000)'
  ]) assert.ok(html.includes(text),"Missing report status integration: "+text);
  assert.ok(!html.includes("NCAA"),"Removed NCAA must not reappear");
});

test("NFL: official extensionless Packers gamebook requires identity proof",()=>{
  const g={pdf_url:"https://static.clubs.nfl.com/image/upload/packers/abc",pdf_verification:"official_club_identity"};
  assert.equal(reports.assess(g,"NFL").category,"verified");
  assert.equal(reports.assess({...g,pdf_verification:undefined},"NFL").category,"pending");
  assert.equal(reports.assess({...g,pdf_url:"https://static.clubs.nfl.com/image/upload/unknown/abc"},"NFL").category,"pending");
});
