import hashlib, json, random, time
from datetime import datetime, timezone
from pathlib import Path
import requests

OUT = Path('food_venues_osm_latest.json')
HEALTH = Path('food_bulk_health.json')
BBOXES = [
  ('ha_noi',20.90,105.70,21.10,105.95),
  ('hcm',10.68,106.55,10.90,106.85),
  ('da_nang',15.95,108.05,16.15,108.30),
  ('hai_phong',20.75,106.55,20.95,106.85),
  ('can_tho',9.95,105.65,10.15,105.90),
  ('hue',16.35,107.45,16.60,107.75),
]
AMENITIES='restaurant|cafe|fast_food|food_court|ice_cream'
OVERPASS_ENDPOINTS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass.nchc.org.tw/api/interpreter',
]

def now(): return datetime.now(timezone.utc).isoformat()

def fetch(name,s,w,n,e):
    q=f'''[out:json][timeout:60];(node["amenity"~"^({AMENITIES})$"]({s},{w},{n},{e});way["amenity"~"^({AMENITIES})$"]({s},{w},{n},{e});relation["amenity"~"^({AMENITIES})$"]({s},{w},{n},{e}););out center tags;'''
    errors=[]
    endpoints=OVERPASS_ENDPOINTS[:]
    random.shuffle(endpoints)
    for attempt in range(6):
        endpoint=endpoints[attempt % len(endpoints)]
        try:
            r=requests.post(endpoint,data=q.encode(),headers={'User-Agent':'FoodAllBulkImporter/1.1 (voucherfreevn food index)','Accept-Encoding':'gzip, deflate'},timeout=90)
            if r.status_code in (429, 502, 503, 504):
                errors.append(f'{endpoint}: HTTP {r.status_code}')
                time.sleep(min(30, (2 ** attempt) + random.random() * 2))
                continue
            r.raise_for_status()
            return r.json().get('elements',[])
        except requests.RequestException as exc:
            errors.append(f'{endpoint}: {exc}')
            time.sleep(min(30, (2 ** attempt) + random.random() * 2))
    raise RuntimeError('; '.join(errors[-6:]))

def norm(el,area):
    t=el.get('tags') or {}; name=t.get('name') or t.get('name:vi')
    if not name: return None
    lat=el.get('lat') or (el.get('center') or {}).get('lat'); lng=el.get('lon') or (el.get('center') or {}).get('lon')
    ext=f"osm:{el.get('type')}:{el.get('id')}"
    addr=', '.join(x for x in [t.get('addr:housenumber'),t.get('addr:street'),t.get('addr:district'),t.get('addr:city')] if x)
    return {'external_id':ext,'name':name,'kind':'food','category':t.get('amenity'),'address':addr or None,'city':t.get('addr:city'),'district':t.get('addr:district'),'province':t.get('addr:province'),'lat':lat,'lng':lng,'phone':t.get('phone') or t.get('contact:phone'),'website':t.get('website') or t.get('contact:website'),'opening_hours':t.get('opening_hours'),'source_type':'openstreetmap','source_url':f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}",'source_hash':hashlib.sha256(ext.encode()).hexdigest(),'canonical_key':ext,'tags':sorted(set(filter(None,[t.get('cuisine'),t.get('amenity'),area]))),'last_verified_at':now()}

def main():
    rows={}; errors=[]; attempted=0
    for b in BBOXES:
        attempted+=1
        try:
            for el in fetch(*b):
                r=norm(el,b[0])
                if r: rows[r['external_id']]=r
            time.sleep(3 + random.random() * 3)
        except Exception as e: errors.append({'area':b[0],'error':str(e)[:300]})
    data=list(rows.values())
    # Never replace a healthy snapshot with a severely degraded partial scan.
    previous=[]
    if OUT.exists():
        try: previous=json.loads(OUT.read_text(encoding='utf-8'))
        except Exception: previous=[]
    degraded = bool(previous) and len(data) < max(100, int(len(previous) * 0.80))
    if not degraded:
        OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    health={'checked_at':now(),'sources_attempted':attempted,'raw_candidates':len(data),'unique_candidates':len(data),'published_candidates':len(previous) if degraded else len(data),'degraded_snapshot_blocked':degraded,'areas':[x[0] for x in BBOXES],'errors':errors}
    HEALTH.write_text(json.dumps(health,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(health,ensure_ascii=False))
    if errors and not data: raise SystemExit(2)
if __name__=='__main__': main()
