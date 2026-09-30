from gifstyle import *
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
def cube_edges(s=1):
    v=np.array([[x,y,z] for x in(-s,s) for y in(-s,s) for z in(-s,s)])
    E=[(i,j) for i in range(8) for j in range(i+1,8) if np.sum(v[i]!=v[j])==1]; return v,E
def bez(p0,p1,p2,p3,t): 
    t=t[:,None]; return (1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t**2*p2+t**3*p3
def build():
    fig=plt.figure(figsize=(11,4.4)); ax=fig.add_axes([0.0,0.0,0.52,1.0],projection="3d"); ax.set_axis_off(); ax.set_facecolor(BG)
    ax.set_xlim(-1.3,1.3);ax.set_ylim(-1.3,1.3);ax.set_zlim(-1.3,1.3); ax.set_box_aspect((1,1,1))
    v,E=cube_edges(1)
    faces=[[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1)],[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)],[(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1)],[(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)],[(-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1)],[(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)]]
    ax.add_collection3d(Poly3DCollection(faces,facecolors=CY,alpha=.05,edgecolors="none"))
    for i,j in E: ax.plot(*zip(v[i],v[j]),color=CY,alpha=.55,lw=1.2)
    # guias: 4 carriles entran por x=-1, se mezclan (2 etapas) y salen por x=+1 (ilustracion)
    t=np.linspace(0,1,80); paths=[]
    ys=[-.6,-.2,.2,.6]; zs=[.5,-.5,.5,-.5]
    mid1=[(-.6,.5),(-.2,-.5),(.2,.5),(.6,-.5)]
    order=[0,2,1,3]
    for k in range(4):
        p0=np.array([-1,ys[k],zs[k]]); p3=np.array([1,ys[order[k]],zs[order[k]]*-1])
        p1=p0+np.array([.8,0,0]); p2=p3-np.array([.8,0,0])
        pts=bez(p0,p1,p2,p3,t); paths.append(pts)
        ax.plot(pts[:,0],pts[:,1],pts[:,2],color=MG,alpha=.8,lw=2.2)
    pulses=[ax.plot([],[],[],"o",color="#ffffff",ms=7,mec=CY,mew=2)[0] for _ in range(4)]
    laser=ax.plot([],[],[],color=AM,lw=2.5,alpha=.9)[0]; spot=ax.plot([],[],[],"o",color=AM,ms=9,alpha=.95)[0]
    fig.text(0.53,0.66,"Silice-Neuro3D-Cube",fontsize=30,fontweight="bold",color=TXT,va="center")
    fig.text(0.535,0.50,"Redes opticas 3D escritas con laser de femtosegundo\nen un cubo de silice: simulacion verificable primero.",fontsize=13,color=CY,va="center",linespacing=1.5)
    fig.text(0.535,0.28,"CPU · BPM · modos acoplados · oraculos independientes\nfallos retenidos · sin dispositivo fabricado (aun)",fontsize=10.5,color=MUTED,va="center",linespacing=1.6)
    fig.text(0.535,0.08,"ilustracion conceptual del cubo · cifras del repo en los demas GIF",fontsize=8,color=MUTED)
    def update(f):
        ax.view_init(elev=16,azim=-90+38*np.sin(f/120*2*np.pi))
        for k,p in enumerate(pulses):
            u=(f/60+k*0.13)%1; i=int(u*79); p.set_data([paths[k][i,0]],[paths[k][i,1]]); p.set_3d_properties([paths[k][i,2]])
        nrm=np.array([(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)][(f//20)%6],float)
        ph=(f%20)/20; tgt=nrm*(1-0.9*ph)      # el foco entra desde la cara y escribe hacia dentro
        src=nrm*1.55; laser.set_data([src[0],tgt[0]],[src[1],tgt[1]]); laser.set_3d_properties([src[2],tgt[2]])
        spot.set_data([tgt[0]],[tgt[1]]); spot.set_3d_properties([tgt[2]])
        return []
    return fig,update
if __name__=="__main__":
    fig,up=build(); save(fig,up,120,"header.gif",fps=20)
