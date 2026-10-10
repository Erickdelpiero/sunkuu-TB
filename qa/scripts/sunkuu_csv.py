"""Utilidades comunes para recalcular métricas de Sunkuu 360 a partir de un CSV
exportado desde el Centro de Exportación.

Formato esperado del CSV (tal como lo genera el widget):
    timestamp_ms,fecha,hora,<clave1>,<clave2>,...
- Codificación UTF-8 con BOM.
- 'fecha' y 'hora' están en la zona horaria del NAVEGADOR que exportó, por eso
  aquí se ignoran: todo se calcula desde timestamp_ms convertido a America/Lima.
- Para instalaciones 3EM las columnas son las keys de TB (energia_total, ...).

Sin dependencias externas (solo biblioteca estándar).
"""
import csv
import datetime as dt
import sys

try:
    from zoneinfo import ZoneInfo
    LIMA = ZoneInfo("America/Lima")
except Exception:  # Python < 3.9 o sin tzdata: Lima es UTC-5 fijo, sin horario de verano
    LIMA = dt.timezone(dt.timedelta(hours=-5), "America/Lima")


def load_series(path, column):
    """Devuelve [(ts_ms, valor_float)] ordenado por ts, omitiendo celdas vacías."""
    out = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "timestamp_ms" not in (reader.fieldnames or []):
            sys.exit("ERROR: el CSV no tiene columna 'timestamp_ms'. ¿Es un export del Centro de Exportación?")
        if column not in reader.fieldnames:
            sys.exit("ERROR: columna '%s' no encontrada. Columnas disponibles: %s"
                     % (column, ", ".join(reader.fieldnames)))
        for row in reader:
            raw = (row.get(column) or "").strip()
            if raw == "":
                continue
            try:
                out.append((int(float(row["timestamp_ms"])), float(raw)))
            except ValueError:
                continue
    out.sort(key=lambda p: p[0])
    if not out:
        sys.exit("ERROR: la columna '%s' no tiene valores." % column)
    return out


def warn_if_aggregated(series, label="serie"):
    """Avisa si el CSV parece agregado (TB devuelve el punto medio del intervalo)."""
    if len(series) < 3:
        return
    steps = {series[i + 1][0] - series[i][0] for i in range(min(len(series) - 1, 50))}
    if len(steps) == 1:
        step = steps.pop()
        print("AVISO: %s con paso constante de %d ms: parece un export AGREGADO. "
              "Para contadores use 'Raw (sin agrupación)'; con datos agregados el "
              "resultado es aproximado." % (label, step))


def lima_dt(text):
    """'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM' interpretado en hora Lima -> datetime aware."""
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text, fmt).replace(tzinfo=LIMA)
        except ValueError:
            pass
    sys.exit("ERROR: fecha '%s' inválida (use YYYY-MM-DD o 'YYYY-MM-DD HH:MM')." % text)


def to_ms(d):
    return int(d.timestamp() * 1000)


def fmt_ms(ts):
    return dt.datetime.fromtimestamp(ts / 1000, LIMA).strftime("%Y-%m-%d %H:%M:%S Lima")


def value_at(series, ts, max_gap_ms=30 * 60 * 1000):
    """Valor del contador en el instante ts por interpolación lineal entre la
    lectura anterior y la siguiente. Devuelve (valor, detalle) o (None, motivo)."""
    before = None
    after = None
    for p in series:
        if p[0] <= ts:
            before = p
        else:
            after = p
            break
    if before is None:
        return None, "no hay lecturas antes de %s (amplíe el rango del export)" % fmt_ms(ts)
    if after is None:
        if before[0] == ts:
            return before[1], "lectura exacta"
        return None, "no hay lecturas después de %s (amplíe el rango del export)" % fmt_ms(ts)
    gap = after[0] - before[0]
    note = "interpolado entre %s y %s" % (fmt_ms(before[0]), fmt_ms(after[0]))
    if gap > max_gap_ms:
        note += " — AVISO: hueco de %.1f min sin datos" % (gap / 60000.0)
    if after[1] < before[1]:
        note += " — AVISO: el contador DISMINUYE en este tramo (¿reset?)"
    frac = (ts - before[0]) / float(gap) if gap else 0.0
    return before[1] + (after[1] - before[1]) * frac, note


def counter_delta(series, start_ms, end_ms):
    """Energía entre start y end sumando solo incrementos positivos del contador
    (robusto a resets). Devuelve (delta, n_resets, detalle_inicio, detalle_fin)."""
    v0, n0 = value_at(series, start_ms)
    v1, n1 = value_at(series, end_ms)
    if v0 is None or v1 is None:
        return None, 0, n0, n1
    pts = [(start_ms, v0)] + [p for p in series if start_ms < p[0] < end_ms] + [(end_ms, v1)]
    total, resets = 0.0, 0
    for a, b in zip(pts, pts[1:]):
        d = b[1] - a[1]
        if d >= 0:
            total += d
        else:
            resets += 1  # tras un reset el contador reinicia: no se suma el salto negativo
    return total, resets, n0, n1


def wh_to_kwh(v):
    return None if v is None else v / 1000.0
