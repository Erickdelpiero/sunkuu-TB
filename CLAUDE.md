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

## Principios técnicos
- Zona horaria **America/Lima (UTC−5) explícita** en todo cálculo de día o mes.
- Los parámetros de negocio (umbrales, tarifas, destinatarios) los configura Sunkuu desde la
  plataforma, en una sola fuente. Nunca hardcodeados.

## Entidades de prueba (no son clientes)
"TG Hotel Prueba", "TG Prueba", "TG Gonex" y cualquier nombre que contenga "Prueba", "Erick" o "Gonex".

**Advertencia F16:** el widget/dashboard DEV (copia `afc86b80…`) lee y PUEDE ESCRIBIR atributos en el
dispositivo de producción TG Pumarinri. No usar su función de guardado hasta que se corrija.

## Prioridad
1. Lo que reporta Romel.
2. Hallazgos de QA (`docs/qa/`), verificando cada uno contra producción antes de corregirlo.

## Configuración fuera del Version Control
ThingsBoard no exporta esto a `../sunkuu-tb-config`; lo que GONEX cambie aquí debe documentarse en `config/`.

| Configuración | Documentado en `config/` |
|---|---|
| Marca blanca de login | `config/white-labeling/` (`login-settings.md`, `login-advanced.css`) |
| Marca blanca general | Pendiente de capturar por Erick |
| Plantillas de correo | Pendiente de capturar por Erick |
| Traducción personalizada | Pendiente de capturar por Erick |
| Menú personalizado | Pendiente de capturar por Erick |
| Configuración de seguridad | Pendiente de capturar por Erick |
| Servidor de correo | Pendiente de capturar por Erick |
| Galería de imágenes | Parcial: solo `assets/brand/LOGO_SUNKUU_BLANCO.json`; resto pendiente de capturar por Erick |

## Herramientas
- `qa/scripts/extract_widgets.py`: extrae los campos de los widgets a `qa/extract/` (ignorado).
- `widgets/*.json` en la raíz: instantánea histórica **previa al logo** (commit `ed00205`); no son la
  fuente de verdad.
