# Punto 3, diagnóstico F: reconstrucción del observable sobre los campos de E

Registro previo al cálculo: 7 de octubre de 2026. E ya se conoce y permanece
FAIL. Este diagnóstico no repite propagaciones, no cambia sus umbrales y no
permite aceptar retrospectivamente E ni cerrar por sí solo el punto 3.

Hipótesis contrastable: integrar una intensidad constante por celda introduce
una dependencia de la posición del borde del detector en la malla. La cobertura
geométrica exacta del círculo no elimina ese error de reconstrucción. Una
reconstrucción suave puede cambiar la irregularidad de los órdenes observados.
También puede no hacerlo: se conservarán ambas posibilidades.

Fuentes fijas: las ocho entradas y campos finales de
`point03_analytic_20261007T004526617696Z`, con identidades tomadas del assessment
original y comprobadas de nuevo. No se modifica ningún array original. No se
alinea fase, ajustan parámetros físicos ni normalizan campos finales.

Dos reconstrucciones prefijadas, sobre las mismas coordenadas de E:

1. Interpolación bicúbica del campo complejo, seguida por su módulo al cuadrado.
2. Interpolación bicúbica de la intensidad nodal original.

Se usa RectBivariateSpline con grados tres, interpolación `s=0` y sin
extrapolación. Se integra el disco de radio 6 um en coordenadas polares, con
Gauss–Legendre sobre t=r²/R² y regla trapezoidal angular periódica. Niveles
fijos: (64,256), (128,512), (256,1024), pares radial/angular. Se calculan todos,
sin seleccionar un nivel por su resultado favorable.

Controles previos: gaussiana de cintura de amplitud 6 um y potencia continua
unitaria, cuya integral del disco es 1-exp(-2). En las cuatro mallas, error
de cada reconstrucción <=1e-5 y en N500 <=1e-6. Cambio entre los dos últimos
niveles de cuadratura <=1e-10 para la gaussiana y <=1e-8 para cada campo óptico.
Las interpolaciones deben ser finitas; una intensidad negativa con magnitud
>1e-12 del máximo nodal invalida esa reconstrucción. No recortar negativos.
La diferencia de métodos en N500 se contrasta contra 1e-7, sin declararla
cota del error real.

Se recalculan los criterios espaciales de E (signos, órdenes, estabilidad del
20%, predicción con residual <=10% del último incremento) para **ambos**
observables, únicamente como diagnóstico. Para cada método se guarda la
predicción basada en N256/320/400 antes de integrar el campo N500. Es una
retención prospectiva del nuevo postprocesado, no una simulación desconocida:
los campos ya existen y E ya fue examinado.

Se integran también los cuatro controles longitudinales. Se conservan q y los
resultados con la banda original [1.8,2.2]. Una corrección formal con orden dos
puede mostrarse como sensibilidad descriptiva, nunca como incertidumbre
aceptada si los prerrequisitos originales fallan. No cambiar banda ni excluir
N400 después de ver los resultados.

Un proceso CPU, un hilo numérico, <=120 s, RAM disponible>1.5 GiB, disco>2 GiB.
Sin nuevas dependencias ni GPU. Salida exclusiva bajo resultados/codex;
retener contrato, fuentes, hashes, controles y todos los resultados o errores.

La referencia metodológica es la [guía NASA sobre convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html):
la extrapolación de un funcional exige discretización consistente y revisión
del régimen asintótico. Se usa como guía de verificación, no de física óptica.

JEV: v2-doctor local comprobado ready. La prohibición heredada de reintentar
el canal por bloqueo de seguridad se conserva; no hay recomendación remota.
Próximo trabajo, condicionado a F: diseñar un ensayo de refinamiento nuevo
que discrimine reconstrucción del detector y resolución del operador, con
criterios registrados antes de nuevas trayectorias. No avanzar al barrido modal.
