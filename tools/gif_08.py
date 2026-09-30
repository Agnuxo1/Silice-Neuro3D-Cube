import sys,json,os,math
from gifstyle import *
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")

def gif8():
    r9=json.load(open(os.path.join(ROOT,"experimentos","glass009_claude","resultados009.json")))
    rows=r9["comparison"]; keys=["cont","t48","t96","t192","t88"]
    labs=["continua","48 trazos","96 trazos","192 trazos","96, hueco"]
    bpm=[rows[k]["bpm007"]*100 for k in keys]; adi=[rows[k]["adi"]*100 for k in keys]
    fig,(ax,bx)=plt.subplots(1,2,figsize=(10.5,4.8),gridspec_kw={"width_ratios":[1.5,1]}); fig.subplots_adjust(left=.07,right=.98,top=.85,bottom=.17,wspace=.22)
    x=np.arange(5); w=.36
    b1=ax.bar(x-w/2,[0]*5,w,color=CY,label="BPM (FFT + esponja) - Codex"); b2=ax.bar(x+w/2,[0]*5,w,color=AM,label="ADI Crank-Nicolson - Claude")
    ax.set_xticks(x); ax.set_xticklabels(labs,fontsize=9); ax.set_ylim(0,52); ax.set_ylabel("% de la entrada en el nucleo (z = 2 mm)"); ax.grid(True,axis="y",alpha=.4); ax.legend(frameon=False,loc="upper left",fontsize=9)
    tx=[ax.text(i,0,"",ha="center",fontsize=8.5,color=TXT) for i in range(5)]
    # panel derecho: el sesgo comun del pixelado del nucleo
    n=25; g=np.arange(-n,n+1)*0.5; X,Y=np.meshgrid(g,g); inside=(X*X+Y*Y<36)
    bx.set_aspect("equal"); bx.set_xlim(-8,8); bx.set_ylim(-8,8); bx.set_xticks([]); bx.set_yticks([])
    bx.set_title("Sesgo comun: el nucleo en pixeles de 0.5 um",loc="left",fontsize=10.5)
    bx.imshow(np.where(inside,1.0,0.12),extent=[g[0]-.25,g[-1]+.25,g[0]-.25,g[-1]+.25],cmap=LIGHT,vmin=0,vmax=1.6,origin="lower")
    th=np.linspace(0,2*np.pi,200); ex,=bx.plot(6*np.cos(th),6*np.sin(th),color=MG,lw=1.8); bx.text(0,-7.3,"area en pixeles = 96.6 % del circulo exacto",ha="center",fontsize=9,color=MUTED)
    ex.set_alpha(0)
    tt=fig.suptitle("",x=.07,ha="left",fontsize=12,fontweight="bold")
    def up(f):
        k=min(5,f//14+1); t=min(1,(f%14)/9) if f<70 else 1
        for i in range(5):
            s1=bpm[i]*(1 if i<k-1 else (t if i==k-1 else 0)); s2=adi[i]*(1 if i<k-1 else (t if i==k-1 else 0))
            b1[i].set_height(s1); b2[i].set_height(s2)
            tx[i].set_position((i,max(s1,s2)+1.2)); tx[i].set_text(f"d = {abs(bpm[i]-adi[i]):.2f} pt" if (i<k-1 or (i==k-1 and t>=1)) else "")
        ex.set_alpha(1 if f>=70 else 0)
        tt.set_text("Dos metodos numericos independientes coinciden (max 0.24 puntos)" if f<70 else "...pero comparten el sesgo del observable: acuerdo no es validacion absoluta")
    caption(fig,"Datos: GLASS-009 vs GLASS-007. Mascaras identicas (0 pixeles de diferencia). K1, K2, K4-dx y K5 fallan y estan retenidos en el repositorio")
    save(fig,up,100,"08_dos_solvers.gif",fps=10)

if __name__=="__main__": gif8()
