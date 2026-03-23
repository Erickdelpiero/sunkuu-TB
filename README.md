# sunkuu-TB

Repositorio del proyecto de plataforma IoT de monitoreo energético para **Sunkuu Energy S.A.C.**
Desarrollado por GONEX S.A.C. — Propuesta Gonex-2026-0302.

## Proyecto
- **Cliente:** Sunkuu Energy S.A.C. — Ing. Romel Valqui
- **Proveedor:** GONEX S.A.C. — Ing. Erick Del Piero Gonzales
- **Plataforma:** ThingsBoard Professional Edition 4.3.0PE
- **Instancia:** thingsboard.gonex.pe (admin GONEX) / plataforma.sunkuu.com (pendiente)
- **Inicio:** Marzo 2026
- **Marco:** Proyecto Proinnovate — 4 entregables en 8 semanas

## Cronograma y estado

| Entregable | Período | Descripción | Estado |
|---|---|---|---|
| E1 | Sem 1-2 (12–25 mar) | Infraestructura y marca blanca | 🟡 En curso |
| E2 | Sem 3-4 (26 mar–08 abr) | Migración 4 instalaciones activas | ⏳ Pendiente |
| E3 | Sem 5-6 (09–22 abr) | Dashboards, exportación y alarmas | ⏳ Pendiente |
| E4 | Sem 7-8 (23 abr–08 may) | Capacitación y entrega formal | ⏳ Pendiente |

## Estructura del repo
```
sunkuu-TB/
├── docs/
│   ├── contexto.md          — resumen del proyecto y decisiones técnicas
│   ├── accesos.md           — credenciales y accesos del sistema (gitignored)
│   └── informes/            — informes de entregable para Proinnovate
│       ├── informe-01.md
│       ├── informe-02.md
│       ├── informe-03.md
│       └── informe-final.md
├── thingsboard/
│   ├── tenant/              — configuración del tenant Sunkuu exportada
│   ├── device-profiles/     — perfiles Shelly Pro 3EM y monofásicos
│   ├── dashboards/          — exports JSON de dashboards
│   ├── rule-chains/         — exports JSON de motor de reglas y alarmas
│   └── white-label/         — assets de marca (logo, colores) — pendiente Sunkuu
└── README.md
```

## Dispositivos monitoreados
- **Tipo principal:** Shelly Pro 3EM (trifásico)
- **Protocolo:** MQTT → broker interno ThingsBoard
- **Instalaciones activas:** 4 (migración en Entregable 2)
- **Variables:** Voltaje, Corriente, Potencia Activa/Aparente, Factor de Potencia, Energía Acumulada/Devuelta, Frecuencia — por fase (A, B, C) y totales

## Infraestructura
La plataforma corre en el VPS de GONEX. Ver detalles técnicos en [gonex-infra](https://github.com/tu-usuario/gonex-infra).

- **Dominio temporal (admin):** https://thingsboard.gonex.pe
- **Dominio cliente (pendiente):** https://plataforma.sunkuu.com
- **MQTT broker:** thingsboard.gonex.pe:1883
- **Mensualidad servicio:** S/ 400 + IGV

## Contactos
| Rol | Nombre | Empresa |
|---|---|---|
| Administrador del sistema | Ing. Erick Del Piero Gonzales | GONEX S.A.C. |
| Administrador del tenant | Ing. Romel Valqui | Sunkuu Energy S.A.C. |
