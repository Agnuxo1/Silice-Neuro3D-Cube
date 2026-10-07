"""Plot retained JSON results; this script performs no optical calculation."""
import argparse
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(ROOT/'resultados/codex/plot_cache')
os.environ['OMP_NUM_THREADS']='1'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--g',type=Path)
    parser.add_argument('--h',type=Path)
    args=parser.parse_args()
    e=json.loads((ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z/assessment.json').read_text())
    f=json.loads((ROOT/'resultados/codex/point03_reconstruction_20261007_run2/diagnostic.json').read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
    fig,ax=plt.subplots(1,2,figsize=(12,4.8))
    fig.subplots_adjust(left=.08,right=.97,bottom=.22,top=.78,wspace=.30)
    fig.suptitle('Punto 3: recuperación y contraste de convergencia',x=.08,ha='left',fontsize=16,fontweight='bold')
    dx=[128/n for n in (256,320,400,500)]
    ax[0].plot(dx,[100*p for p in e['primary_core_powers']],'o-',label='E: intensidad constante por celda',color='#a64636')
    ax[0].plot(dx,[100*p for p in f['spatial']['field']['powers']],'o-',label='F: campo reconstruido',color='#236f8c')
    ax[0].plot(dx,[100*p for p in f['spatial']['intensity']['powers']],'x--',label='F: intensidad reconstruida',color='#328754')
    subtitle='E: FAIL | F: diagnóstico, punto 3 abierto'
    if args.g:
        g=json.loads(args.g.read_text())
        ax[0].plot([128/r['N'] for r in g['rows'][:4]]+[.2],
                   [100*r['methods']['field']['P_core'] for r in g['rows'][:4]]+[100*g['rows'][-1]['methods']['field']['P_core']],
                   's-',label='G: dz menor y nueva malla N640',color='#694694')
        subtitle='E: FAIL conservado | G: '+('PASS local' if g['scientific_pass'] else 'FAIL')
    if args.h:
        h=json.loads(args.h.read_text())
        ax[0].plot([128/r['N'] for r in h['rows']],
                   [100*r['methods']['8']['field']['P_core'] for r in h['rows']],
                   '+--',label='H: referencia temporal sin separación',color='#ca8a20')
        subtitle+=' | H: '+('PASS local de potencia' if h['scientific_pass'] else 'FAIL')
    fig.text(.08,.84,subtitle,fontsize=11)
    ax[0].set(xlim=(.52,.18 if args.g else .24),xlabel='Paso transversal dx (µm)',ylabel='Potencia del núcleo (% de la entrada)')
    ax[0].legend(fontsize=8,frameon=False)
    ax[0].set_title('El método de integración cambia el funcional',loc='left',fontsize=11)
    names=['E','F campo','F intensidad']
    ratios=[e['holdout']['absolute_residual']/e['holdout']['maximum_residual']]
    ratios += [f['spatial'][m]['residual']/f['spatial'][m]['limit'] for m in ('field','intensity')]
    if args.g:
        names+=['G N640'];ratios+=[g['holdout']['field']['residual']/g['holdout']['field']['limit']]
    if args.h:
        names+=['H N640'];ratios+=[h['holdout']['field']['residual']/h['holdout']['field']['limit']]
    ax[1].bar(names,ratios,color=['#a64636','#236f8c','#328754','#694694','#ca8a20'][:len(names)],width=.55)
    ax[1].axhline(1,color='#555555',linestyle='--',lw=1.3)
    ax[1].set(ylabel='Residual de predicción / límite previo',ylim=(0,max(6.3,max(ratios)*1.08)))
    ax[1].set_title('Un valor mayor que 1 incumple el criterio',loc='left',fontsize=11)
    for i,v in enumerate(ratios):ax[1].text(i,v+.08,f'{v:.3f}',ha='center',fontsize=9)
    for a in ax:
        a.spines[['top','right']].set_visible(False)
        a.grid(axis='y',alpha=.18);a.set_axisbelow(True)
    note='Modelo escalar ideal a z = 2 mm. F reutiliza campos; G añade una malla nueva.'
    if args.h:note+=' H predice su nueva referencia N640 con G640 ya conocido.'
    fig.text(.08,.105,note,fontsize=8 if args.h else 9)
    fig.text(.08,.06,'No son medidas de una guía fabricada ni cotas certificadas del error de campo, fase o frontera.',fontsize=9,color='#555555')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.out,dpi=170)
    fig.savefig(args.out.with_suffix('.svg'),metadata={'Date':None})
    plt.close(fig)


if __name__=='__main__':main()
