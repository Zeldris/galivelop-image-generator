# Referentes de interfaz para `gimg` (F4)

Estado: investigación del agente, 2026-10-27, para la propuesta de interfaz (`propuesta.md`). Pregunta: **¿qué hacen
otros generadores de imágenes en los temas que nos importan, y qué de eso nos sirve?** Los temas son los de nuestro
recorrido: marca o estilo por proyecto; cola y espera larga (~3 min por imagen en la máquina de referencia); galería,
veredicto, comparar, historial y variaciones de un intento; retoque del prompt, semilla y parámetros; texto y logo sobre
la imagen; estados vacíos y de fallo. Vocabulario del `GLOSSARY.md` (proyecto, perfil, pedido, intento, candidata,
descartada, elegida, cola, manifiesto, referencia, perfil de máquina).

Lo que se saca de aquí, con coste y recomendación, está en la sección «Ideas de los referentes» de `propuesta.md`.

## Cómo se investigó y qué no se pudo comprobar

- Fuentes primarias: la documentación oficial de cada producto. Leídas directamente: Leonardo (centro de ayuda y
  documentación de la API), Ideogram (`docs.ideogram.ai`, corpus completo), Krea (`krea.ai/docs`), InvokeAI
  (`invoke.ai/features` y notas de versión), Fooocus (`readme.md` y `modules/private_logger.py` del repo) y ComfyUI
  (`docs.comfy.org`).
- **Midjourney, Adobe Firefly y Canva devuelven 403 a la descarga automática.** De ellos solo tengo los extractos de
  sus páginas oficiales que devolvió el buscador (citas literales, pero sin poder leer la página entera). Lo que viene
  de ahí lleva la marca *(extracto)*; lo que no está en ningún extracto, *(suposición)*.
- No probé ningún producto a mano: todo es documentación, no uso.

## Leonardo.ai

Fuentes: [Cómo generar imágenes](https://intercom.help/leonardo-ai/en/articles/8942360-how-to-generate-images-with-leonardo-ai),
[Flow State](https://intercom.help/leonardo-ai/en/articles/10002805-flow-state),
[Image Guidance (API)](https://docs.leonardo.ai/docs/generate-images-using-image-guidance),
[Elements (receta API)](https://docs.leonardo.ai/recipes/generate-images-with-elements.md),
[Compatibilidad de Elements](https://docs.leonardo.ai/docs/elements-and-model-compatibility).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Estilo por proyecto | Tres mecanismos: **modelos** afinados (el estilo es el modelo), **Elements** (LoRAs con un `weight` por elemento, rango propio de cada uno, compatibles solo con su modelo base) y **Style Reference** (imágenes propias con fuerza `Low…Max`; con varias, un `influence` que reparte el peso entre ellas). | Nuestro estilo es texto fijo por perfil (D2) más la paleta; no tenemos LoRA ni, de momento, referencias de estilo en la interfaz. La idea útil es la **referencia de estilo con fuerza**, que nuestro modelo de datos ya contempla («referencia», `maxRefs` del perfil de máquina) pero la propuesta no enseña. |
| Coste antes de generar | «Based on the model and settings, the token cost will be displayed on the Generate button.» Modo **Fast** o **Ultra** («Try ideating in Fast mode and Upscaling your favourite image»). | En nuestro caso el coste es **tiempo**: enseñarlo en el propio botón («Encolar · ~3 min») es lo mismo. Fast/Ultra es nuestro rápido/calidad (D30). |
| Variaciones | Flow State: un flujo de imágenes que se genera al hacer scroll; **«More Like This»** genera «a new stream of images using Style settings based on the selected image», y volver a pulsarlo afina más; los pasos quedan debajo de la barra de prompt para volver atrás. Estilo en cuatro ejes (Vibe, Lighting, Shot Type, Color Theme), aleatorios por defecto. «Scroll to Generate» limita a 8 por tanda y la cuota se ve en una rueda de porcentaje. | A ~3 min por imagen no hay flujo infinito. Lo que sí vale: **«más como esta» desde un intento** (variación con el intento como referencia) y **ver el gasto** (la cola y su tiempo). |
| Galería e historial | Las imágenes van al «AI Creation feed» y a la **Library**; al pasar el ratón: Upscale, share, download, Edit, Video. «Add to Collection» elige el destino antes de generar. Modo privado para que no salga al feed público. | El destino lo da el pedido; no necesitamos colecciones. Las acciones al pasar el ratón son lo que nosotros ponemos en el pie de la tarjeta. |
| Prompt | La API tiene `prompt_enhance` (`AUTO`/`ON`/`OFF`). | Mejora de prompt con un modelo: fuera de alcance (D6, solo stdlib); el prompt lo escribe el agente o la persona. |

## Midjourney *(extracto)*

Fuentes: [Style Reference](https://docs.midjourney.com/docs/style-reference),
[Moodboards](https://docs.midjourney.com/hc/en-us/articles/39193335040013),
[Website Overview](https://docs.midjourney.com/docs/explore-page),
[Draft & Conversational Modes](https://docs.midjourney.com/hc/en-us/articles/35577175650957),
[Creating on Web](https://docs.midjourney.com/hc/en-us/articles/33390732264589),
[The Web Editor](https://docs.midjourney.com/docs/the-web-editor).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Estilo por proyecto | `--sref <código>`: «Each numerical code produces a unique visual style»; `--sref random` genera uno y «reruns or variations keep that code»; `--sw` fija el peso. **Moodboards**: «select specific images to create a unique style», cada tablero tiene su código, se aplica con el conmutador de personalización o `--p`; no se combinan con `--sv`/`--sw`. | Dos lecciones: **un estilo tiene un identificador estable que viaja con la imagen** (nosotros: el `style` del perfil y la ronda que lo aprobó, que ya enseñamos en Piezas), y **un conjunto de imágenes de referencia con nombre por proyecto** (nuestras imágenes de marca, las mismas que calibran D31) es la forma natural de guiar el estilo cuando el texto no basta. |
| Espera y coste | Draft Mode «at half the GPU cost» con un botón junto a la barra de Imagine o `--draft`; en V8.1 «a big batch of 24 images». Velocidad Relax/Fast/Turbo *(suposición: de guías de terceros)*. | Es nuestro borrador (D32, decisión 5): barato y en lote para decidir el prompt; el definitivo después. |
| Galería y organización | **Organize**: «search, filter, and sort your images and videos». **Personalize**: aprende de valorar imágenes. | Filtrar y ordenar la galería de un pedido (por estado) sí nos sirve; la personalización por valoración no: nuestros veredictos ya son datos del pedido. |
| Editor | El editor junta «remix, inpainting (vary region), pan, and zoom—all at once»; **Retexture** «regenerates your entire image using a new style while keeping the structure and composition». | Nuestra edición es la composición (D28), no el repintado. Retexture es lo que haría una referencia de estilo sobre un intento bueno; va con la fila de referencias. |

## Ideogram

Fuentes (corpus `docs.ideogram.ai/llms-full.txt`, rutas): [`/create/image-settings`](https://docs.ideogram.ai/create/image-settings),
[`/create/create`](https://docs.ideogram.ai/create/create), [`/organize-and-share/assets`](https://docs.ideogram.ai/organize-and-share/assets),
[`/create/batch`](https://docs.ideogram.ai/create/batch), [`/edit/studio`](https://docs.ideogram.ai/edit/studio),
[`/edit/text-and-layers`](https://docs.ideogram.ai/edit/text-and-layers), [`/prompting/text-in-images`](https://docs.ideogram.ai/prompting/text-in-images).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Estilo | 62 **presets** bajo «Advanced settings» («Distinct, prescriptive aesthetics that define the image's look even with short prompts»), solo con el estilo Auto/General. **Referencias de estilo**: hasta 10 imágenes; «Style references replace the style preset»; una imagen de degradado «pulls colors toward it». **Código de estilo** en el panel de detalles de cada imagen, con «Use style code» para reutilizarlo. | Nuestro preset es la plantilla de pieza + el `style` del perfil. El detalle fino: la paleta puede guiarse con una imagen de degradado de la propia paleta (barato de generar desde la biblia) si algún día usamos referencias. |
| Parámetros | **Semilla**: campo vacío muestra «Random», botón de dado «New random seed»; aviso «A seed isn't a saved copy of an image and doesn't guarantee identical output or layout». Nº de imágenes Auto o 1-8 (Auto = 4; 2 con referencias). **Magic Prompt** encendido por defecto. Negativo solo en 3.0, como «Things to avoid». **Quality** Turbo/Default/Quality «trades speed and cost against detail». | El **dado de semilla** es la forma clara de «otra semilla» sin inventar un número. El aviso de la semilla es honesto y nos vale igual (FLUX recoloca). Negativo: no aplica (cfg 1). |
| Paleta | En el lote, `color_palette`: «a preset name, or up to 5 hex codes separated by spaces». | La paleta como parámetro de generación: lo nuestro hoy es texto en el `style`; la medida (D31) y la LUT (F5) lo cubren. |
| Historial y reutilizar | En cada imagen: **Copy prompt**, **Reuse prompt** («opens the app with the prompt and source references, but doesn't restore every setting»), **Recreate** («restores the supported inputs and settings from that run»; no genera al abrir). Panel **Details**: tipo, modelo, app, código de estilo; valoración «Good generation / Bad generation». «Search your generations»; vistas List/Grid/Mosaic. | **«Recreate» es la idea que nos falta**: cargar en el panel de retoque la semilla, pasos, modelo y prompt de *ese* intento, no los actuales del pedido. |
| Lote | Hoja de cálculo con hasta 500 filas (`prompt`, `model`, `num_images`, `aspect_ratio`, `seed_number`, `style`, `color_palette`…). Estados **In progress / Done / Stopped** con **Stop** y **Resume**; «If credits run out, the batch stops. Add credits and select Resume»; ZIP parcial descargable; el panel de errores muestra los cinco primeros. | Modelo de **cola parable y reanudable**, con descarga parcial de lo hecho: justo lo que una Deck que también es consola necesita. El lote por hoja no: lo hace la CLI (`ronda.sh`). |
| Texto sobre imagen | Studio: capa de texto («Inter Regular, size 80»; «Fonts come from Ideogram's library, and you can't upload your own»), **Layerize text** convierte letras pintadas en capas editables, «AI edit» con atajos «Change text to…». Consejos de prompt para texto: comillas, pronto, dónde, corto. | Confirma D28/D29: el texto y el logo se componen, no se piden al modelo; nosotros además usamos **las fuentes de la marca**, cosa que Ideogram no deja. |
| Estados | «Generation started» con **Jump to new generation**; fallo: «Could not generate that image. Please try again.»; estados vacíos distintos del «sin resultados» («We couldn't load apps» es error de carga y hay que reintentar). | Aviso de terminado **con enlace al intento**; distinguir «vacío» de «error de carga» (nuestra banda «el generador no responde»). |

## Krea

Fuente: [Training](https://www.krea.ai/docs/features/training).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Estilo por proyecto | Entrenar un estilo con «at least 3 images» (recomienda 10-30, homogéneas en luz, color y resolución); al acabar «Krea assigns a unique style code» aplicable a Flux, Edit y Enhancer; se refina subiendo más imágenes; publicar es opcional. | Un LoRA por marca es la versión cara de lo que hoy hacemos con texto + medida. En la Deck no se entrena; como mucho F5 con un entrenamiento externo. Lo que sí: **las imágenes de marca que ya existen en cada repo son el conjunto** (y ya las usamos para calibrar D31). |

## Adobe Firefly *(extracto)*

Fuentes: [Style Kits overview](https://helpx.adobe.com/firefly/work-with-enterprise-features/collaborate-using-style-kits/style-kits-overview.html),
[Use shared Style Kits](https://helpx.adobe.com/firefly/work-with-enterprise-features/collaborate-using-style-kits/use-shared-style-kits.html),
[Generate with a reference image](https://helpx.adobe.com/firefly/how-to/generate-image-using-reference-image.html).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Kit de estilo | «Once you generate an image you like, you can save it as a Style Kit by specifying the settings (including prompt, specifications for content, structure, style, and more) that are hidden or locked.» Quien lo recibe ve solo «those controls checked while the Style Kit was created and saved. The unchecked ones are either hidden or turned off», con un **Reset** al original. Crear kits exige plan enterprise; usarlos, un enlace. | Es nuestra **plantilla de pieza** con una idea más: la plantilla declara **qué se puede tocar y qué no** (tamaño, zona, logo y fuente fijos; título, subtítulo y prompt editables). Hoy el panel lo enseña todo igual. Y «Restaurar el del proyecto» es su Reset. |
| Referencia de estilo | «Applying the same Style reference image to other Firefly-generated images will help you build out your brand with a consistent look.» | Misma fila que Midjourney y Leonardo: referencia de estilo por proyecto. |

## Canva *(extracto)*

Fuentes: [Brand Kit](https://www.canva.com/help/brand-kit/), [Brand Kit best practices](https://www.canva.com/help/brand-kit-best-practices/),
[Create on-brand designs](https://www.canva.com/help/create-on-brand-designs/), [Magic Media](https://www.canva.com/help/using-magic-media/).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Marca por proyecto | Brand Kit: logos, colores, fuentes y recursos «in one place»; recomienda logos en PNG y **SVG**, «variations for different backgrounds», paletas «primary, secondary, and neutral» con hex y **etiqueta**, pares de fuentes para títulos y cuerpo («letter and line spacing can't yet be set»). **Brand Templates** dentro del kit para que lo generado «match your brand». **Brand Controls**: el admin restringe «to using only colors and fonts that are in Brand Kits». | Nuestra pestaña **Marca** ya es esto (roles con hex, logos sobre claro/oscuro, tipografía con tracking: hasta lo que Canva no deja). Lo nuevo: **Brand Controls** → el color del texto compuesto se elige **entre los de la paleta**, no en un selector libre. |
| Generación | Magic Media: describir, elegir estilo (photography, digital art, fine art) y **layout** (square, landscape, portrait), generar; el admin decide quién lo usa. | Los formatos por nombre son nuestros perfiles; nada nuevo. |

## InvokeAI (local)

Fuentes: [Gallery](https://invoke.ai/features/gallery/), notas de versión [v4.2.6](https://github.com/invoke-ai/InvokeAI/releases/tag/v4.2.6) y [v4.2.7](https://github.com/invoke-ai/InvokeAI/releases/tag/v4.2.7).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Galería e historial | **Boards** (siempre existe «Uncategorized»); **Auto-Assign Board on Click**: «The board selected at the moment you click Invoke becomes the destination. This allows you to queue multiple generations into different boards without waiting for them to finish», con una insignia `AUTO`. **Estrella** «Pins the image to the top of the gallery». **Download Board Images** en ZIP. | El destino lo fija el pedido (equivale a su auto-assign). La estrella es nuestra candidata; **que las candidatas suban arriba** o se filtren es la parte que nos falta. |
| Reutilizar un intento | «Generation data (prompt, seed, models, etc.) is stored inside each image file.» Menú: **Remix Image** («Loads all generation settings except the Seed»), **Use Prompt**, **Use Seed**, **Use All** («Loads all generation settings into the control panel»). | Misma idea que Recreate de Ideogram, y con más grano: **usar todo / solo la semilla**. Y los **metadatos dentro del PNG**: nuestro manifiesto lo hace para la elegida (D13, D21); para cada intento sería un chunk `tEXt` (stdlib). |
| Comparar | *(suposición)*: InvokeAI tiene un modo de comparar dos imágenes (deslizante, lado a lado, al pasar el ratón); no lo encontré en las páginas leídas ni en las notas de versión consultadas. | La decisión 8 (lado a lado) está tomada; aquí solo se anota. |
| Cola | *(suposición)*: cola persistente con pausa/reanudar y recorte de terminados; no lo pude leer en una fuente oficial. | Ver ComfyUI e Ideogram para lo comprobado. |

## Fooocus (local)

Fuentes: [`readme.md`](https://github.com/lllyasviel/Fooocus/blob/main/readme.md), [`modules/private_logger.py`](https://github.com/lllyasviel/Fooocus/blob/main/modules/private_logger.py).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Presets y estilos | Presets por archivo (`presets/default.json`, `realistic.json`, `anime.json`; «After Fooocus 2.3.0 you can also switch presets directly in the browser») que fijan modelo, estilos, negativo y más. Estilos combinables en «Advanced → Style»; «Fooocus V2» es expansión del prompt con GPT-2. Aspect Ratios, Image Number y Negative Prompt en «Advanced». | Preset = archivo JSON de datos sin código: exactamente nuestras piezas (`piezas.json`) y el catálogo de modelos (D30). La expansión de prompt, fuera (D6). |
| Historial | `log.html` por carpeta de fecha, **la más nueva primero**; por imagen, una tabla de metadatos, el «Full raw prompt» plegable y un botón **«Copy to Clipboard»** que copia los parámetros como JSON para pegarlos en el prompt y cargarlos. Los parámetros también van **dentro de la imagen** (PNG `tEXt`, EXIF en JPG/WebP); `--disable-image-log` y `--disable-metadata` lo apagan. | Nuestra galería ya es «la más nueva primero» con metadatos por tarjeta. «Copiar parámetros» para pegarlos al agente encaja con el «Copiar veredicto» del piloto. |

## ComfyUI (local)

Fuentes: [Interface overview](https://docs.comfy.org/interface/overview), [Job history](https://docs.comfy.org/interface/job-history).

| Tema | Qué hace | Qué nos dice |
|---|---|---|
| Cola | **Batch count** («How many times the workflow is queued per run»); `Shift`+Run encola **al frente**; modos Run / Run (On Change) / Run (Instant); **Cancel** «Stop the run that is executing now»; **Active jobs** con el nº en cola y en marcha, clic abre la cola, clic derecho la vacía; **Clear queue** «cancels all pending (queued, not yet running) jobs». | Nuestro cajón de cola ya tiene cancelar y subir; «encolar al frente» y «vaciar lo pendiente» son dos botones baratos. |
| Historial | Pestañas **All / Completed / Failed** («Failed» solo aparece si hay alguno); filas con estado, progreso en marcha y miniaturas. En marcha: abrir como flujo, copiar id, cancelar. Terminado: inspeccionar, **añadir la salida al flujo**, descargar, exportar. Fallido: abrir, **copiar el mensaje de error**, informar, quitar de la lista. | **«Copiar el error»** en la tarjeta de fallo (para pegarlo al agente) y una vista de fallos separada: barato y útil con `sd-cli`. |

## Resumen por tema (lo que se repite)

- **Estilo por proyecto**: todos tienen *algo* más que texto: referencias de estilo con fuerza (Leonardo, Midjourney, Ideogram, Firefly), estilo entrenado (Krea), presets como archivo (Fooocus). Nuestro texto + medida (D31) es la base; la **referencia de estilo por proyecto** es el siguiente escalón, y nuestro modelo de datos ya la nombra.
- **Reutilizar un intento**: Recreate (Ideogram), Use All / Use Seed / Remix (InvokeAI), Copy to Clipboard (Fooocus). Lo más barato y lo que más falta en la propuesta.
- **Coste visible antes de generar**: en el botón (Leonardo), en el modo (Midjourney Draft, Ideogram Quality). Nuestro coste es tiempo.
- **Cola con parar/reanudar y acciones por fallo**: Ideogram (Stop/Resume), ComfyUI (Clear queue, copiar error, pestaña Failed).
- **Plantillas con campos bloqueados y colores restringidos**: Firefly (hidden/locked), Canva (Brand Controls).
- **Texto sobre la imagen**: nadie lo deja en manos del modelo cuando importa (Ideogram lo pone en capas; Canva lo compone). D28/D29 van por el buen camino, y con las fuentes de la marca.
