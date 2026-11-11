# X: Un generador de imágenes por máquina

Hilo de 1 a 4 posts, cada uno de 280 caracteres como mucho (un enlace cuenta 23, un emoji 2). La imagen va en el
primero. Marca cada post con `**1/**`, `**2/**`… Un hashtag como mucho.

## es

**1/** Varios proyectos, un solo generador de imágenes local. Cada proyecto manda un pedido (clave + perfil + prompt + semilla), salen varios intentos y tú eliges uno. Y se puede deshacer.
Imagen: medios/diagrama.webp

**2/** ¿Por qué uno por máquina? Copiarlo en cada proyecto duplicaría los modelos (19 GB en un caso real) y cada copia acabaría distinta. El generador no conoce el dominio de nadie: solo recibe pedidos cerrados.

**3/** Una cola en disco hace una generación a la vez, y cada pedido tiene como mucho una elegida. El motor real aún está en desarrollo. #IAlocal

## en

**1/** Several projects, one local image generator. Each project sends an order (key + profile + prompt + seed), you get several attempts and pick one. And you can undo the pick.
Imagen: medios/diagrama.en.webp

**2/** Why one per machine? Copying it into every project would duplicate the models (19 GB in a real case) and every copy would drift. The generator knows nothing about anyone's domain: it only takes closed orders.

**3/** A queue on disk runs one generation at a time, and each order has at most one chosen image. The real engine is still in development. #LocalAI
