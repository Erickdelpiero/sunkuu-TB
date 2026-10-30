# Cómo conectar un Shelly Pro EM-50 nuevo a Sunkuu 360

Guía para Romel · 2026-10-30 · Tiempo: unos 15 minutos por equipo.

Sirve para cada habitación nueva con un Shelly Pro EM-50 (la próxima: Hab. 104). Es la misma configuración que ya funciona en la Hab. 105.

## 1. Instalación física

1. Coloca la **pinza en el canal 0** (el primero), en la acometida de la habitación.
2. El canal 1 queda libre. No hace falta conectar nada ahí.
3. Si hay red por cable, usa el puerto LAN; si no, el Wi-Fi del hotel.

## 2. En la app Shelly

**a) Anota el ID del equipo.** Entra al equipo → *Información del dispositivo* → **Device ID**.
Tiene que verse así: `shellyproem50-` seguido de 12 letras y números, todo en minúsculas (ejemplo: `shellyproem50-441d6474e3f8`; para la Hab. 104 esperamos `shellyproem50-441d6475f6c0`). Si empieza distinto, no sigas y avísame.

**b) No actualices el firmware**, aunque la app lo ofrezca. Lo actualizamos juntos más adelante.

**c) Configura MQTT.** *Ajustes* → *MQTT*:

| Opción | Qué poner |
|---|---|
| Habilitar MQTT | **Sí** |
| Servidor | `thingsboard.gonex.pe:1884` |
| Client ID | **No lo cambies** (deja el que viene) |
| Prefijo MQTT | **No lo cambies** (viene igual al Device ID) |
| Usuario y contraseña | Vacíos |
| SSL / TLS | Desactivado |
| Actualización genérica del estado a través de MQTT | **Activado** (es lo que envía las mediciones) |
| Notificaciones RPC por MQTT | Desactivado |
| Control por MQTT / RPC por MQTT (si aparece) | **Desactivado** |

**d) Guarda y reinicia el equipo.** Anota la hora del reinicio.

**e) Comprueba:** después de 1–2 minutos, en *Ajustes → MQTT* debe decir **Conectado**.

Shelly Cloud sigue funcionando igual: no hace falta desactivarlo.

## 3. Qué me envías

Por WhatsApp, apenas termines:

1. El **Device ID** (copiado tal cual, mejor una captura de pantalla).
2. El **nombre de la habitación**, como quieres que aparezca en la plataforma (por ejemplo, `Hab. 104`).
3. La **hora del reinicio**.
4. Una **captura de la pantalla de MQTT** ya guardada.
5. Si algo no salió como en esta guía (otra opción, otro nombre, "Desconectado").

## 4. Qué hago yo después

1. **Conexión** (el mismo día): compruebo que los datos llegan, asigno el medidor a Apu Samay y le pongo la tarifa.
2. **Dashboard y registro** (el mismo día o el siguiente): creo el dashboard de la habitación, igual al de la Hab. 105, y la doy de alta en la plataforma.
3. **Revisión al día siguiente**: confirmo que la energía de hoy y la de ayer cuadran con la app Shelly.

Te aviso cuando la habitación ya se vea en Sunkuu 360.
