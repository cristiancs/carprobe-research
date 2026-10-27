# Offline read-only research. Input chunks must be concatenated in capture order.
# Output includes per-session identifiers and is PRIVATE; do not publish it.
# This is a hypothesis-validation aid, not the production parser.
import json,glob,collections,datetime,bisect,statistics,math,sys
from pathlib import Path
if len(sys.argv) != 3:
 raise SystemExit('Usage: python3 research-can.py RAW_NDJSON_DIRECTORY OUTPUT_JSON')
raw_dir=Path(sys.argv[1]);output=Path(sys.argv[2])
def ts(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def corr(x,y):
 if len(x)<3:return None
 mx=statistics.mean(x);my=statistics.mean(y);a=sum((v-mx)**2 for v in x);b=sum((v-my)**2 for v in y)
 return sum((v-mx)*(w-my) for v,w in zip(x,y))/math.sqrt(a*b) if a*b else None
def near(arr,t,maxdt=1):
 if not arr:return None
 i=bisect.bisect_left([x[0] for x in arr],t); c=arr[max(0,i-1):i+1];v=min(c,key=lambda x:abs(x[0]-t))
 return v if abs(v[0]-t)<=maxdt else None
sessions=[]
for p in glob.glob(str(raw_dir/'*.ndjson')):
 rows=[]
 for l in open(p):
  try:stamp,v=l.split(' ',1);r={'t':ts(stamp),'v':json.loads(v)}
  except:continue
  raw=r['v'].get('extras',{}).get('rxpduses',{})
  if r['v'].get('action')=='xy.auto.canbus.rxpduses' and isinstance(raw,dict):
   b=bytes.fromhex(raw.get('hex',''))
   if len(b)>=4 and b[0]==46 and len(b)==b[2]+4 and sum(b)%256==45:r['c']=b[1];r['d']=list(b[3:-1])
  rows.append(r)
 offset=0;previous=rows[0]['t'] if rows else 0;jumps=0
 for r in rows:
  wall=r['t'];delta=wall-previous
  if abs(delta)>86400:offset+=delta;jumps+=1
  r['segment']=jumps;r['wall']=wall;r['t']=wall-offset;previous=wall
 rows.sort(key=lambda r:r['t']);sessions.append((p.split('/')[-1][:-7],rows))
report={};odo=[];intervals=[];keys=collections.Counter();keypairs=collections.Counter();keydelays=[];unmatched=[];door=[];radar=[];lamps=[];gear=[];steerX=[];steerY=[];upper=collections.Counter();config=collections.Counter()
for sid,rows in sessions:
 speed=[(r['t'],int.from_bytes(bytes(r['d'][1:3]),'little')/100) for r in rows if r.get('c')==125 and len(r['d'])==5 and r['d'][0]==3]
 steering=[(r['t'],int.from_bytes(bytes(r['d'][1:3]),'little',signed=True)) for r in rows if r.get('c')==125 and len(r['d'])==3 and r['d'][0]==8]
 rxkeys=[(r['t'],r['d']) for r in rows if r.get('c')==32]
 lampbits=[(r['t'],r['d'][1]) for r in rows if r.get('c')==125 and len(r['d'])==2 and r['d'][0]==1]
 od=[(r['t'],int.from_bytes(bytes(r['d'][1:4]),'little'),int.from_bytes(bytes(r['d'][4:]),'little'),r['segment']) for r in rows if r.get('c')==125 and len(r['d'])==6 and r['d'][0]==4]
 if od:
  begin,end=od[0][0],od[-1][0];points=[s for s in speed if begin<=s[0]<=end];dist=sum((a[1]+b[1])/2*(b[0]-a[0])/3600 for a,b in zip(points,points[1:]) if 0<b[0]-a[0]<=3)
  odo.append({'session':sid,'samples':len(od),'first':od[0][1],'last':od[-1][1],'delta':od[-1][1]-od[0][1],'tailValues':sorted(set(x[2] for x in od)),'canKmBetween':round(dist,4),'negativeSteps':sum(b[1]<a[1] for a,b in zip(od,od[1:])),'span':round(end-begin,1),'clockJumps':sum(abs(b['wall']-a['wall'])>86400 for a,b in zip(rows,rows[1:])), 'gpsKmBetween':round(sum((float(a['v']['payload'].get('speed',0))+float(b['v']['payload'].get('speed',0)))/2*(b['t']-a['t'])/1000 for a,b in zip([r for r in rows if r['v'].get('kind')=='GPS' and begin<=r['t']<=end],[r for r in rows if r['v'].get('kind')=='GPS' and begin<=r['t']<=end][1:]) if 0<b['t']-a['t']<=3 and 0<float(a['v']['payload'].get('accuracy',0))<=25 and 0<float(b['v']['payload'].get('accuracy',0))<=25),4)})
 increments=[b for a,b in zip(od,od[1:]) if b[1]>a[1] and b[3]==a[3]]
 for a,b in zip(increments,increments[1:]):
  if a[3]!=b[3] or b[0]<=a[0] or b[1]<=a[1]:continue
  sp=[r for r in rows if r.get('c')==125 and len(r['d'])==5 and r['d'][0]==3 and r['segment']==a[3] and a[0]<=r['t']<=b[0]]
  pairs=[(x,y) for x,y in zip(sp,sp[1:]) if 0<y['t']-x['t']<=3]
  km=sum((int.from_bytes(bytes(x['d'][1:3]),'little')+int.from_bytes(bytes(y['d'][1:3]),'little'))/200*(y['t']-x['t'])/3600 for x,y in pairs)
  gp=[r for r in rows if r['v'].get('kind')=='GPS' and r['segment']==a[3] and a[0]<=r['t']<=b[0]]
  gpair=[(x,y) for x,y in zip(gp,gp[1:]) if 0<y['t']-x['t']<=3 and 0<float(x['v']['payload'].get('accuracy',0))<=25 and 0<float(y['v']['payload'].get('accuracy',0))<=25]
  gkm=sum((float(x['v']['payload'].get('speed',0))+float(y['v']['payload'].get('speed',0)))/2*(y['t']-x['t'])/1000 for x,y in gpair)
  intervals.append({'session':sid,'delta':b[1]-a[1],'seconds':b[0]-a[0],'canKm':km,'canCoverage':sum(y['t']-x['t'] for x,y in pairs)/(b[0]-a[0]),'gpsKm':gkm,'gpsCoverage':sum(y['t']-x['t'] for x,y in gpair)/(b[0]-a[0])})
 for r in rows:
  d=r.get('d',[]);c=r.get('c');v=r['v'];t=r['t']
  if c==125 and len(d)==5 and d[0]==3:upper[tuple(d[3:])]+=1
  if c==41 and len(d)==2:
   s=near(steering,t,.2)
   if s:steerX.append(int.from_bytes(bytes(d),'big',signed=True));steerY.append(s[1])
  if c==58:
   s=near(speed,t,3);door.append({'session':sid,'data':d,'speed':s[1] if s else None})
  if c==34:
   s=near(speed,t,3);radar.append({'data':d,'speed':s[1] if s else None})
  if c==82:config[tuple(d)]+=1
  if v.get('action')=='xy.xygala.lamplet':
   s=near(lampbits,t,1);lamps.append({'state':v['extras'].get('lamplet_state'),'can':s[1] if s else None,'delay':round(s[0]-t,3) if s else None})
  if v.get('action')=='canbus.intent.action.key':
   h=v['extras'].get('canbus_key',{}).get('hex','');keys[h]+=1
   s=near(rxkeys,t,.5)
   if s:keypairs[(bytes(s[1]).hex(),h)]+=1;keydelays.append(t-s[0])
   else:unmatched.append(h)
report['odometerIntervals']=intervals;report['odometer']=odo;report['odometerCorrelation']=corr([x['delta'] for x in odo if x['samples']>1],[x['canKmBetween'] for x in odo if x['samples']>1]);report['keyValues']=dict(keys);report['keyPairs']=[{'raw':k[0],'broadcast':k[1],'count':v} for k,v in keypairs.items()];report['unmatchedKeys']=dict(collections.Counter(unmatched));report['lampPairs']=lamps;report['radar']={'count':len(radar),'withSpeed':sum(x['speed'] is not None for x in radar),'maxSpeed':max(x['speed'] for x in radar if x['speed'] is not None),'speedMedian':statistics.median(x['speed'] for x in radar if x['speed'] is not None),'values':[{'data':list(k),'count':v}for k,v in collections.Counter(tuple(x['data']) for x in radar).items()]};report['doors']={'count':len(door),'withSpeed':sum(x['speed'] is not None for x in door),'maxSpeed':max(x['speed'] for x in door if x['speed'] is not None),'values':[{'data':list(k),'count':v}for k,v in collections.Counter(tuple(x['data']) for x in door).items()]};report['steering']={'pairs':len(steerX),'pearson':corr(steerX,steerY)};report['speedUpperBytes']=[{'bytes':list(k),'count':v}for k,v in upper.items()];report['configuration']=[{'data':list(k),'count':v}for k,v in config.items()]
good_can=[x for x in intervals if x['canCoverage']>=.9]
good_gps=[x for x in intervals if x['gpsCoverage']>=.9]
report['summary']={
 'sessions':len(sessions),'records':sum(len(rows) for _,rows in sessions),
 'validCanFrames':sum('c' in r for _,rows in sessions for r in rows),
 'odometerSamples':sum(x['samples'] for x in odo),'odometerSessions':len(odo),
 'odometerRangeKm':[min((x['first'] for x in odo),default=None),max((x['last'] for x in odo),default=None)],
 'odometerAggregateDeltaKm':sum(x['delta'] for x in odo),
 'canAggregateKm':sum(x['canKmBetween'] for x in odo),
 'canIntervals90pct':len(good_can),
 'canIntervalMedianAbsoluteErrorM':statistics.median(abs(x['delta']-x['canKm'])*1000 for x in good_can) if good_can else None,
 'canIntervalMaxAbsoluteErrorM':max((abs(x['delta']-x['canKm'])*1000 for x in good_can),default=None),
 'gpsIntervals90pct':len(good_gps),
 'gpsIntervalMedianAbsoluteErrorM':statistics.median(abs(x['delta']-x['gpsKm'])*1000 for x in good_gps) if good_gps else None,
 'lampBroadcasts':len(lamps),'lampOnPairs':dict(collections.Counter(str(x['can']) for x in lamps if x['state']=='1')),
 'keyMessages':sum(keys.values()),'keyUnmatchedWithin500ms':len(unmatched)
}
output.write_text(json.dumps(report,indent=2));print(f'Analyzed {len(sessions)} sessions; report written to {output}')
