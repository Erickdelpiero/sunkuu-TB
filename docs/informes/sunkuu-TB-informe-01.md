# Informe 01 — Entregable 1: Infraestructura y Marca Blanca

**Proyecto:** Sistema de monitoreo remoto de consumo de energía — Sunkuu  
**Propuesta:** Gonex-2026-0302  
**Proveedor:** GONEX S.A.C. — Ing. Erick Del Piero Gonzales  
**Cliente:** Sunkuu Energy S.A.C. — Ing. Romel Valqui  
**Período:** Semanas 1-2 (12 de marzo – 25 de marzo de 2026)  
**Fecha de informe:** Marzo 2026

---

## Hito verificable

> ThingsBoard PE operativo en línea con dominio Sunkuu activo y acceso de administrador funcionando.

**Estado: ✅ Completado**

---

## Actividades realizadas

### 1. Infraestructura de servidor
Se configuró el entorno de despliegue en servidor dedicado VPS con Ubuntu Server 24.04 LTS,
Docker y Nginx como reverse proxy con terminación SSL. La seguridad perimetral DNS está
gestionada por Cloudflare.

### 2. ThingsBoard PE instalado
Se desplegó ThingsBoard Professional Edition v4.3.0PE en contenedor Docker con:
- Base de datos PostgreSQL 16 dedicada
- Broker MQTT interno en puerto 1883
- Componente TB Web Report para generación de reportes PDF automáticos
- Configuración optimizada para producción (logging con rotación, restart automático)

### 3. Dominio y SSL
- Dominio operativo con certificado SSL válido (Let's Encrypt, válido hasta junio 2026)
- Renovación automática configurada
- Acceso HTTPS activo y verificado

### 4. Marca blanca Sunkuu
- Plataforma configurada bajo identidad Sunkuu
- [Completar con detalles de white labeling cuando se reciban los assets]
- Subdominio definitivo de Sunkuu pendiente de confirmación por Ing. Romel Valqui

### 5. Estructura de usuarios
- Tenant Sunkuu Energy S.A.C. creado en la plataforma
- Usuario administrador del tenant asignado al Ing. Romel Valqui
- Acceso verificado y funcional

---

## Evidencias

### Acceso a la plataforma
- **URL:** https://[dominio] *(pendiente subdominio Sunkuu)*
- **Acceso administrador Sunkuu:** Funcional ✅

### Capturas de pantalla
*(Adjuntar: login de la plataforma, dashboard principal, perfil del tenant Sunkuu)*

---

## Estado de entregables del período

| Entregable | Estado |
|---|---|
| Infraestructura de servidor | ✅ Completado |
| ThingsBoard PE instalado | ✅ Completado |
| Marca blanca Sunkuu | 🟡 Parcial (assets pendientes) |
| Estructura de usuarios | ✅ Completado |
| Dominio y SSL | ✅ Completado |

---

## Próximos pasos — Entregable 2
Período: 26 de marzo – 08 de abril de 2026

- Redirección MQTT de las 4 instalaciones activas al nuevo servidor
- Verificación de recepción de datos en tiempo real por cada instalación
- Creación de perfiles de dispositivo para Shelly Pro 3EM

---

*Documento generado por GONEX S.A.C.*
