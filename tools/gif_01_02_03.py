import sys,json,math,os
from gifstyle import *
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","experimentos","glass005_claude"))
import scipy.linalg as la
from radial_ecs import build,k0,n0
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
def tracks(per=32,a=6e-6,t=6e-6):
    cs=[]
    for ring,rad in enumerate(np.linspace(a+1.25e-6,a+t-1.25e-6,3)):
        off=math.pi/per if ring%2 else 0
        for j in range(per): 
            ang=2*math.pi*j/per+off; cs.append((rad*1e6*math.cos(ang),rad*1e6*math.sin(ang)))
    return cs
# ---------- GIF 1: escritura de la camisa deprimida (geometria real del ensayo 007: 3 coronas x 32 trazos, discos de 1.25 um)
def gif1():
    cs=tracks(); fig,(ax,bx)=plt.subplots(1,2,figsize=(10,4.4),gridspec_kw={"width_ratios":[1.15,1]})
    fig.subplots_adjust(left=.04,right=.98,top=.88,bottom=.16,wspace=.15)
    ax.set_aspect("equal"); ax.set_xlim(-15,15); ax.set_ylim(-15,15); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Seccion transversal: el laser dibuja la camisa",loc="left")
    ax.add_patch(plt.Circle((0,0),6,fc="none",ec=CY,lw=1.5,ls="--")); ax.text(0,0,"nucleo\nintacto\n(n = n0)",ha="center",va="center",color=CY,fontsize=9)
    ax.text(0,-13.4,"trazos de indice reducido (dn = -0.003, supuesto)",ha="center",color=MG,fontsize=8.5)
    done=[]; foc=ax.plot([],[],"o",color=AM,ms=12,mec="white",mew=1.5,zorder=5)[0]
    bx.set_xlim(0,1);bx.set_ylim(0,1);bx.axis("off"); bx.set_title("Estado del ensayo",loc="left")
    txt=bx.text(0.02,0.86,"",fontsize=11,va="top",linespacing=1.9)
    bx.text(0.02,0.22,"Modelo: union de discos de radio 1.25 um sobre 3 coronas\n(radios 7.25 / 9 / 10.75 um). Ilustracion de la geometria\ndel ensayo GLASS-007, no una receta de escritura.",fontsize=8.6,color=MUTED,va="top",linespacing=1.5)
    N=len(cs); order=list(range(N))
    def up(f):
        n=min(N,int(f/70*N*1.0)+1)
        for k in range(len(done),n):
            x,y=cs[k]; c=plt.Circle((x,y),1.25,fc=MG,ec="none",alpha=.55); ax.add_patch(c); done.append(c)
        x,y=cs[n-1]; foc.set_data([x],[y])
        txt.set_text(f"trazos escritos: {n} / {N}\nanillo cubierto: {'%.0f'%(100*n/N*0.965)} %\nnucleo modificado: 0 (verificado)")
    caption(fig,"Datos: geometria de src/silice/tracks.py (Codex, GLASS-007) · relleno 96.5 % con 32 trazos/corona")
    save(fig,up,80,"01_escritura_camisa.gif",fps=12)
# ---------- GIF 2: confinamiento real (solver radial ECS, indep. del BPM)
def field_vs_z(dn,zs,a=6e-6,t=6e-6,w=6e-6):
    x,r,s,h,H=build(dn,a,t,R0=60e-6,Rmax=140e-6,N=500,theta=0.6); ev,V=la.eig(H)
    psi0=np.exp(-(x/w)**2).astype(complex); wg=r*s*h; Vn=V/np.sqrt((V*V*wg[:,None]).sum(0)); c=(Vn*wg[:,None]).T@psi0
    F=np.array([np.abs(Vn@(c*np.exp(1j*ev*z)))**2 for z in zs]); P0=np.sum(np.abs(psi0)**2*x*h)
    core=np.array([np.sum(f[x<a]*x[x<a]*h)/P0 for f in F]); return x,F/np.max(F[0]),core
def gif2():
    zs=np.linspace(0,2e-3,60); res={dn:field_vs_z(dn,zs) for dn in (-0.001,-0.003,-0.005)}
    fig,axs=plt.subplots(2,3,figsize=(10.5,5.2),gridspec_kw={"height_ratios":[3,1.3]})
    fig.subplots_adjust(left=.06,right=.985,top=.88,bottom=.13,wspace=.22,hspace=.32)
    ims=[];lines=[];dots=[]
    for i,dn in enumerate(res):
        x,F,core=res[dn]; ax=axs[0,i]; ax.set_title(f"dn camisa = {dn}",loc="left"); ax.set_xlim(0,40); ax.set_ylim(0,1.05)
        ax.set_xlabel("r (um)"); ax.axvspan(0,6,color=CY,alpha=.10); ax.axvspan(6,12,color=MG,alpha=.16)
        ln,=ax.plot([],[],color=CY,lw=2.2); ax.fill_between([0],[0]); lines.append((ln,x*1e6,F))
        bx=axs[1,i]; bx.plot(zs*1e3,core*100,color=MUTED,lw=1); bx.set_xlim(0,2); bx.set_ylim(0,100); bx.set_xlabel("z (mm)"); bx.set_ylabel("% en nucleo")
        d,=bx.plot([],[],"o",color=AM); ln2,=bx.plot([],[],color=AM,lw=2); dots.append((d,ln2,core))
        if i>0: ax.set_yticklabels([])
    axs[0,0].set_ylabel("|A|^2 (norm.)")
    tt=fig.suptitle("",x=.06,ha="left",fontsize=12,fontweight="bold")
    def up(f):
        for (ln,x,F) in lines: ln.set_data(x,F[f]/max(F[f].max(),1e-9)*min(1,F[f].max()/F[0].max()*1.0))
        for (d,l2,core) in dots: d.set_data([zs[f]*1e3],[core[f]*100]); l2.set_data(zs[:f+1]*1e3,core[:f+1]*100)
        tt.set_text(f"El gaussiano se abre o queda retenido segun el contraste  ·  z = {zs[f]*1e3:.2f} mm")
    caption(fig,"Datos: oraculo radial FD+ECS (GLASS-005). Nucleo 6 um, camisa 6 um, lambda 1550 nm. Modelo escalar ideal · final: 1.2 / 36.4 / 72.6 % en el nucleo")
    save(fig,up,60,"02_confinamiento.gif",fps=12)
# ---------- GIF 3: fuga por efecto tunel vs grosor (datos reales de GLASS-006a)
def gif3():
    d=json.load(open(os.path.join(ROOT,"experimentos","glass006a_claude","resultados.json")))["cases"]
    fig,ax=plt.subplots(figsize=(9.5,5)); fig.subplots_adjust(left=.09,right=.97,top=.86,bottom=.17)
    series={}
    for r in d:
        if "gamma_im" in r["configs"].get("nom",{}): series.setdefault((r["a_um"],r["dn"]),[]).append((r["t_um"],r["configs"]["nom"]["loss_dB_per_cm"]))
    sty={(6.0,-0.003):(AM,"o","a=6 um, dn=-0.003"),(6.0,-0.005):(CY,"s","a=6 um, dn=-0.005"),(10.0,-0.003):(MG,"^","a=10 um, dn=-0.003"),(10.0,-0.005):(GR,"D","a=10 um, dn=-0.005")}
    ax.set_yscale("log"); ax.set_xlim(2,19.5); ax.set_ylim(1e-5,60); ax.set_xlabel("grosor de la camisa t (um)"); ax.set_ylabel("perdida por fuga (dB/cm)"); ax.grid(True,alpha=.5)
    ax.axhline(0.05,color=RD,ls="--",lw=1); ax.text(19.3,0.06,"0.05 dB/cm",color=RD,ha="right",fontsize=8.5)
    arts={k:(ax.plot([],[],sty[k][1]+"-",color=sty[k][0],lw=2,ms=8,label=sty[k][2])[0],sorted(v)) for k,v in series.items()}
    ax.legend(loc="lower left",frameon=False,ncol=2)
    fig.suptitle("Duplicar el grosor de la camisa reduce la fuga ~100x  (tunel evanescente)",x=.09,ha="left",fontsize=12,fontweight="bold")
    g3=json.load(open(os.path.join(ROOT,"experimentos","glass006a_claude","resultados.json")))["G3_tunnel"][3]
    note=ax.text(.98,.88,"",transform=ax.transAxes,ha="right",fontsize=9.5,color=TXT)
    def up(f):
        for k,(ln,v) in arts.items():
            n=min(len(v),f//8+1); ln.set_data([p[0] for p in v[:n]],[p[1] for p in v[:n]])
        if f>=30: note.set_text(f"prediccion WKB t {g3['t1']:.0f}->{g3['t2']:.0f} um: x{g3['ratio_pred']:.0f}   observado: x{g3['ratio_obs']:.0f}")
    caption(fig,"Datos: GLASS-006a (barrido de 18 casos con modo, solver radial). Camisa continua ideal: cota de modelo, no perdida medida")
    save(fig,up,50,"03_fuga_tunel.gif",fps=8)
if __name__=="__main__":
    for g in sys.argv[1:]: globals()["gif"+g]()
