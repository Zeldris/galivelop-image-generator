# Web: muro de Portal-Galivelop

La tarea semanal del portal lee solo el bloque JSON. Se publica cuando `estado` es `"listo"` y `fecha` es de hoy o
anterior; lo pasa a `"listo"` la persona. Sin `muro`, la pieza solo da una novedad en la ficha del proyecto. Cada
`archivo` es relativo a la carpeta de la pieza y lleva su `-mini` al lado; con versión por idioma, `archivo` es un
objeto (`{ "es": "medios/<nombre>.webp", "en": "medios/<nombre>.en.webp" }`).

```json
{
  "estado": "borrador",
  "fecha": "AAAA-MM-DD",
  "texto": { "es": "…", "gl": "…", "en": "…" },
  "muro": {
    "titulo": { "es": "…", "gl": "…", "en": "…" },
    "cuerpo": [{ "es": "…", "gl": "…", "en": "…" }],
    "imagenes": [
      { "archivo": "medios/<nombre>.webp", "alt": { "es": "…", "gl": "…", "en": "…" } }
    ]
  }
}
```
