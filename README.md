# Singapore CPF rates — an open, machine-readable dataset

Every CPF contribution rate, allocation ratio, wage ceiling, retirement sum and
interest rate that applies in Singapore for **2025/2026/2027**, as CSV and JSON, plus
the **1995–2027 Retirement Sum series** in one column.

CPF Board publishes these figures across a dozen PDFs and web tables, in different
shapes, with the PR graduated rates split over four separate tables. Nobody
publishes them as data. So payroll code, spreadsheets and articles hand-type them —
and hand-typed rates go stale silently. This repository exists to be the copy you
can `fetch`, `pd.read_csv`, or diff against next year's.

Maintained by the team behind **[cpfcalculatorsg.com](https://cpfcalculatorsg.com)**, a free CPF
contribution calculator for Singapore Citizens and PRs, which is generated from
exactly this data.

## What's here

| File | Rows | What it holds |
|---|---|---|
| `csv/contribution-rates.csv` | 15 | Employee / employer / total rate for each of the five age bands, per year. |
| `csv/allocation-ratios.csv` | 24 | How a contribution splits across OA, SA-or-RA and MA, as CPF Board publishes it. |
| `csv/allocation-of-wage.csv` | 24 | The same split expressed as a percentage of wage — the form most people actually want. |
| `csv/pr-graduated-rates.csv` | 28 | All four PR tables: graduated/graduated and full/graduated, years 1 and 2. |
| `csv/wage-ceilings.csv` | 3 | Ordinary Wage ceiling and Annual Ceiling per year. |
| `csv/max-contribution-on-ordinary-wages.csv` | 10 | Monthly dollar cap per age band, at the ceiling. |
| `csv/partial-wage-formulas.csv` | 10 | The phase-in bands below $750 that CPF Board publishes as formulas, not rates. |
| `csv/retirement-sums.csv` | 2 | BRS / FRS / ERS with CPF LIFE payouts, and the Basic Healthcare Sum. |
| `csv/retirement-sums-history.csv` | 11 | BRS by year of 55th birthday, with FRS and ERS derived at the multiple in force. |
| `csv/minimum-sum-series-1995-onwards.csv` | 32 | The Minimum Sum, renamed the Retirement Sum in 2016, as one unbroken series. |
| `csv/interest-rates.csv` | 1 | Floor rates per account plus the extra-interest tranches above and below 55. |
| `csv/self-employed-medisave.csv` | 8 | Self-employed MediSave rates, both tables, with the phase-in formula. |
| `csv/sources.csv` | 17 | Every primary source, with the date the figure was retrieved from it. |

`cpf-rates.json` is the single source file the CSVs are generated from. It carries
the primary source, with retrieval date, for every figure (`sources`), and notes
on the figures that are commonly confused.

## Use it

```bash
curl -O https://raw.githubusercontent.com/QuikForge-Limited/singapore-cpf-rates/main/csv/contribution-rates.csv
```

```python
import pandas as pd
rates = pd.read_csv("csv/contribution-rates.csv")
rates[(rates.year == 2026) & (rates.age_band == "le55")]
#   employee 20%, employer 17%, total 37% of wages, ceiling $8,000/month
```

```javascript
const data = await fetch(
  "https://raw.githubusercontent.com/QuikForge-Limited/singapore-cpf-rates/main/cpf-rates.json"
).then(r => r.json());
data.years["2026"].contribution["55_60"];   // { employee: 18, employer: 16, total: 34 }
```

## The three things that trip people up

1. **Allocation ratios are ratios of the contribution, not percentages of the
   wage.** `allocation-of-wage.csv` gives the percentage-of-wage form, computed
   the way CPF Board computes it: MediSave first, then the Special or Retirement
   Account, with the Ordinary Account taking the remainder. Computing all three
   independently leaves a rounding artefact that does not sum to the band total.
2. **A PR's rate depends on the scheme as well as the year.** In the first two
   years of PR status, graduated employer / graduated employee (G/G) is the
   default. Full employer / graduated employee (F/G) applies only after CPF Board
   approves a joint application by the employer and the employee; full rates for
   both are the citizen table. `pr-graduated-rates.csv` carries the four PR tables.
3. **"The CPF minimum sum" is three different numbers** — the Retirement Sum
   (renamed from the Minimum Sum in 2016), the Basic Healthcare Sum, and the
   removed MediSave Minimum Sum. The series here is the first.

## Provenance and accuracy

Every figure is transcribed from a CPF Board or IRAS primary source listed in
`sources.csv`, with the date it was retrieved. The dataset is checked by the same
reconciliation the calculator ships behind: employee + employer must equal the
band total, allocation must sum to the total to the cent, the derived Full and
Enhanced Retirement Sums must equal 2× and 4× the transcribed Basic
Retirement Sum, and the 1 January entries of the Retirement Sum series must equal
2× that year's BRS transcribed from a different document. Run `python3 validate.py`.

Rates change on 1 January. If you find a figure that disagrees with CPF Board,
open an issue — with the source — and it will be corrected here and on
[cpfcalculatorsg.com](https://cpfcalculatorsg.com) together.

**Not financial advice.** These are published rates, not a recommendation.

## Corrections

**2026-10-17.** Every value in `cpf-rates.json` was re-proven against CPF Board
and IRAS primary sources: each one is bound to a sourced claim, and the CPF PDF
tables were re-read by a second, independent extractor and compared value by value
(377 values, 0 differences). Three errors in the 2026-08-21 release are corrected:

- `tax.srs.statutory_retirement_age` was **63** (from 1 July 2022). IRAS: SRS
  withdrawals are penalty-free from the statutory retirement age prevailing at the
  member's first contribution, **64 effective from 1 July 2026**. Members who first
  contributed earlier keep the age that applied then.
- `tax.srs._note` called $102,000 the "CPF Annual Limit". $102,000 is the annual
  salary ceiling, which is also the SRS income base; the CPF Annual Limit is
  $37,740 in 2026.
- In `pr-graduated-rates.csv`, `scheme_label` for `fg_year1` and `fg_year2` read
  "Full employee / graduated employer". CPF Board's Tables 4 and 5 are **Full
  Employer & Graduated Employee** rates; the percentages were right, the label was
  reversed.

## Licence

The compilation is released under **[CC BY 4.0](LICENSE)**. The underlying rates
are facts published by CPF Board and are not owned by anyone. Attribution:

> Singapore CPF rates dataset, [cpfcalculatorsg.com](https://cpfcalculatorsg.com), CC BY 4.0.

## Related

- [CPF contribution calculator](https://cpfcalculatorsg.com/calculator.html) — the calculator built on this data
- [CPF contribution rates by age](https://cpfcalculatorsg.com/cpf-contribution-rate-by-age.html)
- [PR contribution rates](https://cpfcalculatorsg.com/cpf-pr-contribution-rates.html)
- [Retirement sums](https://cpfcalculatorsg.com/retirement-sum.html)
- [How every figure is sourced and reviewed](https://cpfcalculatorsg.com/editorial-policy.html)
