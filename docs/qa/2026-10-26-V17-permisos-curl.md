# V17 (B-05): investigación del 200 en TG GOCTA

Fecha: 2026-10-26 · Base: `../sunkuu-tb-config` `8a1f930` (solo lectura) · Origen: `docs/qa/2026-10-25-B-05.md` §9 (V17).
**Estado:** prueba decisiva con `curl` hecha (§5): **los permisos de la plataforma están bien** y H4 queda descartada. Falta explicar el 200 que dio el navegador: §2 (petición exacta del widget con `curl`) y §3 (Firefox con perfil limpio). Usuario GONEX (admin del tenant) y el usuario de GONEX QA.

## Hechos

| Cuándo | Qué | Resultado |
|---|---|---|
| 2026-10-25, C8 de B-03 | Usuario de GONEX QA en Flota DEV (`fetch` con `localStorage.jwt_token`), QA Instalación 1 con dispositivo ficticio | 403 en `c636fa00` |
| 2026-10-25, V13 de B-05 | Admin, QA Instalación 1 → `c636fa00`, 15 min, Último mes | 2 879 filas |
| 2026-10-25, V17 de B-05 | Usuario de GONEX QA (`CUSTOMER_USER`, `c13a9950`, confirmado con `/api/auth/user`) en Exportación DEV (`ctx.http`), QA Instalación 1 → `c636fa00` | **200** en todas las llamadas de telemetría; CSV de 2 878 filas de TG GOCTA |
| 2026-10-25, después de 5.3.2 | Sesión de Firefox del usuario QA, prueba directa | 403 en `c636fa00` y `1bfa8070` |
| **2026-10-26, prueba decisiva con `curl`** | Token propio del usuario QA (`CUSTOMER_USER`, `c13a9950`), sin navegador. Misma petición y mismo token: estado restaurado → QA Instalación 1 apuntada a `c636fa00` → restaurado y comprobado (`{"principal":"…0002"}`) | **403 → 403**. El atributo del registro no abre el acceso; los permisos de la plataforma están bien |

En `../sunkuu-tb-config` (`8a1f930`) ningún permiso, rol, grupo ni rule chain da acceso de GONEX QA a `c636fa00` (detalle en el §6).

## Hipótesis

| # | Hipótesis | Estado |
|---|---|---|
| H1 | Un permiso, un grupo compartido o una membresía de más | **Descartada como permanente** (403 con token propio el 26). Un cambio abierto y cerrado entre el 25 y el 26 solo se descarta con la auditoría (§4, opcional) |
| H2 | `c636fa00` cambió de propietario | Igual que H1 |
| **H3** | **La exportación de V17 corrió con el token de otro usuario.** ThingsBoard guarda el token en `localStorage.jwt_token`, que comparten todas las pestañas del mismo perfil de navegador (y todas las ventanas privadas entre sí). Si después de entrar como QA se inició sesión como admin en otra pestaña o ventana del mismo perfil, la pestaña de QA sigue mostrando al usuario QA, pero sus llamadas salen con el token del admin. Un `/api/auth/user` hecho en otro momento no garantiza el token de la exportación. Dato coherente: V17 dio 2 878 filas y V13 (admin, mismo período) 2 879 | **Principal.** §3 |
| H4 | El atributo `dispositivos` del registro abre el acceso | **Descartada** (prueba decisiva) |
| H5 | La petición del widget es distinta de la probada con `curl` (parámetros con los que la plataforma no comprueba el permiso) | §2 |
| H6 | Caché HTTP del navegador: una respuesta 200 guardada de una sesión de admin con la misma URL | §2 (cabeceras de caché) y §3 ("Desactivar caché") |

## 0. Preparación (bash)

**0.1** Variables y funciones. La clave se lee con `read -rsp` y llega a `jq` por el entorno (`env.PW`), no por `--arg`: un `--arg` la deja en la línea de comandos de `jq`, visible en `ps`. El JSON llega a `curl` por la entrada estándar (`-d @-`) y los tokens van en una cabecera generada con `printf` (builtin), así que tampoco aparecen en `ps`.
```
H=https://360.sunkuu.com
A1=b3a6d630-cbe9-11f1-aa6f-7f75b1e7584b      # QA-Instalación-1
G=c636fa00-2eeb-11f1-a6d8-33f75efe8b97       # TG GOCTA
hdr() { printf 'X-Authorization: Bearer %s\n' "$1"; }
ca()  { curl -s -H @<(hdr "$TA") "$@"; }     # como admin GONEX
cq()  { curl -s -H @<(hdr "$TQ") "$@"; }     # como usuario de GONEX QA
login() {
  local U PW
  read -r -p "Usuario $1: " U >&2; read -rsp "Clave $1: " PW; echo >&2
  PW="$PW" U="$U" jq -n '{username: env.U, password: env.PW}' \
    | curl -s -X POST "$H/api/auth/login" -H 'Content-Type: application/json' -d @- | jq -r .token
}
attrs() { ca "$H/api/plugins/telemetry/ASSET/$A1/values/attributes/SERVER_SCOPE?keys=dispositivos,es_prueba" | jq -c 'map({key, value})'; }
apuntar()   { ca -o /dev/null -w 'apuntar %{http_code}\n' -X POST "$H/api/plugins/telemetry/ASSET/$A1/attributes/SERVER_SCOPE" -H 'Content-Type: application/json' -d "{\"dispositivos\":{\"principal\":\"$G\"}}"; attrs; }
restaurar() { ca -o /dev/null -w 'restaurar %{http_code}\n' -X POST "$H/api/plugins/telemetry/ASSET/$A1/attributes/SERVER_SCOPE" -H 'Content-Type: application/json' -d '{"dispositivos":{"principal":"00000000-0000-0000-0000-000000000002"}}'; attrs; }
```
- Esperado: nada en pantalla.

**0.2** Login del admin y del usuario QA (un solo token de QA para todo el guion):
```
TA=$(login "admin GONEX"); echo ${#TA}; ca "$H/api/auth/user" | jq -c '{authority, email}'
TQ=$(login "QA"); echo ${#TQ}; cq "$H/api/auth/user" | jq -c '{authority, customerId: .customerId.id, email}'
```
- Esperado: mayores que 100; `"TENANT_ADMIN"`; `"CUSTOMER_USER"`, `c13a9950-cbdd-11f1-aa6f-7f75b1e7584b`.

**0.3** Estado restaurado:
```
attrs
```
- Esperado: `dispositivos` = `{"principal":"00000000-0000-0000-0000-000000000002"}`, `es_prueba` = `true`. Si no, **detente**.

## 1. Petición exacta del widget de Exportación

Exportación DEV (`fdc33410`, `apply/` de B-05), "15 minutos" + "Promedio (AVG)", "Último mes":
- `startTs` / `endTs`: los campos Desde/Hasta (precisión de minuto; Último mes = ahora − 30 días → ahora).
- Un solo tramo por variable (el tramo máximo es 4 999 × 15 min ≈ 52 días).
- **Una petición por variable** (25 en 3EM), en secuencia, con `ctx.http.get`:
  `/api/plugins/telemetry/DEVICE/<dispositivo>/values/timeseries?keys=<clave>&startTs=<s>&endTs=<e>&interval=900000&agg=AVG&limit=50000`
- Sin `orderBy` en el agregado. En Raw: `…&startTs=<s>&endTs=<e>&orderBy=ASC&limit=50000`, paginado por variable.

## 2. Réplica con `curl` (registro apuntado, token propio de QA)

**2.1** Período como el del botón "Último mes", redondeado al minuto:
```
E=$(( $(date +%s) / 60 * 60 * 1000 )); S=$(( E - 30*86400000 )); echo "$S $E"
KEYS="potencia_activa_fase_a potencia_activa_fase_b potencia_activa_fase_c potencia_activa_total potencia_aparente_fase_a potencia_aparente_fase_b potencia_aparente_fase_c potencia_aparente_total energia_total energia_fase_a energia_fase_b energia_fase_c energia_ret_total energia_ret_fase_a energia_ret_fase_b energia_ret_fase_c voltaje_fase_a voltaje_fase_b voltaje_fase_c corriente_fase_a corriente_fase_b corriente_fase_c factor_potencia_fase_a factor_potencia_fase_b factor_potencia_fase_c"
```

**2.2** Ventana: apuntar → las 25 peticiones del agregado y una de Raw con el token de QA → restaurar. **Se ejecuta entero, de una vez:**
```
apuntar; sleep 5; for K in $KEYS; do printf '%-26s %s\n' "$K" "$(cq -o /dev/null -w '%{http_code}' "$H/api/plugins/telemetry/DEVICE/$G/values/timeseries?keys=$K&startTs=$S&endTs=$E&interval=900000&agg=AVG&limit=50000")"; done; printf '%-26s %s\n' "raw energia_total" "$(cq -o /dev/null -w '%{http_code}' "$H/api/plugins/telemetry/DEVICE/$G/values/timeseries?keys=energia_total&startTs=$S&endTs=$E&orderBy=ASC&limit=50000")"; restaurar
```
- Esperado: `apuntar 200`, el registro con `$G`, **25 + 1 líneas con 403**, `restaurar 200` y el registro como en 0.3.
- Si `restaurar` falla: repite `restaurar` hasta ver 200 y los valores de 0.3.

**2.3** Cabeceras de caché de una respuesta 200 (admin, sin cambiar nada; para H6):
```
ca -D - -o /dev/null "$H/api/plugins/telemetry/DEVICE/$G/values/timeseries?keys=energia_total&startTs=$S&endTs=$E&interval=900000&agg=AVG&limit=50000" | grep -iE '^(HTTP|cache-control|pragma|expires|vary|etag|last-modified)'
```
- Esperado: `HTTP/… 200` y `Cache-Control: no-cache, no-store, max-age=0, must-revalidate` (o equivalente). Si no hay `no-store` y falta `Vary: X-Authorization`, el navegador **podría** reutilizar una respuesta guardada: H6 posible.

**2.4** Cierre de la sesión de `curl`, al terminar el §3 (lo necesita para apuntar y restaurar): `unset TA TQ`.

## 3. Reproducción en Firefox con un perfil limpio

Un perfil nuevo no comparte `localStorage`, cookies ni caché con el perfil habitual. En él **solo** entra el usuario QA, y ninguna otra pestaña de ThingsBoard. El admin trabaja únicamente desde la terminal (§0–§2).

**3.1** Crear y abrir el perfil (no toca el habitual):
```
P=$(mktemp -d); firefox --no-remote --profile "$P" "$H/login" &
```
- Esperado: Firefox nuevo, sin sesiones.

**3.2** Entra como el usuario QA. F12 → **Red**: marca **"Persistir registros"** y **"Desactivar caché"**. Abre `/dashboard/4b8593a0-cdc6-11f1-aa6f-7f75b1e7584b`.

**3.3** En la **Consola** de esa pestaña, antes de exportar (sin red: lee el token que usa la página):
```
(function(){var t=localStorage.jwt_token||'',p=JSON.parse(atob(t.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));console.log('JWT', p.sub, p.scopes, p.customerId, 'fin del token', t.slice(-12));fetch('/api/auth/user',{headers:{'X-Authorization':'Bearer '+t}}).then(function(r){return r.json();}).then(function(u){console.log('auth/user', u.authority, u.customerId&&u.customerId.id, u.email);});})()
```
- Esperado: `JWT <email del usuario QA> ["CUSTOMER_USER"] c13a9950-…` y `auth/user CUSTOMER_USER c13a9950-… <email del usuario QA>`. **Anota el "fin del token".**

**3.4** En la terminal: `apuntar` (registro → `$G`). En Firefox, **recarga** el dashboard (el widget lee el registro al cargar).

**3.5** Exporta: QA Instalación 1 → 15 minutos → Promedio → Último mes → todas las variables → Exportar.

**3.6** En **Red**, filtra por `timeseries`. Para la primera y la última petición, anota:
- **URL** completa y **device id** del URL (debe ser `c636fa00-…`).
- **Estado** (200 o 403).
- Cabecera de petición **X-Authorization**: los últimos 12 caracteres, para compararlos con 3.3.
- En la respuesta: si dice "en caché" o el tamaño es "en caché".

**3.7** En la **Consola**, después de exportar: repite el bloque de 3.3.
- Esperado: el mismo usuario QA y el mismo "fin del token".

**3.8** En la terminal: `restaurar` (registro → `…0002`; comprobar 200 y los valores de 0.3). Cierra ese Firefox y, si quieres, borra el perfil temporal con `rm -r "$P"`.

## 4. Cómo leer los resultados y qué hacer

| §2.2 (`curl`) | §3 (perfil limpio) | Token en la petición (3.6) frente a 3.3/3.7 | Conclusión | Qué hacer |
|---|---|---|---|---|
| 403 | 403, "❌ Error al obtener …" | Igual (QA) | **H3:** V17 corrió con otro token (otra sesión en el mismo perfil). El 200 de V17 no fue del usuario QA. V17 ✔ en el perfil limpio | Sin cambios en la plataforma. Corrijo las guías (B-05 §5, B-06 §5, B-03): **un perfil de navegador por usuario**, nunca dos usuarios de ThingsBoard en el mismo perfil ni en ventanas privadas a la vez; antes de cada prueba de permisos, el bloque de 3.3. Levantar el bloqueo de B-06 |
| 403 | 200 | **Distinto** (no es el de QA) | **H3 confirmada en vivo:** algo en el perfil cambió el token | Como la fila anterior; además, revisar qué abrió otra sesión en ese perfil |
| 403 | 200 | Igual (QA), respuesta "en caché" | **H6** (caché del navegador) | Revisar 2.3. Si falta `no-store`, es un hallazgo de configuración del servidor (proxy o ThingsBoard): propuesta aparte. Repetir con "Desactivar caché" |
| 403 | 200 | Igual (QA), sin caché | **H5:** la petición del navegador difiere de la de `curl` | Comparar el URL de 3.6 con el de 2.2, parámetro por parámetro, y repetirlo con `cq`. Si `curl` reproduce el 200, es un **incidente de seguridad de la plataforma**: congelar pruebas con el registro apuntado a producción, no aplicar B-06 ni B-08, reunir versión de ThingsBoard, URL y respuesta |
| 200 | — | — | Contradice la prueba decisiva del 26: **incidente** | Detener, restaurar y revisar la auditoría (opcional, abajo) y los cambios de permisos del día |

**Auditoría (opcional, para descartar H1 o H2 transitorios entre el 25 y el 26):**
```
ca "$H/api/audit/logs/entity/DEVICE/$G?pageSize=50&page=0&sortProperty=createdTime&sortOrder=DESC" | jq -c '.data[] | {t: (.createdTime/1000 | todate), user: .userName, action: .actionType, status: .actionStatus}'
ca "$H/api/audit/logs/entity/ENTITY_GROUP/c145e3f0-cbdd-11f1-aa6f-7f75b1e7584b?pageSize=50&page=0&sortProperty=createdTime&sortOrder=DESC" | jq -c '.data[] | {t: (.createdTime/1000 | todate), user: .userName, action: .actionType}'
```
- Esperado: en `c636fa00`, sin `ASSIGNED_TO_CUSTOMER`, `CHANGE_OWNER`, `ADDED_TO_ENTITY_GROUP` ni `REMOVED_FROM_ENTITY_GROUP` recientes; en `c145e3f0`, nada posterior a B-04 (2026-10-22). Vacío = auditoría desactivada (anótalo). Útil también para ver qué usuario hizo las peticiones de V17, si la auditoría registra lecturas (normalmente no).

## 5. Resultados

| Paso | Resultado | Notas |
|---|---|---|
| Prueba decisiva (2026-10-26) | ✔ **403 → 403** | Token propio de QA con `curl`. Estado restaurado: `c636fa00` 403. QA Instalación 1 → `c636fa00`: 403 (misma petición, mismo token). Restaurado y comprobado (`{"principal":"…0002"}`). **H4 descartada**; permisos de la plataforma correctos |
| 2.2 (petición exacta) | Pendiente | |
| 2.3 (caché) | Pendiente | |
| 3.3–3.7 (Firefox limpio) | Pendiente | |
| Conclusión | Pendiente | |

## 6. Evidencia en `../sunkuu-tb-config` (`8a1f930`)

- `c636fa00` pertenece a Gocta (`ownerId` = CUSTOMER `79efbf60`) y solo está en su grupo "All" (`79f2cca0`).
- Customer User (`79f4a160`): GENERIC, `ALL: READ, READ_ATTRIBUTES, READ_TELEMETRY`. Read-only (`35af70e0`): GROUP. Sin cambios después de `fcedb2d`.
- "Customer Users" de GONEX QA (`c145e3f0`, último export `f120230`): Customer User genérico + Read-only sobre los grupos de dashboards `570705a0` y `5363c730`. Ningún permiso de ningún grupo apunta a un grupo de dispositivos; ninguno es público.
- Las rule chains no asignan dispositivos, no cambian propietarios ni crean relaciones; el perfil "Instalación" no tiene rule chain propia.
- Límite: el auto-commit no registra grupos, permisos ni propietarios (los de Gocta y Tucán se exportaron por última vez en `d58d79a`). La prueba decisiva cubre ese hueco para GONEX QA → Gocta: hoy el acceso no existe.
- Customers reales (Gocta, Tucán, Pumarinri, Apu Samay): en el repo, solo Customer User genérico y Read-only sobre su propio grupo de dashboards. Si se quiere confirmar el estado actual sin entrar con sus cuentas: `GET /api/userGroup/<id>/groupPermissions` de `79f368e0`, `aa68a710`, `a2266c00` y `6872af20`.
