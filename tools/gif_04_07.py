import sys,json,math,os
from gifstyle import *
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
sys.path.insert(0,os.path.join(ROOT,"experimentos","glass_min1"))
from oracle import dft4,test_states,target_intensity
from sim_cmt import section,phase_layer,mesh
p=np.load(os.path.join(ROOT,"experimentos","glass_min1","phases.npy")); TH,PH=p[:4],p[4:]
KL=np.pi/4

# ---------- GIF 4: malla DFT4 (2 etapas de acopladores 50/50) con intensidad por guia
def stages(u,x):
    """u en [0,3]: 0-1 acoplador capa1 (kL=u*pi/4), 1-2 fase, 2-3 acoplador capa2."""
    a=phase_layer(TH)@x
    S1=section(4,[(0,2),(1,3)],[1,1],min(u,1)*KL); a=S1@a
    if u>1: a=phase_layer(PH)@a
    if u>2: S2=section(4,[(0,1),(2,3)],[1,1],(min(u,3)-2)*KL); a=S2@a
    return a

def gif4():
    inputs=[np.eye(4,dtype=complex)[i] for i in range(4)]+[np.ones(4,complex)/2]
    names=["entrada solo en guia 1","entrada solo en guia 2","entrada solo en guia 3","entrada solo en guia 4","4 guias en fase"]
    fig=plt.figure(figsize=(10.5,5)); ax=fig.add_axes([.03,.14,.62,.72]); bx=fig.add_axes([.72,.20,.26,.62])
    ax.set_xlim(-.3,4.3); ax.set_ylim(-.6,3.6); ax.axis("off")
    ys=[3,2,1,0]; lane=[ax.plot([-.2,4.2],[y,y],color=GRID,lw=6,solid_capstyle="round")[0] for y in ys]
    for (x0,pairs) in [(0,[(0,2),(1,3)]),(2,[(0,1),(2,3)])]:
        for (i,j) in pairs: ax.add_patch(plt.Rectangle((x0,min(ys[i],ys[j])-.15),1,abs(ys[i]-ys[j])+.3,fc="none",ec=CY,lw=1.2,ls="--"))
    ax.add_patch(plt.Rectangle((1,-.3),1,3.6,fc=MG,alpha=.10,ec="none")); ax.text(1.5,3.45,"fases fijas",ha="center",color=MG,fontsize=9)
    ax.text(.5,-.55,"etapa 1: acopladores 50/50",ha="center",color=CY,fontsize=9); ax.text(2.5,-.55,"etapa 2: acopladores 50/50",ha="center",color=CY,fontsize=9)
    dots=[ax.scatter([0],[y],s=10,color="white",zorder=5) for y in ys]
    bx.set_title("Salida vs objetivo DFT4",loc="left",fontsize=10); bx.set_ylim(0,1.05); bx.set_xticks(range(4)); bx.set_xticklabels(["s1","s2","s3","s4"])
    order=[0,2,1,3]
    bars=bx.bar(np.arange(4)-.18,[0]*4,.36,color=CY,label="malla (CMT)"); tg=bx.bar(np.arange(4)+.18,[0]*4,.36,color=AM,alpha=.85,label="oraculo")
    bx.legend(frameon=False,fontsize=8,loc="upper right"); ttl=fig.text(.03,.92,"",fontsize=12,fontweight="bold")
    def up(f):
        k=(f//60)%5; ph=f%60; u=min(3.0,ph/45*3); x=inputs[k]; a=stages(u,x)
        for i,d in enumerate(dots):
            d.set_offsets([[u,ys[i]]]); d.set_sizes([30+520*abs(a[i])**2]); d.set_color(plt.cm.cool(min(1,abs(a[i])**2*1.5)))
        for i in range(4): lane[i].set_color(LIGHT(0.28+0.72*min(1,abs(a[i])**2*1.3)))
        out=np.abs(stages(3,x))**2; tar=target_intensity(x)[order]
        for b,v in zip(bars,out): b.set_height(v if ph>=45 else 0)
        for b,v in zip(tg,tar): b.set_height(v if ph>=45 else 0)
        ttl.set_text("Malla 4x4 de dos etapas - "+names[k])
    caption(fig,"Datos: experimentos/glass_min1 (modos acoplados, expm por tramos) frente al oraculo de algebra lineal · salidas en orden 0,2,1,3 · backend a matriz, no trazado de escena")
    save(fig,up,300,"04_malla_dft4.gif",fps=15)

# ---------- GIF 5: tolerancias (Monte Carlo 400 piezas por sigma; media vs p95)
def relerr(U,X,T):
    I=np.abs(X@U.T)**2; m=T>0.05; return np.mean(np.abs(I-T)[m]/T[m])

def gif5():
    X=test_states(); T=np.array([target_intensity(x) for x in X])[:,[0,2,1,3]]; r=np.random.default_rng(7)
    sigs=np.linspace(0.0,0.30,31); N=400; data=[]
    for s in sigs: data.append(np.array([relerr(mesh(TH,PH,dph_in=r.normal(0,s,4),dph_mid=r.normal(0,s,4)),X,T) for _ in range(N)]))
    fig,(ax,bx)=plt.subplots(1,2,figsize=(10.5,4.8),gridspec_kw={"width_ratios":[1.2,1]}); fig.subplots_adjust(left=.07,right=.98,top=.85,bottom=.17,wspace=.22)
    ax.set_xlim(0,.3); ax.set_ylim(0,.8); ax.set_xlabel("ruido de fase por elemento (rad, sigma)"); ax.set_ylabel("error relativo de intensidad"); ax.grid(True,alpha=.5)
    ax.axhline(.10,color=RD,ls="--",lw=1.2); ax.text(.298,.115,"limite 10 %",color=RD,ha="right",fontsize=9)
    sc=ax.scatter([],[],s=6,color=CY,alpha=.25)
    mean,=ax.plot([],[],color=AM,lw=2.4,label="media"); p95,=ax.plot([],[],color=MG,lw=2.4,label="p95 (95 % de las piezas)"); ax.legend(frameon=False,loc="upper left")
    tt=fig.suptitle("",x=.07,ha="left",fontsize=12,fontweight="bold")
    def up(f):
        i=min(f//2,len(sigs)-1)
        xs=np.concatenate([np.full(N,sigs[j]) for j in range(i+1)]); ys=np.concatenate(data[:i+1]); sc.set_offsets(np.c_[xs,ys])
        mean.set_data(sigs[:i+1],[d.mean() for d in data[:i+1]]); p95.set_data(sigs[:i+1],[np.percentile(d,95) for d in data[:i+1]])
        bx.cla(); bx.hist(data[i],bins=np.linspace(0,.8,41),color=CY,alpha=.85); bx.axvline(.10,color=RD,ls="--",lw=1.2)
        bx.set_xlim(0,.8); bx.set_ylim(0,120); bx.set_xlabel("error de la pieza"); bx.set_ylabel("piezas")
        bad=(data[i]>.10).mean()*100
        tt.set_text(f"sigma = {sigs[i]:.2f} rad  -  media {data[i].mean()*100:.1f} %  -  p95 {np.percentile(data[i],95)*100:.1f} %  -  {bad:.0f} % de piezas > 10 %")
    caption(fig,"Datos: Monte Carlo GLASS-002 (400 piezas/sigma, semilla 7). La media engana: para que el 95 % de piezas cumpla hace falta sigma ~ 0.05 rad (dn ~ 1e-6 en 10 mm)")
    save(fig,up,62,"05_tolerancias.gif",fps=8)

# ---------- GIF 6: camisa discreta (datos de Codex GLASS-007)
def raster(per,wedge=0.0,n=300,ext=14):
    ax=np.linspace(-ext,ext,n); x,y=np.meshgrid(ax,ax); m=np.zeros_like(x,bool)
    for ring,rad in enumerate([7.25,9,10.75]):
        off=math.pi/per if ring%2 else 0
        for j in range(per):
            ang=2*math.pi*j/per+off; sg=(ang+math.pi)%(2*math.pi)-math.pi
            if wedge and abs(sg)<wedge/2: continue
            m|=(x-rad*math.cos(ang))**2+(y-rad*math.sin(ang))**2<=1.25**2
    r=np.hypot(x,y); return m&(r>=6)&(r<12)

def gif6():
    d=json.load(open(os.path.join(ROOT,"resultados","codex","glass007_complete_v1.json")))["cases"]
    val={c["name"]:c["core_power_fraction_input"]*100 for c in d}
    items=[("camisa continua",None,0,"continuous"),("48 trazos (16/corona)",16,0,"tracks16"),("96 trazos (32/corona)",32,0,"tracks32"),("192 trazos (64/corona)",64,0,"tracks64"),("96 + hueco 30 (real 17.7)",32,math.radians(30),"tracks32_missing")]
    ext=14; ax_=np.linspace(-ext,ext,300); xx,yy=np.meshgrid(ax_,ax_); cont=(np.hypot(xx,yy)>=6)&(np.hypot(xx,yy)<12)
    fig,(ax,bx)=plt.subplots(1,2,figsize=(10.5,4.8),gridspec_kw={"width_ratios":[1,1.15]}); fig.subplots_adjust(left=.03,right=.97,top=.86,bottom=.14,wspace=.42)
    ax.set_aspect("equal"); ax.axis("off"); im=ax.imshow(np.zeros((300,300)),extent=[-ext,ext,-ext,ext],cmap=LIGHT,vmin=0,vmax=1.35,origin="lower")
    ax.add_patch(plt.Circle((0,0),6,fc="none",ec=CY,lw=1.4,ls="--")); nm=ax.text(0,-15.3,"",ha="center",fontsize=9.5)
    masks=[cont if it[1] is None else raster(it[1],it[2]) for it in items]
    bx.set_title("Potencia en el nucleo tras 2 mm (% de la entrada)",loc="left",fontsize=10.5)
    bx.set_xlim(0,45); bx.set_ylim(4.6,-.6); bx.set_yticks(range(5)); bx.set_yticklabels([i[0] for i in items],fontsize=9); bx.grid(True,axis="x",alpha=.4)
    bars=bx.barh(range(5),[0]*5,color=CY,height=.55); labs=[bx.text(0,i,"",va="center",fontsize=9.5) for i in range(5)]
    def up(f):
        k=min(4,f//24); t=(f%24)/24 if f<120 else 1.0
        im.set_data(np.where(masks[k],.35+.6*min(1,t*2),0.06))
        for i in range(5):
            v=val[items[i][3]] if i<=k else 0; s=v*min(1,t*1.5) if i==k else v
            bars[i].set_width(s); bars[i].set_color(MG if i==4 else (AM if i==0 else CY)); labs[i].set_position((s+.6,i)); labs[i].set_text(f"{s:.1f} %" if s>0 else "")
        fill="100 %" if items[k][1] is None else "%.0f %%"%(100*masks[k].sum()/cont.sum())
        nm.set_text(items[k][0]+"  -  relleno del anillo "+fill)
    fig.suptitle("Menos trazos = mas fuga; un hueco de solo ~18 grados duele mucho",x=.03,ha="left",fontsize=12,fontweight="bold")
    caption(fig,"Datos: GLASS-007 (Codex, BPM, dn=-0.003, discos de 1.25 um). Perfil ideal, no receta de escritura ni perdida por cm medida")
    save(fig,up,150,"06_camisa_discreta.gif",fps=12)

# ---------- GIF 7: metodo (contrato -> ejecucion -> auditoria -> fallos retenidos)
def gif7():
    fig,ax=plt.subplots(figsize=(10.5,4.6)); fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.10); ax.axis("off"); ax.set_xlim(0,10.5); ax.set_ylim(0,4.6)
    steps=[("1  Contrato","umbrales y controles\nantes de medir",CY),("2  Ejecucion","CPU un hilo\nhijos <30 s",GR),("3  Auditoria","segundo solver / par\nhashes intactos",AM),("4  Fallos retenidos","se publican;\nno se relajan gates",RD)]
    boxes=[]; xs=[.4,2.98,5.56,8.14]
    for (t,s,c),x in zip(steps,xs):
        b=plt.Rectangle((x,2.75),2.0,1.35,fc=PANEL,ec=c,lw=2,alpha=0); ax.add_patch(b)
        tx=ax.text(x+.12,3.95,t,color=c,fontsize=11.5,fontweight="bold",va="top",alpha=0); sx=ax.text(x+.12,3.5,s,color=TXT,fontsize=9,va="top",alpha=0,linespacing=1.5); boxes.append((b,tx,sx))
    arrows=[ax.annotate("",xy=(xs[i+1]-.05,3.42),xytext=(xs[i]+2.05,3.42),arrowprops=dict(arrowstyle="->",color=MUTED,lw=1.8)) for i in range(3)]
    for a_ in arrows: a_.set_visible(False)
    ev=[("GLASS-003 V1","convergencia FAIL (retenido)",RD),("GLASS-003 V2","dz=10 um insuficiente en dn=-0.005: FAIL -> causa hallada (dz<=2.5 um)",AM),("GLASS-004","media 9 % pero p95 15 %: 37 % de piezas > 10 %",AM),("GLASS-006a","7/18 modos convergen; erratum de signo del contrato propio",RD),("GLASS-006a G3","la prediccion de tunel WKB acierta 4/4",GR),("GLASS-007","96 trazos ~ anillo continuo (33 % vs 35 %)",GR)]
    tl=[ax.text(.5,2.05-i*.36,"",fontsize=9.6,va="center") for i in range(len(ev))]
    ax.text(.4,2.5,"Bitacora real del proyecto",color=MUTED,fontsize=9.5)
    def up(f):
        for i,(b,tx,sx) in enumerate(boxes):
            on=f>=6+i*10; b.set_alpha(1 if on else 0); tx.set_alpha(1 if on else 0); sx.set_alpha(1 if on else 0)
            if i<3: arrows[i].set_visible(f>=12+i*10)
        for i,(a,b_,c) in enumerate(ev):
            if f>=48+i*7: tl[i].set_text("*  "+a+": "+b_); tl[i].set_color(c)
    caption(fig,"Un resultado que no pasa sigue en el repositorio. La evidencia es lo que se puede reproducir, no lo que se espera.")
    save(fig,up,110,"07_metodo_evidencia.gif",fps=10)

if __name__=="__main__":
    for g in sys.argv[1:]: globals()["gif"+g]()
