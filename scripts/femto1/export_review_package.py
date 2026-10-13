"""F7 preparation only. Provisional centerlines; no manufacturing-ready claim."""
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from common import sha,write_json,kappa,from_ratios

def convert(value):
    if isinstance(value,dict):
        out={}
        for key,item in value.items():
            if key.endswith('_per_m'):
                out[key[:-6]+'_per_um']=float(item)/1e6
            elif key.endswith('_m'):
                def scale(v):return [scale(x) for x in v] if isinstance(v,list) else v*1e6
                out[key[:-2]+'_um']=scale(item)
            else:out[key]=convert(item)
        return out
    if isinstance(value,list):return [convert(v) for v in value]
    return value

def stream_hash(path):
    import hashlib
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--geometry',type=Path,required=True)
    p.add_argument('--drc',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError('Keep previous candidate packages')
    a.out.mkdir(parents=True)
    geo=json.loads(a.geometry.read_text(encoding='utf-8'))
    public=convert(geo);public['units']='um for coordinates/lengths; 1/um for kappa; angles radians'
    public['source_SI_sha256']=stream_hash(a.geometry)
    public['status']='REVIEW_ONLY_DRC_FAILED_NOT_FOR_MANUFACTURE'
    write_json(a.out/'FEMTO1_candidate_geometry_um.json',public)
    filename=a.out/'FEMTO1_candidate_trajectories.csv'
    with filename.open('x',encoding='utf-8',newline='') as f:
        writer=csv.writer(f);writer.writerow(['guide_id','segment_id','type','x_um','y_um','z_um','zone','beam'])
        for guide in geo['guides']:
            pts=np.asarray(guide['points_m'])
            for i,point in enumerate(pts):
                kind='coupler' if guide['coupler_id'] else ('straight' if i==0 or np.allclose(point[1:],pts[max(0,i-1),1:],atol=1e-16,rtol=0) else 'bend')
                writer.writerow([guide['id'],i,kind,*[format(v*1e6,'.17g') for v in point],guide['zone'],guide['beam'] or ''])
    # Reimport and compare every coordinate; separately reconstruct interactions
    # from CSV parallel sections and separations, not stored target ratios.
    originals={g['id']:g for g in geo['guides']};coupler_points={};max_error=0.;rows=0
    with filename.open(encoding='utf8',newline='') as f:
        for row in csv.DictReader(f):
            gid=row['guide_id'];idx=int(row['segment_id'])
            point=np.array([float(row[n])*1e-6 for n in ['x_um','y_um','z_um']])
            max_error=max(max_error,float(abs(point-np.asarray(originals[gid]['points_m'][idx])).max()));rows+=1
            if originals[gid]['coupler_id'] and originals[gid]['zone'] in ['N1','N2','N3','N4']:
                coupler_points.setdefault(gid,[]).append(point)
    ratios={zone:np.zeros((16,3)) for zone in geo['networks']}
    for c in geo['couplers']:
        lo=np.array(coupler_points[c['id']+'-arm0']);up=np.array(coupler_points[c['id']+'-arm1'])
        separation=up[:,1]-lo[:,1]
        ks=np.array([kappa(float(np.clip(g,14e-6,20e-6))) if g<=20e-6+1e-14 else 0 for g in separation])
        angle=float(np.trapezoid(ks,lo[:,0]))*c['assumed_process_scale']
        ratios[c['zone']][c['input'],c['tree_index']]=math.sin(angle)**2
    weight_errors={}
    from geometry import network_matrix
    for zone in geo['networks']:
        rr=ratios[zone]
        if zone=='N4':
            w=np.array([[a*b,a*(1-b),(1-a)*c,(1-a)*(1-c)] for a,b,c in rr]).T
        else:w=from_ratios(np.array(geo['networks'][zone]['leaf_classes']),rr)
        weight_errors[zone]=float(abs(w-network_matrix(geo,zone)).max())
    # Standard ASCII 3D POLYLINE entities. External CAD-library reimport remains
    # pending; do not confuse successful writing with an accepted CAM format.
    dxf=a.out/'FEMTO1_candidate_centerlines.dxf'
    with dxf.open('x',encoding='ascii',newline='\n') as f:
        f.write('0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n')
        for guide in geo['guides']:
            f.write('0\nPOLYLINE\n8\n'+guide['zone']+'\n66\n1\n70\n8\n10\n0\n20\n0\n30\n0\n')
            for point in guide['points_m']:
                f.write('0\nVERTEX\n8\n'+guide['zone']+'\n70\n32\n')
                for code,value in zip([10,20,30],point):f.write(str(code)+'\n'+format(value*1e6,'.17g')+'\n')
            f.write('0\nSEQEND\n')
        f.write('0\nENDSEC\n0\nEOF\n')
    drawing_csv=a.out/'coupler_specification.csv'
    with drawing_csv.open('x',encoding='utf8',newline='') as f:
        writer=csv.writer(f);writer.writerow(['id','zone','input','tree_index','gap_um','interaction_length_um','target_ratio','access_angle_rad','assumed_process_scale'])
        for c in geo['couplers']:writer.writerow([c['id'],c['zone'],c['input'],c['tree_index'],c['gap_m']*1e6,c['length_m']*1e6,c['target_ratio'],c['access_angle_rad'],c['assumed_process_scale']])
    result={'source_geometry_sha256':stream_hash(a.geometry),'source_DRC_sha256':stream_hash(a.drc),
            'CSV_rows':rows,'CSV_max_abs_error_um':max_error*1e6,'CSV_transfer_errors':weight_errors,
            'CSV_reimport_passed':bool(max_error*1e6<=.01 and max(weight_errors.values())<=1e-10),
            'DXF_units':'um by package convention; confirm CAD import explicitly','DXF_independent_reimport_passed':False,
            'STEP_available':False,'STL_full_geometry_available':False,'Blender_authority_roundtrip_completed':False,
            'manifest_signed_by_owner':False,'F7_passed':False,'fabrication_ready':False,
            'pending':['STEP and full STL after valid Blender/CAD geometry',
                       'independent STEP/DXF reimport and CAM format confirmation',
                       'source geometry from verified Blender objects','resolved DRC/physical gates']}
    write_json(a.out/'REIMPORT-REVIEW.json',result)
    print(json.dumps(result))

if __name__=='__main__':main()
