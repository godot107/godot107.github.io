---
layout: page
title: Auditable FP&A forecasting on filed SEC data
description: A rolling FP&A forecast built from Netflix's SEC filings, with 23 in-pipeline controls — 21 of them blocking — an ERP round trip that reconciles to $0.00, and an LLM that writes the commentary but never the number.
img: assets/img/auditable-fpa-forecast/regional-revenue-residual.png
importance: 1
category: work
featured: true
---

# Auditable FP&A forecasting on filed SEC data

A rolling financial planning forecast built entirely from public SEC filings, where
every integrity check runs inside the pipeline rather than in a test suite — and stops
the run when it fails.

Actuals come from the XBRL `companyfacts` API, each fact carrying the accession number
of the filing it was tagged in. Cost-center detail below the filed lines is modeled and
labelled as such, and asserted to foot back to the filed total. Everything is posted
into a real ERP as double-entry journal entries, extracted back through SQL, and
reconciled against the 10-Q it started from.

- **Balance sheet:** `Assets = Liabilities + Equity` to **$0.00** across 26 quarters, so
  it posts as a self-balancing journal entry with no clearing account.
- **P&L round trip:** EDGAR → disaggregation → ORM → posted double-entry → analytic
  distribution → `GROUP BY` → back to the filed 10-Q, tying to **$0.02 on $10.4B**.
- **Cash flow:** computed in Python, never posted — no general ledger journalizes a
  cash-flow statement — and reconciled to **$0.00** across 25 quarters.
- **Commentary:** every figure is computed in Python and handed to the model as a facts
  payload; each numeral it returns is checked back against that payload, and a draft
  citing anything else is rejected before a human sees it.

The write-up is about the five defects the controls caught, including a $1.83 billion
error hiding in a number that looked entirely reasonable, and the MCMC diagnostics that
invalidated a result I had already written up as a success.

### Read the write-up

[I let the controls fail, and they told me things I didn't know]({% post_url 2026-09-18-auditable-fpa-forecast %})

### Source

<a href="https://github.com/godot107/auditable-fpa-forecast">https://github.com/godot107/auditable-fpa-forecast</a>

Built on Netflix's public SEC filings (CIK 0001065280), Odoo 18 Community with OCA
modules, NumPyro, DuckDB and Streamlit. Nothing here is investment advice or an analysis
of Netflix — the filings are a well-tagged public dataset, and that is the only reason
they were chosen.
