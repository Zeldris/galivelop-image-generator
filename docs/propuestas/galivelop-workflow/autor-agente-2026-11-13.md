# Propuesta al workflow: bloquear los commits a nombre del agente (2026-11-13)

De `galivelop-image-generator`, rama `ccr-85e9d14e-zt7p8b`. Pedida por la persona.

## Problema

`agentSignatures: false` solo mira el **mensaje** del commit (`commit-msg`) y el texto que se publica en GitHub
(`agent-signatures.py`). El **autor** solo lo avisa `session-start.sh` (l.116) cuando `user.email` es
`noreply@anthropic.com`, sin bloquear nada. Un contenedor nuevo trae `Claude <noreply@anthropic.com>`, y si el agente
pasa por alto el aviso, los commits salen a nombre del agente: en este repo, 57 en `main`.

Además, el gancho de parada del entorno en la nube pide justo lo contrario (autor `noreply@anthropic.com` para que
GitHub no marque el commit como «Unverified»); con `agentSignatures: false` hay que ignorarlo, y conviene decirlo en
`AGENTS.md`/`CLAUDE.md` de la plantilla.

## Cambio (aplicado aquí como cambio local, a llevar a `templates/githooks/`)

- `commit-msg`: con `agentSignatures: false` y fuera de un rebase, `git var GIT_AUTHOR_IDENT` y `GIT_COMMITTER_IDENT`;
  si alguno es `<noreply@anthropic.com>` (sin distinguir mayúsculas), rechaza con la orden que fija la identidad.
- `pre-push`: con `agentSignatures: false` en la configuración del commit que se sube, rechaza los commits nuevos
  (los mismos que mira `private-check.py`) cuyo `%ae` o `%ce` sea `noreply@anthropic.com`, con la orden
  `git rebase --exec 'git commit --amend --no-edit --reset-author' <remoto>/<rama>`.
- Tests: `tests/test_hooks_autor.py` de este repo (commit-msg con autor agente, solo committer agente, persona; pre-push
  con un `commit-tree` a nombre del agente). Rojos sin el cambio (`red-without-fix.sh`).

## Para decidir en el workflow

- Si `session-start.sh` debería, además de avisar, proponer la identidad de los últimos commits humanos de la rama
  protegida (`git log <protegida> --format='%an <%ae>'` sin `noreply@anthropic.com`), sin escribirla en el repo.
- Que `doctor.py` compruebe que `user.email` no es el del agente con `agentSignatures: false`.
- Los commits históricos no se tocan: `pre-push` solo mira lo que no está ya en un remoto.
