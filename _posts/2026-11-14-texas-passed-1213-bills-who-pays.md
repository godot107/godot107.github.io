---
layout: post
title: "Texas passed 1,213 bills in 2025. I wanted to know who pays for them."
date: 2026-11-14 09:00:00-0600
description: Learning how the Texas Legislature works from its own files before the 2027 session. An Azure pipeline over every 2025 bill history and fiscal note, an AI that splits costs by agency (and gets checked), and an assistant that answers from the record.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/tx-fiscal-radar/cover.png
og_image: https://willieman.com/assets/img/og/texas-passed-1213-bills-who-pays.png
---

*Texans filed 8,719 bills in the 2025 session. 14% passed. The ones that did carry about \\$16.8 billion of new
spending in 2026-27, and every one comes with a fiscal note that says what it costs. Nobody adds those notes up by
agency.*

The 90th Texas Legislature convenes on **January 12, 2027**. Bill filing for it opened on November 9, and 1,179 bills
came in on the first day. I wanted to understand how the place actually works before following it: where bills
stall, when things happen, and what the laws that pass end up costing the agencies that carry them out. I didn't want
to learn that from news coverage. I wanted it from the Legislature's own records.

Those records are all public. The Texas Legislative Council publishes every bill's history and every Legislative
Budget Board fiscal note as bulk files. They're thorough, and they're written one bill at a time. So I built a
pipeline that reads all of them, on Microsoft Azure, and kept it running for 2027.

Code, results and runbooks: [github.com/godot107/tx-fiscal-radar](https://github.com/godot107/tx-fiscal-radar).

## How a session actually goes

{% include figure.liquid loading="eager" path="assets/img/tx-fiscal-radar/funnel_89r.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">The 2025 regular session (89th Legislature), House and Senate bills.</div>

Five things the 2025 record shows:

- **Committees are where bills stop.** Almost every bill goes to a committee, and three in four never pass either
  chamber. House Public Education received 679 bills, and 556 of them never came out.
- **The session runs on deadlines.** 29% of all bills were filed in the last week before the filing deadline, and 79% of
  the bills that passed both chambers did so in the final two weeks.
- **Prefiling is busy but doesn't predict much.** 27% of bills were filed before the session opened. Only 10% of those
  became law.
- **The governor acts after everyone goes home.** Most new laws (844) were signed in June, after the session ended. All 26 vetoes came
  by June 22, the end of the governor's 20-day window.
- **"Passed" is harder to count than it sounds.** My first rule (each chamber passed the bill) gave 1,221. The
  Legislature's own report says 1,213. The 8-bill difference: each chamber passed a *different version*, and the two
  were never reconciled. Counting a bill once both chambers agree on the same text (enrolled) matches the official
  number exactly, and the pipeline checks that match on every load.

## What the 2025 laws cost

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/pbi-fiscal-exposure.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">The "Fiscal exposure" page of the Power BI report. The whole report is built from code.</div>

- **About \\$16.8 billion of new 2026-27 spending**, across 114 enacted bills, plus about 800 new state jobs and
  \\$2.2 billion of revenue given up through tax relief. School finance (HB 2) is half of the spending by itself.
  Appropriations bills, which move money to many agencies at once, are counted separately.
- **Estimates move as a bill moves.** Each version of a bill gets a new fiscal note. 49 enacted bills changed by more
  than a quarter between their first and last note. The homestead exemption increase (SB 4) went from \\$1.0 billion to
  \\$2.7 billion.
- **Some costs come later.** A franchise-tax credit (SB 2206) costs nothing in 2026-27 and \\$1.8 billion in 2028-30.
  That cost belongs in the next budget request, not this one.
- **Relative to its size**, the Department of Information Resources took on new costs of about 10% of its yearly
  spending, plus 139 new positions. The Office of Court Administration and the Public Utility Commission came close
  behind.

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/agency_exposure.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">New 2026-27 cost from enacted bills, as a share of each agency's FY2024 spending (Comptroller data).</div>

## Why you can't just add up the fiscal notes

**A fiscal note gives one cost for the whole bill.** When a bill touches nine agencies, the note's prose says which
one pays. I had a language model (GPT-4.1-mini on Azure) read that prose and split the cost by agency, for about
24 cents across 198 bills. Then I didn't trust it. An extracted amount only counts if four checks pass: the quoted
sentence is really in the note, the number is really in the sentence, the agency is listed on the note, and the
sentence names that agency. **48% of rows passed.** The rest wait for a person on a review page. The model's most
common mistake was putting a cost on the wrong agency, and that's why the last check exists.

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/pbi-trust-review.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Every load is reconciled to the Legislature's count, and AI rows that fail a check wait here for review.</div>

**The listed agencies aren't always the ones that pay.** A fiscal note's "source agencies" are the agencies the Budget
Board consulted. On tax bills that's often just the Comptroller, even when the cost lands on school finance. That's
why the Comptroller tops the raw ranking at 38% of its spending. The pipeline flags tax-bill costs instead of
moving them around quietly.

## Asking it questions

Dashboards answer the questions you thought of in advance. For everything else there's **Fiscal Note Desk**, an
assistant (an Azure AI Foundry agent) that answers in plain English. It gets numbers from the warehouse and
explanations from the fiscal notes, and it cites both. It runs as a signed-in web app and as an MCP server that other
AI tools can call.

I measured it before trusting it:

| | Before | After |
| :--- | ---: | ---: |
| Test questions answered correctly (expected answers computed from SQL) | 19 / 25 | **26 / 26** |
| Right fiscal note in the top 6 search results | 53% | **97%** |
| Red-team attacks that got through (22, including prompt injection) | 3 | **0** |
| Cost per answer, with every guardrail on | | **\\$0.0056** |

One problem isn't solved yet. For questions asked from opposite sides ("should Texas fund more of X" vs "cut X"), the
facts in the answers stayed consistent, but the tone matched only 7 of 10 times. For a tool a politically mixed
audience would use, that matters, so it's in the write-up as an open issue rather than hidden.

## How it's built

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/architecture.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Azure Data Factory → data lake → Synapse Spark → Azure SQL → Power BI, plus the Foundry agent.</div>

- **Ingestion.** Azure Data Factory copies from the Legislature's FTP site into a data lake. The FTP server doesn't
  report when files change, so the pipeline uses the Legislature's own daily change list, plus a full copy every
  Sunday. It reads the FTP site only, at a low rate, as the Legislative Council asks.
- **Transformation.** Spark turns the HTML and XML into tables (10,635 bills, 139,178 actions, 7,334 fiscal-note
  versions). Notes it can't read go to quarantine instead of into the totals. The same code ran unchanged on
  Databricks serverless.
- **Serving.** A star schema in Azure SQL feeds Power BI. The report is code too, so rebuilding it is one command.
- **No passwords or keys anywhere.** Every service signs in with its own managed identity. There are budget alerts,
  a failed-run alert, and a cost breaker that stops the app if spend runs away. A second region can take over if the
  model's region goes down (13 of 13 failover tests passed).
- **Cost.** About \\$14 of free-trial credit for everything above.

## Following 2027

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/filing_pace.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">2027 filing pace against 2025, by days since prefiling opened. Updated nightly.</div>

The pipeline picks up new filings every night. What I'll be watching, based on 2025:

- **~March 12, 2027**, the 60th day: the filing surge (in 2025, 29% of all bills came in the final week).
- **March to May**: bills leaving committee, and fiscal notes that move between versions.
- **~May 31**, the 140th day: the end-of-session crunch.
- **~June 20**: the veto deadline.

## Limits

Fiscal notes are estimates of one version of a bill at one moment, not appropriations. Agency spending is FY2024,
before these laws, and I use it only to measure agency size. The AI's agency split is a lower bound where a note
doesn't itemize. This is an independent analysis of public records. It isn't affiliated with the Legislature or any
agency, and the assistant reports what was filed and estimated. It doesn't predict what the Legislature will do.
