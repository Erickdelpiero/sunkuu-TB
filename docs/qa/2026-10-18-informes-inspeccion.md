# Inspección de informes y notificaciones — 2026-10-18

Solo lectura: `../sunkuu-tb-config` HEAD `ed52362`. Sin red, sin escritura fuera de `docs/qa/`. Lo que dice la UI (destinatarios de `8bee5690`, usuario `romelvalqui.r@gmail.com`, informes que llegan al correo del customer con copia a Romel) viene de Erick y **no se puede comprobar desde el repo**.

## 0. Corrección al triage (F09 / I-01)

> **El triage se equivocó.** `2026-10-18-triage-bugs.md` afirmó que los 4 planificadores no tienen destinatarios ("`targets: null`… nadie recibe nada"). Es falso. Se leyó un campo que el export de ThingsBoard no refleja. Los informes sí se entregan. Quedan sin efecto: la frase "nadie recibe nada" del resumen, el tramo 2 de I-01 ("asignar targets y plantilla"), la fila "Destinatarios: ninguno" de la tabla de I-01 y el punto 3 del apartado "Escenario". Lo que sigue vigente de I-01: el planificador de Pumarinri apunta a un dashboard eliminado (`32131e90`) y, según la UI, envía al target de **Gocta** (sección 5). La descripción del contenido del informe (F08) no cambia, pero Romel solo revisa que llegue con la marca de Sunkuu y no se propone nada sobre el contenido.

## 1. JSON crudo de los 4 `scheduler_event`

Los 4 archivos son idénticos salvo `reportTemplateId`, `id` y `name`. La sección completa de configuración de cada uno:

```json
"configuration" : {
  "reportTemplateId" : { "entityType" : "REPORT_TEMPLATE", "id" : "<ver tabla>" },
  "userId" : { "entityType" : "USER", "id" : "12fff710-c43d-11f1-b6ce-f79957c72819" },
  "timezone" : "America/Lima",
  "targets" : null,
  "notificationTemplateId" : null
},
"customerId" : { "entityType" : "CUSTOMER", "id" : "13814000-1dd2-11b2-8080-808080808080" },
"enabled" : true,
"originatorId" : null,
"ownerId" : null,
"schedule" : { "timezone" : "America/Lima", "startTime" : 1780318800000, "repeat" : { "type" : "MONTHLY", "endsOn" : 4115941200000 } },
"type" : "generateReport"
```

| Planificador | `reportTemplateId` | `name` |
|---|---|---|
| `8bee5690-48d6-…` | `defa3090-47e4-…` | Informe Mensual TG PUMARINRI |
| `c72d8880-48d5-…` | `900138f0-44b3-…` | Informe Mensual TG GOCTA |
| `a6773ef0-48d6-…` | `94757860-47e7-…` | Informe Mensual Piscina Temperada |
| `c967cba0-48d6-…` | `258ddba0-47e6-…` | Informe Mensual Medidor Tablero Principal |

(`customerId` `13814000-1dd2-11b2-8080-808080808080` es el UUID nulo de ThingsBoard: propiedad del tenant. `startTime` = 2026-06-01 08:00 Lima; `endsOn` = 2100-06-06.)

### Por qué el triage vio `null`
- Las claves existen (`targets`, `notificationTemplateId`), pero **valen literalmente `null`** en el export. No se leyó otra clave ni se confundió el archivo.
- Los valores en el repo son `null` en **todas** las versiones: en `d58d79a` (2026-10-06, primer export), en `0b0561a` (2026-10-10; solo cambió `userId`) y en HEAD.
- Los targets "Gocta" (`6c645f60`) y "Tucán" (`7b0fdda0`) se crearon el 2026-05-05 17:47–17:48 Lima y los planificadores entre 17:57 y 18:02 del mismo día (fecha extraída del UUID v1). Es decir, los destinatarios se configuraron cinco meses **antes** del primer export. Si el export los hubiera reflejado, el primer commit ya los tendría.
- **Conclusión: el export del Version Control de ThingsBoard no incluye los destinatarios ni la plantilla de notificación de los planificadores** (evidencia sólida, no prueba formal). Por lo tanto, **el repo no sirve para auditar quién recibe los informes**: eso se verifica solo en la UI.
- Esto también invalida usar la ausencia en el repo como evidencia de cualquier otra configuración de notificación de planificadores.

## 2. Targets y plantillas de notificación

### `notification_target/` (6 archivos)

| ID | Nombre | Tipo | Resuelve a |
|---|---|---|---|
| `6c645f60-48d4-…` | Gocta Andes Lodge | `PLATFORM_USERS` · `CUSTOMER_USERS` | Todos los usuarios del customer `79efbf60` (GOCTA ANDES LODGE) |
| `7b0fdda0-48d4-…` | Tucán Suites Aparthotel | `PLATFORM_USERS` · `CUSTOMER_USERS` | Todos los usuarios del customer `aa643a40` (TUCÁN SUITES APARTHOTEL) |
| `ff6cc440-26cf-…` | All users | `ALL_USERS` | Todos los usuarios del tenant |
| `ff6d6080-26cf-…` | Tenant administrators | `TENANT_ADMINISTRATORS` | Administradores del tenant |
| `ff6e23d0-26cf-…` | Users of the entity owner | `ORIGINATOR_ENTITY_OWNER_USERS` | Dueños (usuarios) de la entidad que dispara la regla (customer o tenant) |
| `ff6e71f0-26cf-…` | Affected user | `AFFECTED_USER` | El usuario afectado por la acción (p. ej., alarma asignada) |

- **Gocta:** existe. **Tucán:** existe.
- **Pumarinri (`a2202a70`): no existe ningún target** en el repo. Se confirma lo del triage (P-11) y, dado que el export sí incluye `notification_target`, este hallazgo sí es fiable.
- **Apu Samay (`686e4250`): no existe ningún target.**
- Descripciones: el target de Gocta dice "reciben informes de **TG GOCTA, TG PUMARINRI** y Piscina Temperada" (de antes de ALTA-01: Pumarinri era una instalación de Gocta). Es el origen del cruce descrito en la sección 5.
- Los targets de customer no están referenciados por ninguna `notification_rule` (ver sección 6).

### `notification_template/` — "Report generated notification" (`ff7b4330-26cf-…`, tipo `REPORT_GENERATED`)

| Canal | Habilitado | Contenido |
|---|---|---|
| WEB | sí | Asunto "Report generated"; cuerpo `${reportFormat} report '${reportName}' is ready`; botón "Go to reports" → `/reporting/reports` |
| EMAIL | sí | Asunto "Informe mensual de consumo energético — `${reportName}`"; cuerpo: "Estimado, adjunto encontrará el informe mensual de consumo energético generado automáticamente por la plataforma Sunkuu 360." |

`attachReport: false` en el export. El correo dice "adjunto", pero el flag figura en `false`: dado que el export no es fiable para planificadores, **verificar en la UI si el PDF se adjunta** (Erick confirma que llega; falta saber si adjunto o enlace). `reportTemplateId`, `userId` y `timezone` de la plantilla son `null`.
Las otras 13 plantillas son las de fábrica (solo WEB, o EMAIL para USER_ACTIVATED/USER_REGISTERED).

## 3. `report_template` (4)

Todos: `type: REPORT`, `format: PDF`, `customerId` nulo (tenant), un componente `DASHBOARD`, `type: png`, `baseUrl: http://thingsboard.gonex.pe:8080`, `state: ""` (estado por defecto del dashboard), `timewindow` historial de 30 días (`timewindowMs: 2592000000`, `interval: 7200000`, `aggregation: AVG`, `selectedTab: 1`), `useDashboardTimewindow: false`, `useCurrentUserCredentials: false`, `userId: null`, `timezone: America/Lima`, `fitWidth`, A3 apaisado, márgenes 20, fondo `#fff`, `namePattern: report-%d{yyyy-MM-dd_HH:mm:ss}`, `timeDataPattern: yyyy-MM-dd HH:mm:ss`. Encabezado: logo `LOGO SUNKUU COLOR.png` + título; pie: `FAVICON SUNKUU COLOR.png` + "Sunkuu Energy S.A.C. / RUC: 20609337002 - Chachapoyas, Perú".

| Plantilla | Nombre | Dashboard | ¿Existe? | Título del encabezado | `description` |
|---|---|---|---|---|---|
| `900138f0` | Informe Mensual - TG GOCTA | `e844d080` TG GOCTA | sí | "Informe Mensual de Consumo Energético: TG Gocta" | "…Tablero General Gocta" |
| `defa3090` | Informe Mensual - TG PUMARINRI | **`32131e90`** | **no** (eliminado en `71f1603`) | "Informe Mensual de Consumo Energético - TG Pumarinri" | "…Tablero General Pumarinri" |
| `94757860` | Informe Mensual - Piscina Temperada | `cc2cad90` | sí | "Informe Mensual - Piscina Temperada" | "Informe Mensual - Piscina Temperada" |
| `258ddba0` | Informe Mensual - Medidor Tablero Principal | `0469dc30` | sí | "…Medidor Tablero **General**" | "…Medidor Tablero Principal" |

### Diferencias `900138f0` (Gocta) vs `defa3090` (Pumarinri), campo por campo
Comparación exhaustiva de todas las claves anidadas. Solo difieren 5:

| Campo | Gocta | Pumarinri |
|---|---|---|
| `components[0].config.dashboardId` | `e844d080…` | **`32131e90…` (inexistente)** |
| `header.components[0].rightView.value` | "…Energético: TG Gocta" | "…Energético - TG Pumarinri" |
| `description` | "…Tablero General Gocta" | "…Tablero General Pumarinri" |
| `id` | `900138f0-44b3-…` | `defa3090-47e4-…` |
| `name` | Informe Mensual - TG GOCTA | Informe Mensual - TG PUMARINRI |

Lo demás (formato, página, márgenes, `timewindow`, `state`, zona, logos, pie) es idéntico. **El único defecto funcional es el `dashboardId`.** Observación aparte: la plantilla del Medidor titula "Tablero General" (nombre inconsistente, F49) y la de Piscina no tiene `dataSources[0].type` (no relevante).

El campo "usuario" de la plantilla (`userId`) es `null` en las 4; el usuario se define en el planificador.

## 4. Usuario del planificador (`12fff710…`)

- **El repo no puede identificarlo.** El Version Control no exporta usuarios: no hay carpeta `user/` ni usuarios en `hierarchy/` (los archivos de `groups/user/` son solo los grupos; `groupEntities: true` es una bandera, no una lista de miembros). `grep` de `12fff710`/`f2b383a0` encuentra únicamente los 4 planificadores.
- **Corrección a mi triage:** el triage supuso que era el administrador GONEX (ADM-01). La UI muestra `romelvalqui.r@gmail.com` como usuario del planificador, así que `12fff710…` es la cuenta de Romel (creada el 2026-10-09 18:56 Lima, durante la capacitación; por el UUID). Si es usuario del tenant o de un customer lo debe confirmar Erick en la UI: el repo no lo dice.
- Historial: hasta el 2026-10-10 los 4 planificadores usaban `f2b383a0-26d0-…` (usuario creado el 2026-03-23, anterior a la plataforma actual). El cambio a `12fff710…` entró en `0b0561a` ("estado tras alta de customer y usuarios por Romel"). No sé quién era `f2b383a0` ni si sigue existiendo.
- **Qué significa el campo "usuario"** (a partir de la documentación de ThingsBoard PE, de memoria, **no verificada aquí**): es el usuario **en cuyo nombre se genera** el informe (con sus permisos se abre el dashboard); no es el destinatario. Los destinatarios son los `targets`. Consecuencia práctica: si ese usuario se desactiva o pierde acceso al dashboard, el informe falla aunque los targets sean correctos. Verificar el texto de ayuda del campo en la UI.

## 5. Cruce planificador ↔ dashboard ↔ target

El target de la UI viene de Erick (el repo no lo exporta). Para Gocta, Tucán y Piscina asumo el patrón del nombre; **confirmar en la UI**.

| Planificador | Plantilla | Dashboard (dueño) | Usuario | Targets (UI) | Customer del target | ¿Coincide? |
|---|---|---|---|---|---|---|
| `c72d8880` TG GOCTA | `900138f0` | `e844d080` (Gocta) | Romel | **verificar** (esperado: Gocta + Tenant administrators) | Gocta | verificar |
| `a6773ef0` Piscina | `94757860` | `cc2cad90` (Gocta) | Romel | **verificar** (esperado: Gocta + Tenant administrators) | Gocta | verificar |
| `c967cba0` Medidor | `258ddba0` | `0469dc30` (Tucán) | Romel | **verificar** (esperado: Tucán + Tenant administrators) | Tucán | verificar |
| `8bee5690` TG PUMARINRI | `defa3090` | `32131e90` (**inexistente**; el actual es `8e373390`, Pumarinri) | Romel | "Gocta Andes Lodge" + "Tenant administrators" (UI) | **Gocta** | **NO**: el informe de Pumarinri va a los usuarios de Gocta |

**Desajuste confirmado en Pumarinri.** Dos defectos distintos:
1. La plantilla apunta a un dashboard que ya no existe.
2. El destino es el target de Gocta (heredado de cuando TG Pumarinri era una instalación de Gocta). Cuando el dashboard se corrija, **los usuarios de Gocta recibirían el consumo de Pumarinri** y los usuarios de Pumarinri no recibirían nada. Eso rompe la regla de no mezclar customers.
No hay target de Pumarinri, así que hay que crearlo (sección 8).
Con el dashboard actual inexistente, lo que reciben hoy los usuarios de Gocta el día 1 es [NO VERIFICABLE]: un informe vacío o con error con la marca de Sunkuu. **Mirar en la UI el informe del 2026-10-01 de Pumarinri** (y a quién llegó).

## 6. Otras referencias a targets de customer o a TG PUMARINRI

Búsqueda en todo el repo (excepto `.git`):
- **Targets `6c645f60` / `7b0fdda0`:** aparecen solo en sus propios archivos. Ninguna `notification_rule`, `scheduler_event` ni otra entidad los referencia (consistente con el export lossy de la sección 1; no excluye referencias en la UI).
- **`notification_rule` (11, todas `enabled: false`):** usan solo `ff6d6080` (Tenant administrators), `ff6e23d0` (entity owner) y `ff6e71f0` (affected user). Ninguna menciona customers, TG PUMARINRI ni `32131e90`.
- **`32131e90`:** aparece en `report_template/defa3090` (activo), `widget_type/d88440c0` (Exportación, `DASH_TO_INST`; lo corrige el apply de R0, pendiente) y `widget_type/afc86b80` (copia DEV, no se toca). Ya no aparece en `dashboard/`, `groups/`, Piscina ni 3EM.
- **"Pumarinri" / `8e373390`:** dashboard actual, grupo `b9410100`, customer, dispositivo `717ae5e0`, y los 4 widgets (arrays).
- Texto residual: la descripción del target de Gocta cita TG PUMARINRI.

## 7. Usuarios por customer

**No verificable desde el repo:** no se exportan usuarios (ver sección 4). Solo se ve que cada customer tiene sus grupos "All", "Customer Users" y "Customer Administrators" (Gocta, Pumarinri, Tucán y Apu Samay). El email `amazonlodgepumarinri@gmail.com` aparece en `customer/a2202a70…` (email del customer) y en el JS de Flota, pero **ningún archivo muestra un usuario con ese correo**.
Qué mirar en la UI: Customers → PUMARINRI AMAZON LODGE → Users: cuántos hay y si existe uno con `amazonlodgepumarinri@gmail.com`; lo mismo con Gocta, Tucán y Apu Samay. Importante: un target `CUSTOMER_USERS` envía a los **usuarios** del customer (su email de usuario), no al email del customer.

## 8. Ventana de tiempo (solo descripción)

- Las 4 plantillas piden una captura PNG del dashboard con un `timewindow` de **30 días** (`timewindowMs` 2.592.000.000 ms, AVG, intervalo 2 h), `useDashboardTimewindow: false` y zona `America/Lima`.
- Los widgets (3EM, Piscina) **no leen el `timewindow`** del dashboard: calculan "hoy", "ayer", semana y proyección desde la medianoche del navegador en el momento de renderizar (`todayStart()`, 3EM L80, Piscina L73). Es decir, lo que se ve en el PDF es el estado del widget al renderizar, no los 30 días de la plantilla. Descripción solamente; no se propone ningún cambio de contenido.

## 9. Lo que el repo no puede verificar (mirar en la UI)

| # | Qué mirar |
|---|---|
| 1 | Los 4 planificadores: Targets y "Notification template" de cada uno (el export los muestra como `null`). Confirmar que Gocta/Piscina → Gocta, Medidor → Tucán, Pumarinri → Gocta (como indicó Erick). |
| 2 | El usuario de cada planificador y su ayuda (¿"generar en nombre de"?). ¿`12fff710…` es del tenant o de un customer? ¿Qué era `f2b383a0…`? |
| 3 | Informes → historial del 2026-10-01: de los 4, a quién se notificó (campana/correo), y el de Pumarinri (¿error, vacío?). |
| 4 | Si el correo lleva el PDF adjunto o un enlace (`attachReport: false` en el export). |
| 5 | Usuarios por customer; existencia de `amazonlodgepumarinri@gmail.com` en el customer Pumarinri. |
| 6 | Si algún target o regla adicional se creó después del 2026-05-05 y no figura en el repo (el export de notificaciones es fiable solo para targets, plantillas y reglas, no para planificadores). |

## 10. Propuesta mínima para Pumarinri — pasos manuales en la UI (sin código)

1. **Plantilla.** Informes → Plantillas → "Informe Mensual - TG PUMARINRI" (`defa3090`): cambiar el componente Dashboard de "TG PUMARINRI" viejo a **TG PUMARINRI** (`8e373390`). Guardar. (El título del encabezado ya dice "TG Pumarinri".)
2. **Target nuevo.** Notificaciones → Destinatarios → Añadir: nombre "PUMARINRI AMAZON LODGE", tipo Usuarios de la plataforma → "Usuarios del cliente" → customer PUMARINRI AMAZON LODGE. Descripción: "Usuarios del cliente PUMARINRI AMAZON LODGE — reciben informe de TG PUMARINRI".
3. **Planificador.** Planificador → "Informe Mensual TG PUMARINRI" (`8bee5690`): en destinatarios quitar "Gocta Andes Lodge" y añadir "PUMARINRI AMAZON LODGE"; dejar "Tenant administrators" y la plantilla "Report generated notification". Dejar el usuario como está (Romel). Guardar.
4. **Target de Gocta.** Editar la descripción de "Gocta Andes Lodge" para quitar "TG PUMARINRI" (queda "…reciben informes de TG GOCTA y Piscina Temperada").
5. **Comprobar** antes del 2026-11-01 08:00: que Pumarinri tiene al menos un usuario con correo válido (sección 7), que la plantilla se genera a mano desde Informes (vista previa con el dashboard nuevo) y que el planificador muestra los destinatarios correctos.
6. **Registro.** Es configuración en la UI que **el Version Control no exporta** (sección 1): anotarla en el CHANGELOG/`config/` (o dejar un documento de captura de pantalla), porque el repo no la reflejará.

(Se omite deliberadamente cualquier cambio a Gocta, Tucán o a los widgets. Los pasos 1–4 son los de P-1 del CHANGELOG, ampliados con el target y el destino.)
