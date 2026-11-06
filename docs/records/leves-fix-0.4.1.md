# Leves de `fix-0.4.1` (fusionada en `main` por el PR #5, 2026-11-06)

Se miran solo si una tarea toca lo mismo.

- **Leves de la fase 1 de `fix-0.4.1` (2026-11-06, no se revisan más en este PR):** el sustituto `fresh` que deja otro CLI en `ensure_running` no se compara con la versión y la huella propias (dos copias con código distinto se quedan con la del primero, sin aviso); los sondeos `worker_alive`/`lock_held`/`_no_worker` y los reintentos de `_single_worker`/`_single_instance` están copiados (un `fsutil` común); `server.BUILD` se calcula al importar `gimg.server`.
