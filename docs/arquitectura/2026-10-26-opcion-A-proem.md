# Opción A — Template Shelly Pro EM-50: análisis y plan de implementación

Fecha: 2026-10-26 · Base: `../sunkuu-tb-config` `8a1f930` (solo lectura) · **Análisis y plan: sin código, nada aplicado.**
Antecedente: `docs/arquitectura/2026-10-propuesta-alta-y-proem.md` §3 (2026-10-11, base `873bcd7`). Este documento lo actualiza con lo hecho después (FIX-01, FEAT-01, registro de instalaciones B-02…B-06) y con el caso de Apu Samay.
Equipos de Apu Samay: **Hab. 105** = `441d6474e3f8` (primero, para validar) y **Hab. 104** = `441d6475f6c0` (después). En Apu Samay solo se usa el canal 0, que mide el consumo total de cada habitación.
Decisiones de Erick (2026-10-26): §7. Plan: §8.

## 1. Qué ya existe en `sunkuu-tb-config` (comparado con Pro 3EM y Plus 1)

| Elemento | Pro 3EM (en producción) | Plus 1 · Piscina (en producción) | Pro EM50 |
|---|---|---|---|
| Perfil de dispositivo | `89ae3280` "Shelly Pro 3EM", rule chain raíz explícita (`fee60810`) | `fa155fd0` "Shelly Plus 1", rule chain por defecto (la raíz) | `b75859d0` "Shelly Pro EM50", rule chain por defecto (la raíz). Sin alarmas ni dashboard por defecto, igual que los otros |
| Integración MQTT | `1d4d1880`, `mosquitto:1883` anónima, `+/status/em:0`, `+/status/emdata:0` | `38a2b4d0`, `switch:0`, `temperature:0/1/101` | `e3980900`, **habilitada**, `+/status/em1:0` y `em1data:0` (QoS 0), `em1:1` y `em1data:1` (QoS 1). `allowCreateDevicesOrAssets: true` |
| Converter (campo `decoder`, JS) | `df3eb870`, `deviceType: 'Shelly Pro 3EM'`, **sin** filtro de prefijo | `ed204fa0`, **con** filtro `shellyplus1-` | `b69ff030`, `deviceType: 'Shelly Pro EM50'`, **sin** filtro de prefijo (F18, SEC-03) |
| Dispositivos | 4 (Gocta, Tucán, Pumarinri, QA) | 1 (Gocta) | **Ninguno.** El "Caldero Piscina" de Gocta (`shellyproem50-441d6475fe58`) nunca publicó (WiFi, `README.md`); el Template Piscina dice "Caldero eliminado" |

Nota: en los converters Pro EM50 y Plus 1, el campo `tbelDecoder` tiene la plantilla de ejemplo de ThingsBoard. Como `scriptLang` es `JS`, se ejecuta `decoder`, que tiene el código real. No es un defecto.

**Conclusión:** perfil, integración y converter ya están. Falta el filtro de prefijo (A-01), la vista (template), el catálogo del registro, el formulario, Flota y Exportación.

## 2. Claves de telemetría (converter `b69ff030`, sin cambios de claves)

Un mensaje por canal y por componente; los timestamps de los canales no coinciden.

| Tópico | Claves (N = 0 o 1) | Unidad | Campo Shelly |
|---|---|---|---|
| `<id>/status/em1:N` | `voltaje_canal_N` | V | `voltage` |
| | `corriente_canal_N` | A | `current` |
| | `potencia_activa_canal_N` | W | `act_power` |
| | `potencia_aparente_canal_N` | VA | `aprt_power` |
| | `factor_potencia_canal_N` | — | `pf` |
| | `frecuencia_canal_N` | Hz | `freq` |
| `<id>/status/em1data:N` | `energia_canal_N` | Wh (contador perpetuo) | `total_act_energy` |
| | `energia_ret_canal_N` | Wh | `total_act_ret_energy` |

16 claves. **No hay** `potencia_activa_total` ni `energia_total`: el total se calcula en los widgets (§3.3). Se mantienen los nombres `_canal_N`; la etiqueta visible sale del registro.

**Se verifica con Hab. 105 (A-02):**
- Qué publica `em1:1` sin pinza: ceros, `errors: ["ct_type_not_set"]` u otra cosa. Si llega `voltage` sin `current`, el converter escribe claves con `undefined`.
- Cada cuánto publica. El Shelly envía `status` "si hubo un cambio significativo", no de forma periódica. Con eso se fijan los umbrales de estado del tipo.

## 3. Template Pro EM a partir del Template 3EM (`373ddd50`)

### 3.1 Enfoque
Widget **nuevo** "Sunkuu — Template Pro EM", derivado del 3EM. **El 3EM de producción no se toca.** Las funciones de FIX-01 se copian **literalmente**; un script de build aborta si difieren de las del 3EM, como `build_b06.py`.

### 3.2 Qué se reutiliza y qué cambia

| Parte del 3EM | En el Pro EM |
|---|---|
| Bloque `FIX-01:BEGIN fx` (`fxEnergy`, `fxMonthEnergy`, `fxProject`, `fxFP`, `fxStatus`…), `limaMidnight`, `api()` con sesión | Literal. Se llama una vez **por canal en uso** con `energia_canal_N` (energía hoy, comparativos hoy/ayer/semana, promedio de 30 días, proyección del mes) y se suman los resultados |
| Curva de demanda FEAT-01 (`dcLoad`, `dcRender`: 4h · 8h · Hoy · Ayer, medianoche de Lima, "Total ayer" superpuesto, resolución y huecos) | Igual. Series: una por canal en uso + "Total" (suma por tramo) + "Total ayer" |
| Selector FEAT-01 "Total · Fases · Todo" (recordado por navegador) | "Total · Canales · Todo". **Oculto** con un solo canal en uso (Total = canal 0) |
| Tabla de fases (`PHASE_ROWS`, columnas A/B/C) | Una columna por canal en uso, con el nombre del registro. Voltaje y frecuencia: un solo valor (canal 0), porque el equipo tiene una sola entrada de tensión |
| FP = P/S (FIX-01) | FP total = Σ P / Σ S de los canales en uso; FP por canal en la tabla |
| Costo, proyección, KPIs, inteligencia operativa, alarmas, PDF, estado En línea / Sin datos / Desconectado | Igual, sobre el total. El estado usa el dato más reciente de cualquier canal en uso |
| Origen del dispositivo: `DEVICE_ID` del `<!--CFG:-->` del HTML | Del registro: `REG.porDashboard(lista, dashboardId)` → `dispositivos.principal` y los canales. *Fail-closed*: sin registro o sin instalación, mensaje y ninguna consulta |
| `TARIFA = 0.65` por defecto en el código | **Sin valor por defecto** (P-A5): sin `tarifa_kwh`, el costo no se muestra y sale un aviso |
| Panel de parámetros (`renderCfgPanel`) | Sin los nombres de canal (van en el registro). Solo el tenant edita (F45). La copia DEV lleva el bloque `DEV-ONLY` |
| `EXPORT_DASH` (UUID fijo de Exportación) | Igual que el 3EM hasta FIX-02 |
| Selector de fecha | No va en la base. Se porta desde FIX-02 (A-09) |

### 3.3 Canales y total (P-A2, P-A3, P-A7)

Atributos `SERVER_SCOPE` del **activo de la instalación**, editables con el formulario de Administración:

| Atributo | Valor | Efecto |
|---|---|---|
| `canal_0_nombre` | Texto | Nombre del canal 0 en la tabla, la curva, el PDF y Exportación. El canal 0 siempre está en uso (es el rol obligatorio) |
| `canal_1_nombre` | Texto; **vacío o ausente = canal sin uso** | Con nombre: se muestra y se suma al total. Vacío: se oculta y no se consulta, en el template, en Flota y en Exportación |

**Total = suma de los canales en uso** (los canales son circuitos independientes). Con el canal 1 oculto, total = canal 0. Potencia instantánea: último valor de cada canal, sin emparejar por timestamp. Energía: suma de las diferencias de contador de cada canal.

## 4. Registro de instalaciones: tipo `proem` completo (parche P-A6)

Hoy `proem` existe como esqueleto en `sunkuu-registro.js` (`3f7112c0`): `roles.principal` (perfil "Shelly Pro EM50", prefijo `shellyproem50-`), `template_widget: null`, `flota: null` y `export: {}`. El módulo lo cargan **solo** las copias DEV (Flota, Exportación, 3EM y Piscina) y el formulario "Sunkuu — Registro de instalaciones" (`c1e90290`). Ningún widget de producción de los clientes lo carga todavía (verificado en `8a1f930`).

| Campo / función | Cambio |
|---|---|
| `nombre` | "Pro EM · Monofásico · 2 canales" |
| `template_widget` | "Sunkuu — Template Pro EM" |
| `flota` | Por canal: `kw` `potencia_activa_canal_N`, `contador_wh` `energia_canal_N`, `fp` `factor_potencia_canal_N` y `s` `potencia_aparente_canal_N` |
| `export` | Las 16 claves de §2 en "Potencia", "Energía" y "Calidad Eléctrica", cada una marcada con su canal |
| Q1 (`ATRIBUTOS`) y `normalizar` | Leen `canal_0_nombre` y `canal_1_nombre` → `inst.canales` = canales en uso con su nombre (solo `proem`) |
| `exportacion(inst)` | Omite las variables de los canales sin uso y pone el nombre del canal en la etiqueta |
| Nueva ayuda pura | `canalesEnUso(inst)` para el template y Flota |

## 5. Firmware 1.4.4 (20241011)

**Sí basta**, según lo que sé de la API Gen2 de Shelly (no lo comprobé en línea: este proyecto no hace llamadas de red). "Generic status update over MQTT" es el campo `status_ntf` de `Mqtt.SetConfig`. Existe en la API Gen2 desde antes de la 1.0, y el Pro EM-50 salió con firmware 1.x; los componentes `em1`/`em1data` también son de esa línea.

**Confirmado (Erick, 2026-10-26):** el firmware 1.4.4 de Hab. 105 muestra la opción "Actualización genérica del estado a través de MQTT" (interfaz en español). **No se actualiza el firmware.**

**Comprobación en el equipo, sin actualizar:** en la interfaz web de Hab. 105 → Settings → MQTT debe aparecer el interruptor "Generic status update over MQTT". Equivale a ver `status_ntf` en `Mqtt.GetConfig`. Si aparece, no se actualiza el firmware. Si no aparece, avísame antes de tocar nada.

## 6. Qué tienes que hacer tú (Shelly y VPS)

**En Hab. 105 primero (Shelly Cloud/app o interfaz web local):**
1. Anotar el **Device ID** exacto (Settings → Device information). Esperado: `shellyproem50-441d6474e3f8`. El nombre del dispositivo en ThingsBoard sale del tópico, y A-01 rechaza lo que no empiece por `shellyproem50-`.
2. Activar "Actualización genérica del estado a través de MQTT" (§5: presente en 1.4.4; no se actualiza el firmware).
3. Pinza del canal 0 en la acometida de la habitación, con el tipo de CT configurado (que no aparezca `ct_type_not_set`). En el canal 1 no hay nada.
4. **MQTT:**
   - Habilitado, con el servidor `thingsboard.gonex.pe:1884`.
   - Sin usuario ni contraseña y sin TLS (SEC-03: así funciona hoy).
   - Client ID y prefijo **por defecto**: no cambiarlos.
   - **"Generic status update over MQTT" activado.**
   - Guardar y reiniciar.
5. Dejar Shelly Cloud activo en paralelo (decisión de Romel).
6. Si el tablero tiene red cableada, usar el puerto LAN (el Caldero de Gocta falló por WiFi).
7. No sé si Shelly Cloud permite configurar MQTT a distancia en este modelo: **verificar**. Si no, hay que hacerlo en la interfaz web local, desde la red del lodge.

**En el VPS (`gonex-infra`), solo lectura:**
- Nada obligatorio: Mosquitto ya expone 1884.
- Comprobación de llegada: `docker exec gonex-mosquitto mosquitto_sub -h localhost -p 1883 -t 'shellyproem50-441d6474e3f8/#' -v -W 120`. Esperado: `status/em1:0`, `status/em1:1`, `status/em1data:0` y `status/em1data:1`.

**En ThingsBoard:** §8, A-02.

## 7. Decisiones (Erick, 2026-10-26)

| # | Decisión |
|---|---|
| P-A1 | Una instalación con su dashboard por habitación (Hab. 104 y Hab. 105) |
| P-A2 | Los canales son circuitos independientes ("también para medir consumos de electricidad", Romel). Total = suma de los canales en uso; con el canal 1 oculto, total = canal 0 |
| P-A3 | Nombres de canal en el registro (atributo de la instalación, editable con el formulario de Administración). Nada en el dispositivo ni en el código |
| P-A4 | El selector de fecha entra en el Pro EM, pero se diseña una sola vez en FIX-02 (3EM y Piscina) y luego se porta al Pro EM antes de la entrega. Orden: base del Pro EM → FIX-02 → selector en el Pro EM |
| P-A5 | Sin valor por defecto en el código. `tarifa_kwh` se escribe como atributo en el alta (0,65 salvo que Romel indique otra); sin tarifa, el costo no se muestra y sale un aviso |
| P-A6 | Parche preparado en `widgets/work/` (catálogo + Flota + Exportación), que se aplica junto con B-08 |
| P-A7 | Exportación muestra solo los canales en uso (mismo criterio que el template) |
| SEC-03 | Mosquitto anónimo registrado (`docs/qa/2026-10-26-SEC-03-mosquitto-anonimo.md`). Mitigación mínima ahora: filtro `shellyproem50-` en el converter. La autenticación se evalúa aparte |

## 8. Plan de implementación

Cada paso sigue el ciclo de `CLAUDE.md`: base al día, `widgets/work/<ID>/` con apply y rollback, revisión del diff, aplicas tú y luego vienen el versionado y el CHANGELOG. Horas de GONEX, estimadas.

| Orden | ID | Qué | Dónde se aplica | Depende de | Opt. | Prob. | Pes. |
|---|---|---|---|---|---|---|---|
| 1 | **A-01** | SEC-03 M1 y M2: filtro `shellyproem50-` en el converter `b69ff030` y `shellypro3em-` en `df3eb870` (`return null` si no coincide, como Plus 1). Pruebas node. **Preparado** (`docs/qa/2026-10-26-A-01.md`) | Converters (producción), con rollback | — | 0,5 | 1 | 1,5 |
| 2 | **A-02** | Conexión de **Hab. 105** (§6). Pasos en ThingsBoard: debug "all" de la integración unos 15 min, dispositivo creado (del tenant), "Cambiar propietario" → APU SAMAY NATURE LODGE (`686e4250`) y versión manual Overwrite con todos los tipos. `tarifa_kwh` = 0,65 en el dispositivo y versión manual de Dispositivo. Observación de 24–48 h: frecuencia de publicación y qué manda `em1:1` sin pinza. Licencia: 7 → 8 de 100 dispositivos | Shelly (tú/Romel) + ThingsBoard | A-01 | 1 | 1,5 | 2,5 |
| 2b | A-01b | Solo si A-02 lo pide: el converter omite las claves `undefined` del canal sin pinza | Converter | A-02 | 0 | 0,5 | 1 |
| 3 | **A-03** | Módulo `sunkuu-registro.js` (§4): catálogo `proem`, `canal_N_nombre`, `canalesEnUso`, `exportacion` filtrada. Las 26 pruebas existentes más las nuevas | Recurso del tenant (**cuándo: P-A9**) | — | 2,5 | 3,5 | 5 |
| 4 | **A-04** | Formulario de Administración (`c1e90290`): campos "Nombre del canal 0" (obligatorio para `proem`) y "Nombre del canal 1" (vacío = sin uso), validación y escritura. Comprobar que 3EM y Piscina no cambian | Widget del tenant (**cuándo: P-A9**) | A-03 | 1,5 | 2 | 3 |
| 5 | **A-05** | Template Pro EM, **base** (§3): copia DEV primero, con `DEV-ONLY`; suma de canales; FIX-01 literal con script de build; FEAT-01 adaptado; registro *fail-closed*; tarifa sin valor por defecto. Pruebas headless con TZ=Asia/Tokyo, 1 y 2 canales, y mutaciones | Widget nuevo (DEV → producción) | A-03 | 12 | 16 | 22 |
| 6 | **A-06** | Instalación y dashboard de **Hab. 105**: dashboard desde el template; activo `INST · Hab. 105` de Apu Samay (tipo `proem`, `dashboard_id`, `dispositivos`, `canal_0_nombre`, `es_prueba=false`) con el formulario (P-A10); +1 activo. Validación solo con el admin (SEC-02: Apu Samay sin usuarios) | Dashboard + registro | A-02, A-04, A-05 | 1 | 1,5 | 2,5 |
| 7 | **A-07** | Flota con `proem` sobre B-06: generalizar los `inst.type==='3em'` (energía, ayer, proyección, costo, FP), sumar los canales en uso y `EST_DEF.proem` con lo observado en A-02 | Parche P-A6, **con B-08** | B-06, A-02, A-03 | 2,5 | 3,5 | 5 |
| 8 | **A-08** | Exportación: solo los canales en uso y su nombre (con `exportacion` de A-03); verificación sobre B-05 | Parche P-A6, **con B-08** | B-05, A-03 | 0,5 | 1 | 2 |
| — | FIX-02 | Selector de fecha y resto de FIX-02 en 3EM y Piscina (diseño B §7, ≈ 16 h e, **fuera de esta suma**) | 3EM y Piscina | A-05 (por el orden de P-A4) | — | — | — |
| 9 | **A-09** | Portar el selector de fecha de FIX-02 al Pro EM (sobre las mismas funciones, 1 y 2 canales) | Template Pro EM | FIX-02 | 2 | 3 | 5 |
| 10 | **A-10** | Alta de **Hab. 104** (`441d6475f6c0`) con el procedimiento de A-02 y A-06, ya probado | Shelly + ThingsBoard | A-06 | 0,5 | 1 | 2 |
| 11 | **A-11** | Guiones de QA, informe de cada paso, CHANGELOG y manual de alta para `proem` (repartido en los pasos) | sunkuu-TB | — | 2 | 2,5 | 3,5 |
| | | **Total Opción A** | | | **26** | **37** | **55** |

Respecto de la estimación anterior (27 h), suben: la suma de canales (+2), el formulario (+2), Exportación filtrada (+1), la portabilidad del selector de fecha (+3), la conexión en dos tiempos (+1) y A-01 (SEC-03, +1).

**Tipo:** Evolutivo (Opción A), salvo A-01. Propongo A-01 como Correctivo (seguridad, configuración de GONEX); confírmalo.

**Ruta crítica y bloqueos:**
- A-01 → A-02 se puede hacer ya: no depende de SEC-02 ni de B-08.
- A-05 necesita el módulo con los canales (A-03). Si A-03 espera a B-08, que está bloqueado por SEC-02, la base del Pro EM solo se puede probar con el entorno simulado. **P-A9.**
- La entrega a Apu Samay (usuarios) depende de cerrar SEC-02.
- B-08 debe ir antes del primer usuario de Apu Samay con Flota o Exportación (diseño B §7).

## 9. Decisiones del plan (Erick, 2026-10-26)

**Plan de 37 h aprobado.** Tipo: A-01 Correctivo (seguridad); el resto, Evolutivo.

| # | Decisión |
|---|---|
| P-A9 | A-03 (módulo) y A-04 (formulario) se aplican **antes** de B-08. Flota y Exportación (A-07, A-08) van con B-08 |
| P-A10 | A-04 habilita los customers de producción en el formulario (`SOLO_CLIENTES_DE_PRUEBA=false`, con el diff revisado). El formulario es solo del tenant y Apu Samay no tiene usuarios |
| P-A11 | `canal_0_nombre` es obligatorio para `proem`; si falta al leer, la instalación se descarta con aviso |
| P-A12 | El mismo filtro de prefijo en el converter Pro 3EM (`shellypro3em-`), con rollback (SEC-03 M2). Va en A-01 |

**A-01 preparado:** `docs/qa/2026-10-26-A-01.md` (Pro EM50 y Pro 3EM; 23 de 23 pruebas; `base` ✔ sobre `ce213c8`). Siguiente: A-02 (conexión de Hab. 105) después de aplicar A-01.
