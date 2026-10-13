import os
for n in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[n]='1'
from pathlib import Path
import json,time,collections
import numpy as np
from scipy.spatial import cKDTree
r=json.loads(Path('resultados/codex/femto1_layout_20261013_v2/DRC.json').read_text());g=json.loads(Path(r['geometry_path']).read_text());byid={x['id']:x for x in g['guides']};pairs=[p for p in r['separation_failures'] if p['sample_distance_m']>=p['required_m']]
def nearest_segment(a,b,threshold):
 for ea in [a[0],a[-1]]:
  for eb in [b[0],b[-1]]:
   if np.linalg.norm(ea-eb)<1e-12:
    a=a[np.linalg.norm(a-ea,axis=1)>60e-6];b=b[np.linalg.norm(b-eb,axis=1)>60e-6]
 if len(a)<2 or len(b)<2:return None
 av=np.diff(a,axis=0);bv=np.diff(b,axis=0);am=(a[:-1]+a[1:])/2;bm=(b[:-1]+b[1:])/2
 radius=threshold+np.linalg.norm(av,axis=1).max()/2+np.linalg.norm(bv,axis=1).max()/2
 neighbors=cKDTree(bm).query_ball_point(am,radius,workers=1)
 ia=np.repeat(np.arange(len(am)),[len(v) for v in neighbors]);ib=np.asarray([i for v in neighbors for i in v],int)
 if not len(ia):return None
 aa=a[ia];bb=b[ib];u=av[ia];v=bv[ib];w=aa-bb
 A=np.einsum('ij,ij->i',u,u);B=np.einsum('ij,ij->i',u,v);C=np.einsum('ij,ij->i',v,v);D=np.einsum('ij,ij->i',u,w);E=np.einsum('ij,ij->i',v,w)
 def endpoint(point,s,e):
  edge=e-s;t=np.clip(np.einsum('ij,ij->i',point-s,edge)/np.maximum(np.einsum('ij,ij->i',edge,edge),1e-30),0,1)
  return np.linalg.norm(point-s-t[:,None]*edge,axis=1)
 values=np.minimum.reduce([endpoint(aa,bb,bb+v),endpoint(aa+u,bb,bb+v),endpoint(bb,aa,aa+u),endpoint(bb+v,aa,aa+u)])
 den=A*C-B*B;mask=den>1e-30
 s=(B*E-C*D)/np.where(mask,den,1);t=(A*E-B*D)/np.where(mask,den,1);interior=mask&(s>=0)&(s<=1)&(t>=0)&(t<=1)
 values[interior]=np.minimum(values[interior],np.linalg.norm(w[interior]+s[interior,None]*u[interior]-t[interior,None]*v[interior],axis=1))
 return float(values.min())
start=time.perf_counter();confirmed=[];not_proven=[]
for p in pairs:
 a=np.asarray(byid[p['first']]['points_m']);b=np.asarray(byid[p['second']]['points_m']);distance=nearest_segment(a,b,p['required_m'])
 value={'first':p['first'],'second':p['second'],'required_m':p['required_m'],'exact_polyline_distance_m':distance}
 (confirmed if distance is not None and distance<p['required_m'] else not_proven).append(value)
print(json.dumps({'scope':'Exact distance of saved polylines after same endpoint exclusions as DRC; not physical coupling solver','conservative_pairs_checked':len(pairs),'additional_true_polyline_rule_violations':len(confirmed),'conservative_false_positives_at_polyline_rule':len(not_proven),'false_positive_examples':not_proven[:4],'additional_true_violation_examples':confirmed[:4],'elapsed_s':time.perf_counter()-start}))
