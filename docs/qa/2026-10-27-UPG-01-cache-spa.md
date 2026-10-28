# UPG-01 · Hallazgo §6.11 — Index viejo de ThingsBoard en caché del navegador (Nginx: `no-cache` para la SPA)

Fecha: 2026-10-27 · Base: `../gonex-infra` `faf92be` (solo lectura) · **Cerrado como "no aplica" (Erick, 2026-10-27):** el paso 0 mostró que ThingsBoard ya manda `no-cache` en el index; Nginx y `gonex-infra` sin cambios. Resultado en §7.
Origen: UPG-01 (4.3.0PE → 4.3.1.8PE). Tipo: Correctivo (infraestructura de GONEX), dentro de UPG-01.

## 1. Hallazgo (Erick, 2026-10-27)

- En Chromium, después del upgrade, el editor de widgets (`/widget-editor`) cargaba el `index.html` de 4.3.0 desde la caché. Ese index pedía bundles que ya no existen (`main-L7BQTBE3.js`, `chunk-*.js`, `polyfills-5W6QH7SK.js`): 404 y "Refused to apply style… MIME application/json" (el 404 de ThingsBoard llega como JSON).
- "Clear site data" no lo resolvió. En Firefox funciona.
- **Riesgo:** Romel y los usuarios de los customers pueden tener la misma caché vieja en Chromium y ver la plataforma rota, o en blanco, hasta que su navegador revalide el index.

## 2. Causa probable (a confirmar con §4, paso 0) — **descartada por el paso 0** (ver §7)

Los dos vhosts (`nginx/360.sunkuu.com.conf` y `nginx/thingsboard.gonex.pe.conf`) solo hacen `proxy_pass` a `localhost:9090` y no definen cabeceras de caché: Nginx reenvía lo que mande ThingsBoard. Si el index y las rutas de la SPA llegan **sin `Cache-Control`** pero con `Last-Modified`, el navegador aplica **caché heurística**: lo da por fresco durante ~10 % de su antigüedad (días, si el index se compiló hace semanas) y no pregunta al servidor. Los bundles cambian de nombre en cada versión (hash), pero el index que los nombra no.

Esto **no se puede confirmar desde el repo** (sin red). El paso 0 mide las cabeceras reales. Si ThingsBoard ya manda `no-cache`/`no-store` en el index, la causa es otra (service worker, caché del perfil de Chromium) y este cambio no sirve: avísame antes de aplicarlo.

## 3. Cambio propuesto

Archivos: `widgets/work/UPG-01/nginx/360.sunkuu.com.conf` y `widgets/work/UPG-01/nginx/thingsboard.gonex.pe.conf` (completos, desde `faf92be`); diff en `widgets/work/UPG-01/nginx-cache-spa.diff`. En cada vhost, **antes** de `location /` (que no cambia), se agregan dos bloques:

- `location ~ ^/(?!api(/|$)|oauth2/|login/oauth2/|assets/|static/)[^.]*$`: rutas sin extensión de la SPA (`/`, `/home`, `/login`, `/dashboards/…`, `/dashboard/…`, `/widget-editor`, `/resources/…`).
- `location = /index.html`.

Los dos hacen el mismo `proxy_pass`, quitan el `Cache-Control`, `Expires` y `Pragma` de ThingsBoard **solo en esas rutas** y ponen `Cache-Control: no-cache`. Con `no-cache`, el navegador puede guardar el index pero lo revalida en cada carga (respuesta 304 si no cambió). Tras un upgrade recibe el index nuevo enseguida.

**No cambia:**
- la API ni el WebSocket (`/api/…`, `/api/ws`), con sus cabeceras de ThingsBoard (no se quita ningún `no-store`);
- OAuth;
- `/assets/` (estáticos sin hash);
- los bundles con hash (`main-…js`, `chunk-…js`, `polyfills-…js`, `styles-…css`), que tienen extensión y siguen por `location /`;
- certbot, SSL y la redirección HTTP→HTTPS.

Las rutas de la SPA no son WebSocket, así que la nueva `location` no lleva `Upgrade`/`Connection`.

**Precedencia:** en Nginx, `location =` gana primero y las `location ~` (regex) se evalúan antes que el prefijo `location /`. Comprobado con 25 rutas reales: las de la SPA llevan `no-cache`; `/api/ws`, `/api/auth/user`, `/api/noauth/…`, `/oauth2/…`, `/assets/…`, los bundles con hash y `/thingsboard.ico` no cambian. `nginx -t` lo hace Erick en el VPS (aquí no hay Nginx).

## 4. Aplicación (Erick, en el VPS; un bloque por vez)

**0. Medir antes** (desde tu máquina, sin tocar nada). Rutas de la SPA, index y un bundle con hash:
```
for u in / /index.html /widget-editor /dashboards /login; do printf '%-16s ' "$u"; curl -sI "https://360.sunkuu.com$u" | grep -iE '^(HTTP|cache-control|expires|pragma|last-modified|etag):' | tr -d '\r' | tr '\n' ' '; echo; done
```
```
M=$(curl -s https://360.sunkuu.com/ | grep -oE 'main-[A-Z0-9]+\.js' | head -1); echo "bundle actual: $M"; curl -sI "https://360.sunkuu.com/$M" | grep -iE '^(HTTP|cache-control|expires|last-modified):'
```
- Esperado (lo que confirma la causa): las rutas SPA e `/index.html` con `200` y **sin `Cache-Control`** (o con `max-age`), con `Last-Modified`. El bundle actual **no** es `main-L7BQTBE3.js` (el de 4.3.0).
- Si las rutas ya traen `Cache-Control: no-cache` o `no-store`: **no sigas**. En el Chromium afectado revisa F12 → Application → Service Workers (¿hay uno registrado para el dominio?) y pásame lo que veas.

**1. Ubicar los archivos activos y comparar con el repo:**
```
ls -l /etc/nginx/sites-enabled/ && sudo nginx -T 2>/dev/null | grep -E '^# configuration file|server_name (360\.sunkuu\.com|thingsboard\.gonex\.pe)'
```
- Anota la ruta real de cada vhost (p. ej. `/etc/nginx/sites-available/360.sunkuu.com`). Compara cada uno con su versión del repo:
```
sudo diff <(sudo cat /etc/nginx/sites-available/360.sunkuu.com) ~/gonex/nginx/360.sunkuu.com.conf && echo "360 = repo"
```
```
sudo diff <(sudo cat /etc/nginx/sites-available/thingsboard.gonex.pe) ~/gonex/nginx/thingsboard.gonex.pe.conf && echo "gonex = repo"
```
- Esperado: `360 = repo` y `gonex = repo`. Si los nombres de archivo son otros, usa los del paso anterior. Si hay diferencias (por ejemplo, certbot cambió algo), pásamelas: el cambio se rehace sobre el archivo real.

**2. Copia de respaldo** (es el rollback):
```
mkdir -p ~/upg01/nginx-pre-cache && sudo cp -p /etc/nginx/sites-available/360.sunkuu.com /etc/nginx/sites-available/thingsboard.gonex.pe ~/upg01/nginx-pre-cache/ && ls -l ~/upg01/nginx-pre-cache/
```

**3. Instalar los archivos nuevos.** Copia al VPS los dos `.conf` de `widgets/work/UPG-01/nginx/` (por ejemplo con `scp` a `~/nginx-cache/`) y:
```
sudo cp ~/nginx-cache/360.sunkuu.com.conf /etc/nginx/sites-available/360.sunkuu.com && sudo cp ~/nginx-cache/thingsboard.gonex.pe.conf /etc/nginx/sites-available/thingsboard.gonex.pe
```

**4. Probar la sintaxis y recargar sin caída:**
```
sudo nginx -t && sudo systemctl reload nginx && systemctl status nginx --no-pager | head -5
```
- Esperado: `syntax is ok`, `test is successful` y `active (running)`. `reload` no corta conexiones: los procesos viejos terminan lo que están sirviendo (incluidos los WebSocket abiertos de los dashboards) y los nuevos toman las conexiones nuevas. **Si `nginx -t` falla, no se recarga nada:** vuelve a copiar los archivos del paso 2 (rollback) y pásame el error.

**5. Medir después** (desde tu máquina): repite los dos bloques del paso 0, más la API:
```
curl -sI https://360.sunkuu.com/api/auth/user | grep -iE '^(HTTP|cache-control):'; curl -sI https://thingsboard.gonex.pe/widget-editor | grep -iE '^(HTTP|cache-control):'
```
- Esperado:
  - Rutas SPA e `/index.html`: `200` y **un solo** `Cache-Control: no-cache`.
  - El bundle con hash: igual que antes.
  - `/api/auth/user`: `401` con las mismas cabeceras que antes.
  - `thingsboard.gonex.pe/widget-editor`: `no-cache`.

**6. Prueba en el navegador:**
- **Chromium afectado:** una sola vez, F12 abierto → clic derecho en recargar → "Vaciar caché y volver a cargar de manera forzada". Después, recargas normales: en Red, el documento (`widget-editor`, `/`) aparece como `200` o `304`, **nunca** "(disk cache)", y no hay 404 de `main-*.js`.
- **Dashboards (WebSocket):** abre TG GOCTA; en Red → WS, `/api/ws` con `101` y mensajes en vivo; los valores se actualizan.
- **Login de 360.sunkuu.com:** marca blanca y CSS avanzado como antes.

**7. Usuarios que ya tienen el index viejo:** el cambio sirve desde la próxima vez que su navegador pida el index al servidor. Un index ya cacheado por heurística puede seguir usándose hasta que venza. Si alguien ve la plataforma en blanco o con errores, la solución inmediata es una recarga forzada (Ctrl+Shift+R). A partir de este cambio, los próximos upgrades no repiten el problema.

## 5. Rollback

```
sudo cp -p ~/upg01/nginx-pre-cache/360.sunkuu.com ~/upg01/nginx-pre-cache/thingsboard.gonex.pe /etc/nginx/sites-available/ && sudo nginx -t && sudo systemctl reload nginx
```
- Esperado: `test is successful`. Las cabeceras vuelven a las del paso 0. Sin caída.

## 6. Después

- `gonex-infra` (Erick): commit de los dos `.conf` con el diff de `widgets/work/UPG-01/nginx-cache-spa.diff`, y una línea en `docs/servicios.md` (Nginx: "SPA de ThingsBoard con `Cache-Control: no-cache`; API y bundles sin cambios").
- Resultado en UPG-01 §8 (fila §6.11).
- Si con `max-age` en `/assets/` aparecieran problemas parecidos (traducciones viejas tras un upgrade), se trata aparte. Hoy no hay evidencia.

## 7. Resultados

| Paso | Resultado | Notas |
|---|---|---|
| 0 medición antes | ✔ Erick, 2026-10-27 | ThingsBoard ya envía `Cache-Control: no-cache, no-store, max-age=0, must-revalidate` y `Expires: 0` en `/`, `/home`, `/widget-editor` e `/index.html`. La causa de §2 queda descartada: **no se sigue** (como indica el paso 0) |
| 1 archivos activos = repo | No aplica | |
| 2–4 instalación y reload | No aplica | Nginx sin cambios |
| 5 medición después | No aplica | |
| 6 navegador (Chromium, WebSocket, login) | No aplica | |

**Conclusión:** el index viejo venía de la caché local de ese Chromium (no de la caché heurística ni de Nginx); se resolvió borrando "Imágenes y archivos en caché" del navegador, y desde entonces Chromium funciona (B-08 se aplicó desde él). Para usuarios que lo vean tras un upgrade: Ctrl+Shift+R. Los archivos de `widgets/work/UPG-01/nginx/` y `nginx-cache-spa.diff` quedan sin uso.
