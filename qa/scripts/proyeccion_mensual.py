#!/usr/bin/env python3
"""Proyección mensual de consumo y costo, recalculada de forma independiente y
comparada con la fórmula que usan los widgets.

Métodos:
  A. Fórmula actual de los widgets: energía_hoy / horas_transcurridas_hoy × 24 × días_del_mes
     (se replica con la energía real 00:00→ahora; el widget además pierde la 1ª hora, ver H1).
  B. Mes a la fecha + promedio diario de los días completos ya transcurridos × días restantes.
  C. Mes a la fecha / horas transcurridas del mes × horas totales del mes.
  D. Fórmula del Portal de Flota ("Costo estimado — mes"): energía_hoy × 30 × 0.65.

Uso:
    python3 qa/scripts/proyeccion_mensual.py --csv export.csv --a-las "2026-10-06 14:30" --tarifa 0.65
"""
import argparse
import calendar
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sunkuu_csv import (counter_delta, lima_dt, load_series, to_ms, warn_if_aggregated,
                        wh_to_kwh)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", required=True)
    ap.add_argument("--a-las", dest="asof", required=True, help="'YYYY-MM-DD HH:MM' hora Lima")
    ap.add_argument("--tarifa", type=float, default=0.65, help="S/. por kWh (por defecto 0.65)")
    ap.add_argument("--columna", default="energia_total")
    args = ap.parse_args()

    serie = load_series(args.csv, args.columna)
    warn_if_aggregated(serie, args.columna)

    now = lima_dt(args.asof)
    hoy0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    mes0 = hoy0.replace(day=1)
    dias_mes = calendar.monthrange(now.year, now.month)[1]
    mes_fin = mes0 + dt.timedelta(days=dias_mes)

    e_hoy, _, n0, n1 = counter_delta(serie, to_ms(hoy0), to_ms(now))
    e_mtd, r_mtd, m0, m1 = counter_delta(serie, to_ms(mes0), to_ms(now))
    e_comp, _, _, _ = counter_delta(serie, to_ms(mes0), to_ms(hoy0))
    if e_hoy is None:
        sys.exit("No se puede calcular la energía de hoy: %s / %s" % (n0, n1))
    print("Momento de referencia: %s (Lima) · mes de %d días" % (now.strftime("%Y-%m-%d %H:%M"), dias_mes))
    print("Energía hoy (00:00→ahora): %.3f kWh" % wh_to_kwh(e_hoy))

    horas_hoy = max((now - hoy0).total_seconds() / 3600.0, 0.5)
    a = wh_to_kwh(e_hoy) / horas_hoy * 24 * dias_mes
    print("A. Fórmula widgets:          %10.1f kWh  ≈ S/. %10.2f" % (a, a * args.tarifa))

    if e_mtd is None:
        print("B/C: el CSV no cubre desde el 1 del mes (%s). Exporte desde %s."
              % (m0, mes0.strftime("%Y-%m-%d 00:00")))
    else:
        print("Mes a la fecha:              %10.1f kWh" % wh_to_kwh(e_mtd))
        if r_mtd:
            print("  AVISO: %d disminución(es) del contador en el mes." % r_mtd)
        dias_completos = (hoy0 - mes0).days
        if dias_completos > 0 and e_comp is not None:
            prom = wh_to_kwh(e_comp) / dias_completos
            restante_h = (mes_fin - now).total_seconds() / 3600.0
            b = wh_to_kwh(e_mtd) + prom * restante_h / 24.0
            print("B. MTD + promedio diario:    %10.1f kWh  ≈ S/. %10.2f  (prom. %.1f kWh/día, %d días completos)"
                  % (b, b * args.tarifa, prom, dias_completos))
        else:
            print("B. No aplica (aún no hay días completos en el mes).")
        h_mes = (now - mes0).total_seconds() / 3600.0
        if h_mes > 0:
            c = wh_to_kwh(e_mtd) / h_mes * dias_mes * 24
            print("C. MTD / horas del mes:      %10.1f kWh  ≈ S/. %10.2f" % (c, c * args.tarifa))

    d = wh_to_kwh(e_hoy) * 30 * 0.65
    print("D. Fórmula Portal de Flota:  S/. %10.2f  (energía_hoy × 30 × 0.65, tarifa fija)" % d)


if __name__ == "__main__":
    main()
