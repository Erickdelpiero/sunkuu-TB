# SEC-02 — Historial de telemetría legible entre customers

Fecha: 2026-10-26 · Base: `../sunkuu-tb-config` `8a1f930` (solo lectura) · **Abierto. Nada aplicado.**
Origen: V17 de B-05 (`docs/qa/2026-10-25-B-05.md` §9) y su investigación (`docs/qa/2026-10-26-V17-permisos-curl.md`).

## 1. Hallazgo (verificado por Erick el 2026-10-26)

Un usuario de customer puede leer el **historial** de telemetría de dispositivos de **otros customers** si conoce su UUID. El **último valor** sí está protegido (403).

- Probado con `curl` y token propio del usuario de GONEX QA (`CUSTOMER_USER`, `c13a9950`), con el registro **restaurado**.
- Afecta al menos a un dispositivo de Gocta (`c636fa00`) y a uno de Tucán (`1bfa8070`).
- **No es un fallo del registro de instalaciones:** ocurre sin el registro (H4 descartada) y con el token correcto (H3 descartada).
- Los permisos del tenant son los esperados: en `8a1f930` ningún rol, grupo, permiso ni rule chain da acceso entre customers (detalle en el guion de V17, §6).

## 2. Referencias públicas

- **PR #16134** de ThingsBoard ("Fixed unauthorized access to attributes and time series of other tenants"), **abierto y sin fusionar**, contra `lts-4.2`. El autor indica que el mismo defecto existe en `lts-4.3` y `master`. Describe que el validador de acceso, al denegar, no corta la petición y el historial de timeseries responde 200. El PR habla de acceso **entre tenants**; nuestro caso es **entre customers del mismo tenant**, con el mismo síntoma (200 en el historial, 403 en el último valor). Es la explicación más probable, pero **no está confirmada** por ThingsBoard.
- **Notas de versión de PE 4.3.x:** ninguna entrada menciona permisos del historial de timeseries. Última versión de la rama: 4.3.1.7 (2026-10-22). La 4.4 está publicada; el PR #16407 (fusionado en `lts-4.4`) es de dependencias y no trata este tema.
- No se encontró un CVE ni un aviso de seguridad publicado para este caso.

Fuentes: https://github.com/thingsboard/thingsboard/pull/16134 · https://thingsboard.io/docs/pe/releases/releases-table/v4-3-x/ · https://github.com/thingsboard/thingsboard/pull/16407

**Causa probable (Erick, 2026-10-26):** la del PR #16134. `AccessValidator` pasa la denegación a `onSuccess` y `DefaultTbTelemetryService.getTimeseries` la ignora; `lts-4.3` está afectado. Según Erick, la corrección está en el **PR #16308**, fusionado en `lts-4.4` el 2026-10-14. No aparece en las notas de 4.3.x hasta 4.3.1.7. Falta confirmar en qué versión publicada de 4.4.x entra (§9).

**Escritura de atributos (riesgo descrito en el PR #16134):** Erick probó con el usuario de GONEX QA escribir un atributo en QA-Ajeno (activo del tenant). Resultado: **pendiente de registrar** (código de respuesta y si el atributo quedó escrito). Limpieza: **pendiente de registrar** (código).

**Ticket a ThingsBoard:** enviado por el formulario thingsboard.io/contact-us (acuse: "respuesta en 24 h") y, el 2026-10-26, a **security@thingsboard.io**, con evidencia sin UUID ni datos de clientes (códigos de respuesta y tamaños). El archivo de evidencia (`evidence.txt`) estuvo sin seguimiento en la raíz de sunkuu-TB y se eliminó; nunca entró en el historial de git. Texto del reporte: **pendiente de copiar aquí** (sin datos sensibles).

## 3. Exposición: dónde ven hoy los usuarios de customer UUID de dispositivos ajenos

Revisado en `8a1f930`. Los UUID solo se exponen a quien carga ese widget o dashboard.

| Dónde | UUID de dispositivos que contiene | Quién lo carga |
|---|---|---|
| **Portal de Flota** (`6902b8c0`, dashboard `9648fe20`) | 4: Gocta ×2, Tucán, Pumarinri | Usuarios de Gocta, Tucán y Pumarinri (el dashboard está en sus grupos) |
| **Centro de Exportación** (`d88440c0`, dashboard `75c7e760`) | 6: Gocta ×4, Tucán, Pumarinri | Usuarios de Gocta, Tucán y Pumarinri |
| Template Piscina (`5f7b51c0`) | 3 de Gocta | Solo Gocta (dashboard `cc2cad90`) |
| Dashboards por instalación (`e844d080`, `0469dc30`, `8e373390`, `cc2cad90`) | Solo los del propio customer | Su customer |
| Copias DEV y dashboards QA (`f2b42860`, `51b3e9c0`, `59117110`, `5d08ea00`, `cd3a2050`) | Dispositivos de Gocta | Usuarios de prueba de GONEX QA y QA 2 |

**Conclusión:** cualquier usuario de Gocta, Tucán o Pumarinri tiene hoy en su navegador los UUID de todos los medidores de producción (vienen en el JS de Flota y Exportación). B-05, B-06 y B-08 quitan esos arrays (cada usuario solo recibe sus instalaciones), pero **un UUID no es un secreto**: la corrección tiene que estar en el servidor.

## 4. Diagnóstico de mañana (solo lectura)

Con la sesión de `curl` del guion de V17 (§0), sin navegador:
1. **Versión exacta de ThingsBoard** (pie de página o "Acerca de" en la UI como admin del tenant). Anotarla tal cual (p. ej. `4.3.0PE`, `4.3.1.x PE`).
2. **Permisos, roles, grupos y auditoría actuales:** los pasos 3.1–3.7 del guion anterior de V17 (propietario, grupos, permisos de los grupos de usuarios de los 7 customers, roles y auditoría). Confirman que la configuración del tenant no es la causa.
3. **Alcance:** repetir las mismas cuatro comprobaciones que ya hiciste (último valor e historial) contra **un dispositivo de cada customer** (Gocta, Tucán, Pumarinri) y contra el propio dispositivo de QA (`99eae720`) como control, y además la lectura de **atributos** del dispositivo. Solo leer, solo con el usuario de GONEX QA (de prueba). No usar cuentas de clientes. Anotar código y tamaño de respuesta; no guardar los datos de otros customers y borrar las salidas al terminar.

## 5. Mitigación: opciones

| # | Opción | Efecto | Riesgo | Rollback |
|---|---|---|---|---|
| M1 | **Actualizar ThingsBoard** a una versión con la corrección | Cierra la causa | Hoy **no hay versión publicada** con la corrección (PR abierto). Una actualización de versión mayor es un proyecto aparte | Restaurar la versión anterior (copia de seguridad previa obligatoria) |
| M2 | **Reporte a ThingsBoard** (soporte PE / canal de seguridad) y seguimiento del PR #16134 | Obtener confirmación, plazo y, si existe, parche o hotfix para PE 4.3 | Ninguno | — |
| M3 | **Filtro en el proxy** (`gonex-infra`) para las peticiones de historial de usuarios de customer, permitiendo solo los dispositivos de su customer | Cierra la exposición sin esperar a ThingsBoard | Alto: requiere leer el token en el proxy y mantener una lista de dispositivos por customer; un error rompe los dashboards de los clientes. Debe diseñarse y probarse aparte, primero con QA | Quitar la regla del proxy |
| M4 | **Quitar los UUID ajenos del JS servido** (aplicar B-08 en Flota y Exportación de producción) | Reduce quién los conoce | No cierra la causa (los UUID ya se distribuyeron y no se pueden cambiar sin perder histórico). B-08 está bloqueado hasta cerrar SEC-02 | Rollback de B-08 |
| M5 | **Contención inmediata:** no crear usuarios nuevos de customer (Apu Samay sin usuarios), no compartir dashboards nuevos y no usar el registro apuntado a dispositivos de producción en pruebas | Evita ampliar la exposición | Retrasa el alta de Apu Samay | Levantar la medida al cerrar SEC-02 |
| M6 | **Informar a Sunkuu (Romel)** del hallazgo, la exposición y el plan | Transparencia con el cliente del SaaS | — | — |

Recomendación: M5 y M2 ya; M6 en cuanto haya confirmación de alcance (§4); M3 solo si ThingsBoard no da plazo; M4 cuando se levante el bloqueo de B-08.

## 6. Borrador de reporte para ThingsBoard (sin datos sensibles)

> **Asunto:** Customer user can read time-series history of devices owned by another customer (PE 4.3)
>
> **Product / version:** ThingsBoard PE, `<versión exacta>`, self-hosted.
>
> **Summary:** In a single tenant with several customers, a user with authority CUSTOMER_USER (generic role with READ, READ_ATTRIBUTES and READ_TELEMETRY over its own customer's entities) receives HTTP 403 when requesting the latest values of a device owned by a different customer, but HTTP 200 with data when requesting the time-series history of the same device through the REST telemetry API. The device is not shared with the user's customer by any entity group or permission.
>
> **Expected:** HTTP 403 for both requests.
>
> **Possibly related:** PR #16134 (cross-tenant variant of the same symptom; the author states that lts-4.3 is also affected).
>
> **Reproduction:** we can share step-by-step details privately through your security channel.
>
> **Impact:** confidentiality of telemetry between customers of the same tenant.
>
> **Questions:** Is this confirmed for PE 4.3? Is there a fixed version or hotfix? Is there a recommended configuration workaround?

Antes de enviarlo: versión exacta (§4.1) y confirmación del alcance (§4.3).

## 7. Estado y bloqueos

- **B-06 desbloqueado solo para DEV** (Erick, 2026-10-26): toca solo la copia DEV y quita los UUID de producción de su JS; el fallo no depende del registro. En su guion, F16 y toda prueba que espere 403 en el historial de un dispositivo ajeno pasan a "conocido por SEC-02" (solo el último valor debe dar 403). Su §5.4 con datos reales se mantiene.
- **B-08 bloqueado** hasta cerrar SEC-02.
- **Apu Samay sin usuarios** hasta cerrar SEC-02.
- Las pruebas con el registro apuntado a dispositivos de producción quedan suspendidas, salvo la §5.4 de B-06 (decisión de Erick, 2026-10-26).

## 8. Resultados

| Paso | Resultado | Notas |
|---|---|---|
| Hallazgo (2026-10-26) | Confirmado | §1 |
| Causa probable | Identificada | PR #16134 (defecto) y PR #16308 (corrección en `lts-4.4`, 2026-10-14). §2 |
| Prueba de escritura de atributo (QA → QA-Ajeno) | **Pendiente de registrar** | Código, si quedó escrito y código de la limpieza |
| 4.1 Versión | Pendiente | |
| 4.2 Permisos y auditoría | Pendiente | |
| 4.3 Alcance | Pendiente | |
| Reporte a ThingsBoard | ✔ contact-us (acuse "respuesta en 24 h") y ✔ security@thingsboard.io (2026-10-26) | Evidencia sin UUID ni datos de clientes; `evidence.txt` eliminado (nunca versionado). Texto pendiente de copiar en §2. Esperando respuesta |
| Aviso a Sunkuu | Pendiente | |
| §9 Decisión upgrade / parche | Pendiente (2026-10-27) | |

## 9. Evaluación para mañana: upgrade a 4.4.x o esperar un parche de 4.3 PE

Solo evaluación; nada se aplica. Los datos marcados "verificar" se confirman mañana en las fuentes oficiales.

**Datos a confirmar primero**
- Versión exacta instalada (§4.1).
- **Primera versión publicada de PE 4.4.x que incluye el PR #16308** (fusionado el 2026-10-14; la 4.4 salió el 2026-09-29, así que hace falta una 4.4.x posterior). Si aún no existe, la opción A no está disponible todavía.
- Respuesta de ThingsBoard al ticket: confirmación, plazo de un 4.3.1.x con la corrección, o workaround.
- Compatibilidad de la **licencia Pilot** con 4.4 y si permite una **segunda instancia** (de prueba) para ensayar el upgrade: la licencia es de 1 instancia de producción.
- Ruta de upgrade soportada desde nuestra versión a 4.4.x (instrucciones de upgrade de PE: si exige pasar por versiones intermedias).

**Opciones**

| | A. Upgrade a 4.4.x con la corrección | B. Esperar un parche de 4.3 PE (4.3.1.x) |
|---|---|---|
| Cierra SEC-02 | Sí, si la versión incluye el PR #16308 (verificar) | Sí, cuando salga |
| Plazo | Inmediato si la versión existe; más el ensayo | Desconocido (depende de ThingsBoard) |
| Cambio | Versión menor nueva: migración de base de datos, cambios de UI y de API | Parche de la misma rama: cambio mínimo |
| Riesgo funcional | **Medio–alto:** widgets propios (Flota, Exportación, 3EM, Piscina, Registro), módulo `sunkuu-registro.js`, integración MQTT de los Shelly, rule chains, informes programados, marca blanca y Version Control. Cambios de comportamiento citados en el PR #16134: los usuarios de customer dejan de leer atributos del tenant y de perfiles por WebSocket (revisar si algún dashboard de cliente usa un alias "Current Tenant") | Bajo |
| Exposición mientras tanto | Hasta el día del upgrade | Hasta el parche: hay que sostener la contención (M5) y valorar M3 |
| Rollback | Restaurar la base de datos del backup (B2) y la imagen anterior en el VPS. **La migración de base de datos no tiene vuelta atrás sin backup** | Volver a la imagen anterior (normalmente sin migración; verificar) |

**Pasos de la opción A (borrador, para revisar mañana)**
1. Confirmar versión destino, ruta de upgrade, licencia y notas de "breaking changes" de 4.4.x.
2. **Backup completo verificado:** base de datos (PostgreSQL) y volúmenes de ThingsBoard, subidos a B2. Prueba de restauración en un entorno aparte antes del día del upgrade (un backup sin restaurar probado no cuenta como rollback).
3. Anotar la imagen actual de ThingsBoard PE (tag exacto) y el `docker-compose` del VPS en `gonex-infra`.
4. Ensayo en una instancia de prueba (si la licencia lo permite) restaurada desde el backup: upgrade, y checklist de dashboards (Flota, Exportación, TG GOCTA, Piscina, Tucán, Pumarinri, Administración), integración MQTT, rule chains, informes, marca blanca y Version Control. Repetir la prueba de SEC-02 (debe dar 403) y la de escritura de atributos.
5. Ventana de mantenimiento acordada con Sunkuu (Romel): aviso previo a los clientes por la caída del servicio.
6. Upgrade en producción según las instrucciones oficiales; checklist del paso 4; versión manual en ThingsBoard y `git pull` en `../sunkuu-tb-config`.
7. Fila en el CHANGELOG y cierre de SEC-02; levantar los bloqueos de B-06, B-08 y Apu Samay.

**Rollback de la opción A:** detener ThingsBoard → restaurar la base de datos y los volúmenes del backup B2 → volver al tag de imagen anotado en el paso 3 → arrancar → checklist del paso 4 (con la versión anterior, SEC-02 vuelve a estar abierto).

**Criterio de decisión propuesto:** si existe una 4.4.x publicada con el PR #16308, el ensayo del paso 4 sale bien y la licencia lo permite, **A**. Si no existe aún, o ThingsBoard da un plazo corto para un 4.3.1.x, **B** con la contención M5 (y M3 si el plazo es largo).
