# SEC-03 — Mosquitto expuesto a internet sin autenticación

Fecha: 2026-10-26 · Base: `../sunkuu-tb-config` `8a1f930` y `../gonex-infra` `2cf8302` (solo lectura) · **Abierto. Nada aplicado.**
Origen: análisis de la Opción A (`docs/arquitectura/2026-10-26-opcion-A-proem.md` §6).

## 1. Hallazgo (lectura de configuración, sin pruebas en vivo)

- `gonex-infra/mosquitto/mosquitto.conf`: `listener 1883` y `allow_anonymous true`. No hay `password_file` ni `acl_file`.
- `gonex-infra/docker-compose.yml`: el contenedor `gonex-mosquitto` publica `1884:1883` en todas las interfaces. Los Shelly se conectan desde internet a `thingsboard.gonex.pe:1884` (`docs/servicios.md`). La nota "red interna + UFW" no protege este puerto: está abierto a propósito, para los dispositivos.
- Las 5 integraciones MQTT de ThingsBoard leen de ese broker de forma anónima y tienen `allowCreateDevicesOrAssets: true`.

| Converter | Filtro de prefijo |
|---|---|
| Shelly Pro 3EM (`df3eb870`) | **No** |
| Shelly Pro EM50 (`b69ff030`) | **No** |
| Shelly Plus 1 Temp (`ed204fa0`) | `shellyplus1-` |
| Shelly H&T G3, Shelly 1PM Mini Gen3 | Sí, según `docs/sunkuu-TB-contexto.md` (no se revisó el código de estos dos) |

## 2. Impacto (por deducción de la configuración; no se probó)

1. **Crear dispositivos:** quien publique `<cualquier nombre>/status/em:0` o `…/em1:0` crea un dispositivo del tenant y gasta cupo de licencia (100). Con prefijo, solo se pueden crear nombres que lo cumplan.
2. **Inyectar telemetría** en dispositivos existentes, conociendo su nombre (`shellypro3em-<mac>`). Los dashboards, los informes y el costo mostrarían datos falsos.
3. **Leer en tiempo real** la telemetría de todos los equipos, suscribiéndose a `#`. Sin ACL, Mosquitto lo permite a cualquier cliente anónimo. Es una exposición de confidencialidad entre customers y frente a terceros, independiente de SEC-02.

## 3. Mitigación

| # | Medida | Cubre | Estado |
|---|---|---|---|
| M1 | **Filtro `shellyproem50-` en el converter Pro EM50** (igual que Plus 1: `return null` si no coincide) | Impacto 1, solo para la integración Pro EM50 | **Decidido (Erick, 2026-10-26)**. Va como A-01, antes de conectar Hab. 105 |
| M2 | El mismo filtro en el converter Pro 3EM (`shellypro3em-`) | Impacto 1 para el 3EM | **Decidido (Erick, 2026-10-26)**, con rollback. Va en A-01. Los 4 nombres actuales cumplen el prefijo |
| M3 | Autenticación en Mosquitto (`password_file`, `allow_anonymous false`) y ACL por usuario (lectura de `#` solo para ThingsBoard) | Impactos 1, 2 y 3 | **Se evalúa aparte** (decisión de Erick). Requiere usuario y contraseña en cada Shelly en campo (visita o Shelly Cloud) y en las 5 integraciones. Coordinar con Romel |
| M4 | TLS en el listener | Credenciales y datos en tránsito | Con M3 |

## 4. Resultados

| Paso | Resultado | Notas |
|---|---|---|
| Hallazgo | Registrado (lectura de configuración) | §1 |
| M1 y M2 | Preparados en A-01 (`docs/qa/2026-10-26-A-01.md`), no aplicados | |
| M3 | Pendiente de evaluación | |
