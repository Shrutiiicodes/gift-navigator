# Sources & verification log

Every threshold and rule in `backend/app/data/` should trace to a primary source here.
The values shipped in the prototype are **indicative placeholders** drawn from publicly
described IFSCA frameworks. **Before any real or assessed use, verify each row against the
current circular / Act and replace the "Status" with the version and date you confirmed.**

## How to verify

1. Open the IFSCA legal repository: https://www.ifsca.gov.in (Legal / Regulations).
2. For each entity in `entities.json`, find the governing regulation and confirm the
   capital / net-worth figure and eligibility conditions.
3. For tax, confirm Section 80LA wording and the current Finance Act for the holiday
   length, block period, and concessional rate.
4. Update the `accessed` date and note the exact circular number below.

## Entities

| Entity | Key figure in data | Source cited | Status |
|--------|--------------------|--------------|--------|
| AIF (via FME) | Net worth USD 500k (non-retail) / USD 3M (retail) | IFSCA (Fund Management) Regulations, 2022 | ☐ verify current version |
| IFSC Banking Unit | Min assigned capital ~USD 20M | IFSCA (Banking) Regulations, 2020 / Banking Handbook | ☐ verify current threshold |
| Global In-House Centre | Group-only, FX currency | IFSCA (Global In-House Centres) Regulations, 2020 | ☐ verify |
| Aircraft/Ship Leasing | Min owned funds | IFSCA (Finance Company) Regulations, 2021 | ☐ verify thresholds |
| IFSC Insurance Office | Min assigned capital | IFSCA (Registration of Insurance Business) Regulations, 2021 | ☐ verify |
| Fintech Entity | Sandbox / authorisation | IFSCA (FinTech Entity) Framework, 2022 | ☐ verify |
| Capital Markets Intermediary | Net-worth thresholds | IFSCA (Capital Market Intermediaries) Regulations, 2021 | ☐ verify |

## Tax

| Parameter | Value in data | Source cited | Status |
|-----------|---------------|--------------|--------|
| Deduction | 100% on eligible income | Income-tax Act, 1961 — Section 80LA | ☐ confirm wording |
| Holiday length | 10 consecutive years | Section 80LA | ☐ confirm |
| Block period | 25 years | Budget 2026 (claimed) | ⚠ **must verify against the enacted Finance Act** |
| Post-holiday rate | ~15% | Concessional regime (verify) | ☐ confirm |
| Surcharge | 12% (advanced mode) | Finance Act surcharge schedule | ☐ confirm current band |
| Cess | 4% (advanced mode) | Health & education cess | ☐ confirm |
| MAT rate | 9% (advanced mode) | s.115JB MAT for IFSC units | ☐ confirm current rate |

## Stated model limitations

- The tax estimator ignores minimum alternate tax (MAT), surcharge, cess, GST and
  entity-specific rules.
- Recommendations are eligibility routing, not legal advice.
- Keyword classification has no full stemmer (lightweight plural tolerance only); the LLM
  fallback mitigates this but carries its own non-zero misclassification rate, quantified
  by `eval/run_eval.py`.
