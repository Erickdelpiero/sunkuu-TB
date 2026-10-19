# Informes mensuales: configuración fuera del Version Control

Fecha de captura: 2026-10-18 (hora de Lima). Fuente: la UI de ThingsBoard, confirmada por Erick.

El Version Control **no exporta** los destinatarios ni la plantilla de notificación de los planificadores:
en `../sunkuu-tb-config/scheduler_event/*.json` aparecen siempre `targets: null` y `notificationTemplateId: null`
aunque existan en producción. Lo que sí exporta es la plantilla de informe (`report_template/`), el
planificador (sin destinatarios) y los targets (`notification_target/`). Esta tabla es la única referencia
escrita de quién recibe cada informe.

## Configuración vigente

Usuario generador de los 4 planificadores: `romelvalqui.r@gmail.com` (ID `12fff710…`).
Plantilla de notificación de los 4: **Report generated notification** (`ff7b4330…`).

| Informe (dashboard) | Plantilla de informe | Planificador | Destinatarios (targets) |
|---|---|---|---|
| TG GOCTA (`e844d080`) | `900138f0…` | Informe Mensual TG GOCTA (`c72d8880…`) | Gocta Andes Lodge + Tenant administrators |
| Piscina Temperada (`cc2cad90`) | `94757860…` | Informe Mensual Piscina Temperada (`a6773ef0…`) | Gocta Andes Lodge + Tenant administrators |
| Medidor Tablero Principal (`0469dc30`) | `258ddba0…` | Informe Mensual Medidor Tablero Principal (`c967cba0…`) | Tucán Suites Aparthotel + Tenant administrators |
| TG PUMARINRI (`8e373390`) | `defa3090…` | Informe Mensual TG PUMARINRI (`8bee5690…`) | Pumarinri Amazon Lodge + Tenant administrators |

Targets de customer (tipo "Usuarios del customer"): Gocta Andes Lodge, Tucán Suites Aparthotel y
Pumarinri Amazon Lodge (este último, `notification_target/4685a730-cb5c-11f1-aa6f-7f75b1e7584b.json`, creado el 2026-10-18 y respaldado en la versión manual `ad72ef9`; ver `CHANGELOG.md`, INF-01).
"Tenant administrators" es el target de fábrica de ThingsBoard.

## Procedimiento para una instalación nueva

Hay **una plantilla de informe por dashboard**. Para cada instalación:

1. Plantilla de informe: duplicar una existente (Informes → Plantillas) y reapuntarla al dashboard de la
   instalación; ajustar nombre y título.
2. Target del customer: Notificaciones → Destinatarios → crear "<Customer>" de tipo "Usuarios del
   customer" con el customer correcto. Un target por customer; se reutiliza si el customer ya tiene otro informe.
3. Planificador: crear el evento de tipo "Generar informe" con la plantilla del paso 1, el usuario
   generador `romelvalqui.r@gmail.com`, destinatarios = target del paso 2 + "Tenant administrators", y la
   plantilla de notificación "Report generated notification".
4. Verificar que el customer tiene al menos un usuario con correo válido y probar el envío.
5. Actualizar la tabla de este archivo y registrar el cambio en `CHANGELOG.md`.

## Advertencias

- El auto-commit no captura `notification_target`; tras crearlos o editarlos, hacer una versión manual.
- El export trae `targets: null` aunque existan: no usar el repo para auditar destinatarios.
- Si se elimina o desactiva el usuario generador, los informes fallan.
- Al eliminar o mover un dashboard, revisar plantilla de informe, planificador y target (el caso de
  Pumarinri: el dashboard `32131e90` se eliminó el 2026-10-11 y la plantilla quedó apuntando a él hasta 2026-10-18).
- El target de un customer solo debe usarse para informes de dashboards de ese customer.
