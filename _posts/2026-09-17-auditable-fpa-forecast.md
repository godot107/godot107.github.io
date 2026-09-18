---
layout: post
title: "I let the controls fail, and they told me things I didn't know"
date: 2026-09-17 12:00:00-0500
description: Building an auditable FP&A forecasting pipeline on real SEC filings — and what happens when you make the integrity checks blocking.
tags: data-science machine-learning
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/auditable-fpa-forecast/regional-revenue-residual.png
---

_Building an auditable FP&A forecasting pipeline on real SEC filings — and what happens when you make the integrity checks blocking. Source: [github.com/godot107/auditable-fpa-forecast](https://github.com/godot107/auditable-fpa-forecast)._

---

I set out to build a demo of AI-assisted financial planning. What I ended up with was mostly a
demonstration of a much duller idea: **write the arithmetic identities down as code, run them
on every execution, and let them stop the pipeline.**

That sounds like process hygiene. In practice it was the most productive thing in the project.
The controls caught five defects I would not have found by reading the code, and one of them
was a $1.83 billion error sitting in a number that looked completely reasonable.

This is a write-up of those failures, because they're more interesting than the parts that
worked.

---

## The setup

The pipeline takes Netflix's SEC filings and builds an FP&A rolling forecast from them:

```
SEC EDGAR XBRL ──> three statements ──> disaggregation ──> Odoo (posted double-entry)
                          │                                        │
                    articulation                              SQL extract
                     controls                                      │
                          └──────────> control gate <──────────────┘
                                            │
                     ┌──────────────────────┼──────────────────────┐
                 forecast              variance bridge        commentary
              (+ NUTS intervals)      (spend / mix)         (groundedness gate)
```

Actuals come from the XBRL `companyfacts` API, and every fact keeps the **accession number** of
the filing it was tagged in. Cost-center detail below the filed lines is modeled — Netflix does
not publish spend by department — and asserted to foot back to the filed total. Everything gets
posted into a real ERP as double-entry journal entries, extracted back out through SQL, and
reconciled against the 10-Q it started from.

Twenty-three controls run inside the pipeline on every execution. Twenty-one of them are
blocking: if one fails, no forecast is produced and no commentary is generated. Not a warning
in a log — the run stops.

That last decision is the one everything else came from.

> A control that only runs in a test suite protects the developer. A control that runs in the
> pipeline protects the number.

---

## Failure 1: the $1.83B quarter that looked fine

Companies don't file a Q4 10-Q. They roll the fourth quarter into the 10-K as a full year, so
if you pull "quarterly" facts from XBRL you get three quarters a year and a hole every
December. The standard fix is to derive it:

```
Q4 = FY − (Q1 + Q2 + Q3)
```

I wrote that. In pandas it looks like this:

```python
filled.loc[q4_end, account] = annual_row[account] - filled.loc[in_year, account].sum()
```

Then I added pre-tax income to the chart of accounts, and a control I'd just written —
`pretax − tax = net income` — went red by **$1,831,472,000**.

Netflix only started tagging pre-tax income as a _quarterly_ fact in 2020-Q3. For 2020, Q1 and
Q2 were missing. And `Series.sum()` skips `NaN` by default.

So the code computed `FY − Q3`. Two missing quarters' worth of a $3.2B year, silently folded
into a single derived quarter, in a cell that looked exactly like every other cell.

The fix is one keyword:

```python
prior = filled.loc[in_year, account].sum(skipna=False)
if pd.isna(prior):
    incomplete.append(account)   # refuse, and record why
    continue
```

Nothing raised. Nothing logged. The only reason I know about it is that an unrelated identity
disagreed by an amount too large to ignore.

---

## Failure 2: the same bug, wearing a different hat

Netflix's three largest balance-sheet lines can't be obtained as tags at all. Content assets
sit under a company extension the API doesn't expose. Treasury stock stopped being tagged in
2022 while the buyback programme kept running. Content liabilities are presented but never
tagged.

So they're derived as residuals — `total − sum(the parts)` — which is fine as long as you're
honest that a residual is only a financial statement line if it _behaves_ like one.

I built the derivations, and `other_current_assets` came back populated for 26 of 26 quarters.
Great. Except short-term investments are only tagged from 2021-Q4 onward, so ten of those
quarters were resting on an assumption nobody had declared: that an untagged line is a zero
balance.

Same root cause. `DataFrame.sum` skipping `NaN`, a missing input contributing nothing, and a
result that looks complete.

That reading is often _correct_ — a company holding no short-term investments doesn't tag the
concept. But it's an interpretation, not a fact, so now it's declared:

```python
ABSENT_MEANS_ZERO: frozenset[str] = frozenset({"short_term_investments"})
```

Anything in that set may be treated as zero. Everything else propagates `NaN`. And a control
reports the count on screen: _"10 period-lines read an absent tag as a zero balance."_

By this point I'd started thinking of it as a bug _class_ rather than two bugs:

> **A missing input that produces a plausible number instead of an error.**

The third instance was in the original ingest, which hardcoded `units["USD"]`. For a per-share
tag — reported in `USD/shares` — that returns an empty list. Not an error. The tag just
silently vanishes from the chart of accounts.

None of the three raise. All three are caught by controls that test an _identity_ rather than a
value. That's the argument for having them.

---

## Failure 3: the negative liability

Here's one where the control caught something I'd have defended in review.

To post a balance sheet into a ledger you need a **partition** of the filed totals: no gaps, no
overlaps. Every line exactly once. I mapped Netflix's tags to lines, including the ASC 842
lease tags, which look exactly like balance-sheet lines.

The non-current liability residual came out at **−$571 million**.

A negative liability is nonsense, which is the only reason it was visible. Everything else in
the statement looked plausible.

The lease tags aren't lines on the face of the statement — they're _disclosures_, nested
**inside** the "other non-current" captions. Including them alongside double-counts.

I didn't want to settle that by reading the filing and trusting my reading, so I tested it
against the ASC 842 adoption in 2019-Q1, the quarter both tags first appear:

| Caption                      | Step at adoption | Amount recognised             |
| ---------------------------- | ---------------- | ----------------------------- |
| `OtherAssetsNoncurrent`      | **+$816M**       | right-of-use assets **$812M** |
| `OtherLiabilitiesNoncurrent` | **+$663M**       | lease liability **$765M**     |

A caption that jumps by the amount of the thing being adopted contains it. The lease tags are
now carried as disclosure columns and excluded from the posting partition.

The control that caught it is four lines and does nothing but assert each residual keeps its
expected sign — content assets can't be negative, treasury stock can't be positive:

```python
worst = float((series * spec.sign).min())
if worst < 0:
    offenders[name] = worst
```

---

## The part that made the ERP worth it

With the partition fixed, `Assets = Liabilities + Equity` holds to **$0.00** across all 26
quarters. That's not a trivia fact. It means the balance sheet can be posted to the ledger as a
**self-balancing journal entry with no clearing account** — the debits and credits _are_ the
filed statement.

And Odoo will reject the entry outright if it doesn't balance. So the ERP stops being a
destination for the data and becomes an independent check on the ingest.

The balances post as _movements_, not restated positions, which makes the round trip
meaningfully harder: every quarter's balance is a cumulative sum of every entry before it, so
one bad entry in 2021 corrupts all twenty quarters after it. Reading it back out through SQL:

**$0.00 across all 17 lines and all 26 quarter ends.**

The P&L round trip — EDGAR → disaggregation → ORM → posted double-entry → analytic
distribution → `GROUP BY` → back to the filed 10-Q — ties to **$0.02 on $10.4B**. Those two
cents are cent-rounding at the ERP boundary, which is correct behaviour for a ledger that
stores cents.

One thing I got right by accident and only understood afterwards: **the cash-flow statement is
not posted at all.** No general ledger journalizes a cash-flow statement — it's derived from
the movement in balance-sheet accounts. That's why a consolidation tool computes it and a
transactional system doesn't. It's built in Python, reconciled against the filed roll-forward
(**$0.00** across 25 quarters), and reported.

---

## Failure 4: a discrepancy that turned out to be a business

Revenue by region isn't in `companyfacts` at all. The API has no dimension field — it only ever
exposes the consolidated value of a tag. Regional data lives in SEC's Financial Statement Data
Sets: bulk quarterly ZIPs, ~85 MB each, with a `segments` column you stream and filter.

I pulled four archives, summed the four regions, compared to filed total revenue, and the
control failed by **$182.3 million**.

First cause was a straightforward trap: Netflix tags _two_ overlapping geographic breakdowns.
The four operating regions carry `ProductOrService=Streaming`. There's also a standalone
`Geographical=US` disclosure worth $18.5B in FY2025. Sum everything on the geographic axis and
you inflate revenue by roughly 40% — glaringly obvious in a total, completely invisible in a
per-region chart.

But after fixing that, a residual remained. And it had a shape:

{% include figure.liquid loading="eager" path="assets/img/auditable-fpa-forecast/regional-revenue-residual.png" title="The residual between summed regional revenue and the filed total, by fiscal year. A declining tail reaching exactly zero in FY2024." class="img-fluid rounded z-depth-1" %}

A declining tail reaching _exactly_ zero.

That's the DVD-by-mail business, which Netflix shut down in September 2023.

My control had asserted the wrong identity. The regions sum to **streaming** revenue, not
consolidated revenue, and the gap is a real segment. The control now ties against the filed
streaming line — **$0.00** across the three years it's tagged — and separately requires the
legacy residual to be non-negative and to stay at zero.

I like this one because the control was wrong and the _data_ corrected it.

---

## The LLM is allowed to write, never to count

There's a language model in this pipeline. It writes the variance commentary. It is
structurally incapable of producing a number.

Every figure is computed in Python and handed over as a facts payload. The model may describe
those figures in prose. Then every numeral it returns is checked back against the payload, and
a draft citing anything else is rejected before a human sees it.

The rule is borrowed from another project of mine, an energy trading bot, where the house rule
is that the LLM may run the anomaly gate and never decides a trade:

> **The model is given a job it cannot get wrong in a way that matters.**

Writing the checker immediately found bugs in the checker. The best one: my numeral regex ended
with `(?![\w.])`, which was meant to avoid matching partial numbers. It also meant a figure at
the end of a sentence — `$999.9M.` — never matched at all. A fabricated number was passing not
because it was verified but because it was **never checked**.

That's the failure mode that matters for validators. Not "it rejected something valid" — you
notice that immediately. It's "it silently checked nothing," which looks identical to working.

So the test suite includes tests that assert the checks _fail_ when they should. A dozen of the
90 tests deliberately corrupt the data: an unbalanced balance sheet, a double-counted line, a
negative content-asset balance, a broken cash roll-forward, a share count misread as dollars.

> A validator that always passes is worse than no validator. It certifies nothing while looking
> like assurance.

---

## Never publish a metric without its benchmark

The forecast scores **MASE 0.632** on the monthly ledger. I don't quote that number.

The monthly grain is filed _quarterly_ data that this project disaggregated into months. Some
of the intra-quarter structure a model finds there is structure the disaggregation put there. A
model scores well partly by rediscovering my own allocation weights.

Re-run on filed quarterly data only — where every value is a figure Netflix actually reported —
the same model scores **0.936**. It beats a seasonal-naive benchmark by about 6%, and loses
outright on two of them — marketing (1.421) and operating income (1.308).

Both numbers are reported side by side, with the gap named as the artifact. Operating income
being hardest is not a surprise once stated: it's a small difference between two large numbers,
so proportionally modest errors either side compound in the residual. Which is the argument for
forecasting the **drivers** and letting the margin fall out.

---

## The uncertainty layer, and the average that hides the answer

The last piece was posterior-predictive intervals — a NumPyro local linear trend with monthly
seasonality, fitted with NUTS.

The first full evaluation threw **1,418 divergent transitions**, about 10.5% of draws. So I
tuned `target_accept_prob` up to 0.99, watched divergences fall to 0.4%, wrote it up as a
measured improvement, and moved on.

That was wrong, and it took a methodology review to catch it.

Divergences are one of _three_ standard MCMC diagnostics. The other two are **R-hat**, which
compares variance between chains to variance within them, and **effective sample size**. I was
running a single chain — which makes R-hat, a between-chain statistic, impossible to compute
at all. I had been reporting the diagnostic that happened to be available.

Adding three chains:

```
R-hat 1.93     ESS 3     (thresholds: 1.01 and 400)
```

The intervals I'd published came from a posterior the sampler had never explored.

Two causes. The first was a **non-identified model**: it had both a level shock and
observation noise, and both explain month-to-month variation, so the data can't separate them.
Chains settled at `sigma_obs` values spanning 0.012 to 0.025 — a 2× spread in the parameter
that sets the width of every interval. Dropping the redundant level shock fixed it.

The second was my own tuning:

| `target_accept` | divergences | R-hat        | ESS     |
| --------------- | ----------- | ------------ | ------- |
| 0.80            | 85–142      | 1.010–1.028  | 141–551 |
| 0.90            | 32–189      | 1.007–1.037  | 121–387 |
| 0.95            | 9–87        | 1.006–1.069  | 85–452  |
| **0.99**        | **0–38**    | **999–1804** | **2**   |

At 0.99 divergences reach zero because the step size collapses and **the chains stop moving**.
Nothing diverges because nothing is being integrated through. I had optimized the one
diagnostic I was watching and destroyed the two I wasn't — in a project whose entire argument
is that you should measure the thing rather than assert it.

There's a related one. My priors carried a comment claiming they were "weakly informative."
McElreath is blunt about this: _"To figure out what this prior implies, we have to simulate
the prior predictive distribution. There is no other reliable way to understand."_ So I
simulated. `trend0 ~ Normal(0, 0.10)` — a 10% log-slope per month — implied a 90% band on
**annual** growth of 0.16× to 6.4×, with draws reaching 127×. A prior that says a cost center
might grow 127-fold in a year is driving the answer, whatever you call it.

With the model and the sampler fixed, I re-ran the evaluation. Here is where it actually
stands:

| series                           | coverage | rel. width | beats naive? | R-hat     | ESS   |
| -------------------------------- | -------- | ---------- | ------------ | --------- | ----- |
| `Content / Original Productions` | 83%      | 0.20       | no           | 1.008     | 521   |
| `Marketing / Brand & Media` ⚠    | 92%      | 0.42       | no           | 1.081     | 54    |
| `G&A / Facilities` ⚠             | 78%      | 0.44       | no           | 1.020     | 272   |
| `T&P / CDN & Delivery` ⚠         | 86%      | 0.21       | **yes**      | 1.358     | 10    |
| `T&P / Cloud Infrastructure` ⚠   | 92%      | 0.22       | **yes**      | **1.991** | **3** |

**Eight of the nine fits still fail their convergence thresholds.** The full-data fits mostly
converge; the _backtest_ fits often don't, because rolling origin trains on 42 to 66 months
instead of 78, and a shorter series identifies the trend and noise scales less well.

Which produces a genuinely awkward result. Two of the three series that beat the naive
benchmark are the two worst-converged rows in the table. The one fit that cleanly converged
loses to it.

So the honest summary of my uncertainty layer is: **it does not yet work well enough to quote.**
I could have picked the three winning rows and written a paragraph about posterior-predictive
intervals beating a seasonal-naive benchmark. The diagnostics I'd just finished adding say
those particular rows are the least trustworthy ones I have.

What does survive is the diagnosis, because it shows up in converged and unconverged rows
alike: Marketing is _over_-covered — above nominal — **while losing to the benchmark**. The
band is wide, not well-placed. Ranked on coverage alone it would be among the best rows here.
That's McElreath's forecaster who predicts a 40% chance of rain every single day: perfectly
calibrated, perfectly useless. It's exactly why coverage is never reported alone, and why the
benchmark isn't optional.

---

## What I'd take from this

**Write identities as code, not as comments.** Every one of these bugs was in territory a
comment already claimed was fine. The comment can't fail. The assertion can.

**Make them blocking.** A warning in a log is a warning nobody reads. The moment a failing
check stops the run, you find out immediately — and you find out in the one place that
matters, on real data, rather than on whatever a fixture happened to contain.

**Distrust the plausible number.** Every serious defect here produced output that looked
correct. None raised. The `NaN`-skipping default in pandas is a reasonable design decision that
happens to be catastrophic in accounting code, because in accounting a missing input isn't zero
— it's unknown, and those are different.

**Test the validators.** Half the value of the control layer came from writing tests that
corrupt the data and assert the control catches it. That's where I learned my groundedness
regex had been checking nothing at all.

**Report the number that makes you look worse.** The honest MASE is 0.936, not 0.632. And
the honest state of the interval layer is "eight of nine fits don't converge," not "beats the
benchmark on three of nine." A metric without its benchmark — and an average without its
distribution — isn't a result. It's a marketing claim with a decimal point.

**The diagnostics you add last are the ones that indict the work you were proudest of.** I
added R-hat and ESS at the very end, as housekeeping, expecting to confirm what I already
believed. They invalidated a published table and a tuning decision I'd written up as a
success. That is what a good diagnostic is _for_, and it's an argument for adding them before
you need them rather than after you've drawn conclusions.

---

_Built on Netflix's public SEC filings (CIK 0001065280), Odoo 18 Community with OCA modules,
NumPyro, DuckDB and Streamlit. All actuals are filed figures carrying accession numbers;
cost-center detail is modeled and labelled as such. Nothing here is investment advice or an
analysis of Netflix — the filings are a well-tagged public dataset, and that is the only reason
they were chosen._
