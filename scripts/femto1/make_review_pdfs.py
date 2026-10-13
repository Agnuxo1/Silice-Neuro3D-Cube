"""Review PDFs with the bundled reportlab runtime; no fabrication clearance."""
import argparse
import json
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def main():
    p=argparse.ArgumentParser();p.add_argument('--geometry',type=Path,required=True)
    p.add_argument('--f2',type=Path,required=True);p.add_argument('--drc',type=Path,required=True)
    p.add_argument('--noise',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();geo=json.loads(a.geometry.read_text());f2=json.loads(a.f2.read_text());drc=json.loads(a.drc.read_text());noise=json.loads(a.noise.read_text())
    a.out.mkdir(parents=True,exist_ok=True)
    drawing=a.out/'FEMTO1_candidate_drawing.pdf';report=a.out/'SIMULATION-REVIEW.pdf'
    if drawing.exists() or report.exists():raise FileExistsError('Preserve prior drawings')
    width,height=landscape(A4);canvas=Canvas(str(drawing),pagesize=(width,height))
    canvas.setTitle('FEMTO-1 provisional review drawing - not for manufacture')
    canvas.setFont('Helvetica-Bold',18);canvas.drawString(45,height-42,'FEMTO-1 | Plano de revision')
    canvas.setFillColor(colors.HexColor('#a11d24'));canvas.setFont('Helvetica-Bold',11)
    canvas.drawString(45,height-65,'PROVISIONAL - DRC FALLIDO - NO FABRICAR')
    canvas.setFillColor(colors.black);canvas.setFont('Helvetica',10)
    canvas.drawString(45,height-83,'Bloque supuesto: 45 x 25 x 2 mm. Radios de red: >=25 mm. Unidades del plano: mm.')
    ox,oy,scale=90,165,13.5
    canvas.setLineWidth(.8);canvas.rect(ox,oy,45*scale,25*scale)
    palette={'N1':'#097a73','N2':'#4969b3','N3':'#ce7a25','N4':'#854ba0','K1':'#66707a','K2':'#66707a','K3':'#66707a'}
    for guide in geo['guides']:
        canvas.setStrokeColor(colors.HexColor(palette[guide['zone']]));canvas.setLineWidth(.12)
        pts=guide['points_m'];indices=list(range(0,len(pts),max(1,len(pts)//250)))
        if indices[-1]!=len(pts)-1:indices.append(len(pts)-1)
        path=canvas.beginPath();path.moveTo(ox+pts[0][0]*1000*scale,oy+pts[0][1]*1000*scale)
        for i in indices[1:]:path.lineTo(ox+pts[i][0]*1000*scale,oy+pts[i][1]*1000*scale)
        canvas.drawPath(path)
    canvas.setFillColor(colors.black);canvas.setFont('Helvetica',9)
    canvas.drawString(ox,oy-17,'Entrada x=0');canvas.drawRightString(ox+45*scale,oy-17,'Salidas x=45')
    canvas.drawCentredString(ox+22.5*scale,oy-32,'45 mm (x)')
    canvas.saveState();canvas.translate(ox-30,oy+12.5*scale);canvas.rotate(90);canvas.drawCentredString(0,0,'25 mm (y)');canvas.restoreState()
    canvas.setFont('Helvetica-Bold',10);canvas.drawString(45,112,'Estado: '+str(drc['error_count'])+' entradas de error; '+str(len(drc['separation_failures']))+' alertas conservadoras de separacion.')
    canvas.setFont('Helvetica',9)
    for i,text in enumerate(['N1 entrenada | N2 precompensacion supuesta | N3 prototipos | N4 calibracion | K1-K3 cupones',
                             'Proyeccion superior de ejes: superposicion en 2D no prueba un cruce en 3D. No muestra volumen de nucleos.',
                             'Escalonado de coherencia, descartes T, acceso a cupones y reglas reales del fabricante pendientes.',
                             'No hay tolerancias aprobadas. CSV/JSON en um son candidatos de revision; CAM por confirmar.']):
        canvas.drawString(45,94-i*14,text)
    canvas.showPage();canvas.save()
    styles=getSampleStyleSheet();story=[]
    def para(text,style='BodyText'):story.append(Paragraph(text,styles[style]));story.append(Spacer(1,9))
    para('FEMTO-1 | Revision de simulacion','Title')
    para('PROVISIONAL - SIN DISPOSITIVO - NO ES PAQUETE DE FABRICACION','Heading2')
    para('13/10/2026. Fan-out incoherente 16 a 4; chip mas ocho parametros electronicos. Datos MNIST reducidos por media 7x7. Uso exploratorio anterior declarado. La nueva prueba de 4.955 imagenes sigue sellada. Validacion: 4.949 imagenes; calibracion separada del entrenamiento: 2.968.')
    table=[['Referencia en validacion','Precision (%)']]
    names={'majority':'Clase mayoritaria','logistic_C10_biasFalse':'Logistica sin sesgo (C=10)',
           'logistic_C10_biasTrue':'Logistica con sesgo (C=10)','prototype_normalized':'Prototipos normalizados',
           'nearest_neighbor_1':'Vecino mas cercano','MLP16_seed20261013':'MLP de 16 neuronas'}
    for name,label in names.items():
        table.append([label,f"{100*f2['references'][name]['accuracy']:.2f}"])
    t=Table(table,colWidths=[330,115]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#163a54')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.25,colors.lightgrey),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]));story.append(t);story.append(Spacer(1,12))
    para('Acoplamiento y calibracion','Heading2')
    table=[['Sigma kappa','Sin calibrar','8 parametros','8 parametros + TIA5%']]
    for point in f2['tolerance_points']:
        table.append([f"{100*point['sigma_kappa']:.0f}%",*[f"{100*point[k]['mean']:.2f}%" for k in ['uncalibrated','eight_parameters','eight_parameters_tia_sigma_005']]])
    t=Table(table,colWidths=[80,105,110,150]);t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.25,colors.lightgrey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eef1')),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,12))
    para('200 realizaciones por tolerancia sobre la misma validacion. La dispersion entre chips no es el IC binomial de precision. Calibracion: cuatro ganancias positivas y cuatro offsets, que rompen invariancia global al brillo. La variante con ruido alcanzo su limite de 30 iteraciones y no fue seleccionada; el fallo se conserva.')
    story.append(PageBreak())
    para('Ruido y potencia: requisito condicional','Heading2')
    para('Con calibracion ruidosa y error de kappa del 10%, sigma TIA del 0,5% alcanza 86,85%; sigma del 1% da 83,51%; sigma del 5% da 59,85%. El maximo nivel ensayado que supera el objetivo medio del 85% es 0,5%. No se atribuye este ruido a un componente real.')
    para('NEP supuesto de 10 pW/sqrt(Hz), banda de 500 MHz, eficiencia de entrada del 50%, salida del 50% y perdidas de 0,2 dB/cm en 55 mm dan una fuente requerida de aproximadamente 3,7 mW. Es una condicion de diseno: no incluye conjuntamente disparo, peor polarizacion, desalineacion o todos los errores de proceso. El modelo de retardo analogico tampoco incluye ADC/decision ni es una medida de banco.')
    para('Geometria y dependencias pendientes','Heading2')
    para(f"192 acopladores de red (48 por zona), {drc['guide_count']} segmentos/guias, radios de red de 25 mm y error de reconstruccion de matrices menor de 1,2e-16. DRC FALLIDO: {len(drc['separation_failures'])} alertas conservadoras de separacion. El revisor independiente confirma 316 parejas infractoras reales y 190 banderas conservadoras; el criterio prerregistrado sigue fallando. Los 16 haces incumplen el escalonado de caminos; una ruta de descarte no termina como se pretende. Faltan terminaciones T y acceso fisico a cupones.")
    para('Se ha enviado a FEMTOPRINT la consulta de formatos, reglas, cupones y posible colaboracion; la entrega o lectura no esta confirmada. F0 requiere respuesta escrita; F5 requiere perfil/proceso real y solver independiente; F6 completo y F7/F8 no estan cerrados. No se ha encargado, fabricado ni enviado el paquete tecnico final.')
    para('Fuentes: protocolos y recibos Git en la rama codex/femto1-20261013; F2_validation.json; DRC.json v2; NOISE-POWER.json; guia GUIA-PROTOTIPO-FEMTOPRINT.md v1.1. La propuesta de colaboracion se conserva como borrador interno.')
    SimpleDocTemplate(str(report),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=40,bottomMargin=40).build(story)
    print(json.dumps({'drawing':str(drawing),'report':str(report)}))

if __name__=='__main__':main()
