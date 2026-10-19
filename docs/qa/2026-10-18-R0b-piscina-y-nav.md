# R0b — NAV de Piscina y revisión de menús entre dashboards — 2026-10-18

Solo lectura sobre `../sunkuu-tb-config` (HEAD `ed52362`, tras `git pull` de Erick). Sin llamadas de red ni escritura fuera de `sunkuu-TB`.
Los números de línea de los widgets son los del `controllerScript` extraído de HEAD (`entity.descriptor.controllerScript`).

## Veredicto

| Tema | Veredicto |
|---|---|
| Validación de `ed52362` (R0 Piscina) | **OK**: idéntico al apply de R0; solo cambió la línea esperada. |
| **R0b (Piscina, quitar TG Pumarinri y Medidor Tablero Principal del NAV)** | **GO**, con 2 puntos a decidir/verificar por Erick (sección 6). |
| Template 3EM (`373ddd50`) | **El problema existe** para el admin (no para usuarios de customer). Sin cambios preparados. |
| Flota / Exportación | Sin NAV entre dashboards que viole la regla; 1 hallazgo no relacionado en Exportación (ya cubierto por el apply de R0). |

## 1. Pertenencia de dashboards (repo vs tabla de la instancia)

Los dashboards no traen propietario en su JSON (`dashboard/*.json` sin `ownerId`/`customerId`) y `hierarchy/<customer>/` no contiene ningún dashboard: pertenecen al tenant y se asignan por **grupos de dashboards de nivel tenant**, uno por customer (`groups/dashboard/*_entities.json`):

| Grupo (`groups/dashboard/`) | Dashboards |
|---|---|
| `e044b8d0…` Gocta Andes Lodge | TG GOCTA `e844d080`, Piscina Temperada `cc2cad90`, Portal de Flota `9648fe20`, Centro de Exportación `75c7e760` |
| `ab786010…` Tucán Suites Aparthotel | Medidor Tablero Principal `0469dc30`, Portal de Flota, Centro de Exportación |
| `b9410100…` PUMARINRI AMAZON LODGE | TG PUMARINRI `8e373390`, Portal de Flota, Centro de Exportación |

**Coincide exactamente con la tabla de Tableros.** Sin discrepancias. Apu Samay (`686e4250`): sin dashboards ni dispositivos en el repo (ignorado).
Widget usado por dashboard (por `fqn` en el JSON): TG GOCTA, TG PUMARINRI y Medidor → `sunkuu_template_3em`; Piscina → `sunkuu_template_piscina`; Flota y Exportación → sus widgets.

Customers (`customer/*.json`): Gocta `79efbf60`, Tucán `aa643a40`, Pumarinri `a2202a70`.

## 2. Validación de `ed52362`

`git show ed52362`: autor GONEX TENANT, `auto-commit at 2026-10-18T19:57:16Z`, 1 archivo (`widget_type/5f7b51c0….json`), 3 inserciones / 2 eliminaciones.

| Línea | Qué es |
|---|---|
| `-  "controllerScript" : "…"` / `+  "controllerScript" : "…"` | **Cambio real.** Una sola línea del JSON (el script va en una cadena). Comparando el script antes y después (`ed52362^` vs `ed52362`, extraído con Python): la única diferencia es la eliminación de la línea 611 previa: `{n:'TG Pumarinri', d:'32131e90-5aaa-11f1-a6d8-33f75efe8b97', c:'79efbf60-2ef0-11f1-a6d8-33f75efe8b97'},`. |
| `-  }` / `+  },` | **Metadato del JSON.** Cierre del objeto `entity`; ahora lleva coma porque se añadió una clave después. |
| `+  "calculatedFields" : [ ]` | **Metadato del JSON.** Clave nueva que el export de ThingsBoard agrega al reguardar (no existía en el JSON anterior). Sin efecto funcional. |

Comparando todas las claves aplanadas del JSON antes/después, solo difieren `calculatedFields` (nueva) y `entity.descriptor.controllerScript`. No cambió versión, fechas, HTML, CSS, settings ni atributos.

Comparación con el apply de R0: `cmp` del script de HEAD contra `widgets/work/R0/sunkuu_template_piscina/apply/controllerScript.js` → **idéntico byte a byte** (0 CR; 762 líneas). El script previo a `ed52362` es idéntico a `R0/.../rollback/controllerScript.js`.

## 3. NAV de Piscina en HEAD (líneas 609–614)

| # | Entrada | Dashboard | Customer en la entrada (`c`) | Dueño real del dashboard | ¿Cumple la regla? |
|---|---|---|---|---|---|
| 1 | TG Gocta | `e844d080` | `79efbf60` (Gocta) | Gocta | Sí, se queda |
| 2 | Piscina Temperada | `cc2cad90` | `79efbf60` (Gocta) | Gocta | Sí, se queda (es la propia) |
| 3 | Medidor Tablero Principal | `0469dc30` | `aa643a40` (Tucán) | Tucán | **No** → eliminar |
| 4 | TG Pumarinri | `8e373390` | `a2202a70` (Pumarinri) | Pumarinri | **No** → eliminar |

Ninguna otra entrada viola la regla. Las `c` coinciden con el dueño real en las 4 entradas.

### Cómo decide el código qué mostrar (líneas 607–631)
- `isCu = authority==='CUSTOMER_USER'`; `opts = NAV` sin el dashboard actual, y **solo si es usuario de customer** además filtrado por `i.c===cuId`. Para el admin no hay filtro: ve todo el NAV.
- Por eso el problema solo se manifiesta para el admin (el usuario de Gocta ya no veía Tucán/Pumarinri). Con R0b el admin ve lo mismo que el usuario de Gocta.
- Si `opts` está vacío **y** no hay entrada actual → se oculta el caret. Con la entrada actual presente el desplegable se muestra igual.

### Dependencias fuera del NAV
- `grep` de `umarinri|ucán|0469dc30|8e373390|a2202a70|aa643a40` en el script: solo aparecen en las líneas 612–613. Sin referencias hardcodeadas a Pumarinri/Tucán en otras partes.
- Enlaces de regreso: `btn-fleet` (línea 100) → Portal de Flota `9648fe20` (compartido); Exportación (línea 101) → `EXPORT_DASH?from=<dashboard actual>`. No dependen del NAV.
- No hay mapas de dashboards ni lógica que asuma un número de entradas u orden (solo `filter`, `map` y `[0]`).
- **Con NAV de 2 entradas (TG Gocta + Piscina):** en Piscina, `curInst` = Piscina → el desplegable muestra "✓ Piscina Temperada · Estás aquí" + 1 ítem (TG Gocta). No se oculta ni se rompe. El caso "una sola entrada" no ocurre con R0b.
- Caso límite: si el widget Piscina se usara en un dashboard fuera del NAV (p. ej. una copia DEV), `curInst` queda `undefined` y el desplegable lista las 2 entradas sin "Estás aquí". Hoy, según el repo, solo `cc2cad90` lo usa.
- **Cambio mínimo opcional (NO incluido):** ninguno necesario. Solo si se quisiera ocultar el selector cuando no haya `opts` (p. ej. clientes de una sola instalación), cambiar la condición de la línea 620 a `if(opts.length===0){…}`. Es un cambio de comportamiento que afecta también al 3EM; **decide Erick** y va como cambio aparte.

## 4. Artefactos de R0b — `widgets/work/R0b/sunkuu_template_piscina/`

| Archivo | Contenido |
|---|---|
| `apply/controllerScript.js` | HEAD (`ed52362`) menos las entradas de Medidor y TG Pumarinri. |
| `rollback/controllerScript.js` | HEAD (`ed52362`) = producción hoy. Verificado con `cmp` contra el script extraído del JSON. |
| `baseline/controllerScript.js` | Copia de `widgets/work/R0/sunkuu_template_piscina/rollback/controllerScript.js` (estado original anterior a R0, con la entrada rota `32131e90`). |

`node --check` en los tres: OK.

### Diff exacto R0b vs producción (`diff rollback apply`)
```diff
611,613c611
<       {n:'Piscina Temperada',        d:'cc2cad90-5ad5-11f1-a6d8-33f75efe8b97',c:'79efbf60-2ef0-11f1-a6d8-33f75efe8b97'},
<       {n:'Medidor Tablero Principal',d:'0469dc30-5aab-11f1-a6d8-33f75efe8b97',c:'aa643a40-2ef0-11f1-a6d8-33f75efe8b97'},
<       {n:'TG Pumarinri',            d:'8e373390-c4f5-11f1-b6ce-f79957c72819',c:'a2202a70-c454-11f1-b6ce-f79957c72819'}
---
>       {n:'Piscina Temperada',        d:'cc2cad90-5ad5-11f1-a6d8-33f75efe8b97',c:'79efbf60-2ef0-11f1-a6d8-33f75efe8b97'}
```
Equivale a eliminar las dos entradas y quitar la coma final de "Piscina Temperada", que pasa a ser la última. Esa coma es el único carácter modificado en una línea que se conserva (una coma final en un array sería válida en JS, pero se quitó por limpieza; si prefieres un diff de solo eliminaciones, se puede dejar).
Saltos de línea y resto del archivo sin cambios (rollback 762 líneas, apply 760; baseline 763).

## 5. Checklist visual para R0b

Después de que Erick aplique (los pasos 1–2 con hard refresh / Ctrl+F5):

**Admin (tenant)**
1. Abrir Piscina Temperada `cc2cad90`. Clic en la insignia de instalación (arriba a la izquierda, junto al logo).
   - Debe mostrar: título "Instalaciones", "✓ Piscina Temperada — Estás aquí" y un único ítem "TG Gocta".
   - No debe aparecer Medidor Tablero Principal ni TG Pumarinri.
2. Clic en "TG Gocta" → navega a `/dashboard/e844d080…`.
3. En Piscina: "← Inicio" lleva a Portal de Flota; "Exportación" abre Centro de Exportación con `?from=cc2cad90…` y vuelve con "Volver".
4. Pestañas Resumen/Temperatura/Equipos/Consumo/Alertas, tarjetas de datos y botón PDF siguen funcionando; consola del navegador sin errores nuevos (F12).
5. Cerrar el desplegable haciendo clic fuera.

**Usuario de Gocta (customer)**
6. Iniciar sesión (o "Iniciar sesión como") con un usuario de GOCTA ANDES LODGE y abrir Piscina: mismo menú que el admin (Piscina "Estás aquí" + TG Gocta). Igual que antes de R0b.
7. Que "TG Gocta" y "Inicio" abran sin error de permisos.

**No regresión**
8. En TG GOCTA (widget 3EM, sin cambios), el desplegable sigue funcionando para el usuario de Gocta (Piscina). *Al admin le seguirá mostrando Medidor y TG Pumarinri hasta que se corrija el 3EM (sección 7).*

## 6. Riesgos y puntos a decidir / verificar

1. **El 3EM mantiene la violación del admin** (sección 7). R0b la corrige solo en Piscina; no es un riesgo de R0b, pero el menú del admin seguirá siendo inconsistente entre Piscina y 3EM hasta corregir el 3EM. *Decide Erick* si se hace en el mismo paso o aparte.
2. **Coma final eliminada** (sección 4): decisión de Erick si se mantiene.
3. **Verificar manualmente en la instancia:** la tabla de Tableros (grupos asignados a cada customer) coincide con el repo a la fecha de `ed52362`; si Romel cambió grupos después, el repo no lo registra (el auto-commit no cubre cambios de grupos).
4. Riesgo técnico bajo: cambio de 3 líneas de datos dentro de una IIFE; sin lógica tocada. Rollback inmediato con `rollback/controllerScript.js`.
5. Licencia/cupos: no aplica (no se crean dispositivos ni activos).

## 7. Template 3EM (`373ddd50`) — solo lectura, sin cambios preparados

NAV en `3em_head.js` líneas 1195–1200:

| # | Entrada | Dashboard | `c` | Dueño real |
|---|---|---|---|---|
| 1 | TG Gocta | `e844d080` | Gocta | Gocta |
| 2 | Piscina Temperada | `cc2cad90` | Gocta | Gocta |
| 3 | Medidor Tablero Principal | `0469dc30` | Tucán | Tucán |
| 4 | TG Pumarinri | `8e373390` | Pumarinri | Pumarinri |

**Cómo decide qué mostrar** (líneas 1201–1205): igual que en Piscina: `opts = NAV` sin el dashboard actual y, **solo si el usuario es CUSTOMER_USER**, filtrado por `i.c===cuId`. No filtra por el customer dueño del dashboard actual. Para el admin, muestra todo.

**Qué ve hoy cada caso**

| Dashboard (widget 3EM) | Admin ve | Violaciones del admin | Usuario del customer dueño ve |
|---|---|---|---|
| TG GOCTA `e844d080` | Piscina, Medidor, TG Pumarinri | **Medidor (Tucán), TG Pumarinri** | Piscina (OK) |
| TG PUMARINRI `8e373390` | TG Gocta, Piscina, Medidor | **Las 3** (no debería ver ninguna) | Solo "✓ TG Pumarinri — Estás aquí", sin ítems |
| Medidor Tablero Principal `0469dc30` | TG Gocta, Piscina, TG Pumarinri | **Las 3** | Solo "✓ Medidor … — Estás aquí", sin ítems |

**Conclusión:** el problema **existe** para el admin en los 3 dashboards (evidencia: líneas 1196–1204: NAV con 4 entradas y filtro por customer solo si `isCu`). Para usuarios de customer el filtro actual ya cumple la regla.
Observación: para Tucán y Pumarinri el desplegable se muestra con solo la fila "Estás aquí" (el caret solo se oculta si no hay `opts` **y** no hay entrada actual). Es cosmético; *verificar visualmente en la instancia si queda aceptable*.

**Opciones para una corrección futura (no preparada, a decidir por Erick):**
- A. Filtrar el NAV por el customer dueño del dashboard actual: `curC` = `c` de la entrada con `d===curD`; `opts = NAV.filter(i => i.d!==curD && i.c===curC)`, para admin y customer. Un cambio mínimo, sin tabla nueva, pero depende de que cada dashboard esté en el NAV.
- B. Dejar un NAV por dashboard (más duplicación).
- Nota: el 3EM es compartido por 3 dashboards y la copia DEV `afc86b80` no se toca.

## 8. Portal de Flota (`6902b8c0`) y Centro de Exportación (`d88440c0`)

- **Flota:** no hay desplegable de navegación entre dashboards. `INSTALLATIONS` (líneas 67–70) mapea cada instalación a su `dashboardId` y se muestra por customer: el usuario de customer ve solo las de su `customer` (`CUST_UUID_MAP`, líneas 239–246); el admin elige un cliente (capa 0 solo admin) y la capa 1 filtra `i.customer===selectedClient.id`. No hay mezcla de customers dentro de una vista. **Sin violaciones.**
- **Exportación:** no hay NAV. `VISIBLE_INSTALLATIONS` (líneas 228–231) filtra por `client` para usuarios de customer según `CUSTOMER_MAP` (los 3 customers están). Botón "Volver" usa `?from=` (por defecto Flota). **Sin violaciones de la regla.**
  - Observación (distinta de la regla): en producción `DASH_TO_INST` (líneas 235–240) aún trae `32131e90…→'tg-pumarinri'` (UUID muerto) y `fe900bc0→'gonex'`, y no tiene `8e373390`, por lo que la preselección desde TG PUMARINRI falla. El apply de R0 de Exportación ya corrige esto (verificado: el `rollback` de R0 coincide con producción y el apply solo toca esas líneas). Si se aplica R0, esto queda resuelto.
  - Observación: si un usuario de customer no está en `CUSTOMER_MAP`, `clientLabel` queda `null` y se muestran **todas** las instalaciones (fail-open). Hoy los 3 customers están en el mapa; un customer nuevo requeriría añadirse. *No es violación actual.*
- Los rollback de R0 de Flota y Exportación coinciden byte a byte con HEAD (producción), por lo que su base sigue vigente tras `ed52362`.

## 9. Borrador de fila para CHANGELOG (NO escrito en CHANGELOG.md)

| Fecha | ID | Tipo | Horas | Cambio | Componentes | Commit sunkuu-tb-config | Commit sunkuu-TB | Estado |
|---|---|---|---|---|---|---|---|---|
| 2026-10-18 | R0b | Correctivo | | NAV de Piscina limitado a las instalaciones de su customer (Gocta): se eliminan "Medidor Tablero Principal" (Tucán) y "TG Pumarinri" (solo `controllerScript`). Regla: un NAV solo muestra los dashboards del customer dueño del dashboard que lo contiene. | widget_type Template Piscina | `<hash auto-commit>` | `<hash>` | Preparado |

(R0 de Piscina está aplicado con auto-commit `ed52362`; para el resto de R0 — Flota y Exportación — no hay hash aún.)

## 10. Qué verificar manualmente en la instancia
1. Grupos de dashboards por customer en producción (coinciden con la tabla de Tableros).
2. Checklist visual de la sección 5 tras aplicar.
3. Con qué usuario se ven los desplegables de una sola fila en Tucán/Pumarinri (3EM) y si es aceptable.
4. Que no haya otros dashboards con los widgets Piscina/3EM además de los listados (el repo solo muestra uno por widget por dashboard).
