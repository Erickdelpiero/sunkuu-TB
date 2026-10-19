# CLAUDE.md — sunkuu-TB

## Proyecto
Sunkuu 360: plataforma IoT de monitoreo energético (ThingsBoard PE 4.3, 360.sunkuu.com) que GONEX
entregó a Sunkuu Energy (Romel Valqui) y opera como SaaS mensual.

- `../sunkuu-tb-config`: Version Control nativo de ThingsBoard. Lo escribe SOLO ThingsBoard
  (auto-commit + versiones manuales). Push bloqueado. **Solo lectura.**
- `sunkuu-TB` (este repo): documentación, QA, scripts, marca blanca, `CHANGELOG.md`.

**Jerarquía de fuentes:** producción > `../sunkuu-tb-config` (a la fecha de su último commit) >
documentación de sunkuu-TB. Romel puede cambiar cosas en cualquier momento. Nunca des por vigente
la documentación de este repo sin verificarla contra `../sunkuu-tb-config`.

## Reglas
- `../sunkuu-tb-config`: solo leer archivos y `git log/show/status/diff` (y `git pull` cuando Erick lo pida).
- Nunca `git push` en ningún repo: Erick revisa y hace push.
- Nunca llamadas de red (ni ThingsBoard ni otros servicios).
- Cambios quirúrgicos: no reescribir ni reorganizar documentos sin que se pida.
- No borrar archivos del disco; para sacar algo del repo, `git rm --cached` y avisar.
- Nada se aplica en ThingsBoard: lo aplica Erick manualmente.
- Autoría: los cambios de GONEX se hacen con el usuario GONEX, nunca con la sesión de Romel.

## Ciclo de cada cambio
0. Base al día: Erick crea una versión en ThingsBoard (o confirma que el auto-commit está al día)
   y se hace `git pull` en `../sunkuu-tb-config`. Nunca preparar un parche sobre una base desactualizada.
1. Preparar en `widgets/work/<ID>/` (apply + rollback; carpeta ignorada por git).
2. Revisión del diff con Erick.
3. Erick aplica en ThingsBoard (DEV primero cuando corresponda).
4. Versionado en ThingsBoard:
   - El auto-commit cubre todos los tipos de entidad, incluidos widgets y paquetes de widgets: al
     guardar un widget se genera un commit automático con mensaje genérico.
   - Las versiones manuales con nombre (`fix(<ID>): …`, `chore: …`) quedan para baselines o cambios
     agrupados: exportar solo el tipo de entidad afectado y con "credenciales" **desmarcado**
     (se vuelve a marcar solo).
5. `git pull` en `../sunkuu-tb-config` y `git show --stat <hash>` para confirmar el alcance.
6. Fila en `CHANGELOG.md` con el ID del cambio y el hash de `sunkuu-tb-config` (automático o manual),
   y commit en sunkuu-TB con el mismo ID.

### Auto-commit (comportamiento observado)
- Se dispara al guardar cualquier entidad de los tipos activados (incluidos widgets y dashboards),
  por cualquier usuario del tenant (GONEX o Romel).
- El autor del commit es el usuario que guardó; el mensaje es `auto-commit at <fecha UTC>`.
- No se dispara por telemetría.
- **No registra eliminaciones, cambios de propietario ni cambios de grupos** (confirmado el
  2026-10-11: el repo siguió mostrando entidades eliminadas y el propietario anterior de `717ae5e0`).
  Después de cada alta, baja o cambio de propietario se crea una **versión manual con estrategia
  Overwrite y todos los tipos de entidad** (verificado en `71f1603`: eliminó 43 entidades y movió
  `717ae5e0` a `hierarchy/` de su customer).

## Altas, bajas y cambios de propietario (reglas confirmadas)
- Antes de eliminar o reemplazar un dashboard o un dispositivo, buscar qué lo referencia: plantillas
  de informe, eventos del planificador, `NAV` y arrays de los widgets, grupos.
- Nunca eliminar un dispositivo con historial. Para moverlo a otro customer se usa "Cambiar
  propietario" (conserva UUID, telemetría y atributos). Eliminarlo borra su telemetría
  (housekeeper, PE ≥ 3.7).
- Licencia ThingsBoard PE plan Pilot: **100 dispositivos, 100 activos y 1 instancia de producción**.
  Cada alta debe revisar el cupo: el registro de instalaciones (Nivel 1) usa 1 activo por
  instalación, y los dispositivos espejo de un tenant de desarrollo cuentan para el límite de
  dispositivos.
- Entorno de desarrollo (decisión tomada, por implementar): un tenant separado de GONEX en la misma
  instancia. Hasta entonces, los parches pequeños se aplican directo en producción con rollback.

## Principios técnicos
- Zona horaria **America/Lima (UTC−5) explícita** en todo cálculo de día o mes.
- Los parámetros de negocio (umbrales, tarifas, destinatarios) los configura Sunkuu desde la
  plataforma, en una sola fuente. Nunca hardcodeados.

## Entidades de prueba (no son clientes)
"TG Hotel Prueba", "TG Prueba", "TG Gonex" y cualquier nombre que contenga "Prueba", "Erick" o "Gonex".

**Copia DEV (F16):** el widget "Sunkuu — Template 3EM DEV" (`afc86b80…`), en el dashboard TG PRUEBA,
lee el dispositivo de producción TG GOCTA (`c636fa00…`). Su guardado de atributos está bloqueado por
el bloque `// DEV-ONLY (FEAT-01)` en `renderCfgPanel`: mantenerlo en toda versión DEV y **nunca
copiarlo a producción**.

## Prioridad
1. Lo que reporta Romel.
2. Hallazgos de QA (`docs/qa/`), verificando cada uno contra producción antes de corregirlo.

## Configuración fuera del Version Control
ThingsBoard no exporta esto a `../sunkuu-tb-config`; lo que GONEX cambie aquí debe documentarse en `config/`.

| Configuración | Documentado en `config/` |
|---|---|
| Marca blanca de login | `config/white-labeling/` (`login-settings.md`, `login-advanced.css`) |
| Destinatarios y plantilla de notificación de los planificadores de informes (el export trae `targets: null`) | `config/informes/README.md` |
| Marca blanca general | Pendiente de capturar por Erick |
| Plantillas de correo | Pendiente de capturar por Erick |
| Traducción personalizada | Pendiente de capturar por Erick |
| Menú personalizado | Pendiente de capturar por Erick |
| Configuración de seguridad | Pendiente de capturar por Erick |
| Servidor de correo | Pendiente de capturar por Erick |
| Galería de imágenes | Parcial: solo `assets/brand/LOGO_SUNKUU_BLANCO.json`; resto pendiente de capturar por Erick |

Lección: el auto-commit no captura `notification_target`; tras crear o editar targets, hacer una versión manual (tipo `notification_target`) y `git pull`.

## Herramientas
- `qa/scripts/extract_widgets.py`: extrae los campos de los widgets a `qa/extract/` (ignorado).
- `widgets/*.json` en la raíz: instantánea histórica **previa al logo** (commit `ed00205`); no son la
  fuente de verdad.
