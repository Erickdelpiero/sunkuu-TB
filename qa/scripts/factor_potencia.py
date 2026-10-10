#!/usr/bin/env python3
"""Factor de potencia correcto (P_total / S_total) frente al "promedio" que
muestran los widgets (media aritmética de las tres fases).

Calcula:
  1. Instantáneo en el último instante con P_total y S_total: P/S.
  2. Media aritmética de factor_potencia_fase_a/b/c en ese mismo instante (método widget).
  3. FP del periodo: ∫P dt / ∫S dt (integración trapezoidal) entre --desde y --hasta.

Uso:
    python3 qa/scripts/factor_potencia.py --csv export.csv
    python3 qa/scripts/factor_potencia.py --csv export.csv --desde "2026-10-05 00:00" --hasta "2026-10-06 00:00"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sunkuu_csv import fmt_ms, lima_dt, load_series, to_ms, warn_if_aggregated


def integrate(series, a, b):
    pts = [p for p in series if a <= p[0] <= b]
    total = 0.0
    for p, q in zip(pts, pts[1:]):
        total += (p[1] + q[1]) / 2.0 * (q[0] - p[0])
    return total, len(pts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", required=True)
    ap.add_argument("--desde", help="'YYYY-MM-DD HH:MM' hora Lima (para el FP del periodo)")
    ap.add_argument("--hasta", help="'YYYY-MM-DD HH:MM' hora Lima (para el FP del periodo)")
    args = ap.parse_args()

    P = load_series(args.csv, "potencia_activa_total")
    S = load_series(args.csv, "potencia_aparente_total")
    warn_if_aggregated(P, "potencia_activa_total")
    fases = {}
    for k in ("factor_potencia_fase_a", "factor_potencia_fase_b", "factor_potencia_fase_c"):
        fases[k] = dict(load_series(args.csv, k))

    s_by_ts = dict(S)
    comunes = [ts for ts, _ in P if ts in s_by_ts]
    if not comunes:
        sys.exit("No hay instantes con potencia_activa_total y potencia_aparente_total a la vez.")
    ts = comunes[-1]
    p = dict(P)[ts]
    s = s_by_ts[ts]
    print("Instante: %s" % fmt_ms(ts))
    print("  P_total = %.1f W   S_total = %.1f VA" % (p, s))
    if s > 0:
        print("  FP correcto  (P_total / S_total):        %.3f" % (p / s))
    else:
        print("  FP correcto: no definido (S_total = 0)")
    vals = [fases[k].get(ts) for k in fases]
    if all(v is not None for v in vals):
        media = sum(vals) / 3.0
        print("  FP widget    (media aritmética de fases): %.3f   [A=%.3f B=%.3f C=%.3f]"
              % (media, vals[0], vals[1], vals[2]))
        if s > 0:
            print("  Diferencia widget − correcto:            %+.3f" % (media - p / s))
        if any(v <= 0 for v in vals):
            print("  AVISO: alguna fase con FP ≤ 0 (fase sin carga o signo): distorsiona la media y la alarma 'FP bajo'.")
    else:
        print("  FP por fase no disponible en el mismo instante.")

    if args.desde and args.hasta:
        a, b = to_ms(lima_dt(args.desde)), to_ms(lima_dt(args.hasta))
        ip, n_p = integrate(P, a, b)
        is_, n_s = integrate(S, a, b)
        print("Periodo %s → %s (%d / %d lecturas)" % (args.desde, args.hasta, n_p, n_s))
        if is_ > 0:
            print("  FP del periodo (∫P / ∫S): %.3f" % (ip / is_))
        else:
            print("  FP del periodo: no definido (sin potencia aparente en el rango)")


if __name__ == "__main__":
    main()
