# Verificación previa a R0 — 2026-10-18

Solo lectura: se analizó `../sunkuu-tb-config` (HEAD `419e891`) y `widgets/work/R0/`. No se tocó producción ni se hicieron llamadas de red.
Los números de línea de los apply son los del archivo `widgets/work/R0/<widget>/apply/controllerScript.js`.

## Veredicto

| Widget | Veredicto | Motivo |
|---|---|---|
| Template Piscina (`5f7b51c0…`) | **GO** | Rollback idéntico a producción; 1 línea eliminada; sin UUIDs muertos. |
| Centro de Exportación (`d88440c0…`) | **GO** | Rollback idéntico; `DASH_TO_INST` consistente con el id de instalación `Pumarinri`; sin UUIDs muertos. |
| Portal de Flota (`6902b8c0…`) | **GO** | Rollback idéntico; id de customer coincide; el conteo de clientes ahora da 3. |

No hay correcciones obligatorias a los apply/rollback. Sí hay 6 observaciones (sección 5), ninguna bloquea.

## 1. Estado del repo

### 1.1 Último commit
`git log -3 --stat`:

| Hash | Autor | Fecha (UTC) | Mensaje | Alcance |
|---|---|---|---|---|
| `419e891` | GONEX TENANT | 2026-10-18 16:54:47 (11:54 Lima) | `BASELINE A+B 2026-10-18 · estado previo a R0 (Overwrite, todos los tipos)` | 6 archivos `device/*.json`, 29 líneas: solo atributos de actividad (`active`, `lastActivityTime`, `inactivityAlarmTime`) |
| `d8f6f57` | Romel Valqui | 2026-10-17 04:26 | auto-commit | `customer/79efbf60…` (nombre y título pasan a mayúsculas) |
| `019baf4` | Romel Valqui | 2026-10-17 04:26 | auto-commit | `customer/aa643a40…` (ídem) |

Es el BASELINE manual. Árbol limpio, `main` al día con `origin/main`.

Desde `71f1603` (11-oct) hasta HEAD no cambió ningún `widget_type`, `dashboard`, `report_template` ni `scheduler_event`:
`git diff 71f1603 HEAD --stat -- . ':!hierarchy' ':!customer'` está vacío. R0 se preparó el 11-oct sobre esa misma base, así que no está desactualizado.

### 1.2 Conteo de entidades (archivos del repo)

| Tipo | Repo | CLAUDE.md / CHANGELOG | Diferencia |
|---|---|---|---|
| widget_type | 5 | 4 widgets + copia DEV | Coincide. La copia DEV `afc86b80` **no está** en el bundle `d726fab0` (el bundle lista 4 fqns: Exportación, Flota, 3EM, Piscina). |
| widgets_bundle | 1 (Sunkuu) | — | — |
| dashboard | 6 | — | `0469dc30` Medidor Tablero Principal, `75c7e760` Centro de Exportación, `8e373390` TG PUMARINRI, `9648fe20` Portal de Flota, `cc2cad90` Piscina Temperada, `e844d080` TG GOCTA |
| customer | 4 | "4 customers reales" | Coincide: Apu Samay `686e4250`, Gocta `79efbf60`, Pumarinri `a2202a70`, Tucán `aa643a40` |
| device | 6 | informe 02: "6 dispositivos de 2 clientes" | Hoy son 6 en 3 customers: Gocta 4, Pumarinri 1, Tucán 1. Apu Samay: 0. |
| asset | **0** (solo `asset_profile` default) | Licencia: 100 activos | Coincide con el estado "Nivel 1 por implementar". |
| device_profile | 6 | — | Incluye `b75859d0` Pro EM50 |
| converter | 5 | — | Incluye `b69ff030` |
| integration | 5 | — | Incluye `e3980900` |
| entity groups (`groups/` + `hierarchy/`) | 11 + 32 | — | — |
| notification_rule / target / template | 11 / 6 / 14 | — | Mayoría son los de fábrica de TB; propios: regla `31dc7d70` "Alarmas Sunkuu — Email", targets `6c645f60` y `7b0fdda0`. |
| report_template | 4 | — | `258ddba0`, `900138f0`, `94757860`, `defa3090` |
| scheduler_event | 4 | — | `8bee5690`, `a6773ef0`, `c72d8880`, `c967cba0` |
| role / rule_chain / tb_resource | 3 / 2 / 4 | — | 4 logos/favicons |

Diferencia relevante: **no hay dispositivo Pro EM50** (Caldero Piscina `shellyproem50-441d6475fe58`), coherente con la nota de `docs/arquitectura/2026-10-propuesta-alta-y-proem.md` L227. Pumarinri no tiene dashboard de Piscina, solo `8e373390`.

### 1.3 Entidades requeridas

| Entidad | Estado |
|---|---|
| 4 customers reales | Presentes |
| Dashboard TG PUMARINRI `8e373390` | Presente (`dashboard/8e373390-c4f5-11f1-b6ce-f79957c72819.json`) |
| Portal de Flota `9648fe20` | Presente |
| Centro de Exportación `75c7e760` | Presente |
| Widgets `373ddd50`, `5f7b51c0`, `6902b8c0`, `d88440c0` | Presentes |
| Copia DEV `afc86b80` | Presente |
| Converter `b69ff030`, integración `e3980900`, perfil `b75859d0` | Presentes |
| Dispositivo `717ae5e0` en `hierarchy/a2202a70…/device/` | Propietario Pumarinri (correcto) |
| Grupo de dashboards Pumarinri `b9410100` | Contiene `75c7e760`, `8e373390`, `9648fe20` |

### 1.4 Qué NO versiona ThingsBoard y dónde está documentado

Según la tabla de CLAUDE.md ("Configuración fuera del Version Control"):

| Configuración | Documentada en `config/` |
|---|---|
| Marca blanca de login | Sí: `config/white-labeling/login-settings.md`, `login-advanced.css` |
| Marca blanca general, plantillas de correo, traducción, menú, seguridad, servidor de correo | **No**: pendiente de capturar por Erick |
| Galería de imágenes | Parcial (`assets/brand/LOGO_SUNKUU_BLANCO.json`). El repo sí exporta 4 `tb_resource` (logos y favicon). |

Los `report_template` y `scheduler_event` **sí** están en el repo (contrario a lo que sugiere la pregunta). No se verificó desde el repo: usuarios, credenciales, telemetría, contraseñas de integraciones. Verificar manualmente en la instancia.

## 2. Validación de R0 contra producción

### 2.1 Rollback vs producción
Se extrajo `entity.descriptor.controllerScript` de cada `widget_type` del repo y se comparó byte a byte:

| Widget | Bytes repo | Bytes rollback | Resultado |
|---|---|---|---|
| Piscina | 52 539 | 52 539 | **Idéntico** |
| Exportación | 39 765 | 39 765 | **Idéntico** (CRLF conservado: 879 líneas con CR) |
| Flota | 42 763 | 42 763 | **Idéntico** |

R0 no se preparó sobre una versión vieja. Solo se compara `controllerScript`; HTML, CSS, esquema y settings de los widgets no se tocan en R0 y no se compararon.

### 2.2 Diff apply vs rollback

**Piscina — −1 línea (L611 del rollback).** Elimina `{n:'TG Pumarinri', d:'32131e90…', c:'79efbf60…'}`, que era la entrada rota: dashboard borrado y customer equivocado (Gocta). La entrada correcta ya existía en L613: `d:'8e373390…', c:'a2202a70…'`. Dentro de alcance.

**Exportación — 2 cambios en `DASH_TO_INST` (L234–239).**
- Quita `'32131e90…': 'tg-pumarinri'`: UUID muerto y además id que no existe (la instalación se llama `Pumarinri`, L168).
- Quita `'fe900bc0…': 'gonex'`: dashboard de prueba borrado; no existe instalación `gonex`. Dentro de alcance (baja de ALTA-01) y figura en la fila R0 del CHANGELOG.
- Agrega `'8e373390…': 'Pumarinri'`. Coincide exacto con `id: 'Pumarinri'` (L168), que es el valor que compara `inst.id === instId` (L244–249).

**Flota — 4 cambios.**
1. L58–60 Pumarinri: letra `T`→`P`, color `#6366F1`→`#059669`, gradiente verde. Antes compartía letra y color con Tucán. Dentro de alcance (A3-3).
2. L341 (`pk-s1`): `'de 2 clientes'` → `'de '+CUSTOMERS.length+' clientes'` (A3-5).
3. L349 (`pk-v1`): `'2'` → conteo de customers con al menos una instalación (3 hoy). Dentro de alcance (A3-5).
4. **Fuera de alcance, benigno:** L6 se elimina el texto residual `f9fa3680-68da-11f1-b6ce-f79957c72819` pegado al comentario de cabecera (`drill-downf9fa3680…`). Es un UUID del customer de prueba "Erick Prueba" y estaba dentro de un comentario `/* */`. No altera el comportamiento. Conviene mencionarlo en el CHANGELOG o en el mensaje de versión.

Ningún cambio toca lógica de medianoche de Lima ni `// DEV-ONLY (FEAT-01)`: los apply de los 3 widgets no contienen `DEV-ONLY` ni `FEAT-01` (y Flota, Exportación y Piscina no tienen la lógica de curva de demanda de FEAT-01, que vive en 3EM). El comportamiento horario de los tres no cambia.

### 2.3 UUIDs en los 3 apply vs dashboards existentes
Se extrajeron todos los UUID de cada apply y se buscaron como archivo/ruta del repo.
- Los 3 apply: **todos existen** (dashboards, customers, dispositivos).
- Búsqueda de `32131e90`, `fe900bc0`, `f9fa3680` en `apply/`: **sin resultados**.

### 2.4 IDs nuevos usados por R0

| Uso | Valor en el apply | Debe igualar | ¿Coincide? |
|---|---|---|---|
| Flota: `INSTALLATIONS[3].customer` (L70) | `'Pumarinri'` | `CUSTOMERS[2].id` (L55) = `'Pumarinri'` | Sí, exacto (mayúscula P) |
| Flota: `CUSTOMERS[2].uuid` | `a2202a70-c454-11f1-b6ce-f79957c72819` | `customer/a2202a70…` | Sí |
| Flota: `dashboardId` / `deviceId` Pumarinri | `8e373390…` / `717ae5e0…` | dashboard y dispositivo del repo | Sí |
| Exportación: `DASH_TO_INST['8e373390…']` | `'Pumarinri'` | `INSTALLATIONS[].id` (L168) | Sí |
| Exportación: `CUSTOMER_MAP['a2202a70…']` | `'PUMARINRI AMAZON LODGE'` | `client` de la instalación (L170) | Sí |
| Piscina NAV (L613) | `d:8e373390…`, `c:a2202a70…` | dashboard y customer | Sí |

Los renombres de Romel del 17-oct (Gocta y Tucán a mayúsculas) **no afectan** a los widgets: comparan por UUID o por etiquetas internas (`CUSTOMER_MAP`), no por el título de ThingsBoard. `/api/customer/<uuid>` solo se usa para ciudad y correo (Flota L257).

### 2.5 Sintaxis
`node --check` sobre los 6 archivos (envueltos en función): **sin errores**.

## 3. Referencias a `8e373390` y al dashboard anterior `32131e90`

**Apuntan a `32131e90` (inexistente):**

| Archivo | Referencia | Cubierto por R0 |
|---|---|---|
| `widget_type/5f7b51c0…` (Piscina) | NAV | Sí |
| `widget_type/d88440c0…` (Exportación) | `DASH_TO_INST` | Sí |
| `report_template/defa3090-47e4-11f1-a6d8-33f75efe8b97.json` | `dashboardId: 32131e90…` | **No** (pendiente CHANGELOG, vence 2026-11-01) |
| `scheduler_event/8bee5690-48d6-11f1-a6d8-33f75efe8b97.json` | Usa la plantilla `defa3090`; no referencia `32131e90` directo | No; se arregla al reapuntar la plantilla |
| `widget_type/afc86b80…` (3EM DEV) | NAV, junto con 3 dashboards de prueba borrados | **No** (ver observación 3) |

**Apuntan a `8e373390` (existe):** `dashboard/8e373390…`, `groups/dashboard/b9410100…_entities.json`, widgets 3EM prod `373ddd50`, Piscina `5f7b51c0`, Flota `6902b8c0`.

Otras referencias a UUID inexistentes en `widget_type/afc86b80` (3EM DEV): `fe900bc0`, `a19db210` (Hotel Prueba), `b6e5d840` (Erick Prueba), y los customers de prueba `3246b8e0`, `f9fa3680`, `b0ab8f20`. Los demás UUID "no presentes" que reporta el escáner en dashboards, informes y planificadores son ids internos de widgets/alias o usuarios y el id nulo del sistema (`13814000-1dd2-11b2-8080-808080808080`); no son referencias rotas.

No se encontraron referencias a `32131e90` en `groups/`, `integration/`, `notification_*` ni `rule_chain/`.

Verificar manualmente en la instancia: que `8bee5690` siga activo (en el repo `enabled: true`) y, tras reapuntar, que la fecha de la próxima ejecución del 1 del mes sea correcta.

## 4. Orden y riesgo

**Orden recomendado: Piscina → Exportación → Flota.** Son independientes en código (cada uno solo lee sus propios arrays); el orden sirve para ir de menor a mayor superficie visible. Dependencias de datos que ya se cumplen en producción: el dashboard `8e373390` y el dispositivo `717ae5e0` existen y están en el grupo de Pumarinri. Los enlaces entre Exportación y Flota no cambian en R0 (ids de dashboard `75c7e760` y `9648fe20` intactos).

| Widget | Tamaño | Riesgo | Cómo verificar tras aplicar (recargar con Ctrl+F5) |
|---|---|---|---|
| Piscina | −1 línea | **Bajo** | Abrir Piscina Temperada como admin: el selector del encabezado debe listar TG Gocta, Medidor Tablero Principal y TG Pumarinri; **no** debe mostrar dos "TG Pumarinri". Al elegir TG Pumarinri debe abrir `8e373390` (no 404). Como usuario de Gocta, TG Pumarinri no debe aparecer. |
| Exportación | 3 líneas en un mapa | **Bajo** | Desde TG PUMARINRI, abrir el Centro de Exportación con `?from=8e373390…` (o con el botón del dashboard): debe quedar preseleccionada la tarjeta "TG Pumarinri". Repetir desde TG GOCTA, Piscina y Medidor Tucán. Entrar como usuario de Pumarinri: solo ve su instalación. |
| Flota | ~4 líneas | **Bajo–medio** (es el widget que ve todo el portafolio) | Como admin, capa 0: la tarjeta "Clientes activos" dice **3** y el subtítulo "de 3 clientes"; la fila de Pumarinri muestra avatar **P** verde, distinto del de Tucán (T violeta). Abrir el detalle de Pumarinri: avatar y borde con el mismo verde, KPIs cargan. Como usuario de customer: ve su capa sin errores en consola (F12). |

Cómo revertir: pegar el `rollback/controllerScript.js` correspondiente (idéntico al actual). Aplicar un widget por vez y guardar; el auto-commit deja un commit por widget.

## 5. Observaciones (ninguna bloquea R0)

1. **Flota `pk-s2` hardcodeado** (L342): `'de 4 instalaciones monitoreadas'`. Hoy coincide (4 instalaciones), pero R0 arregla el conteo de clientes y deja este número fijo. Si se da de alta otra instalación se desfasa. Decisión de Erick: ¿incluirlo en R0 con `INSTALLATIONS.length` o dejarlo para el Nivel 1?
2. **Cambio fuera de alcance en Flota L6** (comentario con UUID residual). Benigno; mencionarlo en el commit.
3. **Copia DEV 3EM (`afc86b80`) conserva en su NAV** `32131e90` y tres dashboards de prueba borrados. R0 no la toca. Ya lo registra A3-10 de la propuesta de arquitectura como de impacto bajo. No aplicar en esa copia nada que afecte `// DEV-ONLY (FEAT-01)`.
4. **Plantilla de informe `defa3090`** sigue apuntando a `32131e90`: el informe mensual de Pumarinri saldrá roto hasta reapuntarlo (pendiente existente, vence 2026-11-01).
5. **Exportación mezcla estilos de id** (`tg-gocta`, `piscina-temperada`, `medidor-tucan` vs `Pumarinri`). Funciona; cambiarlo implicaría tocar más líneas, así que no se propone.
6. **Customers renombrados por Romel a mayúsculas el 17-oct** (Gocta, Tucán): sin impacto en los widgets, pero los documentos del repo y los nombres de los grupos de dashboards y de los `notification_target` siguen con el formato anterior.

## 6. Verificar manualmente en la instancia

- Que en producción el `controllerScript` de los 3 widgets siga siendo el del repo (por si Romel guardó algo después de las 11:54 Lima del 18-oct): abrir cada widget en el editor y comprobar la fecha de modificación, o crear otra versión y revisar `git diff`.
- Que `fe900bc0` y `32131e90` ya no existan como dashboards (el repo así lo indica desde `71f1603`).
- Que el cupo de licencia siga bajo 100 dispositivos / 100 activos (Administración → Licencia). El repo muestra 6 dispositivos y 0 activos.
- Los pasos visuales de la tabla de la sección 4.

## 7. Siguiente paso tras aplicar

Después de aplicar: `git pull` en `../sunkuu-tb-config`, `git show --stat <hash>` (esperado: 3 `widget_type`, uno por auto-commit), y fila R0 en `CHANGELOG.md` con esos hashes. Esta verificación no modifica el CHANGELOG ni crea commits.
