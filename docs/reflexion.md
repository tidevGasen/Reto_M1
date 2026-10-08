# Reflexión final

**Nombre:** Juan Pablo Alegría
**Reto:** Refactorización asistida por IA — Módulo 1

Mi reflexión sobre el reto, y en general sobre el módulo, es lo complejo y al
mismo tiempo simple que puede volverse usar la IA como herramienta de
desarrollo.

## Lo que aporta

Permite ahorrar mucho tiempo y estructurar mejor lo que vamos a realizar.
Hace diagnósticos, ejecuta cambios y los verifica mucho más rápido de lo que
lo haríamos nosotros: en este reto se pasó de 20 errores de ruff a 0 con 8
refactorizaciones, todas con los tests en verde a la primera iteración.
También propone detalles que uno puede pasar por alto. Los tests originales no
revisaban el texto del ticket ni los mensajes de error, y fue la IA la que
propuso agregar pruebas de caracterización **antes** de tocar el código. Al
pedirle una revisión de rendimiento, encontró algo más importante: el guardado
vaciaba el archivo antes de escribir y una interrupción podía borrar todos los
datos.

## Por qué hay que tener cuidado

Pero también hay que tener cuidado, porque llega a cometer errores u omitir
cosas, y lo hace con seguridad. En la refactorización 3 afirmó que la salida
era idéntica antes y después del cambio, pero su comparación ejecutaba el
código nuevo en ambos casos; lo detectó ella misma una refactorización
después. En otra ocasión, al quitar nombres crípticos, volvió a introducir uno.
Ninguno de los dos errores lo detectaron los tests: solo revisar la evidencia.

Además, demasiado contexto o demasiadas peticiones juntas la hacen perder el
foco de lo que se le solicita. Mis prompts vagos ("realiza una limpieza",
"realiza una optimización") la obligaron a interpretar, y funcionaron solo
porque el `CLAUDE.md` le ponía límites. En cambio, los prompts explícitos y
con un criterio medible ("debe eliminar los C901, SIM102 y SIM108") dejaron
claro qué hacer y cuándo terminar.

## Lo que me llevo

Por eso la importancia de todo lo visto en este módulo. No solo lo he aplicado
aquí, también lo he llevado a mi ambiente laboral:

- **Redacción:** he mejorado mis redacciones y la forma de hacer solicitudes.
- **Planear antes de ejecutar:** como el flujo que definí en el `CLAUDE.md`
  (revisar, planear, ejecutar, probar y solo entonces hacer commit).
- **Automatizaciones:** apoyarme en ellas para tareas repetitivas y de
  verificación.
- **La IA como auditora de sí misma:** usarla como revisora de su propio
  trabajo **sin el contexto inicial**, para no contaminar la auditoría y
  encontrar más fácilmente errores o detalles. Una sesión que ya "cree" que su
  solución es correcta tiende a confirmarla; una sesión limpia la revisa con
  ojos nuevos.

La conclusión es que la IA no sustituye el criterio: lo multiplica. El
responsable de cada cambio sigue siendo uno, y la calidad del resultado
depende de qué tan bien se planea, se pide y se verifica.
