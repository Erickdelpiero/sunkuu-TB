# Informe 02 — Entregable 2
## Sistema de Monitoreo Remoto de Consumo de Energía
**Proyecto:** Gonex-2026-0302
**Cliente:** Sunkuu Energy S.A.C.
**Proveedor:** GONEX S.A.C.
**Período:** 26 de marzo – 08 de abril de 2026
**Fecha de emisión:** 02 de abril de 2026

---

## 1. Resumen ejecutivo

Durante el período correspondiente al Entregable 2 se completó exitosamente la migración
de las instalaciones activas de Sunkuu Energy S.A.C. a la nueva plataforma ThingsBoard PE.
Se configuró la arquitectura de integración MQTT y se conectaron 6 dispositivos de 2 clientes
distintos, los cuales envían telemetría en tiempo real a la plataforma.

El hito verificable del entregable — *"Los proyectos activos de Sunkuu recibiendo y
visualizando datos en tiempo real en la nueva plataforma"* — ha sido alcanzado.

---

## 2. Hito verificable

**Estado:** ✅ Cumplido

Los siguientes dispositivos se encuentran activos y enviando telemetría en tiempo real
a la plataforma ThingsBoard PE en 360.sunkuu.com:

| Dispositivo | Tipo | Instalación | Cliente | Variables |
|---|---|---|---|---|
| shellypro3em-e08cfe972040 | Shelly Pro 3EM | TG Pumarinri | Gocta Andes Lodge | 25 variables eléctricas trifásicas |
| shellypro3em-ecc9ffe7f3ec | Shelly Pro 3EM | TG Gocta | Gocta Andes Lodge | 25 variables eléctricas trifásicas |
| shellyplus1-b8d61a8c2fe4 | Shelly Plus 1 | Piscina Temperada | Gocta Andes Lodge | Temperatura sonda + estado |
| shelly1pmminig3-84fce63fe438 | Shelly 1PM Mini Gen3 | Piscina Temperada | Gocta Andes Lodge | 8 variables eléctricas monofásicas |
| shellyhtg3-84fce63eed04 | Shelly H&T G3 | Piscina Temperada | Gocta Andes Lodge | Temperatura, humedad, batería |
| shellypro3em-a0dd6ca0bd68 | Shelly Pro 3EM | Tablero Principal | Tucán Suites Apart Hotel | 25 variables eléctricas trifásicas |

---

## 3. Trabajo realizado

### 3.1 Infraestructura MQTT

Se desplegó un broker MQTT externo **Mosquitto** (`eclipse-mosquitto:2`) como contenedor
Docker en el stack GONEX, resolviendo la limitación técnica por la cual ThingsBoard PE
no permite que su Integration se conecte a su propio broker interno.

**Arquitectura implementada:**
```
Shelly en campo → thingsboard.gonex.pe:1884 → Mosquitto → TB Integration → ThingsBoard
```

Cambios en infraestructura:
- Nuevo contenedor `gonex-mosquitto` en `docker-compose.yml`
- Puerto 1884 habilitado en UFW
- Volumen persistente `mosquitto-data`
- Archivo de configuración `mosquitto/mosquitto.conf`

### 3.2 Configuración en ThingsBoard PE

Se crearon los siguientes componentes en el tenant Sunkuu:

**Device Profiles (6 en total):**
- Shelly Pro 3EM, Shelly Pro EM50, Shelly Plus 1, Shelly 1PM Mini Gen3, Shelly H&T G3, default

**Uplink Data Converters (5):**
- Shelly Pro 3EM - Uplink
- Shelly Pro EM50 - Uplink
- Shelly 1PM Mini Gen3 - Uplink
- Shelly H&T G3 - Uplink
- Shelly Plus 1 Temp - Uplink

**MQTT Integrations (5):**
- Sunkuu - Pro 3EM MQTT Integration
- Sunkuu - Pro EM50 MQTT Integration
- Sunkuu - 1PM Mini Gen3 MQTT Integration
- Sunkuu - H&T G3 MQTT Integration
- Sunkuu - Plus 1 Temp MQTT Integration

### 3.3 Migración de dispositivos

Se configuró el broker MQTT en cada dispositivo Shelly online apuntando a
`thingsboard.gonex.pe:1884`. ThingsBoard creó automáticamente cada dispositivo
al recibir el primer mensaje.

---

## 4. Observaciones y pendientes

Los siguientes dispositivos no pudieron ser migrados por causas externas al alcance
técnico de GONEX:

| Dispositivo | Instalación | Razón | Acción requerida |
|---|---|---|---|
| shellyproem50-441d6475fe58 | Caldero Piscina | Señal WiFi inutilizable | Romel: instalar repetidor WiFi |
| shelly1pmminig3-54320440ad00 | Iluminación vereda | Sin conectividad | Romel: verificar dispositivo físico |
| shelly1pmminig3-84fce6385768 | Iluminación vestidor | Sin conectividad | Romel: verificar dispositivo físico |
| shelly1pmminig3-ecda3bc05a10 | Recepción | Sin conectividad | Romel: verificar dispositivo físico |

Estos dispositivos serán incorporados a la plataforma en cuanto Romel resuelva
los problemas de conectividad física. La infraestructura está lista para recibirlos
sin cambios adicionales.

---

## 5. Accesos verificados

| Plataforma | URL | Usuario | Estado |
|---|---|---|---|
| ThingsBoard PE (admin GONEX) | https://thingsboard.gonex.pe | sysadmin | ✅ Operativo |
| ThingsBoard PE (tenant Sunkuu) | https://360.sunkuu.com | Ing. Romel Valqui | ✅ Operativo |

---

## 6. Próximo entregable

**E3 — Dashboards, exportación y alarmas (09–22 abril 2026)**
- Dashboard por instalación con visualización en tiempo real
- Widget de exportación mensual a 15 minutos (CSV/Excel)
- Reportes automáticos mensuales por email
- Motor de alarmas con notificaciones por email y WhatsApp