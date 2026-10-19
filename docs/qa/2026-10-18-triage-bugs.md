# Triage de hallazgos pendientes — 2026-10-18

Solo lectura: `../sunkuu-tb-config` HEAD `ed52362` (auto-commit de R0 Piscina), `docs/qa/2026-10-revision-tecnica.md` (F01–F53, analizada sobre `7bb4384`), `CHANGELOG.md` y `docs/arquitectura/2026-10-propuesta-alta-y-proem.md`. Sin red, sin escribir fuera de `docs/qa/`, sin apply/rollback.

**Cómo se verificó.** Los `controllerScript` y `templateHtml` de los 4 widgets se extrajeron de HEAD y se compararon con `7bb4384`: 3EM cambió solo por FEAT-01 (curva de demanda, L663–818) y por el NAV; Piscina solo por R0; Flota y Exportación solo por ALTA-01 (arrays). **Todo lo que no tocaron esos cambios sigue idéntico al análisis original**; las líneas citadas abajo son de HEAD (las de 3EM posteriores a L700 se desplazaron ~+120 respecto al informe original).
**Etiquetas:** `ACTIVO` (reproduce en HEAD), `CORREGIDO` (por ALTA-01/R0/FEAT-01/etc.), `NO VERIFICABLE` (depende de la instancia; en la sección 5 está qué mirar).
**Horas:** estimadas (`e`), de GONEX, a confirmar por Erick.
**"B":** el único diseño de B disponible en el repo es el Nivel 1 ("registro de instalaciones" como Activos) de la propuesta de arquitectura. Si B es otra cosa, la columna "se resuelve con B" debe revisarse.

## 0. Resumen

- **9 impostergables** (I-01 … I-09), 3 de ellos condicionales a una verificación o a una decisión de calendario (I-06, I-07, I-09; marcados). Estimación total ≈ **41 h e** (35–50) sin el informe mensual real, ≈ 53 h e con él.
- Los 3 más urgentes: **I-01** informes mensuales del 2026-11-01 08:00 (4 planificadores sin destinatarios; el de Pumarinri apunta a un dashboard que ya no existe); **I-02** KPIs de energía, comparativos y proyección erróneos que ven los 3 clientes en cada dashboard 3EM; **I-04** "En línea" fijo + llamadas sin refresco de token (pantalla que se congela sin avisar).
- Una conclusión incómoda del análisis: **nadie recibe nada automáticamente**. Informes sin destinatario, 11 reglas de notificación apagadas, botón "Configurar Alarmas · email y WhatsApp" sin función. Hoy el cliente se entera de una falla solo si abre el dashboard, y ahí el encabezado dice "En línea" aunque no haya datos.
- Corregidos desde la revisión original: F07 (entidades de prueba fuera de los arrays y de la lista de customers), F16 (parcial), F53, y los defectos de ALTA-01 (A3-1, A3-7, propietario de `717ae5e0`).

## 1. Tabla resumen

Categoría: **IMP** impostergable · **OMI** omisible · **B** se resuelve con B · **OPO** omisible pero casi gratis si se aplica el widget de todas formas (decide Erick, sección 6).

| ID | Descripción corta | Estado | Cat. | Quién lo ve | h e |
|---|---|---|---|---|---|
| F01 | "Energía hoy" pierde la 1.ª hora | ACTIVO | **IMP** I-02 | Gocta, Tucán, Pumarinri; admin | (I-02) |
| F02 | "Ayer" pierde la 1.ª hora | ACTIVO | **IMP** I-02 | ídem | (I-02) |
| F03 | "vs semana anterior" usa ventana de 48 h | ACTIVO | **IMP** I-02 | ídem | (I-02) |
| F04 | Comparativos: hoy parcial vs días completos | ACTIVO | **IMP** I-02 | ídem | (I-02) |
| F05 | Proyección/costo extrapola solo el día parcial | ACTIVO | **IMP** I-02 | ídem (3EM y Piscina) | (I-02) |
| F06 | Flota: costo mes = kWh hoy × 30 × 0,65 | ACTIVO | **IMP** I-03 | admin (Romel) | 4 |
| F07 | Entidades de prueba en Flota | CORREGIDO (ALTA-01; resto "de 2 clientes" en R0) | OMI | nadie | 0 |
| F08 | Informe mensual = captura del día parcial | ACTIVO | **IMP** I-01 | clientes si se entrega | 12 (opción) |
| F09 | Planificadores sin destinatarios | ACTIVO | **IMP** I-01 | nadie lo recibe | 1,25 |
| F10 | Notificaciones apagadas; botón "email y WhatsApp" muerto | ACTIVO | **IMP** I-08 | todos los clientes (botón) | 0,5 + D6 |
| F11 | 4 juegos de umbrales de temperatura de la piscina | ACTIVO | **IMP** I-07 | Gocta | 1,5 |
| F12 | Umbrales "editables" que no cambian la alarma | ACTIVO | OMI (D3) | clientes admin | — |
| F13 | Alarma de FP por fase sin carga | NO VERIFICABLE (código ACTIVO) | **IMP** I-07 (cond.) | los 3 clientes | 1,5 |
| F14 | Emails de todos los clientes en el JS de Flota | ACTIVO | **IMP** I-06 (cond.) / B | Gocta, Tucán, Pumarinri | 0,5 |
| F15 | Fail-open en Flota y Exportación | ACTIVO | **IMP** I-06 (cond.) / B | **Apu Samay** (próximo) | 1,25 |
| F16 | Dashboards de prueba / DEV sobre producción | CORREGIDO parcial; NO VERIFICABLE | OMI | nadie (verificar) | 0 |
| F17 | Rol de cliente con READ_CREDENTIALS y RPC_CALL | ACTIVO | **IMP** I-05 | los 3 clientes | 0,75 |
| F18 | MQTT anónimo, sin TLS | ACTIVO (infra) | OMI (pospuesto) | nadie | — |
| F19 | Exportes 15 min/1 h/1 d no alineados | ACTIVO | OMI | clientes (CSV) | — |
| F20 | Pérdida silenciosa de datos en Raw | ACTIVO; magnitud NO VERIFICABLE | **IMP** I-09 (cond.) | clientes (CSV) | 3 |
| F21 | "En línea" fijo | ACTIVO | **IMP** I-04 | los 3 clientes | (I-04) |
| F22 | Datos viejos tratados como válidos | ACTIVO | **IMP** I-04 | clientes; admin | (I-04) |
| F23 | `fetch` con JWT sin refresco | ACTIVO | **IMP** I-04 | cualquiera con pantalla abierta | (I-04) |
| F24 | "Energía hoy" calculada de 3 formas | ACTIVO | **IMP** I-02/I-03 | admin compara Flota vs 3EM | (I-02) |
| F25 | FP = media de fases | ACTIVO; magnitud NO VERIFICABLE | **IMP** I-02 (cond.) | clientes | (I-02) |
| F26 | Promedio 30 d con buckets desalineados | ACTIVO | **IMP** I-02 | clientes | (I-02) |
| F27 | Sin `America/Lima` (usa el navegador) | ACTIVO | OMI aislado; se resuelve dentro de I-02 | usuarios fuera de UTC−5; **renderer de informes** | (I-02) |
| F28 | Etiquetas que no corresponden al cálculo | ACTIVO | OPO | clientes | 1 |
| F29 | Costo/energía de piscina = solo iluminación | ACTIVO | **IMP** I-02 (rótulo) | Gocta | 0,5 |
| F30 | Listeners duplicados en Piscina | ACTIVO | OMI | Gocta | — |
| F31 | Fugas / modal duplicado en Flota | ACTIVO | OMI | admin | — |
| F32 | PDF con "+Infinity%"/NaN | ACTIVO | OPO | clientes (PDF) | 0,25 |
| F33 | Botón "Informe mensual" genera resumen de hoy | ACTIVO | OPO | clientes | 0,25 |
| F34 | Glifo ✓ en jsPDF | ACTIVO | OMI | clientes (PDF) | — |
| F35 | `setFillColor` con 4 args (PDF Piscina) | ACTIVO | OMI | Gocta (PDF) | — |
| F36 | Diferencial agua–ambiente "+-2.0" | ACTIVO | OMI | Gocta | — |
| F37 | "Piscina vs ayer" instantáneo vs promedio | ACTIVO | OMI | Gocta | — |
| F38 | Textos varios ("hace 0 segundos", "2 de 2") | ACTIVO; "2 de 2" en R0 | OPO | clientes; admin | 0,5 |
| F39 | Botón "Repetir" sin handler | ACTIVO | OMI | clientes | — |
| F40 | Mapeo `temperature:101` | ACTIVO | OMI | nadie | — |
| F41 | Decoders con plantilla TBEL muerta, QoS 0 | ACTIVO | OMI | nadie | — |
| F42 | `statusList` en `/api/alarm` posiblemente ignorado | NO VERIFICABLE | **IMP** I-07 (cond.) | clientes; admin | 0,5 |
| F43 | Plus 1 (calentador) sin alarma de desconexión | ACTIVO | **IMP** I-07 | Gocta | 1 |
| F44 | Umbrales de "sin señal" incoherentes | ACTIVO | **IMP** I-04 (parte Piscina) | Gocta; admin | (I-04) |
| F45 | Panel de configuración visible en Piscina | ACTIVO | OMI (D8) | Gocta | — |
| F46 | Exportación: SUM/AVG sobre contadores | ACTIVO | OMI | clientes | — |
| F47 | CDN sin SRI; informes por `http://…:8080` | NO VERIFICABLE | OMI | nadie | — |
| F48 | Histórico 6 meses (oculto) | ACTIVO, oculto | OMI | nadie | — |
| F49 | Nombres/marca inconsistentes | ACTIVO | OMI (D9) | clientes | — |
| F50 | Reset del contador oculto por `Math.max(0,…)` | NO VERIFICABLE | OMI (se mitiga en I-02) | clientes | — |
| F51 | `status:'online'` fijo | ACTIVO | OMI | admin | — |
| F52 | "Tarifa BT5B" fija, sin cargo fijo ni IGV | ACTIVO | **IMP** I-02 (rótulo; D2) | clientes | 0,5 |
| F53 | Login: textos invisibles | CORREGIDO (CHANGELOG F53) | — | — | 0 |
| P-1 | Informe de Pumarinri → dashboard eliminado (`defa3090`/`8bee5690`) | ACTIVO | **IMP** I-01 | Pumarinri | 0,25 |
| P-2 | Aplicar R0 (Flota, Exportación) | Pendiente de aplicar (validado) | fuera de triage | — | — |
| P-3 | Propietario de `717ae5e0` (G1) | CORREGIDO (`hierarchy/a2202a70…/device/717ae5e0…`) | — | — | 0 |
| P-4 | Piscina muestra "TG Pumarinri" roto (A3-1, G2) | CORREGIDO (`ed52362`) | — | — | 0 |
| P-5 | Dashboard viejo `32131e90` en grupos (A3-7) | CORREGIDO en repo (no está en `dashboard/` ni en `groups/`); NO VERIFICABLE en instancia | — | — | 0 |
| P-6 | Histórico de Pumarinri perdido (G4) | NO RECUPERABLE por código | decisión | Pumarinri | — |
| P-7 | Fail-open con usuarios de prueba (A3-6, G5) | CORREGIDO (ya no existen customers de prueba en `customer/`) | — | — | 0 |
| P-8 | Alta de Apu Samay incompleta (A3-12) | ACTIVO, esperable | ver I-06 | — | — |
| P-9 | PoC de `entitiesQuery` para usuarios de customer (G8) | PENDIENTE (de B) | B | — | 1 |
| P-10 | Integración 3EM con relación a `cf7ddac0` (A3-11) | NO VERIFICABLE | OMI | nadie | — |
| P-11 | `notification_target` "Gocta" cita TG PUMARINRI; no existe target de Pumarinri | ACTIVO | **IMP** (en I-01) | Gocta, Pumarinri | (I-01) |
| P-12 | NAV mezcla customers para el admin en 3EM (R0b diferido) | ACTIVO | B | admin | — |
| P-13 | Trazabilidad: A3-9, G6, G7 | proceso | OMI | — | — |
| P-14 | Pro EM-50 / template para Apu Samay | Evolutivo (27 h) | fuera de triage | — | — |

## 2. IMPOSTERGABLES (por urgencia)

### I-01 · Informes mensuales (2026-11-01 08:00 Lima) — F08, F09, P-1, P-11
> **CORRECCIÓN (ver `2026-10-18-informes-inspeccion.md`):** el afirmado "targets: null / nadie recibe nada" es falso. El export de TB no incluye destinatarios ni plantilla de notificación de los planificadores; en la UI sí existen y los informes llegan. F09 (y el tramo 2 de abajo) quedan sin efecto. Sigue vigente: el planificador de Pumarinri apunta a un dashboard eliminado y envía al target de Gocta.

**Estado: ACTIVO.**

**Qué hay en el repo (`scheduler_event/`, `report_template/`):**

| Customer | Planificador | `enabled` | Plantilla → dashboard | ¿El dashboard existe? | Destinatarios | Próxima ejecución |
|---|---|---|---|---|---|---|
| Gocta | `c72d8880` "Informe Mensual TG GOCTA" | sí | `900138f0` → `e844d080` | sí | **ninguno** (`targets: null`, `notificationTemplateId: null`) | 2026-11-01 08:00 Lima |
| Gocta | `a6773ef0` "…Piscina Temperada" | sí | `94757860` → `cc2cad90` | sí | ninguno | ídem |
| Tucán | `c967cba0` "…Medidor Tablero Principal" | sí | `258ddba0` → `0469dc30` | sí | ninguno | ídem |
| Pumarinri | `8bee5690` "…TG PUMARINRI" | sí | `defa3090` → **`32131e90`** | **no** (no está en `dashboard/`; eliminado en `71f1603`) | ninguno | ídem |

Todos: `MONTHLY` desde 2026-06-01 08:00, `endsOn` 2100, zona `America/Lima`, generados como el usuario `12fff710…` (creado el 2026-10-09 18:56 Lima; probablemente el administrador GONEX de ADM-01, [Supuesto]), formato PDF de una captura PNG del dashboard con `timewindow` de 30 días y `useDashboardTimewindow: false`.

**Qué saldría el 2026-11-01 08:00:**
- **Gocta (TG GOCTA, Piscina) y Tucán (Medidor):** se genera un PDF por dashboard, que queda **solo en la lista de informes del tenant**; nadie lo recibe. Su contenido no sería el mes de octubre: los widgets ignoran el `timewindow` y calculan "hoy" desde la medianoche (`todayStart()`, 3EM L80; Piscina L73) en la zona del navegador del renderer. Saldrían ~8 h del 1 de noviembre (si el renderer corre en Lima), la comparación contra el 31 de octubre incompleto, "vs semana anterior" con 48 h (F03) y una proyección de noviembre basada en 8 h (F05). Si el renderer corre en UTC, el "día" empezaría a las 19:00 del 31 de octubre.
- **Pumarinri:** la captura apunta a un dashboard inexistente. Resultado esperado: informe vacío o fallo de generación **[NO VERIFICABLE desde el repo]**.
- Desconocido: si el renderer tiene `localStorage.jwt_token` (los widgets usan `fetch` con ese token, F23). Si no lo tiene, los KPI saldrían en "—" y los informes de junio–octubre ya habrían salido vacíos.

**Quién lo sufre:** hoy nadie recibe nada. Se vuelve problema el día que Romel reenvíe un informe a un cliente, o cuando se asignen destinatarios sin corregir el contenido.
**Escenario:** el 2026-11-01 se generan 4 PDF con datos del día parcial (y 1 fallido). Si en ese momento ya se había conectado el envío (F09) el cliente recibe un "informe mensual" de 8 horas con porcentajes del orden de −90 %.

**Cambio mínimo (sin escribirlo), en tramos independientes:**
1. **P-1** — reapuntar `defa3090` de `32131e90` a `8e373390` (UI, plantilla). 0,25 h, riesgo bajo. Ya está asignado a Erick en CHANGELOG (fecha 2026-11-01).
2. **F09 / P-11** — asignar en los 4 planificadores el target del cliente y la plantilla `ff7b4330` ("Report generated", con EMAIL). Crear el target "PUMARINRI AMAZON LODGE" (hoy no existe) y corregir la descripción del target "Gocta" (cita TG PUMARINRI). 1 h, riesgo bajo. **Conviene hacerlo después de resolver el contenido (tramo 3): activar destinatarios con el contenido actual enviaría informes erróneos a clientes.**
3. **F08** — el informe debe leer un periodo (mes anterior): vista mensual del dashboard que use `ctx.timeWindow`, o informe con widgets nativos agregados por mes en `America/Lima`. 10–14 h, riesgo medio, requiere decisión **D5**.
4. Interim sin código si no hay tiempo antes del 1 de noviembre: pausar (`enabled: false`) los 4 planificadores. 0,25 h.

**Dependencias:** tramo 2 después de 3; tramo 3 y la corrección de I-02 comparten la definición de "mes/día" (D1); F27 afecta al renderer.

### I-02 · Energía, comparativos y proyección — F01–F05, F24, F25, F26, F29, F32*, F52, y F27 como parte del cambio
**Estado: ACTIVO** (3EM `controllerScript` L80, L272–284, L290–297, L304, L402/461/556, L540/578, L596–600; Piscina L73, L468–479; el código no cambió desde el análisis original).
**Widget:** `sunkuu_template_3em` `373ddd50` (dashboards TG GOCTA, TG PUMARINRI, Medidor) y `sunkuu_template_piscina` `5f7b51c0`.
**Quién lo ve:** Gocta, Tucán y Pumarinri en cada dashboard 3EM; Gocta en Piscina; PDF del botón "Generar Reporte".
**Escenario:** el cliente mira "Energía acumulada hoy" y "vs ayer" a cualquier hora del día. Valores: la energía del día pierde entre 30 y 120 min de consumo (F01), "ayer" también (F02), "vs semana" compara con ≈2 días (F03), todo contra días completos (F04) y la proyección del mes se calcula con el día parcial (F05). A cualquier hora de la madrugada el chip dice "↓ −9x %". Ocurre hoy y cada día; con cada instalación nueva aparece en el dashboard nuevo (ya ocurre en Pumarinri).
**Medianoche de Lima por widget (pedido):**

| Widget | Cálculo de día | Zona |
|---|---|---|
| 3EM (KPI, comparativos, proyección, PDF) | `todayStart()` L80, `setHours(0,0,0,0)` | **navegador** |
| 3EM curva de demanda (FEAT-01) | `limaMidnight()` L669–671, UTC−5 fijo | **Lima explícita** (correcto) |
| Piscina | `todayStart()` L73 | navegador |
| Flota | `todayStart()` L90 | navegador |
| Exportación | `toInputFormat` L814 con `getTimezoneOffset()` | navegador |
| Informes (`scheduler_event`/`report_template`) | `timezone: America/Lima` | Lima (pero los widgets que renderizan usan la del navegador del renderer) |

El cambio de F01–F04/F26 necesita límites de día en Lima de todos modos, así que F27 se resuelve dentro de I-02 reutilizando `limaMidnight()` (no cuesta aparte).
**Cambio mínimo propuesto:** una función compartida `contadorEn(ts)` (último valor crudo con `ts ≤ instante`, `limit=1`, orden DESC) y, sobre ella: hoy = contador(ahora) − contador(00:00 Lima), ayer = contador(00:00 hoy) − contador(00:00 ayer), semana = mismo día de la semana pasada hasta la misma hora, promedio 30 d con días completos, proyección = mes a la fecha + promedio diario de días cerrados × días restantes (método B de `qa/scripts/proyeccion_mensual.py`), FP = P_total/S_total, deltas positivos tramo a tramo (cubre F50). Rótulos: Piscina "Costo iluminación" (F29) y "costo de energía, sin cargos ni IGV" (F52). F32 (`p1` del PDF, L1162, sin `>0`) y el rótulo del botón (F33) son oportunistas.
**Esfuerzo:** 3EM 11 h, Piscina 2,5 h, + 2 h de validación con los scripts = ~15 h. **Riesgo:** bajo-medio (los números mostrados suben y dejan de coincidir con capturas antiguas; avisar a Romel).
**Dependencias / bloqueos:** **D1** (definición de día y comparativos), **D2** (qué es costo, tarifa 0,65, tarifa de Pumarinri), **D7** (FP). I-03 usa la misma función. Valida con `qa/scripts/` (ver sección 5).
**Nota F25:** la magnitud no se puede cuantificar sin datos reales (puede ser mayor). Por la regla de duda queda IMP.

### I-03 · Portal de Flota: costo, energía y potencia — F06, F24, F22 (Flota)
**Estado: ACTIVO** (`sunkuu_portal_de_flota`: L495 costo `totalKWH*30*0.65`; L730–734 y L753–754 energía por buckets alineados; L696 último kW sin comprobar antigüedad).
**Quién lo ve:** administradores (Romel) en la Capa 0. Los clientes ven la Capa 1 (kWh de su cuenta, mismo método).
**Escenario:** Romel mira "Costo estimado — mes" (a las 08:00 es ≈ ⅓ del valor real; a las 22:00 es ≈ el doble) y "Potencia total" que suma el último kW aunque tenga días (el "Potencia total: —" que ya se vio, H7, tiene como causa plausible F23).
**Cambio mínimo:** costo = Σ proyección por instalación con la misma función que I-02 y su tarifa; excluir lo que no sea producción; kW de más de N minutos no se suma. **Esfuerzo:** 4 h. **Riesgo:** bajo. **Dependencias:** I-02 (función), D1/D2.

### I-04 · Estado "En línea" y frescura de datos — F21, F22, F23, F44, F38 (L209)
**Estado: ACTIVO.** 3EM: el encabezado es HTML estático "En línea · <hora>" (`templateHtml` L20–22); el JS busca `.hdr-sdot`/`.hdr-ts` (L196–197), que no existen, así que nunca cambia (L195–206). Piscina: `.hdr-sdot` existe pero no `.hdr-ts` (L150–160), solo cambia el color. Si no hay `lastRealTs`, 3EM muestra "hace 0 segundos" (L209). `api()` usa `fetch` con `localStorage.jwt_token` sin refresco en 3EM (L92–98), Piscina y Flota (L114–119); falla con `console.warn` (F23). Piscina trata "sin señal" a las 12 h/30 h (L137–138) y Flota 120/360 min para 3EM, 720/1800 min para Piscina (L132–133) y 60 min en otro punto (L432).
**Quién lo ve:** Gocta, Tucán, Pumarinri (cada dashboard); Flota para admin.
**Escenario:** un medidor deja de enviar. El cliente abre el dashboard y lee "En línea" con datos de ayer; la línea "Actualizado hace X" y el color del texto son la única pista. Con la pantalla abierta (TV de recepción, Romel con Flota abierta) el JWT vence, las llamadas fallan en silencio y los números quedan congelados mientras el encabezado sigue diciendo "En línea". Se agrava con la piscina: el calentador (Plus 1) puede estar 12 h sin datos y figurar "normal".
**Qué pasa al vencer la sesión [NO VERIFICABLE]:** el widget `fetch`-ea con el token viejo; no hay pantalla en blanco ni error visible. Los KPI se quedan en el último valor o en "—". TB renueva el token solo cuando la interfaz de TB hace una llamada propia; los widgets que usan `ctx.http` (Exportación) pasan por esa renovación, `fetch` no. Duración del JWT: no se exporta (valor por defecto de TB, a verificar).
**Cambio mínimo:** (a) `api()` sobre `ctx.http.get(...).subscribe` en los 3 widgets (misma firma de callbacks); (b) alinear selectores del encabezado con el HTML y usar los umbrales ya existentes (3EM 2 h/6 h); (c) Piscina: medir el estado sobre el Plus 1 (siempre encendido) con umbral corto y dejar 12/30 h solo para el H&T. **Esfuerzo:** 3EM 1,5 h, Piscina 1,5 h, Flota 2 h = 5 h. **Riesgo:** bajo (`ctx.http` ya se usa en Exportación). **Dependencias:** I-07 (F43); no depende de decisiones, salvo el umbral (D3).

### I-05 · Rol de cliente: credenciales de dispositivo y RPC — F17
**Estado: ACTIVO** (`role/79f4a160…` Customer User: `ALL: [READ, RPC_CALL, READ_CREDENTIALS, READ_ATTRIBUTES, READ_TELEMETRY]`; `role/35af70e0…` grupo, mismos permisos; asignados en Gocta, Pumarinri y Tucán (Tucán duplicado); `role/79f71260…` Customer Administrator `ALL: [ALL]`).
**Qué puede hacer un usuario cliente:** leer el token de acceso de sus dispositivos y con él publicar telemetría falsa por la API de dispositivo (si el transporte nativo es alcanzable) o suplantar al Shelly; enviar RPC (hoy sin efecto: no hay downlink). Un Customer Administrator puede además modificar atributos (tarifa, umbrales) y eliminar sus dispositivos (borra la telemetría, housekeeper PE ≥ 3.7).
**Cuándo:** hoy; se amplía con cada usuario nuevo (Apu Samay hereda los roles).
**Cambio mínimo:** quitar `RPC_CALL` y `READ_CREDENTIALS` de los dos roles de cliente (UI → Roles). No afecta a ningún widget (ninguno usa credenciales ni RPC). **Esfuerzo:** 0,75 h con prueba como usuario cliente (`/api/device/{id}/credentials` debe dar 403). **Riesgo:** bajo-medio (los roles se aplican a todos los clientes a la vez; probar con un usuario por customer). **Dependencias:** **D8** (qué hace el Customer Administrator). Sin apply de widget.

### I-06 · Alta de Apu Samay: arrays y fail-open — F15, F14, P-8 (condicional a B)
**Estado: ACTIVO** (Flota `CUSTOMERS` L34–64 y `CUST_UUID_MAP`; si `custObj` es nulo `showLayer1(null)` usa `INSTALLATIONS` completa, L523 y L539–541; Exportación `CUSTOMER_MAP` L216–220, `clientLabel` L225–227, `VISIBLE_INSTALLATIONS = … : INSTALLATIONS.slice()` L229–231; emails en Flota L42, L52, L62).
**Qué se rompe al dar de alta Apu Samay con el flujo actual (7 pasos de A.4; el "manual N4" no está en el repo):**

| Si… | Pasa |
|---|---|
| Se hace el paso 6 completo (Flota `CUSTOMERS`/`INSTALLATIONS`, Exportación `CUSTOMER_MAP`/`INSTALLATIONS`/`DASH_TO_INST`, NAV) | Funciona. Un error de sintaxis en cualquier array tumba el widget **para todos los clientes** (G12; `node --check` antes de guardar). |
| Se comparte Flota/Exportación con Apu Samay **sin** el paso 6 | **Los usuarios de Apu Samay ven la lista completa de instalaciones de Gocta, Tucán y Pumarinri** (nombres, dashboards, tipos). La telemetría ajena da 403, pero la lista, los nombres y los enlaces se muestran. En Flota, además, los emails de los otros 3 clientes ya van dentro del JS (F14). |
| Apu Samay se queda sin grupo de dashboards (hoy: sin grupo, A3-12) | No ve nada. Esperable. |
| Llegan los Pro EM-50 | Flota solo conoce tipos `3em` y `piscina` (L140, L145, L683): el EM-50 no tendría lecturas ni salud. El perfil Pro EM50 no tiene alarma de desconexión. Es el Evolutivo del template EM-50 (P-14), no un defecto. |

**Escenario/cuándo:** el primer usuario de Apu Samay con Flota o Exportación compartidos. Hoy no hay dispositivos ni grupo, así que el riesgo aún no se materializa.
**Se resuelve con B** (N1: instalaciones como Activos del customer; "sin PII ni UUIDs en el JS, *fail-closed* natural", propuesta §4 y G5) **solo si** B llega antes que el primer usuario de Apu Samay **y** pasa la prueba de concepto de `entitiesQuery` para usuarios de customer (P-9/G8, hoy un supuesto). Si no, queda como IMP.
**Cambio mínimo si B no llega a tiempo:** Flota `showLayer1(null)` y Exportación `clientLabel == null` → lista vacía + mensaje; eliminar los 3 campos `email:` de `CUSTOMERS` (el widget ya los trae de `/api/customer/{uuid}` para el admin, L253–262; el cliente perdería solo su propio email en la cabecera). **Esfuerzo:** Flota 1 h, Exportación 0,75 h. **Riesgo:** bajo. **Dependencias:** se aplica junto con R0 (mismo `controllerScript`); decisión de calendario de B (sección 6).

### I-07 · Alarmas: umbrales y cobertura — F11, F13, F42, F43 (condicional)
**Estado:** F11 ACTIVO (CF *Temperatura Agua* 20–35 °C 5 min en `device_profile/fa155fd0…`; atributos de `96594b70…` 30/40/33; el dashboard Piscina usa los atributos); F13 código ACTIVO (CF *Factor de Potencia Bajo*: condición `OR` de fp_a/fp_b/fp_c < 0,85, 5 min, `device_profile/89ae3280…`), frecuencia real NO VERIFICABLE; F42 NO VERIFICABLE (`statusList=` en 3EM L321, Flota L742, Piscina L232); F43 ACTIVO (solo el perfil 3EM tiene *Dispositivo Desconectado*; Plus 1 y 1PM no).
**Quién lo ve:** Gocta (piscina), los 3 clientes (FP), admin (Flota cuenta alarmas como "requieren acción").
**Escenario:** a 36 °C la alarma se crea y la tarjeta dice "✓ Sobre objetivo"; a las 03:00 un 3EM con una fase sin carga marca FP 0 y crea "Factor de Potencia Bajo" que el cliente ve como alarma activa y Flota cuenta como acción; si el calentador pierde conexión no hay alarma. Se repite en cada 3EM nuevo (la CF vive en el perfil). Si `statusList` se ignora, la lista y el contador de Flota incluyen alarmas ya resueltas.
**Cambio mínimo:** CF Temperatura Agua con `dynamicValueArgument` hacia los atributos (F11); condicionar F13 a corriente/potencia de la fase o usar FP total; crear *Dispositivo Desconectado* para el Plus 1 y no para el H&T (F43); si F42 se confirma, `searchStatus=ACTIVE` o v2. **Esfuerzo:** 4,5 h. **Riesgo:** medio (cambia cuándo se disparan las alarmas; probar en un dispositivo de prueba). **Dependencias:** **D3** (valores), I-08.

### I-08 · Botón "Configurar Alarmas — Umbrales, email y WhatsApp" y notificaciones apagadas — F10
**Estado: ACTIVO.** El botón `#btn-alarms` no tiene handler (3EM `templateHtml` L367, Piscina L335; sin `btn-alarms` en ningún JS). Las 11 `notification_rule` tienen `enabled: false`, incluida *Alarmas Sunkuu — Email* (`31dc7d70`), cuya plantilla `ff6ec010` es solo WEB. Existen los targets "Gocta" y "Tucán" pero ninguna regla ni planificador los usa.
**Quién lo ve:** todos los clientes (el botón está en cada dashboard).
**Escenario:** un cliente cree que recibirá avisos por correo o WhatsApp de una alarma; no llega nada (ahora ni cuando se arregle F13: activar las reglas sin F13 genera ruido).
**Cambio mínimo sin decisión:** cambiar el texto del botón a lo que existe (p. ej. "Ver alarmas") en 3EM y Piscina (HTML). Habilitar la regla es decisión **D6** (qué alarmas, a quién, por qué canal) y debe ir **después** de I-07. **Esfuerzo:** 0,5 h el texto; habilitar ≈ 2 h adicionales tras D6. **Riesgo:** bajo.

### I-09 · Exportación: pérdida silenciosa de datos en Raw — F20 (condicional)
**Estado: ACTIVO en el código** (`fetchRaw` L666–712: pagina con el total de puntos y avanza al `maxTs` global, L697; multidispositivo Raw L529–540 sin paginar con `limit=50000`); la magnitud depende de la frecuencia de muestreo, **NO VERIFICABLE desde el repo**. El rango por defecto es de 30 días (L355).
**Quién lo ve:** cualquier cliente que descargue Raw de varias variables o de la Piscina.
**Escenario:** una variable de alta frecuencia supera 50 000 puntos en el rango; el CSV termina sin avisar antes del final para esa columna, mientras las demás llegan hasta el final. A 1 muestra cada 52 s o menos, 30 días ya superan el límite.
**Cambio mínimo:** paginar por variable y avisar si alguna llega al límite. **Esfuerzo:** 3 h. **Riesgo:** bajo. **Verificar primero:** exportar 30 días Raw de una instalación y comprobar la última fila de cada columna (sección 5). Si ninguna columna se corta, baja a OMI.

## 3. OMISIBLES (una línea)

- F07 corregido por ALTA-01 (entidades de prueba fuera de los arrays y de `customer/`; "2 de 2 clientes" lo corrige R0). Resto: B.
- F12 umbrales "editables" que no cambian la alarma — solo aplica a Customer Administrator; bloqueado por D3, se aborda con I-07/I-08 si Erick decide.
- F16 parcialmente corregido: sin Hotel Prueba ni `32131e90` en grupos; el widget DEV lee `c636fa00` con guardado bloqueado (FEAT-01). Falta confirmar que el dashboard TG PRUEBA existe en la instancia (no está en `dashboard/` de HEAD, pero CLAUDE.md lo describe).
- F18 MQTT anónimo sin TLS: infra de Romel, pospuesto. Riesgo en una línea: si Mosquitto es alcanzable desde fuera, cualquiera puede inyectar telemetría o crear dispositivos que consumen el cupo de 100 dispositivos de la licencia.
- F19 exportes sin alinear a cuarto de hora/día — datos correctos, timestamps de punto medio; mejora con el selector de fecha.
- F27 aislado (usuarios fuera de UTC−5) — se resuelve dentro de I-02.
- F28, F32, F33, F38 (OPO): rótulos y textos del 3EM/Piscina; se aplican gratis dentro de I-02/I-04 si Erick los incluye.
- F30, F31, F34, F35, F36, F37, F39, F40, F41, F46, F47, F48, F49, F51: cosmético o deuda técnica sin efecto visible hoy (F47: informes por `http://thingsboard.gonex.pe:8080`, a revisar con Romel; F49: D9, los PDF firman "GONEX S.A.C.").
- F45 panel de configuración visible en Piscina — el Customer User no puede escribir (403); queda D8.
- F50 reset del contador: se mitiga en I-02 (deltas positivos); sin evidencia de reset real.
- P-10 relación de la integración 3EM con `cf7ddac0` (export desactualizado). P-13 trazabilidad.

**Se resuelven con B (diseño N1 de la propuesta de arquitectura):**
- F07 (resto), F14, F15 (condicional, ver I-06), P-12 (NAV mezcla customers para el admin: B reemplaza los NAV, R0b diferido), y los defectos de arrays hardcodeados (A3-2, A3-3, A3-4, A3-5, A3-12, G12). Confirmación: la propuesta §4 y el resumen ejecutivo atribuyen a N1 "cero UUIDs en el JS", "sin PII" y "*fail-closed* natural". Dos matices: depende de la prueba de concepto P-9 (supuesto, no probado) y de que N1 no se haga después del primer usuario de Apu Samay.

## 4. Orden de trabajo propuesto

Un solo apply por widget. Todos los widgets de la lista incluyen el R0 pendiente de ese widget, si Erick decide unificarlo (D-1).

| Paso | Qué | Entidad | Incluye | h e |
|---|---|---|---|---|
| 0 | Verificaciones manuales (sección 5) | instancia | decide los condicionales | 1 |
| 1 | Informes — tramos 1 y 4 (reapuntar `defa3090`; pausar o no según D-3) | `report_template`, `scheduler_event` | I-01 | 0,5 |
| 2 | Roles de cliente | `role` | I-05 | 0,75 |
| 3 | **Exportación** (un apply) | `centro_de_exportaci_n_sunkuu` | R0, I-06, I-09 | 3,75 |
| 4 | **Flota** (un apply) | `sunkuu_portal_de_flota` | R0, I-06, I-03, I-04, parte F42 | 7,25 |
| 5 | **3EM** (un apply) | `sunkuu_template_3em` | I-02, I-04, I-08 (texto), F42, OPO | 13,25 |
| 6 | **Piscina** (un apply) | `sunkuu_template_piscina` | I-02, I-04, I-08 (texto) | 4,25 |
| 7 | Perfiles de dispositivo | `device_profile` Plus 1, 3EM | I-07 | 4,5 |
| 8 | Informes — contenido y destinatarios | `scheduler_event`, 3EM/Piscina vista mensual | I-01 tramos 2–3 (D5) | 1 + 12 |
| 9 | Notificaciones | `notification_rule` | I-08 (D6) | 2 |
| | Validación con `qa/scripts/` y checklist visual | | | 3 |
| | **Total** | | | **≈ 41 h e** sin el tramo 3 del informe (≈ 53 h e con él) |

Antes del 2026-11-01 (14 días): pasos 0, 1, 2 y la decisión de I-01 son obligatorios; 3 y 4 recomendables si Apu Samay recibe usuarios pronto; 5–6 son lo de mayor exposición a clientes pero necesitan D1/D2.

## 5. Verificar manualmente en la instancia

| # | Qué mirar | Para decidir |
|---|---|---|
| 1 | Informes → historial: abrir el generado el 2026-10-01 de TG GOCTA y de Piscina. ¿Tiene KPI o salen en "—"? ¿Hora y zona de los datos? ¿Y el de Pumarinri (¿se generó?, ¿error?) | I-01; si el renderer tiene `jwt_token` y qué zona usa |
| 2 | ¿Alguien (Romel) ha enviado o descargado esos informes a clientes? | urgencia de I-01 |
| 3 | Planificadores: quién es el usuario `12fff710…` y si sigue activo; si `targets` sigue vacío en los 4 | I-01 |
| 4 | Alarmas → historial de "Factor de Potencia Bajo" del último mes en cada 3EM: ¿hay creadas de madrugada o en intervalos regulares? | F13 |
| 5 | Alarmas activas de cualquier dispositivo: ¿aparecen ya resueltas en la lista del dashboard o en el contador de Flota? | F42 |
| 6 | Export Raw de 30 días de una instalación 3EM con 3 variables (potencia, tensión, energía): última fila de cada columna frente a la fecha "hasta"; intervalo real entre muestras | I-09 |
| 7 | Contrastar el "Energía acumulada hoy" de una captura con `qa/scripts/energia_hasta_hora.py` sobre un export Raw de **solo** `energia_total` (README §2); y "Ayer" con `energia_dia.py` | magnitud de I-02 (los scripts compilan y corren; con un CSV sintético de contador constante dieron los valores esperados; **no hay CSV reales en el repo**) |
| 8 | Factor de potencia del 3EM frente a `factor_potencia.py` | F25 |
| 9 | Dashboard TG PRUEBA: ¿existe?, ¿con qué grupo?, ¿qué widget y dispositivo usa? Usuarios de prueba que sigan activos | F16 y datos de prueba |
| 10 | Usuarios por customer: ¿hay Customer Administrator? ¿Algún usuario de Apu Samay? ¿Tiene algún dashboard compartido? | I-05, I-06 |
| 11 | Vida del JWT (Configuración de seguridad) y comportamiento con Flota abierta más tiempo | I-04 |
| 12 | Dashboard `32131e90` y dispositivo `cf7ddac0`: ¿siguen eliminados? ¿La relación de la integración 3EM con `cf7ddac0` sigue? | P-5, P-10 |
| 13 | Tarifa 0,65 S/./kWh: ¿es la vigente de cada concesionaria (Gocta, Tucán, Pumarinri)? Atributos de `717ae5e0` (no tiene `tarifa_kwh`; el CFG del dashboard fija 0,65) | D2 |
| 14 | Alarmas del dispositivo Plus 1: probar que no hay "desconectado" | F43 |

**Datos de prueba que un cliente podría ver (repo):** ninguno visible en HEAD. `customer/` solo tiene Gocta, Tucán, Pumarinri y Apu Samay; `hierarchy/` solo dispositivos de producción (6); `dashboard/` solo los 6 de producción; el widget DEV `afc86b80` solo lo ven quienes editan widgets. Pendiente de la instancia: TG PRUEBA (punto 9), usuarios de prueba.

## 6. Decisiones que te tocan (sin decidir)

| # | Decisión | Afecta |
|---|---|---|
| D-1 | R0 de Flota y Exportación: ¿aplicarlos ya como están (validados, un apply cada uno) o esperar para unificarlos con I-06 y demás cambios del mismo widget y ahorrar una aplicación por widget? | Pasos 3–4 |
| D-2 | Definición de día y comparativos (D1 del informe QA): día 00:00–24:00 Lima con comparativos a la misma hora (recomendado en el informe) o solo contra días cerrados | I-02, I-03, I-01 |
| D-3 | Informes del 2026-11-01: (A) pausar los 4 planificadores hasta tener el informe correcto; (B) dejarlos correr sin destinatarios y revisarlos; (C) priorizar el informe mensual real (10–14 h) antes de esa fecha. Y si el tramo F08 es Correctivo o Evolutivo (Tipo) | I-01 |
| D-4 | Costo: ¿"costo de energía" o con cargos e IGV?; ¿0,65 vale para los tres clientes? (D2) | I-02, I-03 |
| D-5 | Calendario de B frente a Apu Samay: ¿B llega antes de su primer usuario o se hace el cambio mínimo de I-06? ¿Se hace la PoC P-9 antes? | I-06 |
| D-6 | Umbrales únicos (D3): temperatura de la piscina, FP (0,85/0,95; por fase o total), voltaje, kW máx. por instalación | I-07, F12 |
| D-7 | Notificaciones (D6): qué alarmas, a quién, por qué canal; ¿se quita el texto "WhatsApp" o se implementa? | I-08 |
| D-8 | Permisos de cliente (D8): quitar `RPC_CALL`/`READ_CREDENTIALS` del Customer User; qué puede hacer un Customer Administrator | I-05, F45 |
| D-9 | ¿Se incluyen los OPO (F28, F32, F33, F38) en los apply de 3EM/Piscina? | Pasos 5–6 |
| D-10 | Histórico de Pumarinri (P-6): ¿se intenta recuperar desde un respaldo de `gonex-postgres` anterior al 2026-10-10 16:00 Lima o desde Shelly Cloud? Si hay rotación de respaldos, el plazo corre | Romel/Erick |
| D-11 | ¿Sunkuu (admin) cuenta como "cliente" para la severidad de F06 y F07 (D11)? Aquí se trató como cliente | I-03 |
| D-12 | Si "B" es el Nivel 1 de la propuesta de arquitectura (supuesto de este triage) | Clasificación "se resuelve con B" |
