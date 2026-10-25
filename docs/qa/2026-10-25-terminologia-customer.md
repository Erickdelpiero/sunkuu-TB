# Terminología: "Customer" para la entidad de ThingsBoard

Fecha: 2026-10-25 · Base: `../sunkuu-tb-config` `6cbab41` (solo lectura) · Alcance: textos **visibles** (literales del JS y texto del HTML; sin comentarios ni identificadores como `f-cliente` o `.inst-client`).

## Criterio

En la plataforma, el menú dice **"Customers"**, sin traducir. Los textos de los widgets usan el mismo término cuando se refieren a la entidad de ThingsBoard:

| Se refiere a | Texto | Ejemplo |
|---|---|---|
| La entidad (propietario, lista, filtro, grupos) | **Customer / Customers** como etiqueta o título; **customer / customers** dentro de una frase. Género masculino: "el customer", "los customers" | "Todos los customers", "Fuga entre customers" |
| Las personas que entran con un usuario del customer | **los usuarios del customer** | "Los usuarios del customer no ven el panel de parámetros." |
| Nombres de ThingsBoard | Sin traducir y entre comillas | "Customer Users", "Customer User", "Customer Administrators" |

Así ya escribe B-03 sus textos nuevos (columna "Customer", campo "Customer", "El customer no verá este dashboard…"). Los textos que ve el usuario final de un customer (un hotel) no se cambian sin acuerdo: para esa persona, la entidad es "su cuenta" o "sus instalaciones" (Flota ya usa "Tus instalaciones").

## Inventario

### B-03 · Sunkuu — Registro de instalaciones (`c1e90290`, = `widgets/work/B-03/widget/`, solo `TENANT_ADMIN`)

Cuatro textos del JS con "cliente". El HTML no tiene ninguno.

| JS | Texto actual | Se refiere a | Propuesta |
|---|---|---|---|
| L347 | "… no tiene un rol genérico de cliente: sus usuarios no verían nada." | Rol genérico de ThingsBoard ("Customer User") | "… no tiene un rol genérico (como "Customer User"): sus usuarios no verían nada." |
| L360 | "Fuga entre clientes: el dashboard está en el grupo …" | Entidad | "Fuga entre customers: …" |
| L495 | "El cliente verá el panel de parámetros en solo lectura (FIX-02)." / "El cliente no ve el panel de parámetros." | Personas | "Los usuarios del customer verán …" / "Los usuarios del customer no ven …" |
| L612 | Casilla "Mostrar parámetros al cliente (solo lectura)" | Personas | "Mostrar parámetros a los usuarios del customer (solo lectura)" |

**Estado:** preparado como **R1**, que se aplica **después** del checklist C1–C17 (`docs/qa/2026-10-25-B-03-guion.md` §7). El checklist se ejecuta con los textos actuales. Material en `widgets/work/B-03/R1/`:
- `apply/`: el JS con los 4 textos (5 literales), más cambios que no son de terminología: el motivo "sin tipo", un comentario sobre el orden de la validación y las mejoras R1a–R1c del guion §7. `rollback/` = `widget/`.
- `_build/build_r1.py`: `generar`, `base` y `verificar`. Aborta si queda algún texto visible con "cliente".
- `_test/run_tests.sh`: pruebas de B-03 contra `R1/apply/` (**32 de 32** en node y **24 de 24** en la interfaz) y **8 de 8** propias de R1 (`test_r1.js`).
- `widgets/work/B-03/widget/` no se modificó.

### B-05 · DEV — Centro de Exportación (`widgets/work/B-05/apply/`)

| JS | Texto anterior | Se refiere a | Ahora |
|---|---|---|---|
| L122 | Chip "Todos los clientes" | Entidad (filtro E3 por propietario; solo admin) | **"Todos los customers"** |

**Estado:** **aplicado en el apply** (B-05 aún no está en ThingsBoard). Pruebas: 40 de 40 + 3 de 3 (comparación con producción). El resto del widget no tenía textos visibles con "cliente". El JS de producción `d88440c0` es igual al DEV: el cambio llega en B-08.

### Flota · DEV — Portal de Flota (`f2b42860`), anotado para **B-06**

Mismos textos que producción (`6902b8c0`). Ver la columna "Lo ve" antes de cambiar.

| Ubicación | Texto actual | Lo ve | Propuesta |
|---|---|---|---|
| HTML L15 | Botón "← Clientes" (migas, Capa 1) | Admin | "← Customers" |
| HTML L53 · JS L341 | KPI "Clientes activos" (Capa 0) | Admin | "Customers activos" |
| HTML L54 · JS L341 | "de 2 clientes" (Capa 0) | Admin | "de N customers". El **2 está fijo** en el código; en B-06 sale del registro |
| HTML L75 | Título "Clientes" (Capa 0) | Admin | "Customers" |
| HTML L76 | "Vista de gestión · Selecciona un cliente para ver sus instalaciones" | Admin | "… Selecciona un customer para ver sus instalaciones" |
| JS L416 | "Nuevo cliente" · "Alta guiada de cliente, dispositivos y dashboards" | Admin | "Nuevo customer" · "Alta guiada de customer, dispositivos y dashboards". En B-06 se decide si este marcador sigue o lo reemplaza el botón "Administración" |
| JS L575 | "en este cliente" (KPI de Capa 1, rama admin) | Admin | "en este customer" |
| JS L577 | "Potencia cliente" (KPI de Capa 1, rama admin) | Admin | "Potencia del customer" |
| HTML L110 | "Potencia cliente" (cabecera de Capa 1, `chk-lbl`) | **Por verificar en B-06**: la cabecera puede mostrarse también al usuario del customer | Admin: "Potencia del customer". Si la ve el usuario final: "Potencia actual", como su KPI (`renderLayer1KPIs` rama `isCustomerUser`) |

### 3EM y Piscina · DEV — Template 3EM (`3b5205e0`) y DEV — Template Piscina (`aff83c70`), anotado para **FIX-02**

Sin textos visibles con "cliente". Piscina solo lo tiene en el comentario `// DEV-ONLY (B-04): bloquea escritura en dispositivo de cliente`, que no se ve; no se cambia. **FIX-02** revisa los textos nuevos que agregue (NAV, panel de parámetros con `mostrar_parametros`) con este criterio.

## Pendientes

| Dónde | Qué | Cuándo |
|---|---|---|
| B-03 | R1 (4 textos) | Después de C17 (guion §7) |
| B-05 | Ya en el apply | Con B-05 en DEV; en producción, en B-08 |
| Flota | 9 textos de la tabla; confirmar quién ve "Potencia cliente" de la cabecera | B-06 |
| 3EM / Piscina | Nada hoy; aplicar el criterio a los textos nuevos | FIX-02 |
| Documentación | Las guías y los informes siguen usando "cliente" en el sentido comercial (los hoteles de Sunkuu). No se cambian | — |
