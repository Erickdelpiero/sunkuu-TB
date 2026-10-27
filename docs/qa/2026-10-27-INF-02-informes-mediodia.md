# INF-02 — Informes mensuales: Erick como destinatario, envío a las 12:00 de Lima y monitor de n8n a las 13:00

Fecha: 2026-10-27 · Base: `../sunkuu-tb-config` `85a9623` (solo lectura) · **Preparado, no aplicado.** Se aplica el **2026-10-28**, después de UPG-01.
Tipo: **por confirmar por Erick** (propuesta: Cortesía, 1 h e: el destinatario es para el control de GONEX y la hora la pide GONEX).
Relacionado: INF-01 (`CHANGELOG.md`), `config/informes/README.md` (destinatarios, fuera del Version Control), UPG-01 §2 y §6.6.

## Resumen

| Qué | Antes | Después |
|---|---|---|
| Destinatarios de los 4 eventos | target del customer + "Tenant administrators" | lo mismo + target nuevo **"GONEX — Erick"** (lista de usuarios: tu usuario del tenant) |
| Hora de los 4 eventos | día 1, **08:00** Lima | día 1, **12:00** Lima |
| Monitor de n8n "Monitor Reporte Mensual Sunkuu" | `30 8 1 * *` (08:30 Lima) | `0 13 1 * *` (13:00 Lima) |

## 0. Lo que dice la configuración (leído en `85a9623`)

**Zona horaria del planificador.** Los 4 eventos (`scheduler_event/*.json`) tienen `schedule.timezone = "America/Lima"`, `startTime = 1780318800000` (= 2026-06-01 13:00 UTC = **08:00 de Lima**), `repeat.type = MONTHLY` (fin en 2100) y `configuration.timezone = "America/Lima"`. La repetición mensual toma **el día y la hora de `startTime`** en la zona del evento, así que el cambio es solo la hora de inicio: de 08:00 a 12:00 **dejando la fecha en un día 1**. Lima no tiene horario de verano: 12:00 Lima = 17:00 UTC todo el año. Valor esperado después: `startTime = 1780333200000` (2026-06-01 12:00 Lima), o el mismo día 1 de otro mes si la UI cambia la fecha.

| Evento | UUID | Plantilla de informe | Destinatarios vigentes (`config/informes/README.md`) |
|---|---|---|---|
| Informe Mensual TG GOCTA | `c72d8880` | `900138f0` | Gocta Andes Lodge + Tenant administrators |
| Informe Mensual Piscina Temperada | `a6773ef0` | `94757860` | Gocta Andes Lodge + Tenant administrators |
| Informe Mensual Medidor Tablero Principal | `c967cba0` | `258ddba0` | Tucán Suites Aparthotel + Tenant administrators |
| Informe Mensual TG PUMARINRI | `8bee5690` | `defa3090` | Pumarinri Amazon Lodge + Tenant administrators |

**Efecto en el contenido.** Las 4 plantillas usan una ventana fija de **los últimos 30 días** desde la hora de generación (`timewindowMs = 2592000000`, sin `useDashboardTimewindow`). A las 08:00 del 1-nov cubren del 2-oct 08:00 al 1-nov 08:00; a las 12:00, del 2-oct 12:00 al 1-nov 12:00. Ninguna de las dos es el mes calendario (falta el 1-oct y parte del 2-oct en los dos casos); el corrimiento suma 4 h del 1-nov y quita 4 h del 2-oct. Es un problema previo (informe mensual real, I-01 tramo 3), no lo crea ni lo corrige INF-02.

**Notificación.** La plantilla "Report generated notification" (`ff7b4330`) tiene WEB y **EMAIL** activados. El target "Tenant administrators" (`ff6d6080`) es `TENANT_ADMINISTRATORS`. **Si tu usuario GONEX (ADM-01) es administrador del tenant, ya está incluido:** la última ejecución fue el 2026-10-01, antes de ADM-01 (2026-10-09), por eso aún no recibiste ninguno. No está verificado si ThingsBoard elimina duplicados entre dos targets que contienen al mismo usuario: con el target nuevo podrías recibir **dos correos por informe**. §1.2 lo decide.

**n8n.** `workflow.json` (instantánea en este repo, del 2026-10-06): disparador "Cron Mensual 8:30am" con `30 8 1 * *`; lee `docker logs gonex-tb-web-report --since 2h` por SSH y alerta por Telegram si hay algún `ERROR` o menos de 4 "Dashboard report generated". El contenedor de n8n tiene `GENERIC_TIMEZONE: America/Lima` (`gonex-infra` `docker-compose.yml`, L66), así que el cron se interpreta en hora de Lima salvo que el workflow tenga otra zona en sus ajustes (§4.1 lo comprueba). A las 13:00, `--since 2h` cubre de 11:00 a 13:00: incluye los informes de las 12:00 ✔.

## 1. Antes de cambiar nada (2026-10-28)

**1.1 Base al día.** Si UPG-01 se hizo, la versión de su §6.9 ya es la base. Luego, desde `sunkuu-TB`:
```
git -C ../sunkuu-tb-config pull && git -C ../sunkuu-tb-config log --format='%h %an %s' 85a9623..HEAD -- scheduler_event notification_target report_template
```
- Esperado: vacío o solo las versiones de UPG-01. Si aparece un cambio de Romel en esos tipos, pásamelo antes de seguir.
```
python3 -I widgets/work/INF-02/verificar.py antes
```
- Esperado: `RESULTADO: OK` (los 4 a las 08:00 del día 1). Si da "otros campos distintos de 85a9623" solo por la versión de UPG-01 (formato de exportación de 4.3.1.8), pásame la salida.

**1.2 Tu usuario y la decisión del duplicado.** Usuarios → Grupos de usuarios → "Tenant Administrators": ¿está tu usuario GONEX y con tu correo real?
- **Sí (lo esperable):** ya recibirías los 4 informes por "Tenant administrators". **Recomendación:** no crear el target nuevo y hacer solo la prueba de §3.6 con un target temporal; así no hay riesgo de correo doble. Si igual quieres el target explícito (por ejemplo, para no depender del grupo), sigue con §2 y en §5 mira si llegan dos correos.
- **No:** sigue con §2 (el target nuevo es necesario).

**1.3 Capturas para el rollback** (los destinatarios y la plantilla de notificación **no se exportan**): en Planificador, abre cada uno de los 4 eventos y captura la pestaña de configuración (plantilla de informe, usuario generador, destinatarios, plantilla de notificación) y la de programación (inicio, zona horaria, repetición). Deben coincidir con la tabla de §0; si no, **para** y avísame.

**1.4 n8n:** abre "Monitor Reporte Mensual Sunkuu" y descárgalo (menú ⋯ → Download) como `monitor-reporte-mensual-pre-INF-02.json` fuera del repo (contiene el `chatId` de Telegram y la referencia a la credencial SSH). Es el rollback de §4.

## 2. Target nuevo (solo si §1.2 lo pide)

Notificaciones → Destinatarios → Agregar:
- Nombre: **`GONEX — Erick`**
- Tipo: Usuarios de la plataforma → **Lista de usuarios** → tu usuario GONEX (no el de Romel ni el de GONEX QA).
- Descripción: `Control de GONEX: copia de los informes mensuales (INF-02)`.

## 3. Los 4 eventos

Para cada evento de la tabla de §0, en Planificador → editar:

3.1 **Destinatarios:** agrega `GONEX — Erick` **sin quitar** los dos que ya tiene. La plantilla de notificación sigue en "Report generated notification".

3.2 **Programación:** comprueba que la zona horaria dice **America/Lima** y cambia solo la hora de inicio de **08:00 a 12:00**. La fecha de inicio debe seguir siendo un **día 1** (si la UI la cambia a otro día, el informe saldría ese día de cada mes). Repetición: mensual, sin cambios.

3.3 Guardar. Al cerrar, la lista del Planificador debe mostrar la próxima ejecución **2026-11-01 12:00**.

3.4 Repite para los otros 3. Cada guardado genera un auto-commit (`scheduler_event`), que no incluye los destinatarios.

3.5 **Versión manual** (usuario GONEX): `chore(INF-02): informes a las 12:00 y destinatario GONEX`, estrategia **Merge**, tipos **Planificador** y **Destinatarios de notificación** (`notification_target`; el auto-commit no lo captura), credenciales **desmarcado**. Luego:
```
git -C ../sunkuu-tb-config pull && git -C ../sunkuu-tb-config show --stat --format='%h %an %s' HEAD
```
- Esperado: autor GONEX y, como mucho, los 4 `scheduler_event/*.json` y un `notification_target/*.json` nuevo.
```
python3 -I widgets/work/INF-02/verificar.py despues
```
- Esperado: los 4 con `2026-06-01 12:00 Lima (1780333200000)` (u otro día 1 a las 12:00), `target nuevo desde 85a9623: … 'GONEX — Erick' {"type": "USER_LIST", …}` y `RESULTADO: OK`.

3.6 **Prueba de entrega (opcional, recomendada).** Comprueba que el correo con el PDF llega sin esperar al 1-nov y sin enviar nada a clientes:
1. Planificador → Agregar: nombre `PRUEBA INF-02 (borrar)`, tipo "Generar informe", plantilla **Informe Mensual - TG GOCTA** (`900138f0`), usuario generador el mismo de los 4 (`romelvalqui.r@gmail.com`), destinatarios **solo** `GONEX — Erick` (o, si en §1.2 no creaste el target, uno temporal `PRUEBA INF-02` con tu usuario), plantilla "Report generated notification", sin repetición, inicio dentro de 5 minutos.
2. Esperado: un correo con el PDF del dashboard TG GOCTA y una notificación en la campana. En el VPS:
```
docker logs gonex-tb-web-report --since 15m 2>&1 | grep -E 'Dashboard report generated|ERROR'
```
   Debe salir una línea `Dashboard report generated` y ningún `ERROR`.
3. Elimina el evento de prueba (y el target temporal, si lo creaste). Las eliminaciones no las registra el auto-commit: versión manual `chore(INF-02): baja del evento de prueba`, **Overwrite, todos los tipos**, credenciales desmarcado (CLAUDE.md). Después, `git pull` y `git show --stat HEAD`: solo debe desaparecer el evento de prueba (y el target temporal).

## 4. Monitor de n8n

4.1 En el workflow, ⋯ → Settings → **Timezone**: debe decir "Default" (America/Lima) o "America/Lima". Si dice otra, avísame antes de cambiar la hora.

4.2 Nodo "Cron Mensual 8:30am": expresión de **`30 8 1 * *`** a **`0 13 1 * *`** y nombre a **`Cron Mensual 13:00`**. El nodo SSH (`--since 2h`) no cambia.

4.3 Guardar y comprobar que el workflow sigue **Active**. En la lista de ejecuciones no hay forma de ver la próxima; queda verificado por la expresión y la zona de 4.1.

4.4 Descarga el workflow ya cambiado y pásamelo: actualizo `workflow.json` de este repo (hoy es la instantánea del 06-oct) sin el `chatId`.

## 5. Después

- **2026-11-01 12:00–12:15:** llegan los 4 correos (o 8 si quedaste en dos targets, ver §1.2) con el PDF; los clientes y Romel, como siempre.
- **2026-11-01 13:00:** si todo salió bien, el monitor no envía nada a Telegram. Si alerta, `docker logs gonex-tb-web-report --since 2h` y avísame.
- `config/informes/README.md`: lo actualizo cuando confirmes §3 (tabla de destinatarios con `GONEX — Erick`, hora 12:00 y el monitor de n8n). `CHANGELOG.md`: fila INF-02 con los hashes de §3.5.

## 6. Rollback

1. **Eventos:** en cada uno, hora de inicio de vuelta a **08:00** (mismo día 1) y quitar `GONEX — Erick` de destinatarios, comparando con las capturas de §1.3. Versión manual `chore(INF-02): rollback`, Merge, tipos Planificador y Destinatarios de notificación. Luego:
```
git -C ../sunkuu-tb-config pull && python3 -I widgets/work/INF-02/verificar.py rollback
```
   Esperado: los 4 a las 08:00 y `RESULTADO: OK`.
2. **Target:** si se elimina `GONEX — Erick` (opcional: sin eventos que lo usen no envía nada), versión manual **Overwrite, todos los tipos** (las bajas no se registran solas).
3. **n8n:** expresión de vuelta a `30 8 1 * *` y nombre "Cron Mensual 8:30am", o importar `monitor-reporte-mensual-pre-INF-02.json` de §1.4 sobre el mismo workflow. Comprobar que queda Active.
4. Si el rollback se hace el día 1 entre las 08:00 y las 12:00, los informes de ese mes ya no salen ese día (la hora de las 08:00 ya pasó): generar a mano con un evento de una sola vez como el de §3.6, con los destinatarios de los 4 eventos.
