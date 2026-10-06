"""Plot the retained Stage B powers and auxiliary-error screen; no fitting."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("input",type=Path)
parser.add_argument("output",type=Path)
args=parser.parse_args()
data=json.loads(args.input.read_text(encoding="utf-8"))
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"svg.fonttype":"none"})
fig,axes=plt.subplots(1,2,figsize=(12,4.9),gridspec_kw={"width_ratios":[1.35,1]})
fig.subplots_adjust(left=.075,right=.97,bottom=.23,top=.78,wspace=.31)
fig.suptitle("Punto 3 · Serie B: ocho simulaciones completas",x=.075,y=.97,ha="left",fontsize=17,fontweight="bold")
fig.text(.075,.885,"Ejecución e integridad: PASS     |     Criterios de convergencia: FAIL",fontsize=12,color="#8c2929")
dx=[128/n for n in data["primary_grids"]]
power=[100*p for p in data["primary_core_powers"]]
left=axes[0]
left.plot(dx,power,"o-",color="#1b668f",lw=1.8,ms=6,label="Primarias: SS64, Δz = 1,25 µm")
left.scatter([dx[-1]],[100*data["holdout"]["predicted_core_power"]],marker="x",s=80,lw=2,color="#b54636",label="Predicción de la cuarta malla",zorder=5)
left.set(xlim=(.52,.236),xlabel="Paso transversal dx (µm); refinamiento hacia la derecha",ylabel="Potencia del núcleo (% de la entrada)")
left.set_xticks(dx)
left.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f"{v:.3f}".replace(".",",")))
left.grid(axis="y",alpha=.2)
left.legend(loc="lower right",fontsize=9,frameon=False)
left.set_title("Las diferencias disminuyen; la predicción falla",fontsize=11,loc="left",pad=13)
right=axes[1]
geometry=[data["auxiliary"][str(n)]["profile_component"]*1e6 for n in (400,500)]
longitudinal=[data["auxiliary"][str(n)]["longitudinal_component"]*1e6 for n in (400,500)]
geometry.append(sum(geometry));longitudinal.append(sum(longitudinal))
right.bar([0,1,2],geometry,color="#dba450",width=.56,label="Muestreo del perfil")
right.bar([0,1,2],longitudinal,bottom=geometry,color="#5c92a6",width=.56,label="Paso de propagación")
limit=data["auxiliary_maximum_sum"]*1e6
right.hlines(limit,1.63,2.37,colors="#a83131",lw=2,linestyles="--")
right.text(2.35,limit+.75,"Límite de la suma",ha="right",va="bottom",color="#a83131",fontsize=8.5)
right.set(xticks=[0,1,2],xticklabels=["N = 400","N = 500","Suma"],ylabel="Cambio absoluto (10⁻⁶ de la potencia de entrada)",ylim=(0,30))
right.grid(axis="y",alpha=.2)
right.set_axisbelow(True)
right.legend(loc="upper right",frameon=False,fontsize=9)
right.set_title("Sensibilidad auxiliar: 3,66 × el presupuesto",fontsize=11,loc="left",pad=13)
for ax in axes:
    ax.spines[["top","right"]].set_visible(False)
fig.text(.075,.10,"Residuo de la predicción: 1,83 × el límite. No se acepta un indicador GCI.",fontsize=10,fontweight="bold")
fig.text(.075,.052,"Los límites son controles prospectivos del protocolo; estas diferencias no miden el error frente a la solución física exacta.",fontsize=9,color="#555555")
args.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(args.output,metadata={"Date":None})
if args.output.suffix.lower() == ".svg":
    svg_text = args.output.read_text(encoding="utf-8")
    args.output.write_text("\n".join(line.rstrip() for line in svg_text.splitlines())+"\n", encoding="utf-8")
fig.savefig(args.output.with_suffix(".png"),dpi=160)
plt.close(fig)
