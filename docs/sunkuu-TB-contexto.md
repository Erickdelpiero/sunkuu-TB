# Contexto técnico del proyecto

## Situación inicial de Sunkuu
Sunkuu Energy S.A.C. monitoreaba instalaciones activas mediante dispositivos Shelly
desde la plataforma genérica de **Shelly Cloud**, con dos limitaciones críticas:
- Sin identidad de marca propia
- Exportación de datos manual: hasta 30 descargas individuales para obtener datos
  mensuales a 15 min de granularidad

## Solución implementada por GONEX
ThingsBoard Professional Edition auto-hospedado en VPS GONEX, configurado como plataforma
de marca blanca bajo la identidad de Sunkuu (360.sunkuu.com).

## Decisiones técnicas clave

### Docker sobre instalación nativa
Todo el stack de GONEX corre en Docker. ThingsBoard PE se integró como dos contenedores
al `docker-compose.yml` existente:
- `gonex-thingsboard` — plataforma principal (imagen `tb-pe-node:4.3.0PE`)
- `gonex-tb-web-report` — generador de reportes PDF (imagen `tb-pe-web-report:4.3.0PE`)

### PostgreSQL compartido
ThingsBoard usa la instancia PostgreSQL existente del stack GONEX (`gonex-postgres`),
con base de datos dedicada `thingsboard`. Usuario: `gonex`.

### Cola de mensajes: In-Memory
Se eligió In-Memory sobre Kafka por la escala actual del proyecto (<100 dispositivos).
Kafka solo se justifica para >1000 msg/seg sostenidos o despliegues en cluster.

### Arquitectura MQTT: Mosquitto como broker externo
**Decisión clave del E2:** ThingsBoard PE no permite que su MQTT Integration se conecte
a su propio broker interno (puerto 1883). El broker interno solo acepta conexiones de
dispositivos con credenciales nativas de TB (access tokens).

Se desplegó **Mosquitto** (`eclipse-mosquitto:2`) como contenedor Docker independiente:
- Puerto host: 1884 (dispositivos Shelly desde internet)
- Puerto interno Docker: 1883 (ThingsBoard Integration desde gonex-network)
- Autenticación: anónima (red interna + UFW)

Flujo completo:
```
Shelly → thingsboard.gonex.pe:1884 → Mosquitto → TB MQTT Integration → Converter → ThingsBoard
```

### Puerto MQTT directo (sin Nginx)
Puerto 1884 expuesto directamente al exterior sin pasar por Nginx.
Los dispositivos Shelly se conectan vía MQTT TCP puro — Nginx no puede proxear este protocolo.

### Cloudflare: DNS Only para thingsboard.gonex.pe
A diferencia de n8n.gonex.pe y evolution.gonex.pe (proxied), ThingsBoard requiere DNS Only porque:
1. MQTT (1883, 1884) no puede pasar por el proxy de Cloudflare
2. WebSocket de dashboards tiene timeout de 100s en Cloudflare free

### Jerarquía de acceso
| Nivel | Usuario | Acceso |
|---|---|---|
| System Admin | GONEX (sysadmin) | Gestión técnica completa de la infraestructura |
| Tenant Admin | Sunkuu (Romel) | Gestión de todos sus proyectos y clientes |
| Customer User | Clientes de Sunkuu | Solo sus propios dispositivos y dashboards |

### Integrations MQTT (una por tipo de dispositivo)
| Integration | Converter | Topics escuchados |
|---|---|---|
| Sunkuu - Pro 3EM MQTT Integration | Shelly Pro 3EM - Uplink | `+/status/em:0`, `+/status/emdata:0` |
| Sunkuu - Pro EM50 MQTT Integration | Shelly Pro EM50 - Uplink | `+/status/em1:0`, `+/status/em1:1`, `+/status/em1data:0`, `+/status/em1data:1` |
| Sunkuu - 1PM Mini Gen3 MQTT Integration | Shelly 1PM Mini Gen3 - Uplink | `+/status/switch:0` |
| Sunkuu - H&T G3 MQTT Integration | Shelly H&T G3 - Uplink | `+/status/temperature:0`, `+/status/humidity:0`, `+/status/devicepower:0` |
| Sunkuu - Plus 1 Temp MQTT Integration | Shelly Plus 1 Temp - Uplink | `+/status/switch:0`, `+/status/temperature:0`, `+/status/temperature:1`, `+/status/temperature:101` |

### Guard clauses en converters
Los converters de H&T G3, Plus 1 y 1PM Mini Gen3 incluyen guard clauses que verifican
el prefijo del deviceName (`shellyhtg3-`, `shellyplus1-`, `shelly1pmminig3-`) para evitar
contaminación cruzada entre dispositivos que comparten topics similares (ej: `switch:0`
es publicado tanto por Plus 1 como por 1PM Mini Gen3).

### Comportamiento del H&T G3 (batería)
El Shelly H&T G3 es un dispositivo a batería que opera en modo sleep. Se despierta
cada 2 horas para publicar temperatura, humedad y nivel de batería. En ThingsBoard
aparecerá como inactivo entre publicaciones — es comportamiento esperado y correcto.
Los dashboards deben usar el último valor conocido, no estado en tiempo real.

### Shelly Plus 1 con sondas DS18B20
El dispositivo `shellyplus1-b8d61a8c2fe4` tiene sondas de temperatura externas conectadas
que publican en `temperature:101` (no en `temperature:0` o `temperature:1` como es estándar).
Este es el ID asignado por el firmware cuando las sondas se conectan como addon externo.

## Licencia ThingsBoard
- **Plan:** Pilot — $99 USD/mes
- **Límites:** 100 dispositivos, 1 instancia producción, white labeling incluido
- **Facturación:** Tarjeta GONEX S.A.C.
- **Repercusión al cliente:** S/ 400 + IGV mensual (Sunkuu → GONEX)

## Dominio del cliente
- **Dominio activo:** 360.sunkuu.com (DNS en Hostinger, gestionado por equipo técnico de Romel)
- **SSL:** Certbot HTTP-01, vence 2026-06-22, auto-renovación activa
- **White labeling:** Logo Sunkuu, colores #00008c / #00ebc8, título "Sunkuu 360"

## Shelly Cloud en paralelo
Por decisión de Romel, Shelly Cloud se mantiene activo en paralelo con ThingsBoard.
Los dispositivos publican simultáneamente a Shelly Cloud y a Mosquitto.
Esto permite que Romel mantenga acceso a ambas plataformas durante la transición.