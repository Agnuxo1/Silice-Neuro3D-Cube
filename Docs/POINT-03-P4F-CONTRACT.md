# P4F: detector circular independiente para elementos curvos P2

Registrar fuente antes de ensamblar/medir. No propagar GaussianT96 ni
cerrar convergencia. MallaP4C recuperada; mismo núcleo físico r6µm.

Verificar que todas las aristas curvas y sus cuerdas están fuera del
disco r6µm (salvo redondeo1e-12rel). Entonces su intersección con cada
elemento coincide con triángulo lineal de vértices∩disco; la función P2
se evalúa con la INVERSA de geometría curva, no por barycentría lineal.
Si esa propiedad falla, no adoptar este detector ni modificar la malla.

Elementos completos:masa local/cuadratura8. Parciales:integración
vertical y x=R*sin(theta), cortes en vértices/intersecciones arista-círculo.
Gauss16/32 en ambos ejes, pesospositivos. Detectorcampo C=integralphi_i*phi_j.
Segundo diagnóstico:intensidad interpolada linealmente por vértices físicos;
converge al mismo observable, pero su error de reconstrucción se informa.

Controles:momento constante y6campos físicamente lineales complejos,
semilla957; referencia cerrada piR²*(|c0|²+(|cx|²+|cy|²)/4),errorrel<=1e-10.
Pesosintensidadpositivos y área/momentos lineales correctos<=1e-10.
MatrizC simétrica, controlesPSD/potencia<=M para12vectoresaleatorios.
CompararC16/C32 en norma normalizada por cota inferior de masa:
M>=diag(d), d_j=lambda_min(M_ref)*suma_elementos_minJacobian(elemento).
Exigir máximo sumatorio fila deabs(D^-1/2*(C32-C16)*D^-1/2)<=1e-10.

Inicialización:P2proyecciónL2 de Gaussiananalítica cintura6µm, usando
cuadratura12/16, extremosDirichletfijos; comprobar diferencia campoM<=1e-9
y normalizar sóloentrada porM. Informar discrepancia de la potencia
del núcleo frente a1-exp(-2),sin confundir error de proyección espacial
con error de integración. No ajustar malla según esa discrepancia.

Guardar matrices, pesos, camposiniciales, comparación yhashes. CPUunhilo,
1800s,RAM>2GiB/disco>2GiB,sinGPU. TodoFAILseconserva. NoT96evolución
ni validaciónMaxwell. JEVlocal/bloqueoheredado.
