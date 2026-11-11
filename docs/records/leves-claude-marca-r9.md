# Leves de `claude/marca-r9`

De la fase 1 del 2026-11-11 (`/code-review` del diff contra `origin/main` `fa1076e`) y de antes. No se revisan más
en ese PR; se miran solo si una tarea toca lo mismo.

- La pieza `avatar` de `examples/galivelop-image-generator/piezas.json` usa el símbolo r9 mientras `og`/`social`
  siguen con el lockup congelado: va con la tarea de medir `og`/`social` con el lockup nuevo.
- `gimg/ui/assets/gvig-lockup.svg` no lo usa la interfaz; solo lo mantiene `test_ui_lockup_matches_the_brand_one`.
- Los tokens `--brand` y `--family` de `gimg/ui/css/tokens.css` no los usa ninguna regla.
- En tema claro el hover de `.btn-primary` no cambia nada (`--accent` = `--accent-fill`).
- `gimg/ui/mock/api-mock.js` nombra «Sora» en datos simulados.
- El nombre del lockup va en `<text>` vivo (pendiente de pasar a trazados): sin Big Shoulders Display instalada sale
  en la fuente de reserva.
- Monograma «GVIG» sin dibujar.
- Hecho en la retro (P4): los `<title>` de los símbolos decían «galivelop-image-generator: rejilla de intentos».
