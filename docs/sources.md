# Sources & verification log

Every threshold and rule in `backend/app/data/` should trace to a source here. The
figures are **indicative**. This is a prototype, not legal or tax advice.

## How the figures were checked

The numeric figures were checked on **2026-10-05** against the published sources linked
below. Most of those are professional summaries of the regulations rather than the
gazette text itself, so the status column separates two levels:

- **Checked (secondary)**: the figure matches a published summary of the current
  regulation or Act. It has not been read against the gazette notification.
- **Not checked**: carried over from the original draft and not compared with any
  source.

To raise a row to "confirmed against the primary text", open the regulation on the
[IFSCA legal repository](https://www.ifsca.gov.in) (Legal → Regulations) or the Act on
[incometaxindia.gov.in](https://www.incometaxindia.gov.in), find the clause, and record
the regulation number and date in the row.

## Entities

| Entity | Figure or rule in data | Regulation cited | Status |
|--------|------------------------|------------------|--------|
| AIF (via FME) | Net worth USD 500,000 (Registered FME, non-retail) / USD 1,000,000 (Registered FME, retail) | IFSCA (Fund Management) Regulations, 2025 | Checked (secondary) [1]. **Corrected**: retail was USD 3,000,000, and the citation was the repealed 2022 regulations. |
| AIF (via FME) | Principal officer plus a separate compliance officer; minimum scheme corpus USD 3,000,000 (venture capital and retail schemes) | IFSCA (Fund Management) Regulations, 2025 | Checked (secondary) [1][7]. **Reworded**: was "two key managerial personnel" and an unspecified corpus. |
| IFSC Banking Unit | Minimum capital USD 20,000,000, provided and maintained by the parent bank | IFSCA (Banking) Regulations, 2020 | Checked (secondary, and the IFSCA consolidated regulations) [2] |
| Global In-House Centre | Serves only its own financial-services group, deals in freely convertible currency (INR for administrative expenses), services must support a financial service | IFSCA (Global In-House Centres) Regulations, 2020 | Checked (secondary) [8]. IFSCA has consulted on revising these regulations, so check whether a newer version is in force. |
| Aircraft / Ship Leasing | Minimum owned funds USD 200,000 (operating lease) / USD 3,000,000 (financial or hybrid lease) | IFSCA Framework for Aircraft Lease; Framework for Ship Leasing | Checked (secondary) [9]. **Added**: the data had no figure. |
| IFSC Insurance Office | Minimum assigned capital USD 1,500,000 for a branch office, held in the home country; home-regulator licence and no-objection certificate | IFSCA (Registration of Insurance Business) Regulations, 2021 | Checked (secondary) [10]. **Added** the figure; **reworded** two rules (intermediaries fall under separate regulations). |
| Fintech Entity | Authorisation or sandbox route; Limited Use Authorisation for up to 12 months; grants under the incentive scheme | IFSCA Framework for FinTech Entity in the IFSCs, 2022; IFSCA (FinTech Incentive) Scheme, 2022 | Checked (secondary) [11] |
| Capital Markets Intermediary | Net worth in liquid assets: set by the exchange for trading members, USD 100,000 for global-access-only broker-dealers | IFSCA (Capital Market Intermediaries) Regulations, 2025 | Checked (secondary) [3]. Citation **corrected**: the 2021 regulations were repealed in April 2025. |
| All entities | Setup timelines in weeks | None | No source exists. These are the author's rough estimates and are labelled as estimates in the app. |
| All entities | "Fit and proper" and FATF-compliance rules | IFSCA regulations for each entity type | Not checked individually. These are general conditions with no figures. |

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
| Dubai / Singapore comparison | UAE corporate tax 9% above AED 375,000; Singapore 17% | Published rate summaries | Checked (secondary) [12]. The regulator, currency and "maturity" rows are general descriptions, not sourced figures. |

## References

1. [A deep dive into IFSCA (Fund Management) Regulations, 2025](https://www.legal500.com/intelligence/india/finance-and-banking/a-deep-dive-into-ifsca-fund-management-regulations-2025-key-regulatory-insights-for-fund-and-asset-managers) (Legal 500)
2. [Consolidated IFSCA (Banking) Regulations](https://ifsca.gov.in/Document/Legal/consolidated-ifsca-banking-regulations-as-on-july-14-202314082023111415.pdf) (IFSCA)
3. [IFSCA (Capital Market Intermediaries) Regulations, 2025](https://taxguru.in/finance/ifsca-capital-market-intermediaries-regulations-2025.html) (TaxGuru)
4. [IFSC tax holiday extended to 20 years under Finance Bill 2026](https://taxguru.in/income-tax/ifsc-tax-holiday-extended-20-years-finance-bill-2026.html) (TaxGuru)
5. [Finance Act 2026: key amendments related to income tax](https://taxguru.in/chartered-accountant/finance-act-2026-56-key-amendments-related-icnome-tax.html) (TaxGuru; Act notified 30 March 2026)
6. [Minimum Alternate Tax and Alternate Minimum Tax](https://www.incometaxindia.gov.in/w/%E2%80%8Bminimum-alternate-tax-and-alternate-minimum-tax%E2%80%8B) (Income Tax Department)
7. [IFSCA (Fund Management) Regulations, 2025: key provisions](https://taxguru.in/finance/ifsca-fund-management-regulations-2025-key-provisions.html) (TaxGuru)
8. [The Global In-House Centres Regulations](https://www.investindia.gov.in/team-india-blogs/indias-1st-ifsc-gift-city-global-house-centres-regulations) (Invest India)
9. [IFSCA Framework for Aircraft Lease](https://taxguru.in/finance/ifsca-framework-aircraft-lease.html) (TaxGuru)
10. [IFSCA (Registration of Insurance Business) Regulations, 2021](https://taxguru.in/finance/ifsca-registration-insurance-business-regulations-2021.html) (TaxGuru)
11. [IFSCA issues framework for FinTech Entity in IFSCs](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1820475&reg=48&lang=2) (Press Information Bureau)
12. [UAE corporate income tax](https://uae.acclime.com/guides/corporate-income-tax/) (Acclime) and [Singapore corporate income tax rates](https://www.iras.gov.sg/quick-links/tax-rates/corporate-income-tax-rates) (IRAS)

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
