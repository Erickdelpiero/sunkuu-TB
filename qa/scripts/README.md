# qa/scripts — herramientas de revisión técnica de Sunkuu 360

Todo usa solo la biblioteca estándar de Python 3 (se recomienda ≥ 3.9 por `zoneinfo`; si no está disponible se usa UTC−5 fijo, que es equivalente para Lima porque no tiene horario de verano). Ningún script hace llamadas de red ni escribe en `../sunkuu-tb-config`.

| Script | Para qué |
|---|---|
| `extract_widgets.py` | Extrae los widget_type de producción a `qa/extract/` (html/css/js/json) con el commit analizado. |
| `energia_dia.py` | Energía de un día de calendario en hora Lima + peso de la primera y última hora (H1/H2/H4). |
| `energia_hasta_hora.py` | Energía de 00:00 a una hora dada (contrasta "Energía acumulada hoy", H1). |
| `factor_potencia.py` | FP correcto P_total/S_total frente a la media de fases (H5). |
| `proyeccion_mensual.py` | Proyección mensual con 4 métodos (widget, MTD+promedio, MTD/horas, Portal de Flota). |
| `sunkuu_csv.py` | Módulo común (lectura de CSV, hora Lima, interpolación del contador). No se ejecuta solo. |

---

## 1. Extracción de widgets (cada revisión)

```bash
cd sunkuu-TB
python3 -I qa/scripts/extract_widgets.py --config ../sunkuu-tb-config --out qa/extract
```

- Omite la copia DEV por defecto (`--include-dev` para incluirla).
- Escribe `qa/extract/MANIFEST.json` con el `git rev-parse HEAD` de `sunkuu-tb-config`. Las líneas citadas en los informes son las de estos archivos extraídos.
- `qa/extract/` está en `qa/.gitignore`: es derivado y se regenera.

---

## 2. Qué CSV exportar del Centro de Exportación

Hay que exportar **por instalación 3EM** (TG Gocta, TG Pumarinri o Medidor Tucán) con estas opciones:

| Campo | Valor |
|---|---|
| Instalación | la que se quiere validar (p. ej. **TG Gocta**) |
| Variables | botón **Ninguna** y luego marcar solo lo que pida cada script (tabla de abajo) |
| Granularidad | **Raw (sin agrupación)** — obligatorio para contadores. Con 15 min/1 h TB devuelve el punto medio del intervalo y el MAX del bucket, y el resultado deja de ser exacto (el script avisa si detecta un export agregado). |
| Agregación | (no aplica en Raw) |
| Desde / Hasta | en **hora Lima**. Los campos `datetime-local` usan la zona horaria del PC: exporte desde un equipo configurado en America/Lima o ajuste la diferencia. Siempre deje **margen** antes y después (los scripts interpolan el contador en los límites). |

| Script | Variables a marcar | Rango mínimo del export (hora Lima) |
|---|---|---|
| `energia_dia.py --dia D` | Energía Total | D−1 23:00 → D+1 01:00 |
| `energia_hasta_hora.py --hasta "D HH:MM"` | Energía Total | D−1 23:00 → D HH:MM + 30 min |
| `factor_potencia.py` | Pot. Activa Total, Pot. Aparente Total, Factor Pot. Fase A, B y C | el periodo a analizar (1–2 días bastan) |
| `proyeccion_mensual.py --a-las "D HH:MM"` | Energía Total | último día del mes anterior 23:00 → D HH:MM + 30 min |

Precauciones (ver hallazgos del informe sobre el export Raw):

- Exporte **una sola variable** (Energía Total) para rangos largos. El export Raw con varias variables puede truncar datos sin aviso cuando una de ellas supera 50 000 puntos.
- Compruebe que la **última fila** del CSV llega al final del rango pedido. Si no llega, divida el rango en varios exports.
- Las columnas `fecha` y `hora` del CSV están en la zona del navegador. Los scripts las ignoran y usan `timestamp_ms` convertido a America/Lima.

---

## 3. Cómo ejecutar cada script

```bash
# Energía de un día de calendario (y cuánto pesa la 1ª hora que excluyen H1/H2)
python3 qa/scripts/energia_dia.py --csv Sunkuu_TG_GOCTA_..._raw.csv --dia 2026-10-05

# Energía 00:00 → hora dada; --widget = lo que mostraba "Energía acumulada hoy" a esa hora
python3 qa/scripts/energia_hasta_hora.py --csv export.csv --hasta "2026-10-06 14:30" --widget 123.4

# Factor de potencia correcto vs media de fases (instantáneo y del periodo)
python3 qa/scripts/factor_potencia.py --csv export_fp.csv --desde "2026-10-05 00:00" --hasta "2026-10-06 00:00"

# Proyección mensual (compárela con "Proyección del mes" del widget a la misma hora)
python3 qa/scripts/proyeccion_mensual.py --csv export_mes.csv --a-las "2026-10-06 14:30" --tarifa 0.65
```

Todos aceptan `--columna` si el contador tiene otro nombre (por defecto `energia_total`, en Wh).

---

## 4. Protocolo sugerido para validar las hipótesis

Antes de exportar, **capture pantalla** del widget anotando la hora exacta. Después:

| Hipótesis | Qué comparar |
|---|---|
| H1 (excluye la 1ª hora de hoy) | `energia_hasta_hora.py --hasta "<hora captura>" --widget <kv-en>`. Si la diferencia ≈ energía de 00:00–01:00 (la imprime `energia_dia.py`), se confirma. |
| H2 (rango de "ayer") | `energia_dia.py --dia <ayer>` frente al "Ayer: X kWh" de la tarjeta *vs. ayer* del 3EM. El script imprime también la energía de la primera y la última hora para ver cuál falta. |
| H3 (parcial vs día completo) | El % de *vs. ayer* del widget frente a `energia_hasta_hora` de hoy y de ayer a la misma hora. |
| H4 (vs semana anterior) | El "Hace 7d: X kWh" del widget frente a `energia_dia.py` de D−7 y de D−8. Si X ≈ suma de ambos, se confirma la ventana de 48 h. |
| H5 (FP) | `factor_potencia.py`: media de fases frente a P_total/S_total. |
| Proyección | `proyeccion_mensual.py`: método A frente al widget; B/C frente a A para dimensionar el error. |
| Export 15 min | Exporte 15 min/MAX con "Desde" en un cuarto de hora exacto (p. ej. 10:00). Si los `timestamp_ms` caen en 10:07:30, 10:22:30, …, se confirma que TB devuelve el punto medio del intervalo. Con "Desde" en 10:03 los buckets quedan desalineados del cuarto de hora. |
