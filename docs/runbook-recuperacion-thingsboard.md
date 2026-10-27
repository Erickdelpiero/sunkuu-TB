# Runbook de recuperación — base `thingsboard` desde el backup diario de B2

Creado: 2026-10-26 (UPG-01) · Probado: **2026-10-26**, restauración de `thingsboard_2026-10-26_08-00-01.sql.gz` en una base aparte, **RTO 6 min** (descarga + restauración). Detalle de la prueba: `docs/qa/2026-10-26-UPG-01-upgrade-4.3.1.8.md` §3.4.
Infraestructura: `../gonex-infra` (`backup.sh`, `docs/servicios.md`). Este runbook no cambia nada allí.

## 1. Qué hay y qué se pierde

- **Backup:** `backup.sh` hace `pg_dump` (SQL plano) | `gzip` de n8n, evolution, gonex y thingsboard y lo sube con `b2 sync` a `b2://gonex-backups/postgres/`. Cron `0 8 * * *` en la **hora del VPS (Berlín)**: 07:00 UTC = **02:00 de Lima** con horario de invierno de Europa (desde el 25-oct); 06:00 UTC = 01:00 de Lima con horario de verano. El nombre del archivo lleva la hora de Berlín (`thingsboard_AAAA-MM-DD_08-00-01.sql.gz`).
- **Retención:** **hoy no hay** (INC-03, 2026-10-27): la regla "Keep prior versions for N days" no borra backups con nombres distintos y la cuenta está en el plan gratuito de 10 GB, que se llena el 27–28-oct; desde ahí los backups **no suben**. Plan: regla de ciclo de vida en `postgres/` (ocultar a los 30 días, borrar 1 día después). Detalle: `docs/qa/2026-10-27-INC-03-backblaze.md`.
- **Tamaño (2026-10-26):** `thingsboard` ≈ 1,01 GB comprimido; la base restaurada ocupa ≈ 21 GB.
- **Pérdida:** todo lo escrito en ThingsBoard desde el último backup (hasta ~24 h de telemetría y cambios de configuración). La energía diaria y mensual se recupera sola cuando los medidores vuelven a publicar (FIX-01, diferencia de contador); las curvas quedan con hueco.
- **Después de restaurar,** `../sunkuu-tb-config` puede tener commits posteriores al backup: la configuración de ThingsBoard queda **más vieja** que el repo. Revisarlo con Erick antes de cualquier cambio (§4).

## 2. Requisitos previos (comprobar ahora, no en la emergencia)

| Requisito | Estado |
|---|---|
| **Backblaze → Caps & Alerts → "Daily Download Bandwidth Cap"** por encima de todos los backups de un día, con margen para dos descargas completas. El 2026-10-26 la prueba llegó al **100 %** del tope gratuito: con el tope por defecto, una recuperación puede quedar **bloqueada hasta el día siguiente** | Pendiente: INC-03 (cuenta gratuita, caps en USD 0; plan: tarjeta y caps de USD 1/día) |
| Espacio libre en el VPS ≥ base restaurada + archivo + 14 GB de margen (hoy: 21 + 1 + 14 ≈ 36 GB; había 53 libres) | ✔ 2026-10-26 |
| b2 CLI en `~/.local/bin` (v4.6.0 según `gonex-infra` `docs/servicios.md`) con credenciales del bucket | ✔ (usado en la prueba) |
| Backup del día subido (`tail -20 ~/gonex/docker/backup.log`: "completado exitosamente"; si falla la subida, los dumps quedan en `/tmp/gonex-backups`) | Revisar cada mes; **diario hasta cerrar INC-03** |

## 3. Restaurar `thingsboard` (emergencia)

Todo en el VPS, dentro de `tmux` (`tmux new -s recuperacion`; si se corta el SSH, `tmux attach -t recuperacion`). Cada bloque se pega entero, en orden.

**3.1 Elegir el backup y bajarlo:**
```
export PATH="$HOME/.local/bin:$PATH"; b2 version; df -h /
b2 ls b2://gonex-backups/postgres/ | grep thingsboard_ | sort | tail -3
F=$(b2 ls b2://gonex-backups/postgres/ | grep thingsboard_ | sort | tail -1 | sed 's#.*/##'); echo "$F"
mkdir -p ~/recuperacion && cd ~/recuperacion
b2 sync --dry-run --exclude-regex '.*' --include-regex "^${F//./\\.}\$" b2://gonex-backups/postgres/ ~/recuperacion/
T0=$(date +%s); b2 sync --exclude-regex '.*' --include-regex "^${F//./\\.}\$" b2://gonex-backups/postgres/ ~/recuperacion/
ls -l ~/recuperacion/ && gunzip -t "$F" && echo "gzip OK"
```
- Esperado: el último `thingsboard_….sql.gz` (si el de hoy es sospechoso, pon a mano el de un día antes en `F`), la simulación con **un solo** archivo y `gzip OK`.
- Si la descarga se corta por el tope de Backblaze: súbelo en Caps & Alerts y repite.

**3.2 Parar ThingsBoard y apartar la base actual** (no se borra):
```
cd ~/gonex/docker && docker compose stop tb-web-report thingsboard-pe
docker exec gonex-postgres psql -U gonex -d postgres -Atc "select datname, usename, application_name from pg_stat_activity where datname='thingsboard'"
docker exec gonex-postgres psql -U gonex -d postgres -c "ALTER DATABASE thingsboard RENAME TO thingsboard_danada_$(date +%Y%m%d)"
docker exec gonex-postgres createdb -U gonex thingsboard
```
- Esperado: la consulta de conexiones vacía; el `RENAME` sin error (si la base actual ya no existe, el `RENAME` falla y se sigue); `createdb` sin error.
- Si no hay espacio para la base vieja y la nueva a la vez, **avísale a Erick antes** de borrar la vieja.

**3.3 Restaurar** (SQL plano; se detiene en el primer error):
```
time (set -o pipefail; gunzip -c ~/recuperacion/"$F" | docker exec -i gonex-postgres psql -U gonex -d thingsboard -q -v ON_ERROR_STOP=1 > ~/recuperacion/restore.out 2> ~/recuperacion/restore.err); echo "restauración $?"
echo "RTO hasta aquí: $(( ($(date +%s) - T0) / 60 )) min"; wc -l ~/recuperacion/restore.err; head -5 ~/recuperacion/restore.err
```
- Esperado: `restauración 0` y `restore.err` vacío. Si no: `head -20 restore.err` y decide con Erick (otro día de backup, o volver a la base apartada con dos `RENAME`).

**3.4 Arrancar y comprobar:**
```
cd ~/gonex/docker && docker compose up -d --no-deps thingsboard-pe tb-web-report && docker compose logs -f --since 5m thingsboard-pe
docker exec gonex-postgres psql -U gonex -d thingsboard -Atc "select 'device',count(*) from device union all select 'dashboard',count(*) from dashboard union all select 'customer',count(*) from customer"
```
- Esperado: ThingsBoard arranca sin errores de licencia; los conteos son los del día del backup (2026-10-26: device 7, dashboard 13, customer 6).
- En la UI (admin GONEX): las 5 integraciones activas y datos nuevos de los medidores en < 5 min; los dashboards de los customers cargan; Planificador con los 4 informes mensuales.

## 4. Después

- Anotar en `CHANGELOG.md`: fecha, causa, archivo restaurado, RTO y qué se perdió.
- `git -C ../sunkuu-tb-config log --since=<fecha del backup>`: lo que esté en el repo y no en la base restaurada se revisa con Erick; nada se reaplica sin revisar.
- Versión manual en ThingsBoard **Overwrite con todos los tipos** y `git pull`.
- La base apartada (`thingsboard_danada_…`) y `~/recuperacion/` se borran solo cuando Erick lo decida.

## 5. Las otras bases (n8n, evolution, gonex)

Mismo procedimiento con su archivo (`<base>_….sql.gz`) y su servicio parado en lugar de ThingsBoard. **No probado.**
