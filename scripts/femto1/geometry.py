"""Provisional SI centerline layout and conservative sampled DRC.

The positive-index profile, access coupling and tolerances are assumptions.
Failed layouts are retained. This module never marks a chip fabrication-ready.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from common import kappa,tree,from_ratios

STEP=10e-6
RADIUS=.025

def line(a,b):
    a,b=np.asarray(a),np.asarray(b)
    n=max(1,math.ceil(float(np.linalg.norm(b-a))/STEP))
    return a+(b-a)*np.linspace(0,1,n+1)[:,None]

def sbend(start,delta,radius=RADIUS):
    """Two circular arcs; displacement in the y/z plane, zero endpoint slopes."""
    start=np.asarray(start,dtype=float);delta=np.asarray(delta,dtype=float)
    h=float(np.linalg.norm(delta))
    if h<1e-16:return start[None,:]
    if h>=4*radius:raise ValueError('Displacement too large for S bend')
    angle=math.acos(1-h/(2*radius))
    t=np.linspace(0,angle,max(2,math.ceil(radius*angle/STEP)+1))
    xs=np.r_[radius*np.sin(t),radius*(2*np.sin(angle)-np.sin(angle-t[1:]))]
    hs=np.r_[radius*(1-np.cos(t)),h-radius*(1-np.cos(angle-t[1:]))]
    result=np.empty((len(xs),3));result[:,0]=start[0]+xs
    result[:,1:]=start[1:]+hs[:,None]*delta[None,:]/h
    result[-1,1:]=start[1:]+delta
    return result

def route(a,b):
    """S bend followed by straight; retains overshoot if available x is too short."""
    a,b=np.asarray(a),np.asarray(b)
    curve=sbend(a,b[1:]-a[1:])
    if curve[-1,0]>b[0]+1e-12:
        # Keep the route as an explicit failure, not a backward segment.
        return curve,False
    straight=line(curve[-1],b)
    return np.vstack([curve,straight[1:]]),True

def access(gap,orientation=0):
    # Two symmetric arms approach from a 100-um separation.
    h=(100e-6-gap)/2
    lower=sbend([0,-50e-6,0],[h,0])
    upper=lower.copy();upper[:,1]*=-1
    separation=upper[:,1]-lower[:,1]
    ks=np.array([kappa(float(g)) if g<=20e-6+1e-14 else 0 for g in separation])
    theta=2*float(np.trapezoid(ks,lower[:,0]))
    # Setting kappa=0 above 20um is an explicit unknown-tail approximation.
    return lower,upper,theta

def coupler_design(ratio,process_scale=1.):
    target=math.asin(math.sqrt(float(np.clip(ratio,0,1))))
    chosen=None
    for gap in np.arange(14,20.0001,.25)*1e-6:
        lo,up,theta=access(float(gap))
        effective=kappa(float(gap))*process_scale
        length=(target-theta*process_scale)/effective
        chosen={'gap_m':float(gap),'length_m':max(0.,float(length)),
                'kappa_per_m':effective,'access_angle_rad':theta*process_scale,
                'target_ratio':float(ratio),'length_nonnegative':bool(length>=-1e-12),
                'assumed_process_scale':process_scale,'access_tail_above_20um':'omitted_unknown'}
        if length>=-1e-12:break
    return chosen

def coupler_paths(center,c):
    lower,upper,_=access(c['gap_m'])
    center=np.asarray(center);span=lower[-1,0];length=c['length_m']
    paths=[]
    for approach in [lower,upper]:
        straight=line(approach[-1],approach[-1]+[length,0,0])
        leave=approach.copy();leave[:,0]=2*span+length-approach[::-1,0]
        leave[:,1:]=approach[::-1,1:]
        points=np.vstack([approach,straight[1:],leave[1:]])+center
        paths.append(points)
    return paths

def path_length(p):return float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum())

def network_matrix(geometry,zone):
    n=geometry['networks'][zone]
    ratios=np.zeros((16,3))
    for c in geometry['couplers']:
        if c['zone']==zone:
            angle=c['kappa_per_m']*c['length_m']+c['access_angle_rad']
            ratios[c['input'],c['tree_index']]=math.sin(angle)**2
    if zone=='N4':
        w=np.zeros((4,16))
        for j,(a,b,c) in enumerate(ratios):w[:,j]=[a*b,a*(1-b),(1-a)*c,(1-a)*(1-c)]
        return w
    return from_ratios(np.asarray(n['leaf_classes']),ratios)

def compile_geometry(weights):
    geo={'schema':'femto1_si_provisional_v1','units':'m','material':'fused silica',
         'scope':'PROVISIONAL_UNVALIDATED_NOT_FOR_MANUFACTURE','wavelength_m':1.55e-6,
         'block_size_m':[.045,.025,.002],'core_radius_m':6e-6,
         'provisional_profile':'12um step-index analogue; V=2.92; not supplier single-mode profile',
         'assumptions':{'min_bend_radius_m':RADIUS,'interbundle_spacing_m':30e-6,
                        'depth_range_m':[.1e-3,1.8e-3],'coherence_stagger_m':.1e-3,
                        'loss_dB_per_cm':.2,'output_detector_radius_m':100e-6},
         'networks':{},'guides':[],'couplers':[],'fiducials':[],
         'alignment_holes':[],'detectors':[],'routing_errors':[],
         'process_coupons':{'K1':'lateral/vertical pairs, gaps14/16/20um, two depths',
                            'K2':'8 straight cutback guides','K3':'S bends radii15/20/25/30/40mm'}}
    def guide(name,p,zone,beam=None,coupler=None,coupon=False):
        geo['guides'].append({'id':name,'zone':zone,'beam':beam,'coupler_id':coupler,
                              'process_coupon':coupon,'points_m':np.asarray(p).tolist(),
                              'length_m':path_length(np.asarray(p))})
        return path_length(np.asarray(p))
    for zi,(zone,w) in enumerate(weights.items()):
        base=zi*.005
        order,ratios=(np.tile(np.arange(3),(16,1)),np.full((16,3),.5)) if zone=='N4' else tree(w)
        geo['networks'][zone]={'leaf_classes':order.tolist(),'paths':[],
                               'input_grid_pitch_m':250e-6,'process_scale':1.1 if zone=='N2' else 1.}
        for klass in range(4):geo['detectors'].append({'id':f'{zone}-D{klass}','zone':zone,'class':klass,
                                                     'center_m':[.045,base+.0005+klass*.0012,.001],
                                                     'radius_m':100e-6})
        for j in range(16):
            yc=base+.0023;zc=.0002+j*75e-6
            first=coupler_design(ratios[j,0],geo['networks'][zone]['process_scale'])
            centers=[[.012,yc,zc]];couplers=[];paths=[]
            for q in range(3):
                if q:
                    parent=paths[0][1 if q==1 else 0][-1]
                    ychild=yc+(.0003 if q==1 else -.0003)
                    needed=sbend(parent,[ychild-50e-6-parent[1],0])[-1,0]
                    centers.append([needed+.0001,ychild,zc])
                c=first if q==0 else coupler_design(ratios[j,q],geo['networks'][zone]['process_scale'])
                cid=f'{zone}-I{j}-C{q}'
                c.update({'id':cid,'zone':zone,'input':j,'tree_index':q,'center_m':centers[q]})
                geo['couplers'].append(c);couplers.append(c)
                pair=coupler_paths(centers[q],c);paths.append(pair)
                for arm,p in enumerate(pair):guide(cid+f'-arm{arm}',p,zone,coupler=cid)
            input_point=[0,base+.0008+(j%4)*250e-6,.00035+(j//4)*250e-6]
            root,ok=route(input_point,paths[0][0][0])
            if not ok:geo['routing_errors'].append({'id':f'{zone}-I{j}-root','reason':'S bend exceeds available x'})
            root_length=guide(f'{zone}-I{j}-root',root,zone)
            geo['alignment_holes'].append({'center_m':input_point,'radius_m':62.5e-6,'depth_m':.0005,'zone':zone})
            link_lengths=[]
            for q,arm in [(1,1),(2,0)]:
                p,ok=route(paths[0][arm][-1],paths[q][0][0])
                if not ok:geo['routing_errors'].append({'id':f'{zone}-I{j}-link{q}','reason':'S bend exceeds available x'})
                link_lengths.append(guide(f'{zone}-I{j}-link{q}',p,zone))
            leaves=[(1,1),(1,0),(2,1),(2,0)]
            classes=list(order[j])+([3] if zone=='N4' else [None])
            for leaf,((q,arm),klass) in enumerate(zip(leaves,classes)):
                start=paths[q][arm][-1]
                if klass is None:
                    # Dedicated lateral discard face; no detector-facing endpoint.
                    end=[.044,base,zc]
                else:
                    end=[.045,base+.0005+klass*.0012+((j%4)-1.5)*25e-6,
                         .001+((j//4)-1.5)*25e-6]
                p,ok=route(start,end)
                # Side discard must actually intersect y=base, not remain inside.
                if not ok:geo['routing_errors'].append({'id':f'{zone}-I{j}-leaf{leaf}','reason':'S bend exceeds chip face'})
                beam=f'{zone}-D{klass}' if klass is not None else f'{zone}-T'
                leaf_length=guide(f'{zone}-I{j}-leaf{leaf}',p,zone,beam=beam)
                length=root_length+path_length(paths[0][0])+link_lengths[q-1]+path_length(paths[q][arm])+leaf_length
                geo['networks'][zone]['paths'].append({'input':j,'class':klass,'leaf':leaf,'length_m':length,
                                                     'endpoint_m':p[-1].tolist(),'route_complete':ok})
    # Coupons are drawn in the remaining strip and upper depth; bending below
    # network radius is intentional in K3, not a network-rule exemption.
    k1idx=0
    for orientation in ['lateral','vertical']:
        for depth in [.0003,.0012]:
            for gap_um,lengths_mm in [(14,[.5,1,2,3.3]),(16,[1,2,4,8]),(20,[5,10,20,40])]:
                for length_mm in lengths_mm:
                    y=.0203+(k1idx%12)*150e-6+(.002 if orientation=='vertical' else 0);k1idx+=1
                    cid=f'K1-{orientation}-{depth}-{gap_um}-{length_mm}'
                    for arm in range(2):
                        shift=arm*gap_um*1e-6
                        a=[.0005,y+(shift if orientation=='lateral' else 0),depth+(shift if orientation=='vertical' else 0)]
                        b=[.0005+length_mm*.001,a[1],a[2]]
                        guide(cid+f'-arm{arm}',line(a,b),'K1',coupler=cid,coupon=True)
    for length_cm in [1,2,3,4]:
        for replicate in [0,1]:
            y=.024+(length_cm*2+replicate)*80e-6
            guide(f'K2-{length_cm}-{replicate}',line([.0005,y,.00175],[.0005+length_cm*.01,y,.00175]),'K2',coupon=True)
    for i,r in enumerate([.015,.020,.025,.030,.040]):
        guide(f'K3-{r}',sbend([.0005,.0205+i*.0007,.00175],[.0003,0],r),'K3',coupon=True)
    geo['fiducials']=[{'center_m':[x,y,.001],'size_m':50e-6} for x in [0,.045] for y in [.0001,.0249]]
    return geo

def drc(geo,weights):
    errors=list(geo['routing_errors']);paths=geo['guides'];minimum_radius=math.inf
    # Bounds/depth, chord sampling, curvature and physical interaction lengths.
    for guide in paths:
        p=np.asarray(guide['points_m']);lo=p.min(0);hi=p.max(0)
        if np.any(lo< -1e-12) or np.any(hi>np.asarray(geo['block_size_m'])+1e-12):
            errors.append({'id':guide['id'],'reason':'outside provisional chip bounds','min_m':lo.tolist(),'max_m':hi.tolist()})
        if lo[2]<.0001-1e-12 or hi[2]>.0018+1e-12:
            errors.append({'id':guide['id'],'reason':'outside assumed depth range'})
        if len(p)>2:
            a=np.diff(p,axis=0)[:-1];b=np.diff(p,axis=0)[1:];c=a+b
            area2=np.linalg.norm(np.cross(a,b),axis=1)
            mask=area2>1e-24
            if np.any(mask):
                radii=np.linalg.norm(a[mask],axis=1)*np.linalg.norm(b[mask],axis=1)*np.linalg.norm(c[mask],axis=1)/(2*area2[mask])
                r=float(radii.min())
                if not guide['process_coupon']:
                    minimum_radius=min(minimum_radius,r)
                    if r<RADIUS*(1-1e-5):errors.append({'id':guide['id'],'reason':'minimum radius below 25 mm','radius_m':r})
    for c in geo['couplers']:
        if not c['length_nonnegative']:errors.append({'id':c['id'],'reason':'target below access coupling floor even at 20 um'})
    # Conservative lower bound: nearest sampled centers minus one full sample
    # spacing (two half-spacings). Only designated coupling pairs are exempt.
    arrays=[np.asarray(g['points_m']) for g in paths];boxes=[(p.min(0),p.max(0)) for p in arrays]
    spacing_pairs=[]
    for i in range(len(paths)):
        for j in range(i+1,len(paths)):
            g,h=paths[i],paths[j]
            if g['coupler_id'] and g['coupler_id']==h['coupler_id']:continue
            same_beam=g['beam'] is not None and g['beam']==h['beam']
            threshold=12e-6 if same_beam else 30e-6
            lo,hi=boxes[i];lj,hj=boxes[j]
            if np.any(lo>hj+threshold+STEP) or np.any(lj>hi+threshold+STEP):continue
            a,b=arrays[i],arrays[j]
            # Topologically connected segments share an endpoint. Exempt only
            # a short joining neighborhood, never the entire pair of guides.
            for ea in [a[0],a[-1]]:
                for eb in [b[0],b[-1]]:
                    if np.linalg.norm(ea-eb)<1e-12:
                        a=a[np.linalg.norm(a-ea,axis=1)>60e-6]
                        b=b[np.linalg.norm(b-eb,axis=1)>60e-6]
            if not len(a) or not len(b):continue
            distance=float(cKDTree(b).query(a,k=1,workers=1)[0].min())
            lower=distance-STEP
            if lower<threshold:
                spacing_pairs.append({'first':g['id'],'second':h['id'],'sample_distance_m':distance,
                                      'conservative_lower_m':lower,'required_m':threshold})
    if spacing_pairs:errors.append({'reason':'separation/intersection checks failed','count':len(spacing_pairs)})
    matrices={};coherence=[]
    for zone,w in weights.items():
        error=float(np.max(abs(network_matrix(geo,zone)-w)))
        matrices[zone]=error
        if error>1e-10:errors.append({'id':zone,'reason':'compiled transfer differs from target','error':error})
        for klass in range(4):
            selected=[p for p in geo['networks'][zone]['paths'] if p['class']==klass]
            lengths=sorted(p['length_m'] for p in selected)
            min_delta=min(np.diff(lengths)) if len(lengths)>1 else math.inf
            coherence.append({'zone':zone,'class':klass,'minimum_pair_stagger_m':float(min_delta),
                              'required_m':.0001,'passed':bool(min_delta>=.0001)})
            if min_delta<.0001:errors.append({'id':f'{zone}-D{klass}','reason':'coherence staggering below 0.1 mm','minimum_m':float(min_delta)})
            detector=next(d for d in geo['detectors'] if d['id']==f'{zone}-D{klass}')
            center=np.asarray(detector['center_m'])
            for path in selected:
                if np.linalg.norm(np.asarray(path['endpoint_m'])[1:]-center[1:])>detector['radius_m']+1e-12:
                    errors.append({'id':f'{zone}-I{path["input"]}-D{klass}','reason':'outside collection area'})
    return {'scope':'provisional rules; not supplier-certified DRC','passed':not errors,
            'error_count':len(errors),'errors':errors,'separation_failures':spacing_pairs,
            'minimum_network_radius_m':minimum_radius,'weight_max_abs_errors':matrices,
            'coherence':coherence,'guide_count':len(paths),'network_couplers':len(geo['couplers']),
            'sampling_m':STEP,'coupling_model_validated':False,'supplier_rules_confirmed':False,
            'sealed_test_ready':False,'fabrication_ready':False}
