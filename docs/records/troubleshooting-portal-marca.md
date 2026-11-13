# Troubleshooting de la marca del Portal

Lo que el generador no saca bien después de dos o tres intentos se apunta aquí como troubleshooting y se **rediseña con algo que sí sale**
(regla de la persona, 2026-11-12). Una fila por problema: qué falla, con qué intentos, y por qué se cambió.

| Problema | Intentos | Rediseño |
|---|---|---|
| Ventana de editor o terminal: Z-Image inventa glifos dentro; FLUX la respeta pero mete marco y graba pobre; el img2img entre los dos es inestable | q574-q607 | Portadas 06 sin ventana: barcos de papel sobre el mar grabado (lo que salió en la q311) |
| Compás de navegación (06 diseño): sale de latón o metálico, fotográfico y con glifos en las patas | q610, q616 | Barco de papel dibujado solo en línea discontinua, como un plano sin construir (#626-627) |
| Prefijo de cámara «Seen from high above looking down»: el mar sale fotorrealista y se pierde el grabado | q614 | Estructura del prompt de la q311: sujeto + «seen from slightly above» + su cola de estilo |
| Horizonte, cielo y nubes en escenas de mar abierto | q608, q610, q612 | En prueba: «no horizon, no sky, no clouds» en la cola de la q311 (#620-625); si sigue, mar visto como carta plana |
| Barco de papel repetido: la web ya tiene dos (q311 del Developer y la 19 «enviado»); las 06 con barcos se confunden con ellas, y la hoja a medio doblar sale como barco entero (q620) | q608, q612, q620 | Serie del faro en tres estados: en obra con andamio (desarrollo), en plano discontinuo (diseño), encendido (publicado) (#628-633) |
| Dibujo en línea discontinua o de plano (ruta del compás, faro de plano): Z-Image dibuja el objeto macizo y terminado | q616, q630, q631 | 06 diseño = el islote con solo los cimientos, estacas, cuerdas y bloques: la fase antes de la obra (#634-635) |
| Reloj con flecha que gira hacia atrás (08c historial): sin flecha se lee como «hora» (q646); con ella, punta en estrella y bucle (q647) | q646, q647 | Línea de tiempo vertical con tres nodos y sus renglones, de la familia de las ramas del 08d (#648-649) |
| Grafo de commits como cabecera ancha (30 y 30b): sale una sola línea con bolas, un collar sin ramas, con horizonte de mar y en acuarela, no grabado | q821, q830-q832 | Se cambia el motivo por uno que el generador sí saca (pendiente de prompt, 2026-11-13) |
