# sunkuu-TB

Repositorio del proyecto de plataforma IoT de monitoreo energético para **Sunkuu Energy S.A.C.**
Desarrollado por GONEX S.A.C. — Propuesta Gonex-2026-0302.

## Proyecto
- **Cliente:** Sunkuu Energy S.A.C. — Ing. Romel Valqui
- **Proveedor:** GONEX S.A.C. — Ing. Erick Del Piero Gonzales
- **Plataforma:** ThingsBoard Professional Edition 4.3.0PE
- **Instancia admin GONEX:** https://thingsboard.gonex.pe
- **Instancia cliente Sunkuu:** https://360.sunkuu.com
- **Inicio:** Marzo 2026
- **Marco:** Proyecto Proinnovate — 4 entregables en 8 semanas

## Cronograma y estado

| Entregable | Período | Descripción | Estado |
|---|---|---|---|
| E1 | Sem 1-2 (12–25 mar) | Infraestructura y marca blanca | ✅ Completado |
| E2 | Sem 3-4 (26 mar–08 abr) | Migración instalaciones activas | ✅ Completado |
| E3 | Sem 5-6 (09–22 abr) | Dashboards, exportación y alarmas | ⏳ Pendiente |
| E4 | Sem 7-8 (23 abr–08 may) | Capacitación y entrega formal | ⏳ Pendiente |

## Dispositivos activos en ThingsBoard

| Dispositivo TB | Nombre Shelly | Tipo | Estancia | Cliente | Estado |
|---|---|---|---|---|---|
| shellypro3em-e08cfe972040 | TG PUMARINRI | Shelly Pro 3EM | TG Pumarinri | Gocta Andes Lodge | ✅ Activo |
| shellypro3em-ecc9ffe7f3ec | TG GOCTA | Shelly Pro 3EM | TG Gocta | Gocta Andes Lodge | ✅ Activo |
| shellyplus1-b8d61a8c2fe4 | Shelly_Temp_Piscina | Shelly Plus 1 + DS18B20 | Piscina Temperada | Gocta Andes Lodge | ✅ Activo |
| shelly1pmminig3-84fce63fe438 | Iluminación techo piscina | Shelly 1PM Mini Gen3 | Piscina Temperada | Gocta Andes Lodge | ✅ Activo |
| shellyhtg3-84fce63eed04 | Shelly_H&T_Piscina_Temp | Shelly H&T G3 | Piscina Temperada | Gocta Andes Lodge | ✅ Activo (batería — ciclo 2h) |
| shellypro3em-a0dd6ca0bd68 | Medidor Tablero Principal | Shelly Pro 3EM | Tablero Principal | Tucán Suites Apart Hotel | ✅ Activo |

## Dispositivos pendientes (requieren intervención física de Romel)

| Dispositivo | Tipo | Estancia | Razón |
|---|---|---|---|
| shellyproem50-441d6475fe58 | Shelly Pro EM50 | Caldero Piscina | Señal WiFi inutilizable |
| shelly1pmminig3-54320440ad00 | Shelly 1PM Mini Gen3 | Iluminación vereda | Offline — sin conectividad |
| shelly1pmminig3-84fce6385768 | Shelly 1PM Mini Gen3 | Iluminación vestidor piscina | Offline — sin conectividad |
| shelly1pmminig3-ecda3bc05a10 | Shelly 1PM Mini Gen3 | Recepción | Offline — sin conectividad |

## Arquitectura de integración MQTT
```
Shelly en campo
    → publica MQTT a thingsboard.gonex.pe:1884 (Mosquitto)
        → TB MQTT Integration se suscribe a Mosquitto:1884
            → Uplink Converter traduce el payload
                → ThingsBoard almacena telemetría
```

- **Broker MQTT:** Mosquitto (`gonex-mosquitto`) — puerto host 1884, interno 1883
- **Integrations TB:** 5 integrations (una por tipo de dispositivo)
- **Converters TB:** 5 converters JS (uno por tipo de dispositivo)
- **Device Profiles TB:** 5 perfiles (Pro 3EM, Pro EM50, Plus 1, 1PM Mini Gen3, H&T G3)

## Incorporar un nuevo dispositivo Shelly

Para agregar un dispositivo de un **tipo ya existente** (sin intervención técnica de GONEX):
1. En Shelly Cloud o interfaz web del dispositivo ir a **Settings → MQTT**
2. Activar MQTT
3. Marcar **"Notificaciones de estado de RPC"** y **"Actualización genérica del estado"**
4. Host:puerto: `thingsboard.gonex.pe:1884`
5. Sin usuario ni contraseña
6. Guardar y reiniciar el dispositivo

ThingsBoard creará el dispositivo automáticamente al recibir el primer mensaje.

Para un **tipo de dispositivo nuevo** contactar a GONEX para crear el Device Profile, Converter e Integration correspondientes.

## Estructura del repo
```
sunkuu-TB/
├── docs/
│   ├── sunkuu-TB-contexto.md     — decisiones técnicas y arquitectura
│   ├── sunkuu-TB-accesos.md      — credenciales y accesos (gitignored)
│   └── informes/
│       ├── sunkuu-TB-informe-01.md
│       ├── sunkuu-TB-informe-02.md
│       ├── sunkuu-TB-informe-03.md    (pendiente E3)
│       └── sunkuu-TB-informe-final.md (pendiente E4)
├── README.md
└── sunkuu-TB.gitignore
```

## Infraestructura

La plataforma corre en el VPS de GONEX. Ver detalles en [gonex-infra](https://github.com/Erickdelpiero/gonex-infra).

- **Dominio admin GONEX:** https://thingsboard.gonex.pe
- **Dominio cliente Sunkuu:** https://360.sunkuu.com
- **MQTT broker externo:** thingsboard.gonex.pe:1884 (Mosquitto)
- **Mensualidad servicio:** S/ 400 + IGV

## Contactos

| Rol | Nombre | Empresa |
|---|---|---|
| Administrador del sistema | Ing. Erick Del Piero Gonzales | GONEX S.A.C. |
| Administrador del tenant | Ing. Romel Valqui | Sunkuu Energy S.A.C. |