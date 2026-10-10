# CHANGELOG — Sunkuu 360

Registro de cambios en producción (ThingsBoard PE 4.3, 360.sunkuu.com) y su trazabilidad entre repos.
Fuente de verdad de la configuración: `../sunkuu-tb-config` (Version Control de ThingsBoard).
Fechas en hora de Lima (UTC−5).

| Fecha | ID | Cambio | Componentes | Commit sunkuu-tb-config | Commit sunkuu-TB | Estado |
|---|---|---|---|---|---|---|
| 2026-10-06 | BR-01 | Logo real de Sunkuu en los 4 widgets (HTML/CSS; imagen pública "LOGO SUNKUU BLANCO.png" de la galería). Aprobado por Romel. | widget_type ×4 | — (previo al Version Control; incluido en `d58d79a`) | `5620098` (activo del logo) | Aplicado |
| 2026-10-06 | BR-02 | Contraste del texto "360" junto al logo: `rgba(255,255,255,.8)`. | widget_type ×4 | — (previo al Version Control; incluido en `d58d79a`) | — | Aplicado |
| 2026-10-06 | VC-01 | Version Control de ThingsBoard configurado: repo `sunkuu-tb-config`, baseline "baseline 2026-10-06 post-logo", sin credenciales de dispositivos. El bundle "Sunkuu" ya contenía el Centro de Exportación; se le agregaron los otros 3 widgets (Portal de Flota, Template 3EM y Template Piscina) para versionarlos: 4 en total. El primer repo se borró y se recreó porque exportó credenciales de dispositivos (origen de la regla de desmarcar "credenciales"). Ejecutado por GONEX (Erick) con la cuenta de Romel. | Plataforma, widgets_bundle | `d58d79a` | — | Aplicado |
| 2026-10-06 | ERR-01 | Errata "Actualizado hace hace" en Template 3EM (solo HTML). Ejecutado por GONEX (Erick) con la cuenta de Romel. | widget_type 3EM | `7bb4384` | — | Aplicado |
| 2026-10-06 | QA-01 | Revisión técnica QA completa (F01–F52): `docs/qa/2026-10-revision-tecnica.md` y scripts de validación en `qa/scripts/`. | Docs | `7bb4384` (commit analizado) | `0efe2fb` | Entregado |
| 2026-10-09 | F53 | Etiquetas y textos invisibles en las páginas de crear/solicitar/restablecer contraseña (reportado por Romel). Causa: "Primer plano oscuro" desactivado y CSS acotado solo a `.tb-login-content`. Solución: Primer plano oscuro activado, paleta de acento `#00EBC8`, CSS avanzado ampliado a `.tb-password-card`. | Marca blanca (login) | — (el Version Control no exporta la marca blanca; ver `config/white-labeling/`) | `a64a7a9`, `7f2a9dd` | Corregido y validado |
| 2026-10-09 | ADM-01 | Alta de un usuario administrador del tenant propio de GONEX, para que las versiones identifiquen al autor real. | Usuarios del tenant | — | — | Aplicado |
| 2026-10-09 | VC-02 | Auto-commit activado en ThingsBoard + versión manual "chore: estado tras alta de customer y usuarios por Romel". Primera versión con el usuario GONEX. | Plataforma | `0b0561a` | — | Aplicado |
| 2026-10-09/10 | FEAT-01 | Curva de demanda del Template 3EM (pedido por Romel): vistas 4h · 8h · Hoy · Ayer (se retira 24h) con medianoche de Lima explícita, refresco cada 5 min y "Total ayer" superpuesto en Hoy; legibilidad (resolución 5/10/15 min, suavizado monotónico, huecos como tramos tenues); selector Total · Fases · Todo (por defecto Total, recordado por navegador). Antes, la copia DEV se sincronizó con producción y su guardado de atributos quedó bloqueado (bloque DEV-ONLY, mitiga F16 en DEV). | widget_type 3EM y 3EM DEV, dashboard TG PRUEBA | DEV: `d56c6c4` (sync + bloqueo), `adaa5d1`/`2a7732d` (dashboard TG PRUEBA → TG GOCTA), `077a048`, `12af18f`, `09fe822`. Producción: `fd69cad` | — | Aplicado |

Nota: el commit `ed00205` de sunkuu-TB ("chore: instantánea de widgets previa al logo (2026-10-06)") contiene los `widgets/*.json` de la raíz **antes** de BR-01/BR-02; no refleja producción.

## Mejoras opcionales

- FEAT-01: Fase B y Fase C usan tonos azules parecidos; el ámbar no sirve porque ya es el color de advertencia del widget. Ajustar solo si Romel lo pide.
