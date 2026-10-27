"""Read-only analysis of a private CarProbe raw-upload download.

Usage: python3 scripts/research-can-fuel.py PRIVATE_INPUT_DIRECTORY PUBLIC_JSON
Input: uploads.json from the raw/passive.v2 listing and chunks/<chunk_id>.raw.
Synthetic smoke tests are excluded. The input directory receives private
intermediates with timestamps and identifiers; the requested output contains
only aggregate evidence, with no GPS coordinates or device/session IDs.
This identifies candidate fields; it does not calibrate fuel units.
"""
from pathlib import Path
import sys
if len(sys.argv) != 3:
 raise SystemExit('Usage: research-can-fuel.py PRIVATE_INPUT_DIRECTORY PUBLIC_JSON')
import json,gzip,datetime,collections,statistics,bisect,hashlib
root=Path(sys.argv[1]);public_output=Path(sys.argv[2]);rows=json.loads((root/'uploads.json').read_text())
groups=collections.defaultdict(list)
for r in rows:
 if r['app_version']!='smoke-test':groups[(r['device_id'],r['session_id'])].append(r)
def stamp(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def stat(v):
 return {'n':len(v),'min':min(v),'median':statistics.median(v),'max':max(v)} if v else {'n':0}
counts=collections.Counter();actions=collections.Counter();layouts=collections.defaultdict(lambda:{'n':0,'sessions':set(),'payloads':collections.Counter()});kinds=collections.Counter();formats=collections.Counter();sessions=[];alltails=[];seen=set();errors=[];otherfields=collections.Counter()
for idx,(sid,chunks) in enumerate(sorted(groups.items()),1):
 events=[];previous=None;segment=0;dropped=0
 for chunk in sorted(chunks,key=lambda c:(c['created_at'],c['chunk_id'])):
  path=root/'chunks'/(chunk['chunk_id']+'.raw')
  if not path.exists():errors.append({'chunk':chunk['chunk_id'],'error':'missing'});continue
  raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in seen:counts['duplicateChunks']+=1;continue
  seen.add(sha)
  if raw[:2]==b'\x1f\x8b':raw=gzip.decompress(raw)
  counts['bytesDecompressed']+=len(raw)
  for line in raw.decode(errors='replace').splitlines():
   if not line.strip():continue
   counts['records']+=1
   try:st,j=line.split(' ',1);t=stamp(st);v=json.loads(j)
   except Exception:dropped+=1;continue
   kinds[v.get('kind','missing')]+=1
   if previous is not None and (t-previous < -3 or t-previous > 86400):segment+=1
   previous=t;ev={'t':t,'seg':segment}
   action=v.get('action');ex=v.get('extras',{});actions[str(action)]+=1
   if v.get('kind')=='GPS':
    p=v.get('payload',{});ev.update(gps=p.get('speed'),accuracy=p.get('accuracy'));events.append(ev)
   for key,val in ex.items():
    if isinstance(val,dict) and 'hex' in val:
     otherfields[(str(action),key,'byte[]')]+=1
     if action not in ['xy.auto.canbus.rxpduses','xy.auto.canbus.rxpdusesff']:continue
     formats[(str(action),key,val.get('type','?'))]+=1
     try:b=bytes.fromhex(val['hex'])
     except:counts['invalidHex']+=1;continue
     if len(b)<4 or b[0]!=46 or len(b)!=b[2]+4 or sum(b)%256!=45:counts['invalidFrames']+=1;continue
     counts['validFrames']+=1;c=b[1];d=b[3:-1];k=f'{c:02X}/'+(f'{d[0]:02X}/' if c==125 and d else '')+str(len(d))
     lay=layouts[k];lay['n']+=1;lay['sessions'].add(idx);lay['payloads'][d.hex()]+=1
     events.append(dict(ev,c=c,d=d.hex(),layout=k))
    else:otherfields[(str(action),key,type(val).__name__)]+=1
 speed=collections.defaultdict(list);od=[]
 for e in events:
  if e.get('layout')=='7D/03/5':
   b=bytes.fromhex(e['d']);speed[e['seg']].append((e['t'],int.from_bytes(b[1:3],'little')/100))
  if e.get('layout')=='7D/04/6':
   b=bytes.fromhex(e['d']);od.append({'t':e['t'],'seg':e['seg'],'odo':int.from_bytes(b[1:4],'little'),'tailLE':int.from_bytes(b[4:6],'little'),'tailBE':int.from_bytes(b[4:6],'big'),'hex':e['d']})
 for seg in speed:speed[seg].sort()
 times_by_segment={seg:[point[0] for point in points] for seg,points in speed.items()}
 for e in od:
  sp=speed[e['seg']];times=times_by_segment.get(e['seg'],[]);i=bisect.bisect_left(times,e['t']);near=sp[max(0,i-1):i+1]
  s=min(near,key=lambda s:abs(s[0]-e['t'])) if near else None
  e['speed']=s[1] if s and abs(s[0]-e['t'])<=3 else None
  alltails.append({'session':idx,**e})
 session={'index':idx,'privateId':sid,'chunks':len(chunks),'recordsKept':len(events),'dropped':dropped,'clockSegments':segment+1,'frames':sum('c' in e for e in events),'odometerSamples':od,'speed':{str(s):stat([v for _,v in points]) for s,points in speed.items()}}
 stats=[]
 for s,sp in speed.items():
  pairs=[(a,b) for a,b in zip(sp,sp[1:]) if 0<b[0]-a[0]<=3]
  km=sum((a[1]+b[1])/2*(b[0]-a[0])/3600 for a,b in pairs);sec=sum(b[0]-a[0] for a,b in pairs)
  stats.append({'seg':s,'distanceKm':km,'observedSeconds':sec,'stoppedSeconds':sum(b[0]-a[0] for a,b in pairs if a[1]<1 and b[1]<1)})
 session['observed']=stats;sessions.append(session)
 (root/f'session-{idx:03}.json').write_text(json.dumps(events))
report={'counts':dict(counts),'sessions':len(groups),'realSessionsWithFrames':sum(s['frames']>0 for s in sessions),'parseErrors':sum(s['dropped'] for s in sessions),'missing':errors,'kinds':dict(kinds),'actions':dict(actions),'layouts':{k:{'messages':v['n'],'sessions':len(v['sessions']),'distinctPayloads':len(v['payloads']),'topPayloads':v['payloads'].most_common(12)} for k,v in layouts.items()},'formats':[{'format':k,'count':v} for k,v in formats.items()],'extraFields':[{'field':k,'count':v} for k,v in otherfields.items()],'odometerSamples':alltails,'sessionDetails':sessions}
(root/'analysis-private.json').write_text(json.dumps(report,indent=2))
public={k:report[k] for k in ['counts','sessions','realSessionsWithFrames','parseErrors','extraFields']}
# Raw 7D/04 bytes encode the vehicle's absolute odometer. FF/19 may carry a
# decoder identifier, and 52/2 carries vehicle settings. Preserve aggregate
# counts for these layouts, but never their payloads.
public['layouts']={k:({field:value for field,value in layout.items() if field!='topPayloads'}
                      if k in ('7D/04/6','FF/19','52/2') else layout)
                   for k,layout in report['layouts'].items()}
public['scope']={'nonSyntheticChunks':sum(len(c) for c in groups.values()),'excludedSyntheticChunks':sum(r['app_version']=='smoke-test' for r in rows),'missingChunks':len(errors)}
public['candidate']={'layout':'7D/04/6','offsetsInData':[4,5],'littleEndianSamples':len(alltails),'sessions':len(set(x['session'] for x in alltails)),'rawRange':[min((x['tailLE'] for x in alltails),default=None),max((x['tailLE'] for x in alltails),default=None)],'unit':'unverified','stableCaptureGroups':[]}
for value in sorted(set(x['tailLE'] for x in alltails)):
 selected=[s for s in sessions if set(x['tailLE'] for x in s['odometerSamples'])=={value}]
 if not selected:continue
 stats=[a for s in selected for a in s['observed']]
 public['candidate']['stableCaptureGroups'].append({'rawValue':value,'sessions':len(selected),'observedDistanceKm':sum(a['distanceKm'] for a in stats),'observedSeconds':sum(a['observedSeconds'] for a in stats),'stoppedSeconds':sum(a['stoppedSeconds'] for a in stats),'maximumSpeedKmh':max((a['max'] for s in selected for a in s['speed'].values() if a['n']),default=None)})
public_output.write_text(json.dumps(public,indent=2)+'\n')
print(f"Analyzed {len(groups)} non-synthetic sessions, {counts['validFrames']} valid frames. Aggregate report: {public_output}")
