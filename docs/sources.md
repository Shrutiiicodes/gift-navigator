# Sources & verification log

Every threshold and rule in `backend/app/data/` should trace to a source here. The
figures are **indicative**. This is a prototype, not legal or tax advice.

## How the figures were checked

The numeric figures were checked on **2026-10-05** against the published sources linked
below. Most of those are professional summaries of the regulations rather than the
gazette text itself, so the status column separates two levels:

- **Checked (secondary)**: the figure matches a published summary of the current
  regulation or Act. It has not been read against the gazette notification.
- **Not checked**: carried over from the original draft and not yet compared with any
  source.

To raise a row to "confirmed against the primary text", open the regulation on the
[IFSCA legal repository](https://www.ifsca.gov.in) (Legal → Regulations) or the Act on
[incometaxindia.gov.in](https://www.incometaxindia.gov.in), find the clause, and record
the regulation number and date in the row.

## Entities

| Entity | Figure or rule in data | Regulation cited | Status |
|--------|------------------------|------------------|--------|
| AIF (via FME) | Net worth USD 500,000 (Registered FME, non-retail) / USD 1,000,000 (Registered FME, retail) | IFSCA (Fund Management) Regulations, 2025 | Checked (secondary) [1]. **Corrected**: retail was USD 3,000,000, and the citation was the repealed 2022 regulations. |
| AIF (via FME) | KMP, scheme corpus and contribution rules (no figures) | IFSCA (Fund Management) Regulations, 2025 | Not checked. The data says "two" key managerial personnel; confirm the count per FME category. |
| IFSC Banking Unit | Minimum capital USD 20,000,000, provided and maintained by the parent bank | IFSCA (Banking) Regulations, 2020 | Checked (secondary, and the IFSCA consolidated regulations) [2] |
| Global In-House Centre | Group-only services, freely convertible currency (no figures) | IFSCA (Global In-House Centres) Regulations, 2020 | Not checked |
| Aircraft / Ship Leasing | Minimum owned funds (no figure in data) | IFSCA (Finance Company) Regulations, 2021 | Not checked |
| IFSC Insurance Office | Minimum assigned capital (no figure in data) | IFSCA (Registration of Insurance Business) Regulations, 2021 | Not checked |
| Fintech Entity | Sandbox / authorisation routes (no figures) | IFSCA (FinTech Entity) Framework, 2022 | Not checked |
| Capital Markets Intermediary | Net-worth thresholds (no figure in data) | IFSCA (Capital Market Intermediaries) Regulations, 2025 | Citation **corrected**: the 2021 regulations were repealed in April 2025 [3]. Rule wording not checked. |
| All entities | Setup timelines in weeks | None | Not checked. These are estimates with no cited source. |

## Tax

| Parameter | Value in data | Source | Status |
|-----------|---------------|--------|--------|
| Deduction | 100% of eligible income | Income-tax Act, 2025, section 147 (formerly section 80LA of the 1961 Act) | Checked (secondary) [4] |
| Holiday length | 20 consecutive years | Section 147 as amended by the Finance Act, 2026 | Checked (secondary) [4][5]. **Corrected**: was 10 years, the rule before 1 April 2026. |
| Block period | 25 years | Section 147 as amended by the Finance Act, 2026 | Checked (secondary) [4][5] |
| Post-holiday rate | 15%, plus surcharge and cess | Finance Act, 2026 | Checked (secondary) [4][5] |
| MAT rate for IFSC units | 9% | Section 115JB of the 1961 Act | Checked against the Income Tax Department page [6]. Not re-confirmed after the Finance Act, 2026 MAT changes (general rate cut to 14%). |
| Surcharge | 12% | Company surcharge schedule | Standard rate for a domestic company with income above Rs 10 crore (7% between Rs 1 crore and Rs 10 crore). Not re-confirmed for tax year 2026-27. |
| Cess | 4% | Health and education cess | Standard rate. Not re-confirmed for tax year 2026-27. |
| Dubai / Singapore comparison | Headline rates and regulators | None | Not checked |

## References

1. [A deep dive into IFSCA (Fund Management) Regulations, 2025](https://www.legal500.com/intelligence/india/finance-and-banking/a-deep-dive-into-ifsca-fund-management-regulations-2025-key-regulatory-insights-for-fund-and-asset-managers) (Legal 500)
2. [Consolidated IFSCA (Banking) Regulations](https://ifsca.gov.in/Document/Legal/consolidated-ifsca-banking-regulations-as-on-july-14-202314082023111415.pdf) (IFSCA)
3. [IFSCA (Capital Market Intermediaries) Regulations, 2025](https://taxguru.in/finance/ifsca-capital-market-intermediaries-regulations-2025.html) (TaxGuru)
4. [IFSC tax holiday extended to 20 years under Finance Bill 2026](https://taxguru.in/income-tax/ifsc-tax-holiday-extended-20-years-finance-bill-2026.html) (TaxGuru)
5. [Finance Act 2026: key amendments related to income tax](https://taxguru.in/chartered-accountant/finance-act-2026-56-key-amendments-related-icnome-tax.html) (TaxGuru; Act notified 30 March 2026)
6. [Minimum Alternate Tax and Alternate Minimum Tax](https://www.incometaxindia.gov.in/w/%E2%80%8Bminimum-alternate-tax-and-alternate-minimum-tax%E2%80%8B) (Income Tax Department)

## Stated model limitations

- The tax estimator's simple mode ignores minimum alternate tax (MAT), surcharge and
  cess; advanced mode models them using the indicative rates above. Both modes ignore GST
  and entity-specific rules.
- The estimator assumes the unit starts its 20-year deduction window in year 1 and that
  all of the income entered is eligible.
- Units that began their deduction under the pre-2026 rule (10 years out of 15) are not
  modelled.
- Recommendations are eligibility routing, not legal advice.
- Keyword classification has no full stemmer (lightweight plural tolerance only); the LLM
  fallback mitigates this but carries its own non-zero misclassification rate, quantified
  by `eval/run_eval.py`.
- The golden set was labelled by the author, not reviewed by an independent expert.
