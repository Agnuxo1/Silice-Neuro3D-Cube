"""Prospective F1/F2 training and validation. Never loads test features/labels."""
from __future__ import annotations
import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[name]='1'
import argparse
import json
import time
import warnings
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.exceptions import ConvergenceWarning
from common import (write_json,sha,now,save_npy,save_npz,optical_weights,tree,
                    from_ratios,realization,fit_readout,accuracy,metric)

def verify_commitment(root,record_path):
    from agentkit.prereg import committed_protocol,remote_contains,_working_blob
    record=json.loads(record_path.read_text(encoding='utf-8'))
    protocol=committed_protocol(root,record)
    if record.get('published_at_commitment') is not True or not record.get('remote_ref'):
        raise RuntimeError('Preregistration must be verified against server before training')
    if remote_contains(root,record['commit'],record['remote_ref'],True) is not True:
        raise RuntimeError('Commitment no longer verifiable on server')
    for name,blob in record['git_blobs'].items():
        if _working_blob(root,name)!=blob:
            raise RuntimeError('Preregistered source changed: '+name)
    return protocol

def robust_fit(w,x,y,cal_x,cal_y,seed):
    """Analytic gradient through a two-level intensity tree, fixed noisy draws."""
    rng=np.random.default_rng(seed)
    order,r=tree(w); theta=np.arcsin(np.sqrt(r)); origin=theta.copy()
    idx=rng.choice(len(y),min(1024,len(y)),replace=False)
    x,y=x[idx],y[idx]
    gains,offset,_=fit_readout(cal_x@w.T,cal_y)
    # 8 manufactured chips; common correlation .8; TIA .05 full-scale input.
    m=np.maximum(0,1+.1*(np.sqrt(.8)*rng.normal(size=(8,1,1))
                         +np.sqrt(.2)*rng.normal(size=(8,16,3))))
    tia=.05*rng.normal(size=(8,len(x),4))
    def objective(flat):
        t=flat.reshape(16,3)
        total=0.; grad=np.zeros_like(t)
        for mult,noise in zip(m,tia):
            phase=t*mult; rr=np.sin(phase)**2
            wr=from_ratios(order,rr)
            z=(x@wr.T+noise)*gains+offset
            lp=z-logsumexp(z,axis=1,keepdims=True)
            total-=lp[np.arange(len(y)),y].mean()/len(m)
            e=np.exp(lp); e[np.arange(len(y)),y]-=1
            dw=(e*gains).T@x/(len(x)*len(m))
            for j,(a,b,c) in enumerate(rr):
                d=dw[order[j],j]
                dr=np.array([d[0]*b+d[1]*(1-b)-d[2]*c,
                             a*(d[0]-d[1]),(1-a)*d[2]])
                grad[j]+=dr*np.sin(2*phase[j])*mult[j]
        penalty=.02*np.mean((t-origin)**2)
        grad+=.04*(t-origin)/t.size
        return total+penalty,grad.ravel()
    # Paired central differences on six fixed coordinates before fitting.
    flat=theta.ravel(); _,analytic=objective(flat); gradient_errors=[]
    for coordinate in [0,5,12,27,39,47]:
        plus=flat.copy();minus=flat.copy();plus[coordinate]+=1e-6;minus[coordinate]-=1e-6
        numeric=(objective(plus)[0]-objective(minus)[0])/2e-6
        gradient_errors.append(abs(numeric-analytic[coordinate]))
    if max(gradient_errors)>1e-5:
        raise RuntimeError('Noise-aware analytic gradient check failed')
    result=minimize(objective,theta.ravel(),jac=True,method='L-BFGS-B',
                    bounds=[(0,np.pi/2)]*48,options={'maxiter':30,'ftol':1e-7})
    return from_ratios(order,np.sin(result.x.reshape(16,3))**2),{
        'success':bool(result.success),'iterations':int(result.nit),'objective':float(result.fun),
        'termination':str(result.message),'gradient':'analytic through sin^2 and tree products',
        'fitting_samples':len(y),'fixed_noise_draws':8,
        'gradient_central_difference_max_abs_error':max(gradient_errors)}

def tolerance(w,xc,yc,xv,yv,sigmas,repetitions,seed):
    rng=np.random.default_rng(seed); points=[]; records=[]
    # Calibration always uses the dedicated training-calibration split.
    for sigma in sigmas:
        uncal,cal,noisy,success=[],[],[],[]
        for i in range(repetitions):
            wr=realization(w,sigma,rng)
            gains,offset,ok=fit_readout(xc@wr.T,yc)
            uncal.append(accuracy(xv,yv,wr));cal.append(accuracy(xv,yv,wr,gains,offset))
            noisy_power=xv@wr.T+.05*rng.normal(size=(len(xv),4))
            noisy.append(float(np.mean((noisy_power*gains+offset).argmax(1)==yv)))
            success.append(ok)
            records.append((sigma,i,uncal[-1],cal[-1],noisy[-1],ok))
        summary=lambda a:{'mean':float(np.mean(a)),'std_between_chips':float(np.std(a,ddof=1)),
                          'p05':float(np.quantile(a,.05)),'minimum':float(np.min(a))}
        points.append({'sigma_kappa':sigma,'realizations':repetitions,
                       'uncalibrated':summary(uncal),'eight_parameters':summary(cal),
                       'eight_parameters_tia_sigma_005':summary(noisy),
                       'readout_optimizer_success_count':sum(success)})
        print(json.dumps({'progress':'MC point complete','point':points[-1]}),flush=True)
    return points,np.asarray(records,dtype=float)

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--commitment',type=Path,required=True);args=p.parse_args()
    root=args.root.resolve(); protocol=verify_commitment(root,args.commitment)
    if args.out.exists(): raise FileExistsError('Retain every run; new directory required')
    args.out.mkdir(parents=True)
    start=time.perf_counter(); warnings_log=[]
    manifest=json.loads((args.data/'manifest.json').read_text(encoding='utf-8'))
    arrays={}
    for name in ['fit','calibration','validation']:
        file=args.data/(name+'.npz')
        if sha(file)!=manifest['files'][file.name]: raise RuntimeError('Data changed')
        with np.load(file,allow_pickle=False) as d: arrays[name]=(d['X'],d['y'])
    xf,yf=arrays['fit'];xc,yc=arrays['calibration'];xv,yv=arrays['validation']
    references={}; nominal_candidates=[]
    for c in protocol['training']['logistic_C']:
        for bias in [False,True]:
            model=LogisticRegression(C=c,fit_intercept=bias,max_iter=1000,random_state=20261013)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always');model.fit(xf,yf)
            warnings_log.extend(str(v.message) for v in caught)
            name=f'logistic_C{c}_bias{bias}'
            references[name]=metric(model.predict(xv),yv)
            if not bias:
                w,scale=optical_weights(model.coef_)
                if not np.array_equal((xv@w.T).argmax(1),model.predict(xv)):
                    raise RuntimeError('Nonnegative conversion changed argmax')
                nominal_candidates.append((references[name]['accuracy'],c,w,model.coef_,scale))
    _,selected_c,nominal,signed,scale=max(nominal_candidates,key=lambda v:(v[0],-v[1]))
    majority=int(np.argmax(np.bincount(yf,minlength=4)))
    references['majority']=metric(np.full(len(yv),majority),yv)
    means=np.stack([xf[yf==k].mean(0) for k in range(4)])
    normalized=means/np.linalg.norm(means,axis=1,keepdims=True)
    for name,w in [('prototype_raw',means),('prototype_normalized',normalized)]:
        references[name]=metric((xv@w.T).argmax(1),yv)
    proto,_=optical_weights(normalized)
    assert np.array_equal((xv@proto.T).argmax(1),(xv@normalized.T).argmax(1))
    knn=KNeighborsClassifier(n_neighbors=1,algorithm='kd_tree',n_jobs=1).fit(xf,yf)
    references['nearest_neighbor_1']=metric(knn.predict(xv),yv)
    for seed in protocol['training']['mlp_seeds']:
        model=MLPClassifier(hidden_layer_sizes=(16,),max_iter=200,random_state=seed,
                            early_stopping=True,validation_fraction=.15)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always');model.fit(xf,yf)
        warnings_log.extend(str(v.message) for v in caught)
        references['MLP16_seed'+str(seed)]=metric(model.predict(xv),yv)
    robust,robust_info=robust_fit(nominal,xf,yf,xc,yc,20261013)
    candidate_reports={};candidate_weights={'nominal':nominal,'noise_aware':robust}
    # Fixed development selection MC; final audit MC uses a distinct seed.
    for name,w in candidate_weights.items():
        g,b,ok=fit_readout(xc@w.T,yc)
        points,_=tolerance(w,xc,yc,xv,yv,[.1],16,20261014)
        candidate_reports[name]={'ideal_uncalibrated':metric((xv@w.T).argmax(1),yv),
                                 'ideal_eight_parameters':metric((xv@w.T*g+b).argmax(1),yv),
                                 'selection_MC':points[0],'nominal_readout_success':ok}
    baseline=accuracy(xv,yv,nominal)
    eligible=[name for name in candidate_weights
              if candidate_reports[name]['ideal_uncalibrated']['accuracy']>=baseline-.03]
    selected=max(eligible,key=lambda name:(candidate_reports[name]['selection_MC']['eight_parameters']['mean'],
                                           name=='nominal'))
    mainw=candidate_weights[selected]
    points,mc=tolerance(mainw,xc,yc,xv,yv,protocol['tolerances']['sigma_kappa'],
                        protocol['tolerances']['realizations'],20261015)
    g,b,ok=fit_readout(xc@mainw.T,yc)
    for name,w in [('W_main.npy',mainw),('W_nominal.npy',nominal),('W_noise_aware.npy',robust),
                    ('W_signed.npy',signed),('W_proto.npy',proto),('prototype_means.npy',means),
                    ('prototype_normalized.npy',normalized)]: save_npy(args.out/name,w)
    save_npz(args.out/'validation_power.npz',power=xv@mainw.T,y=yv)
    save_npz(args.out/'MC_validation.npz',records=mc)
    save_npz(args.out/'readout_nominal.npz',gain=g,offset=b)
    p10=next(v for v in points if v['sigma_kappa']==.1)
    gates={'F2_ideal_within_3pp':accuracy(xv,yv,mainw)>=baseline-.03,
           'F2_kappa10_recalibration_within_2pp':p10['eight_parameters']['mean']>=baseline-.02,
           'F2_tia5_within_2pp':p10['eight_parameters_tia_sigma_005']['mean']>=baseline-.02,
           'F6_target_kappa10_proxy':p10['eight_parameters']['mean']>=protocol['target_accuracy']-.03}
    report={'experiment_id':protocol['experiment_id'],'scope':'numerical validation only',
            'created_utc':now(),'dataset_manifest_sha256':sha(args.data/'manifest.json'),
            'test_used':False,'references':references,'selected_C':selected_c,
            'conversion_global_scale':scale,'candidate_selection':candidate_reports,
            'selected_candidate':selected,'robust_fit':robust_info,'tolerance_points':points,
            'gates':gates,'warnings':warnings_log,'eight_parameters':{'gain':g.tolist(),'offset':b.tolist()},
            'power_fraction_per_input':{'minimum':float(mainw.sum(0).min()),'mean':float(mainw.sum(0).mean()),
                                        'maximum':float(mainw.sum(0).max())},
            'elapsed_s':time.perf_counter()-start,
            'limits':['Coupling model provisional; no supplier geometry or measured tolerance',
                      'MC spread describes chips on one validation set; not binomial sampling uncertainty',
                      'TIA .05 is normalized to full-scale input, not a characterized physical detector',
                      'Offsets break global brightness invariance',
                      'Gain/offset optimizer failures retained; no change of thresholds',
                      'No fabricated chip, physical latency, energy advantage or worst polarization validated']}
    write_json(args.out/'F2_validation.json',report)
    write_json(args.out/'RUN.json',{'started_for':'F1/F2','finished_utc':now(),'elapsed_s':report['elapsed_s'],
                                  'input_commitment':sha(args.commitment),'files':{f.name:sha(f) for f in args.out.iterdir() if f.is_file()}})
    print(json.dumps({'selected':selected,'baseline':baseline,'gates':gates,'elapsed_s':report['elapsed_s']}))

if __name__=='__main__':main()
