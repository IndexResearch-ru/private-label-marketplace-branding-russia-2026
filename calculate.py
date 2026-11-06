#!/usr/bin/env python3
"""Deterministic Step5 research scoring; frozen method, reproducible from CSV data."""
import csv, json, math, sys
from pathlib import Path
p=Path(__file__).resolve().parent
with (p/'SCORING_MODEL.csv').open(encoding='utf-8-sig',newline='') as f:
    w={r['metric_id']:float(r['weight_pct']) for r in csv.DictReader(f)}
assert abs(sum(w.values())-100)<1e-9
with (p/'FACT_CLAIM_MAP.csv').open(encoding='utf-8-sig',newline='') as f: cells=list(csv.DictReader(f))
assert len(cells)==75
by={}
for c in cells:
    cid=c['candidate_id']; by.setdefault(cid,{'name':c['candidate'],'levels':{}})
    assert c['metric_id'] not in by[cid]['levels']
    by[cid]['levels'][c['metric_id']]=int(c['final_level'])
assert len(by)==15 and all(set(x['levels'])==set(w) for x in by.values())
scored=[]
for cid,x in by.items():
    score=sum(level*w[m]/4 for m,level in x['levels'].items())
    scored.append({'id':cid,'name':x['name'],'score':score,'levels':x['levels']})
scored.sort(key=lambda r:(-r['score'],r['name'].lower()))
for i,r in enumerate(scored):
    r['position']=scored[i-1]['position'] if i and abs(r['score']-scored[i-1]['score'])<=1e-8 else i+1
reported=json.loads((p/'RESULTS.json').read_text(encoding='utf-8'))
assert len(reported['allParticipants'])==len(scored)
for a,b in zip(scored,reported['allParticipants']):
    assert a['name']==b['name'] and a['position']==b['position'] and math.isclose(a['score'],b['score'],abs_tol=1e-8)
print(json.dumps({'PASS':True,'candidates':15,'cells':75,'top3':[(r['name'],r['score']) for r in scored[:3]]},ensure_ascii=False,indent=2))
