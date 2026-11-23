#!/usr/bin/env python3
"""Refresh the small Canadian calendar cache; other countries calculate locally."""
import datetime as dt
import json
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
def validate(data,year):
    rows=data.get('holidays') if isinstance(data,dict) else None
    if not isinstance(rows,list) or not 1<=len(rows)<=200:raise ValueError('Invalid holiday response')
    ids=set()
    for h in rows:
        if not isinstance(h,dict) or not isinstance(h.get('id'),int) or h['id'] in ids:raise ValueError('Duplicate or missing holiday ID')
        ids.add(h['id'])
        if not all(isinstance(h.get(k),str) and h[k] for k in ['nameEn','nameFr','date','observedDate']):raise ValueError('Missing holiday fields')
        if dt.date.fromisoformat(h['date']).year!=year:raise ValueError('Wrong source year')
        dt.date.fromisoformat(h['observedDate'])
        if h.get('federal') not in [0,1] or not isinstance(h.get('provinces'),list):raise ValueError('Invalid jurisdiction')
        for p in h['provinces']:
            if not isinstance(p,dict) or len(p.get('id',''))!=2 or not isinstance(p.get('nameEn'),str):raise ValueError('Invalid province')
    return rows

def main():
    config=json.loads((ROOT/'web/config.json').read_text());now=dt.datetime.now(dt.timezone.utc)
    cache={"schema":"coolcode.holidays.canada.v1","retrievedAt":now.isoformat().replace('+00:00','Z'),"source":"https://canada-holidays.ca/api","years":{}}
    for offset in config['seedYearOffsets']:
        year=now.year+offset
        if not config['minimumYear']<=year<=config['maximumYear']:continue
        request=urllib.request.Request(config['sources']['canadaBase']+f'?year={year}',headers={'User-Agent':'CoolCode Holiday Clock (+https://coolcode.ca/holidayclock/)','Accept':'application/json'})
        with urllib.request.urlopen(request,timeout=30) as response:
            content=response.read(2_000_001)
            if len(content)>2_000_000:raise ValueError('Source response too large')
            cache['years'][str(year)]=validate(json.loads(content),year)
    if not cache['years']:raise ValueError('No valid years configured')
    target=ROOT/'web/data/canada.json';target.parent.mkdir(exist_ok=True)
    pending=target.with_suffix('.tmp');pending.write_text(json.dumps(cache,ensure_ascii=False,separators=(',',':'))+'\n');pending.replace(target)
    print(f"Captured {len(cache['years'])} Canadian years; {sum(map(len,cache['years'].values()))} source records")
if __name__=='__main__':main()
