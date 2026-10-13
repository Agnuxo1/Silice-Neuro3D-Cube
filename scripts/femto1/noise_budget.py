"""Paired validation noise sweep and conditional optical-power requirements.

NEP, bandwidth and insertion efficiencies are design assumptions, not specs of
selected components or measured chip data. Exactly eight gains/offsets are fitted
with labelled training-calibration records and simulated reading noise.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import argparse
import json
import math
from pathlib import Path
import numpy as np
from common import realization,fit_readout,write_json,save_npz,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--models',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError('Never overwrite a noise sweep')
    args.out.mkdir(parents=True)
    with np.load(args.data/'calibration.npz',allow_pickle=False) as d:xc,yc=d['X'],d['y']
    with np.load(args.data/'validation.npz',allow_pickle=False) as d:xv,yv=d['X'],d['y']
    w=np.load(args.models/'W_main.npy',allow_pickle=False)
    levels=[0,.001,.002,.005,.01,.02,.05]
    results=[];raw=[]
    # Same 200 chips and base noise samples for each level: paired sensitivity.
    for level in levels:
        rng=np.random.default_rng(20261016);acc=[];ok_count=0
        for i in range(200):
            wr=realization(w,.1,rng)
            cal_power=xc@wr.T+level*rng.normal(size=(len(xc),4))
            val_power=xv@wr.T+level*rng.normal(size=(len(xv),4))
            gains,offset,ok=fit_readout(cal_power,yc)
            a=float(np.mean((val_power*gains+offset).argmax(1)==yv))
            acc.append(a);ok_count+=ok;raw.append([level,i,a,int(ok)])
        point={'TIA_sigma_input_fullscale':level,'mean':float(np.mean(acc)),
               'std_between_chips':float(np.std(acc,ddof=1)),'p05':float(np.quantile(acc,.05)),
               'minimum':float(np.min(acc)),'optimizer_successes':ok_count,'realizations':200,
               'fixed_target_mean':.85,'mean_gate_passed':bool(np.mean(acc)>=.85)}
        results.append(point);print(json.dumps({'noise_sweep':point}),flush=True)
    passed=[r['TIA_sigma_input_fullscale'] for r in results if r['mean_gate_passed']]
    allowed=max(passed) if passed else None
    h=6.62607015e-34;c=299792458.;wavelength=1.55e-6;n=1.467
    path_m=.055;prop_loss_db=.2*path_m*100 # dB/cm; SI conversion m -> cm
    eta_in=.5;eta_out=.5;eta_prop=10**(-prop_loss_db/10)
    bandwidth=500e6;integration=1e-9
    budgets=[]
    for nep in [1e-12,1e-11,1e-10]:
        noise_W=nep*math.sqrt(bandwidth)
        required=(16*noise_W/(allowed*eta_in*eta_out*eta_prop)) if allowed and allowed>0 else None
        for source_W in [.0001,.0003,.001,.003,.01]:
            input_scale=source_W/16*eta_in
            photon_scale=input_scale*eta_out*eta_prop*integration/(h*c/wavelength)
            sigma=noise_W/(input_scale*eta_out*eta_prop)
            # Conservative next higher measured level; no interpolation claim.
            bracket=next((r for r in results if r['TIA_sigma_input_fullscale']>=sigma),None)
            budgets.append({'assumed_NEP_W_per_sqrtHz':nep,'source_power_W':source_W,
                            'assumed_bandwidth_Hz':bandwidth,'TIA_sigma_input_fullscale':sigma,
                            'fullscale_photons_per_input_after_common_losses_per_ns':photon_scale,
                            'required_source_W_from_noise_grid':required,
                            'conditional_noise_gate':bool(bracket and bracket['mean_gate_passed']),
                            'shot_noise_and_other_errors_included':False})
    propagation=path_m*n/c;rise=.35/bandwidth
    report={'scope':'conditional numerical noise/power design; NOT F6 fabrication validation',
            'weight_sha256':sha(args.models/'W_main.npy'),'test_used':False,'kappa_sigma':.1,
            'calibration':'eight positive gains/offsets fit on noisy training-calibration records',
            'noise_sweep':results,'maximum_passing_tested_noise_sigma':allowed,
            'power_budget_assumptions':{'maximum_path_m':path_m,'input_efficiency':eta_in,
                                      'output_efficiency':eta_out,'propagation_dB_per_cm':.2,
                                      'propagation_loss_dB':prop_loss_db,'propagation_efficiency':eta_prop,
                                      'discard':'already included in W; do not count twice'},
            'budgets':budgets,'latency_model':{'propagation_s':propagation,'assumed_analog_rise_s':rise,
                                            'sum_s':propagation+rise,'measured':False,
                                            'ADC_decision_and_calibration_latency_included':False},
            'missing':['supplier profile/tolerances, polarization/depth/anisotropy and physical solver',
                       'actual TIA NEP and impulse response, source spectrum, detector area/bandwidth trade-off',
                       'shot noise combined with fabrication/fiber losses and input nonuniformity',
                       'full power/energy accounting of source, detector, TIA, ADC and logic'],
            'F6_passed':False,'sealed_test_ready':False}
    save_npz(args.out/'MC_noise.npz',records=np.asarray(raw))
    write_json(args.out/'NOISE-POWER.json',report)
    print(json.dumps({'noise_limit':allowed,'F6_passed':False}))

if __name__=='__main__':main()
