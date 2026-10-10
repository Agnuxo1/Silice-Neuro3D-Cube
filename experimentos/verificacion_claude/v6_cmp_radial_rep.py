import json
a=json.load(open('../radial2_claude/resultados_radial2.json'))
b=json.load(open('v6_rep/radial2_claude/resultados_radial2.json'))
mx=[0,'']
nd=[]
def walk(x,y,p=''):
    if isinstance(x,dict):
        for k in x:
            if k in ('runtime_s','contract_r2_sha256','contract_r1_sha256','ecs_json_sha256','ecs_src_sha256'): continue
            if k not in y: nd.append(('falta',p+'/'+k)); continue
            walk(x[k],y[k],p+'/'+k)
    elif isinstance(x,list):
        for i,(u,v) in enumerate(zip(x,y)): walk(u,v,p+f'[{i}]')
    elif isinstance(x,(int,float)) and not isinstance(x,bool) and isinstance(y,(int,float)):
        d=abs(x-y)/max(abs(x),1e-300)
        if d>mx[0]: mx[0]=d; mx[1]=p
    elif x!=y: nd.append((p,str(x)[:50],str(y)[:50]))
walk(a,b)
print('max rel diff',mx); print('no numericos distintos',nd[:10])
print(a['status'],b['status']); print(a['criterios_r2']==b['criterios_r2'])
print(a['contract_r2_sha256'],b['contract_r2_sha256'])
