# Troubleshooting de la marca del Portal

Lo que el generador no saca bien después de dos o tres intentos se apunta aquí como troubleshooting y se **rediseña con algo que sí sale**
(regla de la persona, 2026-11-12). Una fila por problema: qué falla, con qué intentos, y por qué se cambió.

| Problema | Intentos | Rediseño |
|---|---|---|
| Ventana de editor o terminal: Z-Image inventa glifos dentro; FLUX la respeta pero mete marco y graba pobre; el img2img entre los dos es inestable | q574-q607 | Portadas 06 sin ventana: barcos de papel sobre el mar grabado (lo que salió en la q311) |
| Compás de navegación (06 diseño): sale de latón o metálico, fotográfico y con glifos en las patas | q610, q616 | Barco de papel dibujado solo en línea discontinua, como un plano sin construir (#626-627) |
| Prefijo de cámara «Seen from high above looking down»: el mar sale fotorrealista y se pierde el grabado | q614 | Estructura del prompt de la q311: sujeto + «seen from slightly above» + su cola de estilo |
| Horizonte, cielo y nubes en escenas de mar abierto | q608, q610, q612 | En prueba: «no horizon, no sky, no clouds» en la cola de la q311 (#620-625); si sigue, mar visto como carta plana |
