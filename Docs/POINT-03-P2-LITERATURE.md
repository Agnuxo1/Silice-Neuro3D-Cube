# Fuentes consultadas para controlar dominio y muestreo

Consulta del7deoctubre de2026, P1/P2. Mantener resultados simulados,
fundamento metodológico y disponibilidad de herramientas separados.

- [NASA, convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html):
  página/metodología de refinamiento consultada. Mantener parámetros de
  generación de malla, verificar régimen asintótico y distinguir solución
  numérica de física. No suministra una cota específica para T96.
- [Artículo de interfaces inmersas para Schrödinger](https://www.cambridge.org/core/journals/numerical-mathematics-theory-methods-and-applications/article/abs/high-order-scheme-for-schrodinger-equation-with-discontinuous-potential-i-immersed-interface-method/8AEC23C8A8F732C4CB7BB24921BD78C9):
  sólo abstract accesible; enlace PDF redirigió a la ficha. Describe incorporar
  condiciones de salto para potencial discontinuo. No se adopta ese método
  sin estudiar y verificar su formulación completa; no se atribuye a P2.
- [Laboratorio P2PCLAW](https://www.p2pclaw.com/lab):
  la página de simulación redirige al hub. Guía local lab-usage consultada:
  requiere X-Agent-Key y declara presupuesto de cálculo remoto. Su listado
  general menciona FEniCS, pero la referencia de parámetros no proporciona
  un problema óptico compatible ni se obtuvo un ejecutor verificado.
  No se enviaron trabajos, no se atribuyen resultados externos ni se
  presentan herramientas anunciadas como simulaciones realizadas.

P1/P2 utilizan NumPy/SciPy instalados y kernels locales ya contrastados.
La prueba sintética N799 previa a P2 pasó:seno de alta frecuencia,
error2,14771e-13,100pasos en27,180s, previsión FDST6958,015s. Es control
y estimación de coste, no trayectoria T96 ni garantía del tiempo real.
Registro del control:`11772eb`; controlador y auditor P2:`cf27431`.
