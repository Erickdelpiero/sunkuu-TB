# Mapa de widgets Sunkuu 360

> **Referencia histórica; la fuente de verdad es `../sunkuu-tb-config`.**

Documento de solo lectura: describe los 4 *widget types* exportados de ThingsBoard en `widgets/`. No se modificó ningún JSON.

## Convención de referencias

Cada JSON es un widget type con `descriptor.templateHtml`, `descriptor.templateCss` y `descriptor.controllerScript`. Las líneas citadas son **relativas a cada campo extraído** (línea 1 = primera línea del campo), no a la línea del JSON, que guarda cada campo en una sola cadena escapada.

| Alias | Archivo | fqn | Resources |
|---|---|---|---|
| Exportación | `widgets/centro_de_exportación_-_sunkuu.json` | `centro_de_exportaci_n_sunkuu` | — |
| Flota | `widgets/sunkuu_—_portal_de_flota.json` | `sunkuu_portal_de_flota` | — |
| **Template 3EM** | `widgets/sunkuu_—_template_3em.json` | `sunkuu_template_3em` | Chart.js 4.4.0 (jsdelivr), jsPDF 2.5.1 (cdnjs) |
| Piscina | `widgets/sunkuu_—_template_piscina.json` | `sunkuu_template_piscina` | Chart.js 4.4.0 (jsdelivr) |

---

## 1. Ubicación del logo

El logo **no es una imagen**: es un SVG inline (dos rectángulos redondeados, blanco y `#00EBC8`) más un texto `sunKUU360` en HTML. No hay `<img>`, `data:image` ni `background-image`. El mismo SVG se repite en los 4 widgets (`viewBox="0 0 26 32"`).

```html
<svg width="20" height="26" viewBox="0 0 26 32">
  <rect x="4" y="1" width="22" height="13" rx="5" fill="white" opacity=".95"/>
  <rect x="0" y="17" width="22" height="13" rx="5" fill="#00EBC8"/>
</svg>
```

| Widget | HTML (`templateHtml`) | CSS (`templateCss`) | JS (`controllerScript`) |
|---|---|---|---|
| **Template 3EM** | L9–L14: `div.hdr-logo` > `svg` + `span.logo-text` (`sun<span.logo-teal>KUU</span><span.logo-sub>360</span>`) | L52 `.hdr-logo`, L53 `.logo-text`, L54 `.logo-teal`, L55 `.logo-sub` | L120–L126: `document.querySelector('.hdr-logo')`, click → dashboard de flota |
| **Flota** | L9–L14: `div.pf-logo` > `svg` + `span` (`.lt`, `.ls`), svg 20×26 | L32 `.pf-logo`, L33 `.lt`, L34 `.ls` | Sin handler de click (solo `Logout`, L295–L302) |
| **Exportación** | L11–L16: `div#exp-logo` > `svg` (22×28) + `span#exp-logo-text` | L51–L56 `#exp-logo`, L57–L62 `#exp-logo-text`, L63–L64 `.logo-teal/.logo-sub`; responsive L484–L486 | L419–L422: `getElementById('exp-logo')`, click → inicio |
| **Piscina** | L13–L18: `div.sp-logo` > `svg` (22×28) + `span` (`.logo-t`, `.logo-s`) | L32 `.sp-logo`, L33 `.logo-t`, L34 `.logo-s` | L113: `querySelector('.sp-logo')`, click → inicio |

Detalles:

- Color de acento `var(--teal)` (`#00EBC8`) en "KUU"; "360" va en `rgba(255,255,255,.35)`.
- Comportamiento de click (3EM L120–L126, igual en Exportación y Piscina):

```js
var logo = document.querySelector('.hdr-logo');
if(logo){ logo.style.cursor='pointer'; logo.addEventListener('click',function(){
  window.location.href='/dashboard/9648fe20-5ae6-11f1-a6d8-33f75efe8b97';
}); }
```

- El UUID `9648fe20-5ae6-11f1-a6d8-33f75efe8b97` (dashboard de inicio/flota) está hardcodeado en 3EM, Piscina y Exportación.
- Cambiar el logo implica editar **4 copias** (HTML y CSS en cada widget); no hay componente compartido.

---

## 2. Template 3EM: gráficos, rangos y telemetría

### 2.1 Librería de gráficos

**Chart.js 4.4.0** (`chart.umd.min.js`), cargado como Resource del widget (cabecera del script, L13–L15). jsPDF 2.5.1 se usa solo para el informe PDF.

Como el script puede ejecutarse antes de que cargue el recurso, hay un guard (L67–L76):

```js
function whenChart(cb) {
  if (typeof Chart !== 'undefined') { cb(); return; }
  var attempts = 0;
  var wait = setInterval(function() {
    attempts++;
    if (typeof Chart !== 'undefined') { clearInterval(wait); cb(); }
    else if (attempts > 40) { clearInterval(wait); console.warn('[3EM] Chart.js timeout'); }
  }, 250);
}
```

Gráficos (objeto `CH`; todos se destruyen antes de recrearse y en `onDestroy`, L1120–L1123):

| Instancia | Canvas | Tipo | Función | Línea |
|---|---|---|---|---|
| `CH.demand` | `#demand-canvas` | line (Fase A/B/C + Total) | `renderSec02` | L641 |
| `CH.dist` | (canvas de distribución) | — | `renderSec03` | L683 |
| `CH.energy` | `#energy-canvas` | line apilado por fase | `renderSec04` | L752 |
| `CH.monthly` | `#monthly-canvas` | bar | `renderCostCard` | L834 |
| `CH.fp` | (canvas FP) | line | `renderSec05Chart` | L877 |

### 2.2 Selector de rangos

Solo el gráfico `#energy-canvas` ("Potencia activa acumulada por fase") tiene selector. HTML (`templateHtml` L262–L268):

```html
<div class="t-btns" id="anal-time-btns">
  <button class="tbtn active" data-p="hoy">Hoy</button>
  <button class="tbtn" data-p="semana">Semana</button>
  <button class="tbtn" data-p="mes">Mes</button>
</div>
```

Lógica en `renderSec04` (L772–L793). Los botones se clonan con `cloneNode` para evitar listeners duplicados al re-renderizar:

- `hoy`: **no hace request nuevo**; reutiliza `D.demand` (las últimas 24 h ya cargadas por `loadDemand`).
- `semana` / `mes`: `days = period==='semana' ? 7 : 30` y nueva consulta:

```js
api(tsUrl(keys,daysAgo(days),nowMs(),86400000,'AVG',50), function(d){ ... });
```

Etiquetas: `HH:00` para "Hoy"; `DD Mmm` (con `MESES=['Ene',...]`) para semana/mes.

Nota: "Hoy" en realidad son las **últimas 24 h** (`daysAgo(1)`), no el día calendario.

### 2.3 Cálculo de `startTs` / `endTs`

Helpers de tiempo (L78–L82), todos basados en el reloj y zona del **navegador**:

```js
function nowMs()      { return Date.now(); }
function todayStart() { var d=new Date(); d.setHours(0,0,0,0); return d.getTime(); }
function ydayStart()  { return todayStart()-86400000; }
function daysAgo(n)   { return nowMs()-n*86400000; }
```

- `endTs` es casi siempre `nowMs()`.
- `startTs` es `todayStart()` (medianoche local) o `daysAgo(n)` (ventana móvil, no alineada a medianoche).
- Excepción: `loadWeekComparison` usa límites alineados a medianoche (ver 3.2) y `endTs = weekAgoEnd + 86400000`.

### 2.4 Endpoint y parámetros

Constructor único (L85–L91):

```js
function tsUrl(keys,startTs,endTs,interval,agg,limit){
  var u='/api/plugins/telemetry/DEVICE/'+DEVICE_ID+'/values/timeseries?keys='+keys;
  if(startTs!==undefined) u+='&startTs='+startTs+'&endTs='+endTs;
  if(interval) u+='&interval='+interval+'&agg='+(agg||'AVG');
  if(limit)    u+='&limit='+limit;
  return u;
}
```

Autenticación (L92–L98): `fetch(url, {headers:{'X-Authorization':'Bearer '+localStorage.jwt_token}})`.

Si no se pasa `startTs` se pide el **último valor** (así funciona `loadLatest`). Llamadas reales:

| Loader | Keys | startTs → endTs | interval | agg | limit |
|---|---|---|---|---|---|
| `loadLatest` (L256) | `ALL_KEYS` (25 keys, L246–L255) | — | — | — | — (refresco cada 30 s, L1119) |
| `loadEnergyDaily` (L272) | `energia_total` | `daysAgo(2)` → `nowMs()` | 3 600 000 (1 h) | MAX | 200 |
| `loadWeekComparison` (L290) | `energia_total` | `weekAgoStart` → `weekAgoEnd+86400000` | 3 600 000 | MAX | 50 |
| `load30DayAverage` (L303) | `energia_total` | `daysAgo(31)` → `todayStart()` | 86 400 000 (1 d) | MAX | 35 |
| `loadVoltageRange` (L332) | `voltaje_fase_a/b/c` | `todayStart()` → `nowMs()` | `max(now-todayStart,60000)` | MIN y MAX (2 requests) | 5 |
| `loadDemand` (L339) | `potencia_activa_total` + `_fase_a/b/c` | `daysAgo(1)` → `nowMs()` | 3 600 000 | AVG | 100 |
| `loadFP` (L348) | `factor_potencia_fase_a/b/c` | `daysAgo(1)` → `nowMs()` | 3 600 000 | AVG | 100 |
| `loadMonthly` (L357) | `energia_total` | `daysAgo(180)` → `nowMs()` | 2 592 000 000 (30 d) | MAX | 20 |
| Selector semana/mes (L781) | `potencia_activa_fase_a/b/c` | `daysAgo(7\|30)` → `nowMs()` | 86 400 000 | AVG | 50 |

Alarmas usan otro endpoint (L321): `/api/alarm/DEVICE/{id}?page=0&pageSize=10&fetchOriginator=false&statusList=ACTIVE_UNACK,ACTIVE_ACK`, con fallback sin `statusList`.

### 2.5 Zona horaria

**No hay manejo explícito de zona horaria.** No existe `Intl`, `timeZone`, ni offset fijo (en 3EM solo se usa `toLocaleString('es-PE')` para formatear números, no fechas).

- Todo se calcula con `new Date()`, `setHours(0,0,0,0)`, `getHours()`, `getDate()`, `getMonth()`: es decir, **zona local del navegador**.
- La telemetría de ThingsBoard llega en epoch UTC (ms); `new Date(+p.ts)` la convierte a hora local al mostrarla (`pad(d.getHours())+':00'`).
- Consecuencia: "hoy", "ayer" y "mes" dependen de la zona del equipo del usuario, no de la instalación (Lima, UTC−5 sin DST). Un usuario en otra zona vería "hoy" desfasado.
- Único otro caso en el repo: Exportación `toInputFormat` (L855–L859) corrige `getTimezoneOffset()` para los `datetime-local`.

Además, los `startTs` móviles (`daysAgo`) y `ydayStart = todayStart()-86400000` asumen días de 24 h exactas (válido en Lima, no en zonas con DST).

---

## 3. Funciones de comparación y proyección (Template 3EM)

Todas parten de **una sola key**: `energia_total` (contador acumulado en **Wh**; se divide entre 1000 para kWh). Se guarda en el almacén `D` (L56–L63).

### 3.1 "Energía acumulada hoy" → `D.energyToday`

Calculada en `loadEnergyDaily` (L272–L288), mostrada por `renderSec01KpiEnergy` (L574) en `#kv-en` (tarjeta "ENERGÍA ACUMULADA HOY", HTML L74).

```js
api(tsUrl('energia_total',daysAgo(2),nowMs(),3600000,'MAX',200),function(d){
  var pts=(d.energia_total||[]).map(function(p){return{ts:+p.ts,v:parseFloat(p.value)};});
  pts.sort(function(a,b){return a.ts-b.ts;});
  var today=pts.filter(function(p){return p.ts>=todayStart();});
  var yday =pts.filter(function(p){return p.ts>=ydayStart()&&p.ts<todayStart();});
  if(today.length>=1){
    var baseline=today[0].v;
    var latE=lat('energia_total');
    var current=(latE>0&&latE>=baseline)?latE:today[today.length-1].v;
    D.energyToday=Math.max(0,(current-baseline)/1000);
  }
```

Es el contador actual (último valor en vivo `lat('energia_total')`, o el último bucket horario si no es válido) menos el **primer bucket horario del día** (baseline). Ojo: el baseline es el MAX del primer bucket con dato de hoy (normalmente 00:00–01:00), por lo que el consumo de esa primera hora queda fuera del acumulado.

### 3.2 "vs ayer" → `D.energyYesterday`

- Dato: misma consulta de `loadEnergyDaily` (L284):

```js
if(yday.length>=2) D.energyYesterday=Math.max(0,(yday[yday.length-1].v-yday[0].v)/1000);
```

Último − primer bucket horario de ayer. Esto omite la última hora del día (el salto 23:xx→00:xx entre contadores).

- Presentación: `renderComparisons` (L584–L). Porcentaje (L588):

```js
var pctA=((en-D.energyYesterday)/D.energyYesterday*100), upA=pctA>=0, colA=upA?'#EF4444':'#10B981';
set('cmp-ayer',(upA?'↑ +':'↓ ')+Math.abs(pctA).toFixed(1)+'%');
```

Rojo si sube, verde si baja. También rellena `#cmp-ayer-s`, `#cmp-icon-ayer` y el chip `#kch-en` ("↑ X% vs ayer"). Se compara el acumulado **parcial de hoy** contra el día **completo** de ayer, así que el porcentaje es negativo hasta avanzada la jornada. Solo se muestra si `energyYesterday > 0`. HTML: `templateHtml` L110–L114.
- Duplicado en la tarjeta de inteligencia (`icm-1`, L531–L537) con la misma fórmula.

### 3.3 "vs semana anterior" → `D.energyWeekAgo`

`loadWeekComparison` (L290–L301), llamada desde `loadEnergyDaily` (L286):

```js
var weekAgoEnd=todayStart()-7*86400000, weekAgoStart=weekAgoEnd-86400000;
api(tsUrl('energia_total',weekAgoStart,weekAgoEnd+86400000,3600000,'MAX',50), function(d){
  ...
  var day=pts.filter(function(p){return p.ts>=weekAgoStart&&p.ts<weekAgoEnd+86400000;});
  if(day.length>=2) D.energyWeekAgo=Math.max(0,(day[day.length-1].v-day[0].v)/1000);
  renderComparisons();
```

Calcula el consumo del día completo de hace 7 días (mismo método último − primero). En `renderComparisons` (L597–L606) `pctS = (hoy − hace7d)/hace7d*100`, escribe `#cmp-sem`, `#cmp-sem-s` ("Hoy / Hace 7d"), `#cmp-icon-sem`. Sin datos: "Sin histórico — Disponible tras 7 días de datos en plataforma". HTML L120.

Hay un tercer comparativo, "vs promedio 30 días" (`load30DayAverage`, L303–L318; promedio de deltas diarios 0 < Δ < 10 000 kWh, requiere ≥7 puntos → `D.energy30DayAvg`).

### 3.4 "Proyección del mes"

No hay una función propia: la fórmula está **copiada en cuatro sitios** (misma lógica). Principal: `renderSec01KpiEnergy` (L574–L582):

```js
var now=new Date(), daysInMonth=new Date(now.getFullYear(),now.getMonth()+1,0).getDate();
var hoursElapsed=Math.max((now.getTime()-todayStart())/3600000,0.5);
var proj=(D.energyToday/hoursElapsed*24)*daysInMonth;
set('kv-proj',Math.round(proj).toLocaleString('es-PE'));
set('kch-proj','~'+fmtSol(proj*TARIFA)+' estimado');
```

Key: `energia_total` vía `D.energyToday`. Extrapolación lineal: ritmo horario de hoy × 24 × días del mes. El suelo de 0.5 h evita dividir por ~0 justo tras medianoche (a esa hora la proyección es muy inestable).

Copias idénticas: `tryRenderIntelligence` (`icm-2`, L539–L543), `renderCostCard` (`cc-proj-k`/`cc-proj-s`, L815–L820) y los PDF (L1029+). HTML: tarjeta `#kc-proj` (L96), `#icm-2` y `.cc-proj-lbl` (L153, L300). Costo estimado = `proj * TARIFA` (setting `tarifa_kwh`, por defecto 0.65 S/./kWh).

### Resumen

| Métrica | Key | Variable | Función | Salida DOM |
|---|---|---|---|---|
| Energía acumulada hoy | `energia_total` | `D.energyToday` | `loadEnergyDaily` L272 | `#kv-en` |
| vs ayer | `energia_total` | `D.energyYesterday` | `loadEnergyDaily` L284 + `renderComparisons` L587 | `#cmp-ayer`, `#kch-en`, `#icm-1` |
| vs semana anterior | `energia_total` | `D.energyWeekAgo` | `loadWeekComparison` L290 + `renderComparisons` L597 | `#cmp-sem` |
| Proyección del mes | `energia_total` | derivada de `D.energyToday` | `renderSec01KpiEnergy` L574 (+3 copias) | `#kv-proj`, `#icm-2`, `#cc-proj-k` |

---

## 4. Dónde se genera "Actualizado hace…"

### Template 3EM

- HTML (`templateHtml` L54): `<div class="sec-sub">Actualizado hace <span id="last-sec">—</span> · Shelly Pro 3EM</div>`. El texto fijo "Actualizado hace" está en el HTML; el JS inyecta solo el sufijo.
- JS `updateLastSeen` (L175–L211), llamada tras cada `loadLatest` (L267, cada 30 s):

```js
if(D.lastRealTs){
  var age=Math.floor((now.getTime()-D.lastRealTs)/1000);
  var ageStr;
  if(age<60)        ageStr='hace '+age+' seg';
  else if(age<3600) ageStr='hace '+Math.floor(age/60)+' min';
  else              ageStr='hace '+Math.floor(age/3600)+'h '+Math.floor((age%3600)/60)+' min';
  set('last-sec', ageStr);
```

- `D.lastRealTs` = `ts` del primer valor de `potencia_activa_total` (L264–L266). Es el timestamp real del dato, no la hora del refresco.
- **Bug visible**: `ageStr` ya incluye "hace ", y el HTML también dice "Actualizado hace " → el texto renderizado es "Actualizado hace hace 5 min". Con el `else` (sin dato) escribe `'hace 0 segundos'` (L209), con el mismo duplicado.
- Color de `#last-sec` (L193): rojo si `age>21600` s (6 h), ámbar si `>7200` (2 h), gris `#5A6E8A` si no.
- También actualiza el badge de cabecera (`.hdr-sdot`, `.hdr-ts`): "En línea · HH:MM:SS" / "Datos con retraso · …" (>2 h) / "Sin datos · …" (>6 h), L196–L206. `#last-update` (L173) es la hora local del refresco, no del dato.
- Texto relacionado: `set('ic-date','Actualizado hoy '+t+' · análisis basado en telemetría real')` (L528), en la tarjeta de inteligencia.

### Otros widgets

- **Piscina**: `updateLastSeen` L132–L170, mismo formato, pero escribe `'Actualizado '+ageStr+' · '` en `#last-ts` (`templateHtml` L55; sin duplicado). Umbrales: aviso >12 h, alerta >30 h (sensor H&T con ciclo de sueño). `ic-date` en L369.
- **Flota**: `timeSince(ts)` (L118–L124, devuelve "hace N seg/min/h" o "sin datos"); usado en L526 (`cr-upd-<id>`), L625 (`chk-upd`) y L846. Los umbrales de estado (`SIN SEÑAL` / `ATENCIÓN`) están en L155–L159 (minutos: 360/120 y 1800/720 según tipo).
- **Exportación**: no tiene texto "Actualizado hace".

---

## Observaciones

1. Duplicado "hace hace" en 3EM (ver §4): `templateHtml` L54 más `ageStr` en `controllerScript` L188–L190. Hoy ningún widget aplica "Actualizado" de forma consistente.
2. Fórmula de proyección copiada 4 veces; conviene extraer una `projectMonth()`.
3. "vs ayer" compara un parcial contra un día completo (sesgo hacia ↓ durante el día).
4. Sin zona horaria explícita: todo depende del navegador (Lima UTC−5 es el caso esperado).
5. Logo duplicado en 4 widgets y UUID del dashboard de inicio hardcodeado.
