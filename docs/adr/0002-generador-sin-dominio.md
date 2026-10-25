# El generador no conoce el dominio de los proyectos

El generador solo recibe pedidos cerrados (prompt, perfil, referencias, destino); construir el prompt es cosa de
cada proyecto. En World-Maker-Fantasy el generador leía la enciclopedia del backend, los prompts de su Postgres y el
mundo `helek-sirik` fijo, y eso lo hacía imposible de reutilizar. Lo único del proyecto que el generador aplica es un
estilo del proyecto declarado por perfil, un texto fijo sin lógica.

## Opciones consideradas

- Plugins de dominio dentro del generador (un adaptador por proyecto): rechazado, cada proyecto nuevo cambiaría el
  generador.
