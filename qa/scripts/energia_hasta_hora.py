#!/usr/bin/env python3
"""Energía acumulada desde las 00:00 (hora Lima) de un día hasta una hora dada,
para contrastar con "Energía acumulada hoy" que mostraba el widget a esa hora.

Uso:
    python3 qa/scripts/energia_hasta_hora.py --csv export.csv --hasta "2026-10-06 14:30"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sunkuu_csv import (counter_delta, lima_dt, load_series, to_ms, warn_if_aggregated,
                        wh_to_kwh)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", required=True)
    ap.add_argument("--hasta", required=True, help="'YYYY-MM-DD HH:MM' en hora Lima")
    ap.add_argument("--columna", default="energia_total", help="columna del contador en Wh")
    ap.add_argument("--widget", type=float, default=None,
                    help="(opcional) valor en kWh que mostraba el widget a esa hora, para calcular la diferencia")
    args = ap.parse_args()

    serie = load_series(args.csv, args.columna)
    warn_if_aggregated(serie, args.columna)

    fin = lima_dt(args.hasta)
    ini = fin.replace(hour=0, minute=0, second=0, microsecond=0)
    total, resets, n0, n1 = counter_delta(serie, to_ms(ini), to_ms(fin))
    print("Rango (hora Lima): %s → %s" % (ini.strftime("%Y-%m-%d %H:%M"), fin.strftime("%Y-%m-%d %H:%M")))
    print("  inicio: %s" % n0)
    print("  fin:    %s" % n1)
    if total is None:
        sys.exit("No se puede calcular: el CSV no cubre ambos límites.")
    kwh = wh_to_kwh(total)
    print("ENERGÍA 00:00 → %s: %.3f kWh" % (fin.strftime("%H:%M"), kwh))
    if resets:
        print("  AVISO: %d disminución(es) del contador; se sumaron solo incrementos." % resets)
    if args.widget is not None:
        diff = args.widget - kwh
        print("Widget mostraba %.3f kWh → diferencia %.3f kWh (%.1f%%)"
              % (args.widget, diff, 100.0 * diff / kwh if kwh else 0.0))


if __name__ == "__main__":
    main()
