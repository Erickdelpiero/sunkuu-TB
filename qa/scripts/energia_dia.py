#!/usr/bin/env python3
"""Energía de un día de calendario en hora Lima (00:00 → 24:00 America/Lima),
a partir del contador acumulado energia_total (Wh) de un CSV del Centro de
Exportación. Además cuantifica lo que excluyen los métodos actuales (H1/H2).

Uso:
    python3 qa/scripts/energia_dia.py --csv export.csv --dia 2026-10-05
    python3 qa/scripts/energia_dia.py --csv export.csv --dia 2026-10-05 --columna energia_total
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sunkuu_csv import (counter_delta, lima_dt, load_series, to_ms, warn_if_aggregated,
                        wh_to_kwh)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", required=True)
    ap.add_argument("--dia", required=True, help="YYYY-MM-DD (día de calendario en hora Lima)")
    ap.add_argument("--columna", default="energia_total", help="columna del contador en Wh")
    args = ap.parse_args()

    serie = load_series(args.csv, args.columna)
    warn_if_aggregated(serie, args.columna)

    d0 = lima_dt(args.dia)
    d1 = d0 + dt.timedelta(days=1)
    h1 = d0 + dt.timedelta(hours=1)
    h23 = d1 - dt.timedelta(hours=1)

    total, resets, n0, n1 = counter_delta(serie, to_ms(d0), to_ms(d1))
    print("Día (hora Lima):        %s 00:00 → %s 00:00" % (d0.date(), d1.date()))
    print("  inicio: %s" % n0)
    print("  fin:    %s" % n1)
    if total is None:
        sys.exit("No se puede calcular: el CSV no cubre ambos límites del día.")
    print("ENERGÍA DEL DÍA:        %.3f kWh" % wh_to_kwh(total))
    if resets:
        print("  AVISO: %d disminución(es) del contador; se sumaron solo incrementos." % resets)

    primera, _, _, _ = counter_delta(serie, to_ms(d0), to_ms(h1))
    ultima, _, _, _ = counter_delta(serie, to_ms(h23), to_ms(d1))
    if primera is not None:
        print("  00:00–01:00 (primera hora, la que excluyen H1/H2): %.3f kWh (%.1f%% del día)"
              % (wh_to_kwh(primera), 100.0 * primera / total if total else 0.0))
    if ultima is not None:
        print("  23:00–24:00 (última hora):                         %.3f kWh (%.1f%% del día)"
              % (wh_to_kwh(ultima), 100.0 * ultima / total if total else 0.0))
    if primera is not None:
        print("Referencia — método Portal de Flota para 'ayer' (contador 24:00 − contador 01:00): %.3f kWh"
              % wh_to_kwh(total - primera))


if __name__ == "__main__":
    main()
