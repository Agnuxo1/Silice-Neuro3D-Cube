import json,hashlib,sys
summ={"contract_sha256":hashlib.sha256(open("CONTRACT.md","rb").read()).hexdigest(),"cases":[]}
for i in range(6):
    d=json.load(open(f"out/case{i}.json")); c=d["case"]; cf=d["configs"]; nom=cf["nom"]
    if "gamma_re" not in nom: print(i,c,"sin modo",nom); summ["cases"].append(dict(case=c,note="sin modo")); continue
    allc=[v for v in cf.values() if "gamma_re" in v]
    M1=all(abs(v["M1"]["core_nodes_times_h_um"]-c["a_um"])<1e-9 and abs(v["M1"]["ring_nodes_times_h_um"]-c["t_um"])<1e-9 for v in allc)
    M2=max(v["M2_recon"] for v in allc); M3=min(v["overlap_bilinear"] for v in allc); M4=[]
    for name,v in cf.items():
        if name=="nom": continue
        if "gamma_re" not in v: M4.append((name,"sin candidato")); continue
        dre=abs(v["gamma_re"]-nom["gamma_re"])/abs(nom["gamma_re"]); L0,L1=nom["loss_dB_per_cm"],v["loss_dB_per_cm"]
        rel=abs(L1-L0)/max(abs(L0),1e-12); ab=abs(L1-L0)
        M4.append((name,dict(dRe=dre,dloss_rel=rel,dloss_abs=ab,PASS=bool(dre<5e-3 and (rel<0.10 or ab<0.005)))))
    etas=[v["eta"] for v in allc]; z2=nom["z_mm"]["2.0"]; ratio=z2["ratio_mode_over_total"]
    cls="dominio modal" if ratio>0.9 else ("transitorio" if ratio<0.5 else "mixto")
    summ["cases"].append(dict(case=c,gamma_nom=[nom["gamma_re"],nom["gamma_im"]],loss_nom_dB_cm=nom["loss_dB_per_cm"],core_frac=nom["core_frac"],M1=M1,M2_max_recon=M2,M2_PASS=bool(M2<1e-6),M3_min_overlap=M3,M3_PASS=bool(M3>0.999),M4=M4,
         M6_eta=dict(nom=nom["eta"],min=min(etas),max=max(etas),spread=max(etas)-min(etas)),M5_z2mm=dict(P_core_total=z2["P_core_total"],P_core_mode=z2["P_core_mode"],P_core_rest=z2["P_core_rest"],P_mode_total=z2["P_mode_total"],ratio=ratio,class_=cls),
         series={k:dict(total=v["P_core_total"],mode=v["P_core_mode"],rest=v["P_core_rest"]) for k,v in nom["z_mm"].items()}))
    print(f"({c['a_um']},{c['t_um']},{c['dn']}) ImG={nom['gamma_im']:.3e} loss={nom['loss_dB_per_cm']:.4f}dB/cm M1={M1} M2={M2:.1e} M3={M3:.5f} eta={nom['eta']:.3f}[{min(etas):.3f},{max(etas):.3f}] z2mm tot={z2['P_core_total']:.3f} modo={z2['P_core_mode']:.3f} resto={z2['P_core_rest']:.3f} ratio={ratio:.2f} {cls}")
    print("    M4:",[(n,(v if isinstance(v,str) else (round(v['dRe'],5),round(v['dloss_rel'],4),v['PASS']))) for n,v in M4])
json.dump(summ,open("resultados010_radial.json","w"),indent=1)
