# Propuesta de arquitectura: alta de clientes automatizada y template Shelly Pro EM-50

| | |
|---|---|
| **Fecha** | 2026-10-11 |
| **Base analizada** | `../sunkuu-tb-config` HEAD `873bcd7` (auto-commit 2026-10-10 18:12 Lima). Rango desde `fd69cad`: 13 commits |
| **Versión de referencia** | ThingsBoard PE 4.3 (`tb-pe-node:4.3.0PE` según `docs/sunkuu-TB-contexto.md`) |
| **Método** | Lectura estática del repo y de la documentación oficial pública. Sin llamadas a 360.sunkuu.com ni a thingsboard.gonex.pe |
| **Extracciones** | `qa/extract/head/` (HEAD) y `qa/extract/fd69cad/` (base), generadas con `qa/scripts/extract_widgets.py --include-dev` (carpeta ignorada por git) |

> **Nota de corrección (2026-10-11, base `71f1603`).** Este informe se escribió sobre `873bcd7`. El resto del texto no se modificó.
> - **Propietario de `717ae5e0`.** Es PUMARINRI AMAZON LODGE (`a2202a70`), no el tenant. Erick lo confirmó en producción y sus usuarios ven solo su data. La versión manual `71f1603` lo ubica en `hierarchy/a2202a70…/device/` [Repo]. El informe lo daba como del tenant (A.5.2 y resumen, punto 1) porque el cambio de propietario no generó auto-commit.
> - **Entidades eliminadas.** `71f1603` (versión manual Overwrite) eliminó 43 entidades [Repo]: el dispositivo `cf7ddac0`, el dashboard viejo `32131e90`, los dashboards de prueba (TG PRUEBA, Prueba con Romel, Hotel Prueba, Erick Prueba, Gonex) y los customers de prueba. Quedan 4 customers: Gocta, Tucán, Pumarinri y APU SAMAY. El grupo de Gocta ya no incluye `32131e90`. El widget "Sunkuu — Template 3EM DEV" sigue existiendo, pero sin dashboard.
> - **Siguen vigentes.** A3-1, A3-2, A3-3 y A3-5 se corrigen en R0 (`widgets/work/R0/`). La plantilla `defa3090` y el planificador `8bee5690` siguen apuntando a `32131e90`; Erick los corrige desde la UI antes del 2026-11-01.
> - **Restricción de licencia.** ThingsBoard PE plan Pilot: 100 dispositivos, 100 activos y 1 instancia de producción. El Nivel 1 usa 1 activo por instalación. Hoy el repo tiene 6 dispositivos y 0 activos [Repo], así que hay margen. Los dispositivos espejo de un tenant de desarrollo (entorno decidido, por implementar) cuentan para el límite de dispositivos.

**Etiquetas.**
- **[Repo]**: verificado en `sunkuu-tb-config` (archivo o commit).
- **[Doc]**: verificado en documentación oficial (URL en el Anexo).
- **[Supuesto]**: requiere prueba en la instancia.

La documentación REST citada como [Doc] proviene del cliente REST oficial de ThingsBoard PE en GitHub (rama `master`, generado desde el Swagger). Las rutas pueden variar levemente frente a 4.3.0, así que cada endpoint debe confirmarse en el Swagger de nuestra instancia antes de implementar.

---

## 1. Resumen ejecutivo

1. **Riesgo en producción hoy (urgente, Correctivo).** El alta de Pumarinri del 2026-10-10 dejó defectos:
   - El dispositivo nuevo `717ae5e0` se exportó como propiedad del **tenant**, no del customer [Repo]. Si sigue así, un usuario de Pumarinri no puede leer su telemetría [Supuesto, verificar].
   - El dropdown de **Piscina** sigue ofreciendo a los usuarios de Gocta el "TG Pumarinri" viejo [Repo].
   - El informe mensual de Pumarinri apunta al dashboard viejo [Repo].
   - El histórico del dispositivo eliminado probablemente se perdió: desde 3.7 el *housekeeper* borra la telemetría de las entidades eliminadas [Doc]. Lo correcto era **"Cambiar propietario"**, que conserva el UUID.
2. **Nivel 1, "Alivio" (viable, recomendado ya).** Un registro de instalaciones como **Activos** (perfil "Instalación", propiedad del customer y atributos con dispositivo, dashboard y tipo), leído por los 4 widgets con la Entity Data Query API (`POST /api/entitiesQuery/find`) [Doc].
   - Elimina el paso 6: cero edición de código y cero UUIDs en el JS.
   - Corrige de paso F14/F15: sin PII en el código y con *fail-closed*.
   - La visibilidad para usuarios de customer **requiere prueba** [Supuesto].
   - Esfuerzo probable: **24 h**.
3. **Nivel 2, "Alta en pocos clics" (viable con límites).** Un widget asistente para el administrador del tenant, que usa el JWT de la sesión y endpoints documentados [Doc].
   - Crea el customer, el usuario (con enlace de activación), el dispositivo (precreado con el nombre exacto del Shelly), el dashboard desde plantilla, el grupo y su compartición, el tablero predeterminado y el registro.
   - Lo que **no** automatiza: la configuración MQTT del equipo físico, la verificación del primer dato y la entrega del enlace al cliente.
   - Recomiendo el widget antes que n8n.
   - Esfuerzo probable: **40 h**, después del Nivel 1.
4. **Template Pro EM-50 (viable).** El perfil, la integración y el converter **ya existen** desde la baseline [Repo]: las notas previas estaban equivocadas.
   - No hay ningún dispositivo EM-50 en el repo [Repo]. Hay que confirmar que publican a Mosquitto con `status_ntf` activo [Doc/Supuesto].
   - El template conviene derivarlo del 3EM **después** de corregir F01–F05/F27/F50 y del Nivel 1.
   - Esfuerzo probable: **27 h**.
5. **Pedidos de Romel.**
   - Pantalla completa: es **configuración** de usuario, no código.
   - Selector de fecha: es código, en 6 gráficas (Evolutivo, 16 h).
   - Filtro cliente → instalación en Exportación: 5 h, o 3 h si se hace con el Nivel 1.
6. **Orden recomendado:** remediación de Pumarinri → Nivel 1 (+ filtro de Exportación) → QA del 3EM + selector de fecha → Pro EM-50 → Nivel 2. Hacerlos juntos ahorra unas **12–19 h**.

---

## 2. Sección A: qué cambió desde `fd69cad`

### A.1 Commits del rango (hora de Lima)

| Hash | Autor | Fecha Lima | Entidad tocada | Interpretación |
|---|---|---|---|---|
| `be9e7ea` | Romel Valqui | 10-10 16:22 | dashboard `c03526e0` "Prueba con Romel" (A) | Dashboard de prueba de la capacitación. Sin estados ni widgets [Repo] |
| `60d9ad6` | GONEX TENANT | 16:49 | device `717ae5e0` `shellypro3em-e08cfe972040` (A) | Dispositivo nuevo de Pumarinri, ver A.6 |
| `540a581` | GONEX TENANT | 16:57 | dashboard `8e373390` (A) | Copia de "TG GOCTA" (título y CFG aún de Gocta) |
| `cd42c04` | GONEX TENANT | 16:58 | dashboard `8e373390` (M) | Título → "TG PUMARINRI" |
| `75dded7` | GONEX TENANT | 17:01 | dashboard `8e373390` (M) | CFG `d` → `717ae5e0`, `n` → "TG PUMARINRI" |
| `3223be9` | GONEX TENANT | 17:05 | grupo de dashboards `b9410100` "PUMARINRI AMAZON LODGE" (A) | Grupo propiedad del tenant |
| `0b64644` | GONEX TENANT | 17:37 | widget Portal de Flota (M) | Arrays: alta de Pumarinri y baja de 3 entidades de prueba |
| `505c3b3` | GONEX TENANT | 17:52 | widget Template 3EM (M) | NAV: alta de Pumarinri y baja de 3 entidades de prueba |
| `711dace` | GONEX TENANT | 17:54 | dashboard `8e373390` (M) | Nombre del estado → "TG PUMARINRI" |
| `0c19f1a` | GONEX TENANT | 17:56 | widget Template Piscina (M) | NAV: alta de Pumarinri y baja de pruebas (**no** se quitó el Pumarinri viejo) |
| `457775c` | GONEX TENANT | 18:03 | widget Centro de Exportación (M) | INSTALLATIONS y CUSTOMER_MAP |
| `3e7f328` | GONEX TENANT | 18:10 | widget Template 3EM (M) | **2.º guardado**: quitar el Pumarinri viejo olvidado |
| `873bcd7` | GONEX TENANT | 18:12 | widget Portal de Flota (M) | **2.º guardado**: quitar el Pumarinri viejo olvidado |

**Lo que no aparece en el rango.**
- **Customer.** "PUMARINRI AMAZON LODGE" (`a2202a70`) se creó antes, en `eff4779` (Romel, 2026-10-09 21:45 Lima) [Repo].
- **Apusamay.** "APU SAMAY NATURE LODGE" (`686e4250`) entró en `0b0561a` (VC-02) [Repo].
- **Usuarios, grupos de usuarios y permisos.** El auto-commit no escribe `hierarchy/` (Pumarinri no tiene carpeta `hierarchy/a2202a70…`) ni los `_entities.json` de grupos (`b9410100` no lo tiene) [Repo]. **No se puede verificar desde el repo** a quién se compartió el grupo ni qué dashboards contiene.

**Duración.** El alta de Pumarinri tomó **83 min** (16:49 → 18:12), de los cuales **35 min** fueron solo la edición de arrays (17:37 → 18:12), con **6 guardados de widget** [Repo].

### A.2 Cambios de código en los 4 widgets (diff `fd69cad` → HEAD)

Solo cambió `controllerScript`; el HTML y el CSS quedaron iguales [Repo: `diff` de `qa/extract/fd69cad` contra `qa/extract/head`].

| Widget | Arrays editados | Altas | Bajas | Campos por alta |
|---|---|---|---|---|
| Portal de Flota | `CUSTOMERS`, `INSTALLATIONS` | 1 customer + 1 instalación | Hotel Prueba, Erick Prueba, Gonex (customers e instalaciones) y el Pumarinri viejo | 8 (customer) + 7 (instalación) = **15** |
| Template 3EM | `NAV` | 1 | 3 de prueba y el Pumarinri viejo | **3** (`n`, `d`, `c`) |
| Template Piscina | `NAV` | 1 | 3 de prueba (el Pumarinri viejo **no**) | **3** |
| Centro de Exportación | `INSTALLATIONS`, `CUSTOMER_MAP` (`DASH_TO_INST` **no**) | 1 instalación (se reutilizó el bloque de "Gonex") | El Pumarinri viejo y Gonex | 5 + `devices[{id,name}]` + bloque `varGroups` de 25 variables (≈ 30 líneas) + 2 en `CUSTOMER_MAP` = **≈ 9 campos + 30 líneas** |
| Dashboard `8e373390` (CFG) | `<!--CFG:{d,t,n}-->` | | | **3** |

**Total por alta (caso Pumarinri):**
- **7 lugares en 5 objetos** (4 widgets + 1 dashboard).
- **≈ 33 campos** tecleados y ≈ 30 líneas copiadas.
- **10 UUIDs pegados a mano**: customer ×4, dispositivo ×3, dashboard ×3. Debieron ser 11, porque falta `DASH_TO_INST`.

### A.3 Integridad

**Sintaxis.** `node --check` pasa (OK) en los 5 JS extraídos: 3EM, Piscina, Flota, Exportación y 3EM DEV [Repo].

**Existencia de UUIDs.** Todos los UUID citados en los widgets existen como archivo en el repo [Repo]. Esto **no prueba** que existan en producción: el auto-commit no registra eliminaciones (ver A.6.1). En particular, `cf7ddac0` sigue en el repo aunque Romel lo eliminó.

**Coherencia entre widgets (HEAD):**

| Instalación | Flota | 3EM NAV | Piscina NAV | Export INSTALLATIONS | Export DASH_TO_INST | Export CUSTOMER_MAP |
|---|---|---|---|---|---|---|
| TG Gocta (`e844d080`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (Gocta) |
| Piscina Temperada (`cc2cad90`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Medidor Tablero Principal (`0469dc30`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (Tucán) |
| TG Pumarinri **nuevo** (`8e373390`) | ✓ | ✓ | ✓ | ✓ | **✗ falta** | ✓ |
| TG Pumarinri **viejo** (`32131e90`, dispositivo eliminado) | — | — | **✗ sigue (L611)** | — | **✗ sigue (L236)** | — |
| TG Gonex (`fe900bc0`, prueba) | — | — | — | — | **✗ sigue (L239)** | — |

**Defectos detectados [Repo]:**

| # | Defecto | Ubicación | Efecto | Severidad |
|---|---|---|---|---|
| A3-1 | Entrada huérfana "TG Pumarinri" → `32131e90`, customer Gocta | Piscina JS L611 | Los usuarios de Gocta ven en el dropdown de Piscina un "TG Pumarinri" que lleva a un dashboard cuyo dispositivo ya no existe. Además hay 2 entradas con el mismo nombre para el tenant | **Alta** (visible para el cliente Gocta) |
| A3-2 | `DASH_TO_INST` sin `8e373390`, con `32131e90` y `fe900bc0` huérfanos | Export JS L234–240 | Al ir de "TG PUMARINRI" a Exportar, el administrador del tenant no tiene la instalación preseleccionada (queda Gocta). Para el usuario de Pumarinri no se nota (solo ve la suya) | Media |
| A3-3 | `letter:'T'` y color de Tucán copiados | Flota JS L58–60 | El avatar de Pumarinri muestra "T" con el color de Tucán | Cosmética |
| A3-4 | Ids `'Pumarinri'` con mayúscula (convención distinta) y dispositivo rotulado `'Pumarinri'` | Flota L56, L70; Export L168, L174 | Funciona, pero rompe la convención y F49 (nombres inconsistentes: dispositivo "TG-Pumarinri", dashboard "TG PUMARINRI", Flota "TG Pumarinri") | Cosmética |
| A3-5 | Texto fijo "de 2 clientes" | Flota JS L341 | Ahora hay 3 clientes reales (F07/F38) | Cosmética |
| A3-6 | *Fail-open* (F15) sigue activo y ahora expone más | Flota L241–249 (`custObj=null`), Export L229–231 | Los 3 customers de prueba se quitaron de los arrays, pero **siguen teniendo compartidos** Flota y Exportación (grupos `457f6690`, `b45c5750`, `b1c37be0`). Sus usuarios ven **todas** las instalaciones reales, Pumarinri incluida | Media (usuarios de prueba; hay uno con email `hotelprueba@test.com`) |
| A3-7 | Dashboard viejo `32131e90` sigue en los grupos de Gocta (`e044b8d0`) y de Hotel Prueba (`b45c5750`), con CFG → `cf7ddac0` | `groups/dashboard/*_entities.json`, `dashboard/32131e90…` | Si no se eliminó en producción, Gocta ve en su lista un "TG PUMARINRI" vacío | Alta [Supuesto: depende de si existe en producción] |
| A3-8 | "Informe Mensual - TG PUMARINRI" (`defa3090`) y su scheduler `8bee5690` apuntan a `32131e90` | `report_template/defa3090…`, `scheduler_event/8bee5690…` | El 1 de noviembre se generaría un informe del dashboard viejo, roto o vacío (además de F08/F09) | Alta |
| A3-9 | La baja de las entidades de prueba de los arrays (avance parcial de F07) **no está en `CHANGELOG.md`** | — | Pérdida de trazabilidad | Proceso |
| A3-10 | Copia DEV: el NAV conserva `32131e90` y los 3 dashboards de prueba; el bloque `// DEV-ONLY (FEAT-01)` está presente (L1087) | 3EM DEV JS L1198–1204 | Solo afecta al dashboard TG PRUEBA. El resto del JS es idéntico a producción salvo el bloque DEV-ONLY | Baja |
| A3-11 | La integración 3EM sigue listando la relación `ManagedByIntegration → cf7ddac0` | `integration/1d4d1880…` `relations[1]` | Export desactualizado (la integración no se reexportó). Confirma que el repo no refleja las eliminaciones | Informativa |
| A3-12 | Apusamay (`686e4250`) sin dispositivos, sin grupo de dashboards y fuera de los arrays | `hierarchy/686e4250…` (sin `device/`) | Alta incompleta, esperable mientras no lleguen los Pro EM-50 | Informativa |

### A.4 Mapa del dolor (alta actual)

| Paso | Qué se toca | Datos copiados a mano | Errores probables (observados ✱) |
|---|---|---|---|
| 1. Customer y usuarios | Customer, usuario, activación | Nombre, email, ciudad | Ciudad o nombre inconsistentes con Flota (F49) ✱ ("Bongará" frente a "Chachapoyas") |
| 2. Dispositivo y credenciales MQTT | Dispositivo (por autoaprovisionamiento o creación manual), propietario | Nombre exacto del Shelly | Dispositivo propiedad del tenant ✱; renombrar el `name` crea un duplicado [Doc]; eliminar en vez de "Cambiar propietario" ✱ |
| 3. Dashboard de la instalación | Copiar el dashboard y editar `cardHtml` (`<!--CFG-->`) | 3 (UUID del dispositivo, tarifa, nombre) | Copia con título y estado aún de Gocta ✱ (3 guardados para corregirlo); UUID equivocado |
| 4. Grupo de tableros y asignación | Grupo de dashboards, agregar dashboard, compartir con el grupo de usuarios del customer | Selección en la UI | Dashboard compartido con el customer equivocado (F16 ✱ histórico) |
| 5. Tablero predeterminado | Usuario → Tablero predeterminado y "Siempre pantalla completa" | Selección | Romel pierde el menú (ver E.1) |
| 6. Arrays en 4 widgets | Flota (2 arrays), 3EM (1), Piscina (1), Exportación (3) | ≈ 33 campos, ≈ 30 líneas y 10 UUIDs | Olvido de bajas ✱ (×3), olvido de un mapa ✱ (`DASH_TO_INST`), copiar y pegar letra y color ✱, error de sintaxis que tumba el widget para **todos** los clientes (riesgo, no observado) |
| 7. Verificación en incógnito | Iniciar sesión como cliente | — | Solo detecta lo visible para ese cliente. No detecta los efectos sobre **otros** clientes (A3-1 lo sufre Gocta, no Pumarinri) |

### A.5 Reestructuración de Pumarinri: verificación

#### A.5.1 ¿El auto-commit registra eliminaciones?

**No.** El archivo `hierarchy/79efbf60…/device/cf7ddac0-2eeb-11f1-a6d8-33f75efe8b97.json` (dispositivo eliminado, customer Gocta, `ownerId` = Gocta) **sigue en el repo** en HEAD [Repo].

- La eliminación fue anterior a 16:49, porque el nombre del dispositivo es único por tenant [Doc: `saveDevice`, "Device name is unique in the scope of tenant"] y el nuevo, con el mismo nombre, se creó a esa hora.
- Ninguno de los 12 commits posteriores lo borra [Repo].
- Coincide con el issue oficial #15134 (TB Cloud 4.3.1.3): "The dashboard is deleted in Thingsboard, but the file in the git repository remains" [Doc].
- Matiz: `hierarchy/` solo lo escriben las versiones manuales completas. Queda por probar si una versión manual del tipo DEVICE elimina el archivo [Supuesto].

**Propuesta para CLAUDE.md (sin editar todavía).** Reemplazar "Pendiente de confirmar: si las eliminaciones generan commit" por: "Las eliminaciones **no** generan commit: el archivo queda en el repo (evidencia: `cf7ddac0` tras `60d9ad6`, issue thingsboard#15134). Toda eliminación debe anotarse en `CHANGELOG.md`".

#### A.5.2 ¿Por qué `717ae5e0` tiene `customerId` nulo?

**Evidencia [Repo] (`device/717ae5e0…json`, commit `60d9ad6`):**
- `customerId` = `13814000-1dd2-11b2-8080-808080808080`, que es el UUID nulo de ThingsBoard.
- `ownerId: null`.
- El archivo está en `device/` (nivel tenant), no en `hierarchy/<customer>/device/` como los dispositivos de customers.
- `relations: []`: no tiene la relación `ManagedByIntegration` que sí tenía `cf7ddac0`.
- `attributes` vacíos.
- `label: "TG-Pumarinri"` ya presente en el primer y único commit.

**Interpretación:**
- El dispositivo quedó **propiedad del tenant** y no se asignó al customer **por propietario**.
- Tampoco consta una asignación **por grupo**: el auto-commit no exporta la pertenencia a grupos de dispositivos.
- Que tenga `label` desde el primer commit, autor "GONEX TENANT" y ninguna relación con la integración sugiere que se **creó a mano desde la UI** con el nombre exacto del Shelly, y que luego la integración lo encontró por nombre [Doc: "On every uplink ThingsBoard looks up the entity by deviceName"]. No parece autoaprovisionado [Supuesto].
- No hay commit posterior de "Cambiar propietario". O no se hizo, o ese cambio no dispara auto-commit [Supuesto].

**¿Lo ve un usuario de Pumarinri?**
- El rol "Customer User" (`79f4a160`) es **GENERIC** con `ALL: READ, READ_TELEMETRY…` [Repo].
- Según la documentación, un rol genérico de customer da acceso "only within that customer and its sub-customers" [Doc RBAC].
- Por tanto, si el dispositivo es del tenant, el usuario de Pumarinri **no puede leer su telemetría**, salvo que su grupo de usuarios tenga compartido un **grupo de dispositivos** que lo contenga [Supuesto].
- Síntoma esperado: dashboard con "—" y 403 en la consola.

**Verificación (Erick, 2 min):**
1. Dispositivos → columna "Propietario" de `shellypro3em-e08cfe972040`.
2. Abrir TG PUMARINRI con un usuario de Pumarinri en incógnito.

#### A.5.3 Referencias huérfanas

Ver A3-1, A3-2, A3-7, A3-8, A3-10 y A3-11. Resumen de los UUID viejos:

| UUID viejo | Dónde sigue [Repo] |
|---|---|
| Dispositivo `cf7ddac0` | Dashboard `32131e90` (CFG), integración 3EM (relación) y `hierarchy/` (archivo). **Ya no** en arrays de widgets ni en la copia DEV (que ahora lee `c636fa00`) |
| Dashboard `32131e90` | Piscina NAV (L611), Export `DASH_TO_INST` (L236), 3EM DEV NAV (L1199), grupos de dashboards Gocta y Hotel Prueba, report_template `defa3090` |

#### A.5.4 Telemetría al eliminar y procedimiento correcto

- **Al eliminar un dispositivo:**
  - Hasta 3.1, la telemetría quedaba huérfana en `ts_kv` [Doc: blog 2020].
  - Desde **3.7**, el servicio de *housekeeping* "removes old alarms, attributes, and telemetry records for entities deleted from the platform" [Doc: blog 3.7]. En `thingsboard.yml` (`queue.core.housekeeper`) las tareas `DELETE_TELEMETRY`, `DELETE_ATTRIBUTES` y `DELETE_ALARMS` están activas por defecto (`TB_HOUSEKEEPER_DISABLED_TASK_TYPES` vacío) [Doc].
  - En PE 4.3, salvo configuración distinta en el contenedor, **el histórico de `cf7ddac0` (marzo → octubre 2026) se borró** junto con sus atributos (tarifa y umbrales) y alarmas [Supuesto: confirmar la variable en `docker-compose`].
  - La telemetría no se puede restaurar desde el Version Control [Doc: issue #15134, "it won't work at all" para dispositivos].
- **Recuperación posible [Supuesto]:**
  - (a) Un respaldo de `gonex-postgres` anterior al 2026-10-10.
  - (b) Shelly Cloud, que sigue activo en paralelo [Repo: `docs/sunkuu-TB-contexto.md` L98–100]: exportar a CSV e importar con timestamp al dispositivo nuevo.
  - (c) La memoria interna del 3EM (EMData con registros de 60 s según la API Gen2 [Doc: patrón EM1Data]; la retención no está verificada).
- **"Cambiar propietario"** (`POST /api/owner/CUSTOMER/{ownerId}/{entityType}/{entityId}`, "Tenant/Customer changes Owner to Customer") **transfiere** la entidad [Doc]. La documentación no dice explícitamente que conserve el UUID, pero la operación actúa sobre el mismo `entityId`, no crea ni borra nada. Por tanto conserva UUID, telemetría, atributos, relación con la integración y alarmas [Supuesto, alta confianza; probar con un dispositivo de prueba].
- **Procedimiento correcto (el que debió seguirse):**
  1. Crear el customer Pumarinri (hecho).
  2. **Cambiar propietario** de `cf7ddac0` de Gocta a Pumarinri. No eliminar ni renombrar el `name`; el `label` sí se puede cambiar.
  3. Quitar `32131e90` de los grupos de Gocta y Hotel Prueba, y agregarlo al grupo de Pumarinri compartido con sus usuarios.
  4. En los widgets, cambiar solo el `c`/`customer` de las entradas existentes (con Nivel 1: nada).
  5. Report template y scheduler: sin cambios.
  6. Revisar las alarmas activas del dispositivo.

  Resultado: 0 UUID nuevos, historial intacto y 0 huérfanos.

---

## 3. Sección B: Shelly Pro EM-50

### B.1 Lo que hay en el repo

| Elemento | Estado [Repo] |
|---|---|
| Perfil "Shelly Pro EM50" | `device_profile/b75859d0…` desde la baseline `d58d79a`. **Sin** campos calculados (alarmas) ni dashboard por defecto |
| Integración "Sunkuu - Pro EM50 MQTT Integration" | `integration/e3980900…`, `enabled: true`, `mosquitto:1883` anónima. Tópicos `+/status/em1:0` (QoS 0), `+/status/em1:1` (QoS 1), `+/status/em1data:0` (QoS 0), `+/status/em1data:1` (QoS 1). `relations: []` |
| Converter "Shelly Pro EM50 - Uplink" | `converter/b69ff030…` (JS), `deviceType: 'Shelly Pro EM50'`, **sin filtro de prefijo** (F18) |
| Keys generadas | `voltaje_canal_N`, `corriente_canal_N`, `potencia_activa_canal_N`, `potencia_aparente_canal_N`, `factor_potencia_canal_N`, `frecuencia_canal_N` (de `em1:N`); `energia_canal_N`, `energia_ret_canal_N` (de `em1data:N`), con N ∈ {0, 1}. **Total: 16 keys**, ninguna "total" |
| Dispositivos | **Ninguno** en el repo: ni el "Caldero Piscina" de Gocta (`shellyproem50-441d6475fe58`, pendiente por WiFi según `README.md` L39 y el informe 02) ni los 2 de Apusamay |
| Dashboards | Ninguno. El CSS de Piscina dice "Caldero eliminado": la sección del caldero se retiró del widget |

**Conclusiones.**
- La nota "sin perfil ni converter" **es incorrecta**: el converter existe desde marzo.
- Que no haya ningún dispositivo indica que los EM-50 **no han publicado** en Mosquitto desde que se activó el auto-commit (2026-10-09). La creación de un dispositivo genera commit (caso `717ae5e0`) [Repo].
- Posibles causas [Supuesto]: MQTT no configurado en el equipo, o **`status_ntf` desactivado**. Su valor por defecto es `false`: sin él, el Shelly solo publica en `<id>/events/rpc`, que nuestra integración no escucha [Doc MQTT].

### B.2 Qué entrega el Pro EM por MQTT [Doc]

**Componentes.**
- `em1:0` y `em1:1` (EM1), `em1data:0` y `em1data:1` (EM1Data).
- Además `switch:0`: el equipo tiene una salida, que no usamos.
- "Single phase Energy Metering device", límite de 50 A por canal y 280 V.

**`EM1.GetStatus`, por canal:**

| Campo | Unidad |
|---|---|
| `current` | A |
| `voltage` | V |
| `act_power` | W |
| `aprt_power` | VA |
| `pf` | — |
| `freq` | Hz |
| `calibration` | — |
| `errors` | `power_meter_failure`, `out_of_range:*`, `ct_type_not_set` |
| `flags` | `overcurrent`, `undervoltage`, … |

**Voltaje y frecuencia.** Cada canal reporta su propio `voltage` y `freq`. La documentación no dice si son una medición común. Físicamente el equipo es monofásico con una entrada de tensión, así que ambos canales deberían coincidir [Supuesto]. Propuesta: mostrar un solo voltaje (canal 0) y alertar si difieren más de un 2 %.

**`EM1Data.GetStatus`, por canal.** `total_act_energy` y `total_act_ret_energy` en **Wh**, "perpetual counters" que se guardan en flash, reiniciables con `EM1Data.ResetCounters`. **No hay contador total** del equipo.

**Publicación.**
- Tópico `<topic_prefix>/status/<component>:<id>` con `status_ntf=true`. El prefijo por defecto es el ID del equipo; en nuestro inventario, `shellyproem50-<mac>` [Repo `README.md`].
- Se publica "if a significant change occurred": **no es periódico**.
- Existe `<id>/online` (LWT) para detectar desconexiones.

**Comparación con el converter del 3EM [Repo]:**

| | Pro 3EM (`df3eb870`) | Pro EM-50 (`b69ff030`) |
|---|---|---|
| Unidades | 3 fases (a/b/c) | 2 canales (0/1), monofásico |
| Mensajes | `em:0` (todo junto), `emdata:0` | Un mensaje por canal: `em1:0`, `em1:1`, `em1data:0`, `em1data:1` |
| Potencia total | `potencia_activa_total`, `potencia_aparente_total` (del equipo) | No existe: hay que sumar |
| Energía total | `energia_total` (`total_act`, Wh) | No existe: `energia_canal_0` + `energia_canal_1` |
| Voltaje | Por fase | Por canal (probablemente igual) |
| Frecuencia | No se guarda (F41) | `frecuencia_canal_N` |
| Unidades de energía | Wh | Wh (igual: se reutiliza el `/1000`) |

**Riesgos de ingesta.**
- (a) Al no publicar de forma periódica, una carga apagada puede dejar al dispositivo "inactivo" y disparar falsas alarmas de "Dispositivo desconectado" [Supuesto]. Propuesta: suscribir `+/online` → atributo `online` y basar la alarma en ese atributo.
- (b) Un mensaje por canal: los timestamps de los canales 0 y 1 no coinciden, así que las sumas instantáneas deben usar el último valor de cada canal y no buscar pares por timestamp.
- (c) Agregar el filtro `shellyproem50-` al converter (F18).

### B.3 Reutilización del Template 3EM

| Se reutiliza tal cual | Se adapta | Nuevo |
|---|---|---|
| Estructura, encabezado, marca, nav, PDF (jsPDF), lista de alarmas, panel de configuración (con F45), `api()`/`tsUrl()`, curva de demanda de FEAT-01 (medianoche de Lima, resolución, huecos) | "Fases A/B/C" → "Circuito 1/2" (vista Total · Circuitos · Todo); KPIs de energía y costo por circuito; un solo voltaje con aviso de discrepancia; FP total = ΣP/ΣS (con el criterio de F25); cálculo de "Energía hoy" con la función corregida de F01 aplicada a cada contador | Nombres de circuito por atributo; modo de total; tarjeta por circuito con estado (encendido si `act_power` > umbral) |

**¿Tiene sentido un "Total"?**
- Si los 2 canales son cargas independientes (por ejemplo, bomba de calor y bomba de recirculación), la suma **no es el consumo de la instalación**, solo el de las cargas medidas.
- Sí sirve para el costo agregado y la proyección.
- Propuesta: atributo `modo_total` = `suma` (por defecto; rotular "Suma de circuitos medidos", nunca "Consumo total") o `ninguno` (oculta la vista Total y los KPIs agregados).
- Atributo `circuito_N_activo` (booleano) para equipos con un solo TC instalado.

**Nombres configurables por Sunkuu, sin código.**
- Atributos `SERVER_SCOPE` en el dispositivo (o en el Activo "Instalación" con Nivel 1): `circuito_0_nombre` ("Circuito 1" por defecto) y `circuito_1_nombre` ("Circuito 2" por defecto).
- Se editan desde Dispositivo → Atributos → "+" en la UI de ThingsBoard, o desde el panel de configuración del widget, que ya guarda atributos `SERVER_SCOPE` en el 3EM [Repo] (restringido al administrador del tenant, ver F45).
- Endpoint: `POST /api/plugins/telemetry/DEVICE/{id}/attributes/SERVER_SCOPE` [Doc].
- El `name` de `EM1.GetConfig` del Shelly no viaja en el `status`, así que no sirve como fuente [Doc].
- **Decisión de keys:** como **no hay histórico** de EM-50, este es el único momento en que renombrar keys (`_canal_0` → `_circuito_1`) es gratis. Recomiendo **mantener `_canal_N`** (ya documentado) y mapear la etiqueta en la UI.

### B.4 Integración con el resto

| Componente | Qué cambia | Con Nivel 1 |
|---|---|---|
| Portal de Flota | Tipo `proem`: kW = Σ `potencia_activa_canal_N`; kWh hoy = Σ Δ `energia_canal_N`; sparkline con `potencia_activa_canal_0`+`_1` (dos series o suma); salud según `online` | El tipo llega desde el registro, sin arrays |
| Exportación | Catálogo de variables por tipo `proem` (16 keys); badge "Pro EM · Monofásico · 2 circuitos" (hoy está fijo en "Pro 3EM · Trifásico" para todo lo que no sea Piscina, Export JS L268) | `VARS_BY_TYPE` en código (cambia solo si aparece un **tipo** de equipo nuevo); la lista de instalaciones sale del registro |
| Alarmas | Campos calculados en el perfil `b75859d0`: desconexión (atributo `online` o inactividad mayor que el umbral), tensión fuera de rango (leyendo `voltaje_min/max` de atributos, criterio F12) y sobrecorriente por canal (`alerta_a_max`) | — |
| PDF del widget | Reutilizar el del 3EM con 2 circuitos | — |
| Informe mensual | Depende de F08 (hoy el informe es una captura del dashboard y no sirve como mensual) | — |

### B.5 Dependencias con QA del 3EM

Hay que corregir **antes** de derivar; si no, el error se copia a un tercer widget (F24 ya reporta 3 implementaciones distintas de "energía hoy"):

| Prioridad | Hallazgos | Motivo |
|---|---|---|
| Imprescindible | F01, F02, F03, F04, F05, F27, F50 | Cálculo de energía y día en Lima: el Pro EM los aplica a 2 contadores |
| Muy recomendable | F21 (estado "En línea" fijo), F22 (datos obsoletos), F23 (JWT sin refresco), F25 (FP), F32 (PDF NaN) | Se heredan tal cual |
| Puede ir después | F12/F44 (umbrales de atributos frente a alarmas), F28 (rótulos), F31 (fugas) | No bloquean, pero conviene que el template nazca ya con un solo criterio |

Recomendación: extraer en el 3EM una **función común de energía por contador**, con baseline en 00:00 Lima y deltas positivos (F01/F50). El Pro EM la llama 2 veces.

---

## 4. Sección C: arquitectura del alta, matriz de viabilidad

**Hechos de partida [Repo].**
- Los dashboards no usan alias (`entityAliases` vacío en los 11). Todos los widgets son estáticos y leen por REST: el 3EM, de `ctx.settings.deviceId` o del CFG (JS L23–40).
- No existen Activos (solo el perfil `default`).
- Los clientes tienen 3 grupos de usuarios (All, Customer Users y Customer Administrators).
- El acceso a dashboards se da compartiendo grupos de dashboards del tenant con el rol de grupo "Entity Group Read-only User" (`35af70e0`).

**Sobre la limitación conocida ("no hay endpoint que liste los dashboards compartidos visibles para un customer").**
- Existe `GET /api/user/dashboards`, "Returns a page of Dashboard Info objects available for specified or current user" [Doc]. "Available for" sugiere que incluye los compartidos, pero la documentación no lo confirma [Supuesto, una prueba de 5 min].
- `GET /api/dashboards/all` devuelve solo los "owned by the tenant or the customer" [Doc], lo que explica la limitación observada.
- **ctx.http.** Exportación usa `ctx.http.get` con éxito (Export JS L532, L556, L651, L683) [Repo]. El 403 observado encaja con leer dispositivos fuera del alcance del rol (A.5.2), no con un fallo de `ctx.http` [Supuesto].

| Criterio | 1. Activos "Instalación" + Entity Data Query | 2. Registro en atributos (JSON en tenant o customer) | 3. Relaciones Customer → Instalación → Dispositivo / Dashboard | 4. Un dashboard por TIPO con estado |
|---|---|---|---|---|
| **Viabilidad** | Alta. `POST /api/asset?entityGroupId=` y `POST /api/entitiesQuery/find` con filtro `assetType` y `latestValues` ATTRIBUTE [Doc] | Alta técnica, baja operativa | Media. `POST /api/relation`, filtro `relationsQuery` [Doc]; relación con DASHBOARD no documentada [Supuesto] | Media. Alias "Entity from dashboard state" [Doc]; widgets estáticos a migrar [Repo] |
| **Permisos: usuario de customer** | Con el Activo **propiedad del customer**, el rol genérico Customer User (READ) debería devolver solo sus activos [Doc RBAC + Supuesto: probar que `entitiesQuery` filtra por permisos] | Atributos del tenant: el customer **no** puede leerlos [Supuesto] → habría que copiar el JSON por customer | `find_by_from`: "server checks that the entity is assigned to the same customer" [Doc] | El usuario podría manipular el estado y pasar el ID de otro dispositivo: la telemetría daría 403 por rol (como F15) [Supuesto] |
| **Permisos: tenant** | Ve todos los activos; el owner llega por `ownerId` | Lee todo | Lee todo | Lee todo |
| **Seguridad** | Sin PII ni UUIDs en el JS (resuelve F14); *fail-closed* natural: sin activos, lista vacía (resuelve F15) | PII fuera del código, pero un JSON editable a mano: un error deja sin datos a todos los clientes | Buena | Buena si el dispositivo es del customer |
| **Esfuerzo** | Medio (24 h, ver F) | Bajo (12 h) | Medio-alto (+8 h sobre la opción 1) | Alto (40–60 h + migración) |
| **Mantenimiento** | Alta = crear un activo desde la UI y llenar 4–6 atributos con selectores | Editar un JSON en un cuadro de texto: el mismo dolor del paso 6 en otro lugar | Crear relaciones a mano en la UI: tedioso | Muy bajo por instalación |
| **Migración** | Crear 4 activos (TG Gocta, Piscina, Medidor Tucán, TG Pumarinri); los dashboards se conservan; el CFG queda como respaldo | Trivial | Combinable con la opción 1 | Rehacer usuarios predeterminados, report templates (que hoy capturan un dashboard por instalación) y marcadores; el `defaultDashboardId` del usuario no lleva estado [Doc: campo de usuario] → el widget debe autoseleccionar la instalación |
| **Pasos del alta que elimina** | **6** completo; simplifica el 3 (sin CFG si el widget resuelve el dispositivo por `dashboardId`) | 6 (lo traslada) | 6 (lo traslada a la UI) | 3, 4 (solo se comparte una vez el grupo "Plantillas") y 6 |

**Recomendación.** **Opción 1** como Nivel 1, usando relaciones de la opción 3 solo si una instalación tiene varios dispositivos (Piscina) y el atributo resulta incómodo. La opción 4 queda como evolución posterior: con el registro de la opción 1 la migración se vuelve sencilla, porque el selector de instalación ya existe. La opción 2 no se recomienda.

**Diseño del Activo "Instalación" (Nivel 1).**

| Elemento | Detalle |
|---|---|
| Perfil de activo | "Instalación" |
| Propietario | El customer (alta: crearlo en el grupo del customer, o "Cambiar propietario") |
| Atributos `SERVER_SCOPE` | `tipo` (`3em` / `piscina` / `proem`) · `dashboard_id` · `dispositivos` (JSON `{"principal":"<uuid>"}` o, para Piscina, `{"cal":…,"ilu":…,"amb":…}`) · `etiqueta` · `ubicacion` · `orden` · `es_prueba` (booleano) |
| Lectura | Una sola llamada `POST /api/entitiesQuery/find` con `entityFilter: {type:"assetType", assetTypes:["Instalación"]}`, `entityFields` (`name`, `label`), `latestValues` ATTRIBUTE y `keyFilters` opcionales |
| Customers para Flota (tenant) | `GET /api/customerInfos/all` o `entitiesQuery` con `entityType: CUSTOMER` [Doc]; la letra y el color se derivan del nombre |
| Dispositivo del dashboard | El 3EM y Piscina buscan el Activo cuyo `dashboard_id` = dashboard actual (`keyFilter` EQUAL) → ya no hay que editar el CFG. El CFG queda como respaldo para la copia DEV |
| Tarifa | La tarifa sigue en `tarifa_kwh` del dispositivo (fuente única; principio de CLAUDE.md) |

---

## 5. Sección D: niveles de propuesta

### D.1 Nivel 1, "Alivio"

**Alcance exacto.**
1. Perfil de activo "Instalación" y 4 activos de producción, cada uno con su propietario y atributos. Se hace desde la UI y lo aplica Erick.
2. Módulo `loadInstallations()` (mismo código en los 4 widgets; ThingsBoard no comparte JS entre widgets sin `tb_resource`) que reemplaza:
   - Flota: `CUSTOMERS` e `INSTALLATIONS`.
   - 3EM y Piscina: `NAV`.
   - Exportación: `INSTALLATIONS` (lista), `CUSTOMER_MAP` y `DASH_TO_INST`. El catálogo `VARS_BY_TYPE` queda en el código.
3. *Fail-closed*: sin registro visible, lista vacía y el mensaje "No hay instalaciones asignadas".
4. Filtro `es_prueba`: oculto en la Capa 0 y los KPIs (cierra F07).
5. 3EM/Piscina: dispositivo por `dashboard_id`, con el CFG como respaldo.
6. Llamadas nuevas con `ctx.http` (encamina F23).
7. **Operación "Mover una instalación entre customers" (sin eliminar nada):**
   - (a) "Cambiar propietario" del Activo y de sus dispositivos al customer destino [Doc `POST /api/owner/CUSTOMER/{ownerId}/{entityType}/{entityId}`].
   - (b) Mover el dashboard del grupo del customer origen al del destino [Doc `POST /api/entityGroup/{id}/deleteEntities` y `/addEntities`].
   - (c) Revisar los destinatarios del report y del scheduler.
   - Los widgets lo reflejan solos.
   - Se entrega como procedimiento documentado (`docs/`) con su checklist.
8. Copia DEV actualizada, manteniendo el bloque DEV-ONLY.

**Queda manual:** pasos 1–5 y 7 del alta, y la creación del Activo y sus atributos (sin código).

**Criterios de aceptación medibles:**
- Alta de una instalación de prueba (customer "Gonex") **sin abrir el editor de widgets**, en ≤ 15 min, con 0 UUIDs pegados en código.
- Esa instalación aparece en Flota (tenant y su customer), en el dropdown de 3EM/Piscina y en Exportación con sus variables. Su dashboard preselecciona la instalación en Exportación.
- Con un usuario de Gocta: no aparece la instalación de Gonex ni ninguna ajena (en la UI ni en las respuestas de red).
- Con un usuario de un customer sin activos: lista vacía (*fail-closed*).
- `grep -E '[0-9a-f]{8}-[0-9a-f]{4}-' controllerScript.js` en los 4 widgets solo devuelve `EXPORT_DASH`/`FLEET_DASH` (dashboards compartidos) o nada.
- Mover la instalación de prueba de "Gonex" a "Erick Prueba" sin eliminar nada: se conserva el UUID y el último valor de telemetría, y desaparece de Gonex.
- `node --check` en verde. Diff revisado con Erick. DEV primero.

### D.2 Nivel 2, "Alta en pocos clics"

Asistente (formulario) para el administrador del tenant. Requiere el Nivel 1.

| Paso | Operación | Endpoint [Doc] | Automatizable |
|---|---|---|---|
| 1 | Customer | `POST /api/customer{?entityGroupId}` | Sí |
| 2 | Usuario + activación | `POST /api/user{?sendActivationMail,entityGroupId}`; `GET /api/user/{userId}/activationLink`; `POST /api/user/sendActivationMail?email=` | Sí. El envío por correo depende del servidor de correo (pendiente de capturar en `config/`); el **enlace** se muestra para copiarlo. Entregarlo al cliente es manual |
| 3 | Grupo de usuarios del customer | Se crea con el customer (3 grupos, [Repo] `hierarchy/*/groups/user`); `GET /api/entityGroups/CUSTOMER/{customerId}/USER` | Sí |
| 4 | Dispositivo | `POST /api/device{?entityGroupId}` con `name` = ID exacto del Shelly, propietario = customer; o, si ya se autoaprovisionó, `POST /api/owner/CUSTOMER/{ownerId}/DEVICE/{id}` | Sí, con validación del prefijo (`shellypro3em-` / `shellyproem50-` + 12 hex) y de que no exista otro con ese nombre (`GET /api/tenant/devices?deviceName=`). **Nunca** renombrar `name` (la búsqueda es por `deviceName` [Doc]); el nombre visible va en `label` |
| 5 | Dashboard desde plantilla | `GET` del dashboard plantilla + `POST /api/dashboard` con título nuevo (con Nivel 1, sin tocar el CFG) | Sí [Supuesto: ruta de `saveDashboard` no visible en la doc consultada] |
| 6 | Grupo de dashboards y compartición | `POST /api/entityGroup` (DASHBOARD), `POST /api/entityGroup/{id}/addEntities`, `POST /api/entityGroup/{id}/{userGroupId}/{roleId}/share` (rol `35af70e0`) | Sí |
| 7 | Tablero predeterminado | `POST /api/user` con `additionalInfo.defaultDashboardId` y `defaultDashboardFullscreen` [Doc: campos del formulario de usuario en `user.component.ts`] | Sí |
| 8 | Registro (Activo "Instalación") | `POST /api/asset{?entityGroupId}` + `POST /api/plugins/telemetry/ASSET/{id}/attributes/SERVER_SCOPE` | Sí |
| 9 | Atributos de negocio (tarifa, umbrales) | `POST /api/plugins/telemetry/DEVICE/{id}/attributes/SERVER_SCOPE` | Sí (valores por defecto editables) |
| 10 | Informe mensual y scheduler | API de report_template y scheduler de PE | [Supuesto] no verificado; además está bloqueado por F08/F09 |
| — | Configurar el MQTT del Shelly (servidor `thingsboard.gonex.pe:1884`, `status_ntf=true`) | API local o Cloud del Shelly | **No** (lo hace Romel en el equipo o en Shelly Cloud) |
| — | Verificar el primer dato | Consultar el último valor | Semiautomático: el asistente puede mostrar "esperando primer dato…" |
| — | Mover una instalación entre customers | Igual que D.1 (7), como acción del asistente | Sí |

**Idempotencia.** Si falla a mitad, el asistente reanuda: busca por nombre antes de crear. Hay que anotar en `CHANGELOG.md` cada alta.

**Widget frente a n8n:**

| | Widget asistente (JWT del administrador) | Flujo en n8n (VPS) |
|---|---|---|
| Credenciales | Usa la sesión del usuario que lo ejecuta; no guarda secretos | Necesita un usuario técnico de ThingsBoard con credenciales en n8n (secreto a custodiar y rotar) |
| Autoría | El autor real queda en auditoría y auto-commit (cumple la regla de autoría de CLAUDE.md) | Todo queda a nombre del usuario técnico |
| Interfaz | Dentro de 360.sunkuu.com con la marca | Formulario externo (n8n Form) o webhook |
| Robustez | Corre en el navegador: si se cierra la pestaña, queda a medias (se mitiga con la idempotencia) | Reintentos, registro y notificaciones nativas |
| Versionado | El widget queda en `sunkuu-tb-config` | El flujo vive fuera del Version Control (habría que documentarlo en `config/`) |
| Esfuerzo | 40 h | 48 h (+ endurecimiento) |

**Recomendación:** widget. n8n solo como complemento opcional, por ejemplo para notificar a Sunkuu y GONEX de cada alta.

---

## 6. Sección E: pedidos de Romel

### E.1 Menú visible aunque el dashboard esté en pantalla completa

**Es configuración, no código.**
- "Always fullscreen" (`additionalInfo.defaultDashboardFullscreen`) abre el tablero predeterminado en pantalla completa y oculta la barra de herramientas [Doc users, `user.component.ts`].
- Para el usuario de **Romel (tenant)**: desmarcar "Siempre pantalla completa" y usar Portal de Flota como **Home dashboard** con "Hide home dashboard toolbar" [Doc]. El menú lateral queda visible y Flota se abre como inicio.
- Para los clientes se mantiene pantalla completa.
- Opcional: **Custom menu** (PE) para acortar el menú de Romel o agregar Flota y Exportación como ítems [Doc].
- No hay opción documentada para mostrar el menú **dentro** de la pantalla completa [Doc: no consta]. Si Romel insiste en eso: botón "Administración" en el encabezado de Flota que salga a `/home` (código, 1–2 h).
- Esfuerzo: 0,5–1 h. **Cortesía.**

### E.2 Selector de fecha (día 00:00–24:00 Lima, "Hoy" por defecto)

**Gráficas afectadas [Repo]:**

| Widget | Gráfica | Hoy | Archivo |
|---|---|---|---|
| 3EM | Curva de demanda | 4h · 8h · Hoy · Ayer (FEAT-01, ya en Lima) | HTML L176–179, JS L668–735 |
| 3EM | Estadísticas Pico/Promedio/Mínimo + donut de distribución | 24 h móviles | JS L339–346 (`daysAgo(1)`), HTML L200–222 |
| 3EM | Tendencia del factor de potencia | 24 h móviles | JS L348–355 |
| 3EM | Análisis energético | Hoy · Semana · Mes | HTML L270–272, JS L861–900 |
| Piscina | Temperatura | 6h · 12h · 24h · 7d (móviles) | HTML L166–169, JS L416 |
| Piscina | Potencia de iluminación | 24h · 7 días · 30 días | HTML L262–264, JS L500 |

**Fuera de alcance:**
- Flota: el sparkline de 12 h no es una gráfica de consulta.
- Histórico de 6 meses: está oculto.
- Exportación: ya tiene rango `datetime-local`.

**Propuesta.**
- Un selector de fecha único en el encabezado de cada dashboard ("Hoy" por defecto) que fija el día D en Lima.
- Cada gráfica de día pasa a D 00:00–24:00. "4h/8h" solo se muestran si D = hoy.
- Semana y Mes pasan a ser "7 y 30 días que terminan en D".
- Los KPIs de "hoy" muestran el día D (requiere F01/F02 corregidos).
- La utilidad `limaMidnight()` de FEAT-01 se reutiliza.
- Esfuerzo: 16 h probable (12 h si va junto con las correcciones de QA).
- **Evolutivo.**

### E.3 Exportación: filtrar por cliente y luego por instalación

**Hoy.** El tenant ve todas las tarjetas mezcladas; el customer ve solo las suyas (Export JS L224–231) [Repo].

**Propuesta.** Para el tenant, un selector o chips de cliente sobre la grilla. Para el customer no cambia nada.

- Sin Nivel 1: se agrupa por el campo `client` del array (3–5 h; agrega otro dato a mantener por alta).
- Con Nivel 1: el cliente sale del propietario del Activo (2–3 h, sin datos nuevos).
- **Evolutivo** pequeño.

---

## 7. Sección F: dimensionamiento

Horas de GONEX: análisis, implementación, revisión con Erick, prueba en DEV y documentación. No incluyen el tiempo de Romel.

| Ítem | Tipo | Optimista | Probable | Pesimista | Depende de |
|---|---|---|---|---|---|
| R0. Remediación de Pumarinri: verificar propietario, Cambiar propietario, A3-1/2/3/7/8, grupos de prueba, CHANGELOG | **Correctivo** (errores de arrays de GONEX) | 1,5 | 2,5 | 4 | — |
| R0b. Intento de recuperar el histórico de Pumarinri (backup o Shelly Cloud → importación) | **Cortesía** (la causa fue una eliminación durante la capacitación), valorizada | 2 | 4 | 8 | Pregunta 3 |
| QA. Correcciones del 3EM previas al template: F01–F05, F27, F50, función común (3EM + Flota) | **Correctivo** | 12 | 18 | 28 | — |
| QA+. F21, F22, F23, F25, F32 | **Correctivo** | 4 | 6 | 10 | QA |
| N1. Nivel 1, registro de Activos y procedimiento "mover" | **Evolutivo** (alcance nuevo; también cierra F07/F14/F15, que son Correctivos) | 16 | 24 | 36 | R0 |
| N2. Nivel 2, asistente en widget | **Evolutivo** | 24 | 40 | 60 | N1 |
| N2-alt. Nivel 2 en n8n (alternativa) | **Evolutivo** | 32 | 48 | 72 | N1 |
| PE. Template Pro EM-50: widget, converter con filtro y `+/online`, alarmas, Flota/Export | **Evolutivo** | 18 | 27 | 40 | QA, N1, EM-50 publicando |
| E1. Menú y pantalla completa | **Cortesía** | 0,5 | 1 | 2 | — |
| E2. Selector de fecha (6 gráficas) | **Evolutivo** | 10 | 16 | 24 | QA (F01/F02) |
| E3. Filtro cliente → instalación en Exportación | **Evolutivo** (pequeño; **Cortesía** si va con N1) | 3 | 5 | 8 | — |

**Ahorros al combinar (probable):**
- QA + E2: la misma utilidad de días en Lima y los mismos `load*()`: **−4 h** (E2 baja a 12).
- N1 + E3: el cliente sale del registro: **−2 h** (E3 baja a 3).
- N1 antes de PE: el tipo nuevo no se agrega a arrays en 4 widgets: **−3 h**.
- QA antes de PE: se evita corregir F01–F05 dos veces: **−4 a −6 h**.
- N1 antes de las próximas altas (Apusamay): evita repetir el patrón de 4 defectos por alta: **−1 a −4 h por alta**.
- **Total: ≈ 12–19 h.**

**Orden recomendado:**
1. **R0** (esta semana).
2. **N1 + E3**: antes del alta de Apusamay.
3. **QA + QA+ + E2**: en un solo ciclo sobre el 3EM.
4. **E1**: en cualquier momento, es configuración.
5. **PE**: cuando los EM-50 publiquen.
6. **N2**.

Con Nivel 1, el alta de Apusamay no toca código.

**Paquete probable sin N2:** R0 2,5 + N1 24 + E3 3 + QA 18 + QA+ 6 + E2 12 + E1 1 + PE 24 ≈ **90 h**. De ellas, Correctivo ≈ 26,5, Cortesía ≈ 1–4 y Evolutivo ≈ 63. Con N2: +40 h.

### F.1 Propuesta de columna "Tipo" y "Horas" en `CHANGELOG.md` (sin editar)

**Cambio de formato.** Insertar dos columnas tras `ID`:

```
| Fecha | ID | Tipo | Horas | Cambio | Componentes | Commit sunkuu-tb-config | Commit sunkuu-TB | Estado |
```

- **Tipo:** `Correctivo` | `Cortesía` | `Evolutivo`.
- **Horas:** número; sufijo `e` si es estimado (`2e`) y sin sufijo si es real.
- Al final, una sección `## Valor entregado` con una tabla mensual por tipo (horas Correctivo / Cortesía / Evolutivo cotizado / Evolutivo entregado sin cobro). Es la base para renegociar la mensualidad.

**Clasificación retroactiva (las horas son estimaciones a confirmar por Erick):**

| ID | Tipo propuesto | Horas (est.) | Criterio |
|---|---|---|---|
| BR-01 | Cortesía | 2e | Mejora de marca pedida y aprobada por Romel, pequeña |
| BR-02 | Correctivo | 0,25e | Ajuste de contraste del propio BR-01 |
| VC-01 | Cortesía | 3e | Trazabilidad que protege a Sunkuu (incluye rehacer el repo por las credenciales, error propio, sin cargo) |
| ERR-01 | Correctivo | 0,25e | Errata de GONEX |
| QA-01 | Cortesía | 16e | Auditoría completa (53 hallazgos y scripts). Las correcciones que deriven serán Correctivo |
| F53 | Correctivo | 1,5e | Error de marca blanca de GONEX reportado por Romel |
| ADM-01 | Correctivo | 0,25e | Operación interna (identificar autoría); sin valor facturable |
| VC-02 | Cortesía | 0,5e | Auto-commit y versión de estado |
| FEAT-01 | Evolutivo (entregado sin cotizar) → registrar como **Cortesía valorizada** si no se factura | 10e | Funcionalidad nueva pedida por Romel (vistas, selector, legibilidad) |
| *(nuevo)* ALTA-01 Pumarinri 2026-10-10 | Cortesía (capacitación) + Correctivo (R0) | 1,5 real (16:49–18:12, del repo) + R0 | Hoy no tiene fila en CHANGELOG (A3-9) |

---

## 8. Sección G: riesgos y preguntas

### G.1 Riesgos

| # | Riesgo | Tipo | Mitigación |
|---|---|---|---|
| G1 | Pumarinri ve su dashboard sin datos (dispositivo del tenant) | Producción, hoy | R0: verificar y Cambiar propietario |
| G2 | Gocta ve un "TG Pumarinri" roto (Piscina NAV y, si existe, el dashboard `32131e90` en su grupo) | Producción, hoy | R0 |
| G3 | El informe del 1 de noviembre de Pumarinri sale del dashboard viejo | Producción, 2026-11-01 | R0: reapuntar `defa3090` a `8e373390` (y F08/F09) |
| G4 | Histórico de Pumarinri perdido | Datos | R0b y regla escrita: **nunca eliminar dispositivos con historial; usar Cambiar propietario** |
| G5 | Usuarios de prueba ven todas las instalaciones reales (*fail-open*) | Seguridad | N1 (*fail-closed*), o quitar Flota y Exportación de los grupos de prueba (5 min) |
| G6 | El repo muestra entidades eliminadas; no hay commit de eliminación | Trazabilidad | Anotar eliminaciones en CHANGELOG; probar si una versión manual por tipo limpia el repo |
| G7 | Permisos y comparticiones (`hierarchy/`, `_entities`) fuera del auto-commit | Trazabilidad | Versión manual por tipo tras cada alta |
| G8 | Comportamiento de `entitiesQuery` y `/api/user/dashboards` para usuarios de customer | Diseño de N1 | Prueba de concepto de 1 h en DEV antes de comprometer N1 |
| G9 | EM-50 sin publicación periódica: falsas desconexiones | Template PE | `+/online` y alarma basada en ese atributo |
| G10 | Renombrar el `name` crea un duplicado [Doc] | Operación | En N2, `name` solo de lectura; usar `label` |
| G11 | Romel y GONEX editan los mismos widgets en paralelo (ambos generan auto-commit) | Producción | Avisar las ventanas de cambio; con N1 casi no hay que editar widgets |
| G12 | Error de sintaxis en un array: el widget cae para todos los clientes | Producción (mientras no haya N1) | `node --check` antes de guardar; N1 elimina el riesgo |

### G.2 Preguntas imprescindibles

1. **(Erick)** En producción, ¿quién es el propietario de `shellypro3em-e08cfe972040` (`717ae5e0`)? ¿Un usuario de Pumarinri ve datos en TG PUMARINRI?
2. **(Erick)** ¿El dashboard viejo `32131e90` y el informe "Informe Mensual - TG PUMARINRI" siguen existiendo? ¿Se eliminó algo más en la capacitación (además de `cf7ddac0`)?
3. **(Erick/Romel)** ¿Hay respaldo de `gonex-postgres` anterior al 2026-10-10 16:00 Lima? ¿Quiere Romel recuperar el histórico de Pumarinri desde ese respaldo o desde Shelly Cloud? ¿Se valoriza como Cortesía?
4. **(Romel)** Pro EM-50: ¿los 3 equipos tienen MQTT apuntando a `thingsboard.gonex.pe:1884` con "Generic status update over MQTT" activo? ¿Cuáles son los IDs `shellyproem50-…` de Apusamay y qué carga mide cada canal?
5. **(Romel)** El EM-50 de Gocta ("Caldero Piscina"), ¿va en un dashboard propio o como sección dentro de Piscina Temperada (que ya tuvo una sección "Caldero")?
6. **(Romel)** Pantalla completa: ¿se refiere a su propio usuario (tenant) o a los clientes? ¿Le basta con Flota como inicio y el menú visible?
7. **(Romel)** Selector de fecha: ¿se aplica también a Piscina? ¿Se conservan 4h/8h para "Hoy"? ¿Semana y Mes deben terminar en el día elegido?
8. **(Erick)** Clasificación comercial: ¿FEAT-01 se registra como Cortesía valorizada o como Evolutivo? ¿Hay horas reales para reemplazar las estimadas?

---

## Anexo: fuentes oficiales consultadas

**Shelly (Gen2 API)**
- https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/EM1
- https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/EM1Data
- https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Mqtt
- https://shelly-api-docs.shelly.cloud/gen2/Devices/Gen2/ShellyProEM

**ThingsBoard PE (documentación)**
- https://thingsboard.io/docs/pe/user-guide/integrations/
- https://thingsboard.io/docs/pe/user-guide/integrations/uplink-data-converter/
- https://thingsboard.io/docs/pe/user-guide/ui/users/
- https://thingsboard.io/docs/pe/user-guide/ui/dashboards/
- https://thingsboard.io/docs/pe/user-guide/ui/aliases/
- https://thingsboard.io/docs/pe/user-guide/actions/
- https://thingsboard.io/docs/pe/user-guide/rbac/
- https://thingsboard.io/docs/pe/user-guide/custom-menu/ (vía resultado de búsqueda)
- https://thingsboard.io/blog/thingsboard-3-7-release/ (vía resultado de búsqueda: *housekeeping*)
- https://blog.thingsboard.io/2020/09/deleting-timeseries-of-deleted.html (vía resultado de búsqueda)
- (404) https://thingsboard.io/docs/pe/user-guide/ui/white-labeling/

**GitHub oficial de ThingsBoard**
- https://github.com/thingsboard/thingsboard/issues/15134 (eliminaciones y Version Control)
- https://raw.githubusercontent.com/thingsboard/thingsboard/master/application/src/main/resources/thingsboard.yml (`queue.core.housekeeper`, `sql.ttl.ts`)
- https://raw.githubusercontent.com/thingsboard/thingsboard/master/ui-ngx/src/app/modules/home/pages/user/user.component.ts (campos `defaultDashboardId`, `defaultDashboardFullscreen`, `homeDashboardId`)
- Cliente REST oficial PE (generado desde Swagger), `https://raw.githubusercontent.com/thingsboard/thingsboard-python-rest-client/master/tb_rest_client/`:
  - `rest_client_pe.py`
  - `api/api_pe/owner_controller_api.py`
  - `api/api_pe/dashboard_controller_api.py`
  - `api/api_pe/entity_group_controller_api.py`
  - `api/api_pe/entity_query_controller_api.py`
  - `api/api_pe/user_controller_api.py`
  - `api/api_pe/customer_controller_api.py`
  - `api/api_pe/telemetry_controller_api.py`
  - `api/api_pe/device_controller_api.py`
  - `api/api_pe/asset_controller_api.py`
  - `api/api_pe/entity_relation_controller_api.py`

**Nota.** El "manual N4" citado en el encargo no está en este repo. Los 7 pasos del alta se tomaron del encargo.
