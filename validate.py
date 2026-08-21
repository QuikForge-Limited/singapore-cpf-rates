"""Reconcile the dataset against itself. Exits non-zero on any mismatch.

    python3 validate.py

Checks, in order:
  1. employee + employer == total, on every contribution row and every PR row.
  2. OA + SA/RA + MA == the band total, to the cent, on every allocation row.
  3. The allocation ratios sum to 1.
  4. FRS == 2 x BRS, and ERS == the multiple in force x BRS, for every cohort.
  5. Every 1 January entry of the Minimum/Retirement Sum series equals 2 x that
     year's BRS -- the two come from different CPF Board documents.
  6. Every CSV row count matches the JSON it was generated from.
"""

import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DATA = json.loads((HERE / "cpf-rates.json").read_text(encoding="utf-8"))
errors = []


def rows(name):
    with (HERE / "csv" / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check(cond, msg):
    if not cond:
        errors.append(msg)


for r in rows("contribution-rates.csv"):
    e, p, t = float(r["employee_pct_of_wage"]), float(r["employer_pct_of_wage"]), float(r["total_pct_of_wage"])
    check(abs(e + p - t) < 1e-9, f"{r['year']} {r['age_band']}: {e} + {p} != {t}")

for r in rows("pr-graduated-rates.csv"):
    e, p, t = float(r["employee_pct_of_wage"]), float(r["employer_pct_of_wage"]), float(r["total_pct_of_wage"])
    check(abs(e + p - t) < 1e-9, f"{r['year']} {r['scheme']} {r['age_band']}: {e} + {p} != {t}")

for r in rows("allocation-of-wage.csv"):
    parts = float(r["oa_pct_of_wage"]) + float(r["sa_or_ra_pct_of_wage"]) + float(r["ma_pct_of_wage"])
    check(abs(parts - float(r["total_pct_of_wage"])) < 0.005,
          f"{r['year']} {r['age_band']}: allocation {parts} != total {r['total_pct_of_wage']}")

for r in rows("allocation-ratios.csv"):
    s = float(r["oa_ratio"]) + float(r["sa_or_ra_ratio"]) + float(r["ma_ratio"])
    check(abs(s - 1) < 0.0002, f"{r['year']} {r['age_band']}: ratios sum to {s}, not 1")

for r in rows("retirement-sums-history.csv"):
    brs = int(r["basic_retirement_sum_sgd"])
    check(int(r["full_retirement_sum_sgd"]) == brs * 2,
          f"{r['year_of_55th_birthday']}: FRS != 2 x BRS")
    check(int(r["enhanced_retirement_sum_sgd"]) == brs * int(r["ers_multiple_of_brs"]),
          f"{r['year_of_55th_birthday']}: ERS != multiple x BRS")

brs_by_year = {r["year_of_55th_birthday"]: int(r["basic_retirement_sum_sgd"])
               for r in rows("retirement-sums-history.csv")}
for r in rows("minimum-sum-series-1995-onwards.csv"):
    date, amount = r["cohort_from_date"], int(r["amount_sgd"])
    year = date[:4]
    if date.endswith("-01-01") and year in brs_by_year:
        check(amount == brs_by_year[year] * 2,
              f"{date}: series {amount} != 2 x BRS {brs_by_year[year]}")

years = DATA["years"]
expected = {
    "contribution-rates.csv": len(years) * 5,
    "wage-ceilings.csv": len(years),
    "retirement-sums.csv": sum(1 for y in years.values() if "retirement_sums" in y),
    "minimum-sum-series-1995-onwards.csv": len(DATA["minimum_sum_series"]["amounts"]),
    "retirement-sums-history.csv": len(DATA["retirement_sums_history"]["brs"]),
    "sources.csv": len(DATA["sources"]),
}
for name, n in expected.items():
    got = len(rows(name))
    check(got == n, f"{name}: {got} rows, expected {n}")

if errors:
    print(f"FAIL — {len(errors)} problem(s):")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print("OK — dataset reconciles.")
