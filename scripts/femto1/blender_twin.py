"""F4 preparation: SI double properties in Blender, render curves in float32.

Run only through an exclusive resource reservation. The authoritative scientific
coordinates are double-valued object properties. Blender's visible curve points
are float32 and their deviation is checked and reported separately. This script
never reads the sealed test. Geometry with a failed DRC remains a failed layout.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy
import numpy as np

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def export(scene):
    header=json.loads(scene['scientific_header_json'])
    guides=[];max_curve_error=0.
    for obj in sorted((o for o in scene.objects if o.get('femto_role')=='guide'),key=lambda o:o['order']):
        meta=json.loads(obj['guide_metadata_json'])
        points=np.asarray(obj['points_m_double'],dtype=float).reshape(-1,3)
        visible=np.asarray([p.co[:3] for p in obj.data.splines[0].points])
        if visible.shape!=points.shape:raise RuntimeError('Curve point count changed')
        max_curve_error=max(max_curve_error,float(abs(points-visible).max()))
        if max_curve_error>1e-8:raise RuntimeError('Visible curve diverged from SI property coordinates')
        meta['points_m']=points.tolist();guides.append(meta)
    header['guides']=guides
    couplers=[]
    for obj in sorted((o for o in scene.objects if o.get('femto_role')=='coupler'),key=lambda o:o['order']):
        c=json.loads(obj['coupler_metadata_json'])
        for key in ['gap_m','length_m','kappa_per_m','access_angle_rad']:
            c[key]=float(obj[key])
        couplers.append(c)
    header['couplers']=couplers
    return header,max_curve_error

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--geometry',type=Path,required=True)
    parser.add_argument('--blend',type=Path,required=True);parser.add_argument('--export',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    for file in [args.blend,args.export,args.report]:
        if file.exists():raise FileExistsError('Retain earlier Blender runs')
        file.parent.mkdir(parents=True,exist_ok=True)
    geometry=json.loads(args.geometry.read_text(encoding='utf-8'))
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.
    header={k:v for k,v in geometry.items() if k not in ['guides','couplers']}
    scene['scientific_header_json']=json.dumps(header,allow_nan=False)
    for i,guide in enumerate(geometry['guides']):
        points=np.asarray(guide['points_m'])
        curve=bpy.data.curves.new(guide['id'],'CURVE');curve.dimensions='3D'
        curve.bevel_depth=geometry['core_radius_m'];curve.bevel_resolution=0
        spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
        coords=np.column_stack([points,np.ones(len(points))]).astype(np.float32)
        spline.points.foreach_set('co',coords.ravel())
        obj=bpy.data.objects.new(guide['id'],curve);scene.collection.objects.link(obj)
        obj['femto_role']='guide';obj['order']=i
        obj['points_m_double']=points.ravel().tolist()
        obj['guide_metadata_json']=json.dumps({k:v for k,v in guide.items() if k!='points_m'})
    for i,c in enumerate(geometry['couplers']):
        obj=bpy.data.objects.new(c['id'],None);scene.collection.objects.link(obj)
        obj.location=c['center_m'];obj['femto_role']='coupler';obj['order']=i
        obj['coupler_metadata_json']=json.dumps(c)
        for key in ['gap_m','length_m','kappa_per_m','access_angle_rad']:obj[key]=c[key]
    bpy.ops.mesh.primitive_cube_add(size=1,location=np.asarray(geometry['block_size_m'])/2)
    glass=bpy.context.object;glass.name='FEMTO1_block';glass.dimensions=geometry['block_size_m']
    glass.display_type='WIRE';glass['femto_role']='block'
    for item in geometry['alignment_holes']:
        obj=bpy.data.objects.new('fiber_hole_'+str(len(scene.objects)),None)
        scene.collection.objects.link(obj);obj.location=item['center_m'];obj['feature_json']=json.dumps(item)
    for item in geometry['fiducials']+geometry['detectors']:
        obj=bpy.data.objects.new(item.get('id','fiducial_'+str(len(scene.objects))),None)
        scene.collection.objects.link(obj);obj.location=item['center_m'];obj['feature_json']=json.dumps(item)
    rebuilt,error=export(scene)
    expected=hashlib.sha256(canonical(geometry)).hexdigest();actual=hashlib.sha256(canonical(rebuilt)).hexdigest()
    report={'scope':'Blender scientific-property representation; not optical propagation',
            'geometry_canonical_sha256':expected,'export_canonical_sha256':actual,
            'roundtrip_identical':expected==actual,'visible_float32_max_error_m':error,
            'sealed_test_accessed':False,'fabrication_ready':False}
    args.export.write_text(json.dumps(rebuilt,indent=2),encoding='utf-8')
    args.report.write_text(json.dumps(report,indent=2),encoding='utf-8')
    if expected!=actual:raise RuntimeError('Blender round trip mismatch')
    bpy.ops.wm.save_as_mainfile(filepath=str(args.blend.resolve()))
    print('FEMTO1 '+json.dumps(report),flush=True)

if __name__=='__main__':main()
