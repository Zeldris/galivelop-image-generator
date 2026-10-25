<!-- galivelop-workflow v0.4.0 -->
# Glosario

Vocabulario de galivelop-image-generator. Primero van los términos del flujo; el proyecto añade debajo los de su dominio y los
mantiene al día (skill `domain-modeling`). El flujo nunca sobrescribe este archivo una vez creado.

## Términos del flujo

- **Bitácora**: `docs/traspaso.md`, el estado del trabajo para la siguiente sesión: rama, tarea en curso, siguiente paso,
  check.
- **Relevo**: una sesión que se acaba y otra que sigue desde la bitácora, sin preguntar por dónde iba.
- **Punto estable**: un estado con el check en verde, con commit y subido.
- **Check**: las órdenes del proyecto que tienen que pasar en cada commit que se sube: `bash -n .githooks/pre-commit .githooks/pre-push .githooks/commit-msg`.
- **Commit `WIP:`**: un commit subido con algo a medias o en rojo; la bitácora dice qué falla y por qué.
- **Rama protegida**: `main`, lo publicado; solo recibe trabajo revisado, con confirmación
  de la persona.
- **Marca de revisión**: `docs/registros/revisado.txt`, el archivo versionado con el sha del último commit revisado; los ganchos
  aceptan código hasta él.
- **Contenido frente a código**: el contenido (lo que casa con `content` de `.claude/gw.json`) no necesita revisión
  de código; todo lo demás es código.
- **Encargo a un subagente**: lo que recibe un subagente: objetivo, rutas, restricciones, el check que debe pasar y
  qué tiene que devolver.
- **Retro**: la retrospectiva de la sesión antes de ir a la rama protegida; sus propuestas se presentan a la persona y
  lo que confirme se aplica en la rama.
- **Propuesta (`.gw-nuevo`)**: un archivo del flujo que la actualización no pudo aplicar sin perder cambios locales;
  se fusiona a mano y luego se borra.

## Términos del proyecto

<!-- **Término**: definición, y dónde vive en el código. -->

**Generador**:
El servicio local, uno por máquina, que convierte pedidos en imágenes y los proyectos comparten.
_Evitar_: image-generator (la carpeta de World-Maker-Fantasy), servidor

**Proyecto**:
Un repositorio que usa el generador: declara su configuración y le manda pedidos. El generador no conoce su dominio.
_Evitar_: cliente, mundo, juego

**Configuración del proyecto**:
El archivo que un proyecto tiene en su repo para conectarse al generador: sus perfiles, su estilo y su carpeta de
entrega.

**Pedido**:
La petición cerrada de una imagen que hace un proyecto: prompt, perfil, referencias y destino.
_Evitar_: encargo (en este repo es el «encargo a un subagente» del flujo), trabajo, job, petición

**Intento**:
Una imagen generada para un pedido con una semilla y unos parámetros concretos; un pedido tiene varios.
_Evitar_: prueba, variante, render

**Candidata**:
Un intento que la persona marca como bueno sin elegirlo todavía.
_Evitar_: favorita

**Descartada**:
Un intento que la persona aparta; sigue en el historial.
_Evitar_: borrada, papelera

**Cola**:
Los pedidos pendientes de generar, en orden de llegada; se generan de uno en uno.

**Manifiesto**:
El archivo del proyecto que dice, por cada elegida, con qué se generó, para poder reproducirla.

**Perfil de máquina**:
Los límites con los que el generador trabaja en un equipo concreto (memoria, referencias por pedido, tiempo máximo).
_Evitar_: preset, modo

**Perfil**:
Un tipo de imagen con nombre y tamaño fijos que declara un proyecto (p. ej. `banner`, `thumbnail`).
_Evitar_: tamaño, formato, miniatura

**Estilo del proyecto**:
El texto fijo que el proyecto declara por perfil y el generador añade a cada prompt; no lleva lógica del dominio.

**Referencia**:
Una imagen existente que acompaña a un pedido para guiar la generación.

**Elegida**:
El intento que la persona escoge para un pedido, como mucho uno por pedido; es el único que se entrega al proyecto.

**Carpeta de entrega**:
La carpeta del proyecto donde el generador deja las elegidas.

**Motor**:
El programa externo que genera la imagen a partir del prompt y los modelos (hoy stable-diffusion.cpp).

**Máquina de referencia**:
El equipo donde se mide y se valida el generador: la Steam Deck con Linux y Vulkan.
