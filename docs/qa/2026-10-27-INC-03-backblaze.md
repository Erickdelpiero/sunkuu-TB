# INC-03 — Backblaze B2 al límite del plan gratuito (los backups dejarán de subir)

Fecha: 2026-10-27 (registrado a las 01:15 de Lima) · **Abierto, prioridad 1 del 2026-10-27** · Plan aprobado por Erick, **sin ejecutar**.
Infraestructura: `../gonex-infra` (`backup.sh`; solo lectura). Relacionado: UPG-01 §3.0 (`docs/qa/2026-10-26-UPG-01-upgrade-4.3.1.8.md`) y `docs/runbook-recuperacion-thingsboard.md` §2.

## 1. Situación (Erick, 2026-10-27 01:15)

- La cuenta de Backblaze está en **plan gratuito, sin tarjeta**: 10 GB de almacenamiento y 1 GB/día de descarga, con los topes (caps) en **USD 0**.
- Uso: **8,9 GB en 39 archivos**; entran ~**1,05 GB/día** (los 4 backups diarios). **Se llena entre el 27 y el 28-oct** y desde ahí los backups fallan al subir.
- **La retención de 30 días no existe en la práctica.** La regla del bucket es "Keep prior versions for N days", que solo borra versiones anteriores de un **mismo nombre de archivo**; cada backup tiene un nombre distinto (`<base>_<fecha>.sql.gz`), así que nunca se borra nada. Esto **corrige** lo registrado el 2026-10-26 ("retención de 30 días por regla de ciclo de vida") en UPG-01 0.5 y en el runbook de recuperación.
- El tope de descarga de 1 GB/día es el mismo aviso "Daily Download Bandwidth Cap 100 %" de la prueba de restauración (UPG-01 §3.4).

## 2. Qué pasa cuando falle la subida (de `backup.sh`, leído en `gonex-infra`)

- `backup.sh` corre con `set -euo pipefail`: si `b2 sync` falla, el script **se detiene** antes de `rm -rf /tmp/gonex-backups` y **no** escribe "completado exitosamente" en el log.
- Los dumps del día **se quedan en `/tmp/gonex-backups`** del VPS (mismo disco que Postgres, ~1,1 GB por día) y el `b2 sync` del día siguiente intenta subirlos otra vez junto con los nuevos. Mientras siga lleno, el disco del VPS crece ~1,1 GB/día.
- No hay alerta: el fallo solo se ve en `backup.log`. El correo de aviso de Backblaze por los caps es la única señal externa.
- Deducido del script, no probado.

## 3. Plan aprobado (Erick, 2026-10-27), sin ejecutar

1. **Agregar la tarjeta** a la cuenta de Backblaze. Costo estimado ~**USD 0,15/mes** con 30 días de backups (~32 GB, 10 GB gratis), a cargo de **GONEX**.
2. **Caps & Alerts:** tope de **Storage** y de **Download** en **USD 1/día** cada uno (dejan de ser USD 0). Con eso la descarga de un backup completo deja de bloquearse (UPG-01 §3.0 y runbook §2).
3. **Regla de ciclo de vida personalizada** en el bucket `gonex-backups`, prefijo `postgres/`: **ocultar a los 30 días** de subido y **borrar 1 día después** de ocultado. Reemplaza a "Keep prior versions for N days".
   - Al aplicarla, Backblaze empieza a ocultar los archivos de más de 30 días (los más viejos son del ~19-oct, así que nada se oculta todavía). El almacenamiento sube hasta ~32 GB y ahí se estabiliza.

## 4. Mitigación de la noche del 26 al 27

- Borrado manual de `postgres/thingsboard_2026-10-19_04-11-28.sql.gz` (~1 GB) para que el backup del 27 quepa: **por confirmar** (el mensaje de cierre quedó con "<hice / no hice>" sin completar). Si no se hizo, el backup del 27 (02:00 de Lima) puede fallar al subir.

## 5. Verificación (2026-10-27, antes de nada más)

En el VPS, en tmux, un comando por bloque:

```
tail -20 ~/gonex/docker/backup.log
```
- Esperado: la ejecución del 27 (`[2026-10-27_08-00-…]`) termina con "Backup GONEX completado exitosamente.". Si termina en "Subiendo backups a Backblaze B2..." o con un error de `b2`, la subida falló.

```
ls -la /tmp/gonex-backups 2>&1; df -h /
```
- Esperado: "No such file or directory" (el script lo borra al terminar bien). Si existe con archivos del 27, la subida falló y quedan en el disco.

```
export PATH="$HOME/.local/bin:$PATH"; b2 ls b2://gonex-backups/postgres/ | grep 2026-10-27
```
- Esperado: los 4 archivos del 27 (`n8n_`, `evolution_`, `gonex_`, `thingsboard_`).

Si la subida falló: hacer primero los pasos 1–2 de §3 y repetir a mano con `bash ~/gonex/docker/backup.sh` (sube los dumps pendientes y genera unos nuevos), o solo `b2 sync /tmp/gonex-backups/ b2://gonex-backups/postgres/` para subir los que quedaron. Después, pasos 3 y 4 de §6.

## 6. Ejecución del plan (Erick, en la web de Backblaze) y resultados

| Paso | Estado | Nota |
|---|---|---|
| Borrado manual de `thingsboard_2026-10-19_04-11-28.sql.gz` (noche del 26) | Por confirmar | |
| §5 backup del 27 subido | Pendiente | |
| 1. Tarjeta agregada | Pendiente | |
| 2. Caps Storage y Download en USD 1/día | Pendiente | |
| 3. Regla de ciclo de vida `postgres/` (ocultar 30 d, borrar 1 d) | Pendiente | |
| 4. Corregir en `gonex-infra` (lo hace Erick): `RETENTION_DIAS` y el comentario "Eliminar backups antiguos en B2" de `backup.sh` no borran nada; la retención la hace la regla del paso 3 | Pendiente | |
| Cierre: UPG-01 §3.0 y runbook §2 en ✔ | Pendiente | |
