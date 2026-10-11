# CHANGELOG — Sunkuu 360

Registro de cambios en producción (ThingsBoard PE 4.3, 360.sunkuu.com) y su trazabilidad entre repos.
Fuente de verdad de la configuración: `../sunkuu-tb-config` (Version Control de ThingsBoard).
Fechas en hora de Lima (UTC−5).

- **Tipo:** `Correctivo` (error de GONEX o hallazgo de QA; incluido en la mensualidad), `Cortesía` (mejora pequeña sin costo, valorizada en horas) o `Evolutivo` (se cotiza).
- **Horas:** de GONEX. Con sufijo `e` son estimadas (a confirmar por Erick); sin sufijo, reales.

| Fecha | ID | Tipo | Horas | Cambio | Componentes | Commit sunkuu-tb-config | Commit sunkuu-TB | Estado |
|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | BR-01 | Cortesía | 2e | Logo real de Sunkuu en los 4 widgets (HTML/CSS; imagen pública "LOGO SUNKUU BLANCO.png" de la galería). Aprobado por Romel. | widget_type ×4 | — (previo al Version Control; incluido en `d58d79a`) | `5620098` (activo del logo) | Aplicado |
| 2026-10-06 | BR-02 | Correctivo | 0,25e | Contraste del texto "360" junto al logo: `rgba(255,255,255,.8)`. | widget_type ×4 | — (previo al Version Control; incluido en `d58d79a`) | — | Aplicado |
| 2026-10-06 | VC-01 | Cortesía | 3e | Version Control de ThingsBoard configurado: repo `sunkuu-tb-config`, baseline "baseline 2026-10-06 post-logo", sin credenciales de dispositivos. El bundle "Sunkuu" ya contenía el Centro de Exportación; se le agregaron los otros 3 widgets (Portal de Flota, Template 3EM y Template Piscina) para versionarlos: 4 en total. El primer repo se borró y se recreó porque exportó credenciales de dispositivos (origen de la regla de desmarcar "credenciales"). Ejecutado por GONEX (Erick) con la cuenta de Romel. | Plataforma, widgets_bundle | `d58d79a` | — | Aplicado |
| 2026-10-06 | ERR-01 | Correctivo | 0,25e | Errata "Actualizado hace hace" en Template 3EM (solo HTML). Ejecutado por GONEX (Erick) con la cuenta de Romel. | widget_type 3EM | `7bb4384` | — | Aplicado |
| 2026-10-06 | QA-01 | Cortesía | 16e | Revisión técnica QA completa (F01–F52): `docs/qa/2026-10-revision-tecnica.md` y scripts de validación en `qa/scripts/`. | Docs | `7bb4384` (commit analizado) | `0efe2fb` | Entregado |
| 2026-10-09 | F53 | Correctivo | 1,5e | Etiquetas y textos invisibles en las páginas de crear/solicitar/restablecer contraseña (reportado por Romel). Causa: "Primer plano oscuro" desactivado y CSS acotado solo a `.tb-login-content`. Solución: Primer plano oscuro activado, paleta de acento `#00EBC8`, CSS avanzado ampliado a `.tb-password-card`. | Marca blanca (login) | — (el Version Control no exporta la marca blanca; ver `config/white-labeling/`) | `a64a7a9`, `7f2a9dd` | Corregido y validado |
| 2026-10-09 | ADM-01 | Correctivo | 0,25e | Alta de un usuario administrador del tenant propio de GONEX, para que las versiones identifiquen al autor real. | Usuarios del tenant | — | — | Aplicado |
| 2026-10-09 | VC-02 | Cortesía | 0,5e | Auto-commit activado en ThingsBoard + versión manual "chore: estado tras alta de customer y usuarios por Romel". Primera versión con el usuario GONEX. | Plataforma | `0b0561a` | — | Aplicado |
| 2026-10-09/10 | FEAT-01 | Cortesía (Evolutivo sin cotizar) | 10e | Curva de demanda del Template 3EM (pedido por Romel): vistas 4h · 8h · Hoy · Ayer (se retira 24h) con medianoche de Lima explícita, refresco cada 5 min y "Total ayer" superpuesto en Hoy; legibilidad (resolución 5/10/15 min, suavizado monotónico, huecos como tramos tenues); selector Total · Fases · Todo (por defecto Total, recordado por navegador). Antes, la copia DEV se sincronizó con producción y su guardado de atributos quedó bloqueado (bloque DEV-ONLY, mitiga F16 en DEV). | widget_type 3EM y 3EM DEV, dashboard TG PRUEBA | DEV: `d56c6c4` (sync + bloqueo), `adaa5d1`/`2a7732d` (dashboard TG PRUEBA → TG GOCTA), `077a048`, `12af18f`, `09fe822`. Producción: `fd69cad` | — | Aplicado |
| 2026-10-09/11 | ALTA-01 | Cortesía | 1,5e | Alta de Pumarinri como customer propio (PUMARINRI AMAZON LODGE, `a2202a70`; antes era una instalación de Gocta) durante la capacitación con Romel: dispositivo nuevo `717ae5e0` (shellypro3em-e08cfe972040, propiedad de Pumarinri), dashboard TG PUMARINRI `8e373390` y arrays de los widgets. El dispositivo original `cf7ddac0` se eliminó por decisión del cliente y **se perdió su histórico**. Baja de las entidades de prueba (dashboards TG PRUEBA, Prueba con Romel, Hotel Prueba, Erick Prueba y Gonex; customers de prueba) y del dashboard viejo `32131e90`. | Customer, device, dashboard, grupos, widget_type ×4 | `eff4779` (customer, Romel), `60d9ad6`…`873bcd7` (auto-commits), `71f1603` (versión manual Overwrite: 43 entidades eliminadas, propietario de `717ae5e0`) | — | Aplicado |
| 2026-10-11 | R0 | Correctivo | 2,5e | Remediación posterior a ALTA-01 (solo `controllerScript`): Piscina sin la entrada huérfana "TG Pumarinri" → `32131e90` en el NAV (A3-1); Exportación con `8e373390` → instalación de Pumarinri en `DASH_TO_INST` y sin `32131e90` ni `fe900bc0` (A3-2); Flota con letra "P" y color propio para Pumarinri (A3-3) y conteo de clientes calculado desde el array (A3-5). | widget_type Piscina, Exportación, Flota | — (pendiente de aplicar) | — | Preparado (`widgets/work/R0/`) |

Nota: el commit `ed00205` de sunkuu-TB ("chore: instantánea de widgets previa al logo (2026-10-06)") contiene los `widgets/*.json` de la raíz **antes** de BR-01/BR-02; no refleja producción.

## Pendientes

| Pendiente | Responsable | Fecha límite |
|---|---|---|
| Informe mensual de Pumarinri: la plantilla `defa3090` ("Informe Mensual - TG PUMARINRI") apunta al dashboard eliminado `32131e90`; el planificador `8bee5690` usa esa plantilla. Reapuntar a `8e373390` desde la UI. | Erick | 2026-11-01 |
| Aplicar R0 en producción y registrar los hashes de `sunkuu-tb-config`. | Erick | — |

## Valor entregado

Horas de GONEX por mes y tipo, según la columna "Horas" (solo cambios aplicados). Base para renegociar la mensualidad.

| Mes | Correctivo | Cortesía | Evolutivo cotizado | Total |
|---|---|---|---|---|
| 2026-10 | 2,25e | 33e | 0 | 35,25e |

Detalle 2026-10. Correctivo: BR-02, ERR-01, F53, ADM-01. Cortesía: BR-01, VC-01, QA-01, VC-02, FEAT-01 (Evolutivo entregado sin cotizar, 10e) y ALTA-01. R0 (2,5e) se suma al aplicarse.

## Mejoras opcionales

- FEAT-01: Fase B y Fase C usan tonos azules parecidos; el ámbar no sirve porque ya es el color de advertencia del widget. Ajustar solo si Romel lo pide.
