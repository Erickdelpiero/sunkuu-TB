# FIX-01 — Verificación con datos reales

Fecha: 2026-10-19 · Base: `../sunkuu-tb-config` HEAD `b0df850` (solo lectura).
Producción = `widgets/work/FIX-01/*/apply/controllerScript.js` (3EM `373ddd50` y Piscina `5f7b51c0`, comparados con el export).
Datos: exports Raw del Centro de Exportación en `widgets/work/FIX-01/datos/` (ignorado por git; no se copian aquí datos crudos):
TG GOCTA `energia_total` del 2026-09-19 00:00 al 2026-10-19 10:44 Lima, y Piscina Temperada (Plus 1 + H&T) del 2026-09-12 al 2026-10-19 10:42 Lima.
Capturas del 3EM TG GOCTA a las 10:32:42 y 10:45:33 Lima.

## 1. Atributos de estado que lee FIX-01

| Widget | Atributo | Ámbito | Dispositivo | Defecto |
|---|---|---|---|---|
| Piscina | `estado_alerta_h` | SERVER_SCOPE | calentador `CAL_ID` = Plus 1 `96594b70` (`cal` del CFG del dashboard) | 2 h |
| Piscina | `estado_desconexion_h` | SERVER_SCOPE | ídem | 6 h |
| 3EM | `estado_alerta_h` | SERVER_SCOPE | `DEVICE_ID` del dashboard (`d` del CFG o `ctx.settings.deviceId`): `c636fa00` TG GOCTA, `1bfa8070` Medidor Tablero Principal, `717ae5e0` TG PUMARINRI | 2 h |
| 3EM | `estado_desconexion_h` | SERVER_SCOPE | ídem | 6 h |

- Lectura: `GET /api/plugins/telemetry/DEVICE/<id>/values/attributes/SERVER_SCOPE`; escritura desde "Editar parámetros": `POST …/DEVICE/<id>/SERVER_SCOPE`. No se leen atributos compartidos.
- Un valor no numérico o 0 conserva el defecto; si `desconexión ≤ alerta`, ambos vuelven a 2/6.
- En `b0df850` ningún dispositivo tiene todavía estos atributos: rige 2/6 en todos.
- **2026-10-19:** cargados en el Plus 1 (`96594b70`), como atributos del servidor, `estado_alerta_h` = 4 y `estado_desconexion_h` = 8 (ver §4). Los 3EM siguen con el defecto 2/6. Registrado en la versión manual `fcedb2d` ("FIX-01 umbrales de estado 4/8 en Plus 1"); el resto de ese commit son marcas de tiempo de `active`/`lastActivityTime`/`inactivityAlarmTime` y la omisión de `calculatedFields: []` vacíos en roles y widgets, sin cambios funcionales.
- Lección: el auto-commit no captura cambios de atributos de dispositivos; tras editarlos, versión manual.

## 2. 3EM: la réplica coincide con la pantalla

Función `fx` de FIX-01 ejecutada en node (bloque `FIX-01:BEGIN fx` tal cual) sobre el CSV Raw, con una API simulada de ThingsBoard (crudo `DESC limit` y `MAX` por tramo).

| Métrica | Pantalla 10:32:42 | Réplica 10:32:42 | Pantalla 10:45:33 | Réplica 10:45:33 |
|---|---|---|---|---|
| Energía hoy | 100,0 | 100,0 | 104,6 | 104,2 ¹ |
| Ayer, misma hora | 137,4 (−27,3 %) | 137,4 (−27,3 %) | 143,3 (−27,0 %) | 143,3 |
| Hace 7 días, misma hora | 120,9 (−17,3 %) | 120,9 (−17,3 %) | 125,6 (−16,7 %) | 125,6 |
| Ayer completo | 371,4 | 371,4 | 371,4 | 371,4 |
| Promedio 30 días | 321,6 | 321,2 ² | 321,6 | 321,2 ² |
| Proyección del mes | 10 463 | 10 463 | 10 465 | 10 465 |

¹ El CSV termina a las 10:44:01; le falta la lectura de las 10:45.
² El CSV no tiene lectura anterior al 19/09 00:00 y la réplica descarta ese día (29 días). Con los 30 días completos, los scripts dan 321,6, igual que la pantalla.

Contraste con `qa/scripts/` (interpolan en el instante exacto): hoy 99,8, ayer 137,3, 12/10 120,8 (00:00→10:32), ayer completo 371,45, proyección método B 10 464. La diferencia de unas décimas con el widget se debe a que este toma la última lectura ≤ ahora (10:32:42), no la interpolación a las 10:32.

## 3. 3EM: contador

- `energia_total` está en **Wh** (≈ 58 223 kWh acumulados) y se publica cada ~60 s.
- Sin resets reales en el periodo. Única bajada: el **16/10 a las 12:44:03** llega un dato duplicado con el valor de las 12:43:01 (−484 Wh). FIX-01 no se ve afectado (toma el MAX por tramo). `counter_delta()` de `qa/scripts/sunkuu_csv.py` lo cuenta como reset y suma ~0,48 kWh de más ese día.
- La columna cruda `energia_total` del CSV (etiqueta "Energía Total" en Exportación) es el contador de toda la vida del medidor, no la "Energía acumulada hoy": se puede confundir.
- Los huecos largos del 3EM (21/09 01:07–06:10, 23/09 23:27–24/09 06:09, 24/09 22:51–25/09 07:11) coinciden con huecos del Plus 1: cortes de toda la instalación, no del equipo.

## 4. Piscina: Plus 1 (`temperatura_sonda`)

- "Temperatura Piscina (°C)" de Exportación = `temperatura_sonda` del Plus 1 (`96594b70`), que la integración MQTT toma del tópico `status/temperature:101` (sonda externa).
- **Reporta por cambio**, no periódicamente: el salto típico es de 0,1 °C y solo el 1,4 % de las muestras consecutivas repiten valor.
- Intervalos desde el 14/09: mediana 1,8 min, p95 27 min, máximo 70,6 h. Desde el 12/10: mediana 2,2 min, p95 25 min, p99,9 82 min, máximo 2,65 h.
- 11 huecos > 2 h desde el 14/09. Los de 59–71 h (15–18/09, 21–23/09, 09–12/10) y los nocturnos del 21, 23 y 24/09 son desconexiones reales (la temperatura cambió más de 1 °C sin reporte; varios coinciden con el 3EM). Los de 2–4 h a mediodía (26/09, 08/10, 16/10) son normales: piscina estable cerca de 32 °C.
- Con el defecto de 2 h, el 16/10 de 10:45 a 13:24 se habría mostrado "Sin datos recientes" con el equipo funcionando.
- **Valores adoptados para el Plus 1: `estado_alerta_h` = 4 y `estado_desconexion_h` = 8.** Margen sobre el hueco normal más largo observado (2,65 h) y detectan los cortes nocturnos (> 7 h). Cargados el 2026-10-19 (ver §1).
- Señal alternativa: el Plus 1 también publica `status/switch:0` (`temperatura_interna`, `estado_salida`), así que `lastActivityTime` del dispositivo se actualiza más seguido que la sonda. Falta exportar `temperatura_interna` para medir su frecuencia. `active` depende de un `inactivityTimeout` que el dispositivo no define. El Shelly publica además su estado de conexión en `<id>/online` (LWT), que la integración no está suscribiendo hoy.

## 5. Piscina: H&T G3 (`temperatura`)

- "Temperatura Ambiente (°C)" = `temperatura` del H&T G3 (`b9dbf740`).
- Dispositivo a batería: despierta de forma periódica (muchos huecos de exactamente 2,0 h) y además cuando la temperatura cambia.
- Intervalos: mediana 81 min, p95 8 h, máximo 22,8 h; 145 huecos > 2 h. No sirve como señal de estado (FIX-01 ya usa el Plus 1).

## 6. Exportación

- Los dos CSV son Raw (pasos irregulares). `timestamp_ms` es UTC; `fecha`/`hora` están en la zona del navegador (aquí Lima).
- En modo agregado ThingsBoard sitúa el punto en el centro del tramo: con MAX, el contador queda desplazado medio tramo; AVG/SUM no tienen sentido para un acumulado (F46).
- Piscina pide hasta 50 000 puntos por variable sin paginar (F20 / I-09); aquí no se alcanzó (6 613 puntos del Plus 1).
