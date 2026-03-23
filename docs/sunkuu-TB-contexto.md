# Contexto técnico del proyecto

## Situación inicial de Sunkuu
Sunkuu Energy S.A.C. monitoreaba 4 instalaciones activas mediante dispositivos **Shelly Pro 3EM**
desde la plataforma genérica de **Shelly Cloud**, con dos limitaciones críticas:
- Sin identidad de marca propia
- Exportación de datos manual: 30 descargas individuales para obtener datos mensuales a 15 min de granularidad

## Solución implementada por GONEX
ThingsBoard Professional Edition auto-hospedado en VPS GONEX, configurado como plataforma
de marca blanca bajo la identidad de Sunkuu.

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
Se eligió In-Memory sobre Kafka por la escala actual del proyecto (4 instalaciones, <100 dispositivos).
Kafka solo se justifica para >1000 msg/seg sostenidos o despliegues en cluster.

### Puerto MQTT directo (sin Nginx)
Puerto 1883 expuesto directamente al exterior sin pasar por Nginx.
Los dispositivos Shelly se conectan vía MQTT TCP puro — Nginx no puede proxear este protocolo.

### Cloudflare: DNS Only para thingsboard.gonex.pe
A diferencia de n8n.gonex.pe y evolution.gonex.pe (proxied), ThingsBoard requiere DNS Only porque:
1. MQTT (1883) no puede pasar por el proxy de Cloudflare
2. WebSocket de dashboards tiene timeout de 100s en Cloudflare free

### Jerarquía de acceso
| Nivel | Usuario | Acceso |
|---|---|---|
| System Admin | GONEX (sysadmin) | Gestión técnica completa de la infraestructura |
| Tenant Admin | Sunkuu (Romel) | Gestión de todos sus proyectos y clientes |
| Customer User | Clientes de Sunkuu | Solo sus propios dispositivos y dashboards |

## Licencia ThingsBoard
- **Plan:** Pilot — $99 USD/mes
- **Límites:** 100 dispositivos, 1 instancia producción, white labeling incluido
- **Facturación:** Tarjeta GONEX S.A.C.
- **Repercusión al cliente:** S/ 400 + IGV mensual (Sunkuu → GONEX)

## Dominio del cliente
Pendiente confirmación de Romel sobre el subdominio a usar en sunkuu.com.
Mientras tanto, acceso de administración en thingsboard.gonex.pe.
Cuando se confirme el subdominio:
1. Agregar registro A en DNS de Sunkuu apuntando al VPS GONEX (77.237.233.255)
2. Generar certificado SSL con Certbot para el nuevo dominio
3. Agregar vhost en Nginx (mismo backend, diferente server_name)
4. Configurar white labeling en ThingsBoard con el dominio de Sunkuu
