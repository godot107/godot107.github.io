---
layout: post
title: "When a bank fails, someone has to read its loan files. I tested how far AI can be trusted with that."
date: 2026-11-16 09:00:00-0600
description: Azure Document Intelligence, a loan-file review app and Power BI on synthetic failed-bank loan files and 22 real FDIC deal agreements. Rules broke at every new bank; the safety checks came from the failures.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/failed-bank-docai/loan_view.png
og_image: https://willieman.com/assets/img/og/reading-a-failed-banks-loan-files.png
---

*In 2009 and 2010, U.S. banks failed at a pace of two to three a week. In March 2023, Silicon Valley Bank lost its
depositors in about a day. Each time, someone had to turn a failed bank's paperwork into numbers a buyer would
pay for, quickly.*

When a bank fails, the FDIC steps in as **receiver**. It sells the bank, usually to a healthy one, and manages
whatever the buyer doesn't take. Buyers price what they're getting by its loans, and the loans live in **loan
files**: scanned promissory notes, mortgages, appraisals, payment histories and collectors' notes. Every bank
formats them differently.

So the question I wanted to answer was simple to state: **how quickly can a stack of unfamiliar paperwork become
numbers people can trust, and which numbers still need a person?**

## What I built

{% include figure.liquid loading="eager" path="assets/img/failed-bank-docai/architecture.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Scanned loan files in; a versioned loan tape, a review queue and dashboards out. Everything is on Microsoft Azure and the Power Platform, deployed from code.</div>

1. **A document AI pipeline** (Azure AI Document Intelligence) that splits a scanned loan file into its
   documents, reads the key numbers (loan amount, rate, payment, maturity, balance, appraised value), and flags
   problem loans from the free text (bankruptcy, litigation, hardship, underwriting exceptions).
2. **Safety checks** that decide what a person has to look at: model confidence, validity rules, and a
   cross-check against the bank's own loan schedule.
3. **A review app** (Power Apps) where a person confirms or corrects whatever the machine wasn't sure about, and
   **automations** (Power Automate) that apply those decisions to the official record, keep every past value and
   escalate anything that waits too long.
4. **Dashboards** (Power BI): can we trust the data, is review keeping up, and what is it costing?

Real loan files are confidential, so I generated synthetic ones for about 50 fictional banks. Each copies a real
failed bank's loan mix (from its last public financial report), and each has its own layout, wording, date and
money formats and note-writing style. **Every test uses whole banks the model has never seen.**

## What I found

**1. Hand-written rules don't survive a new bank.** A parser written from three banks' paperwork read 84% of
their values correctly and **0% at the next bank**, which wrote "Sum Borrowed" where the others wrote "Principal
Amount". It failed safely (blank, not wrong), but a person would have typed everything.

**2. A trained model generalizes, once it has seen enough variety.** Trained on three banks, the model read
87–99.5% of values at new banks. Trained on twenty more randomly styled banks, it read **96–99.7%**. How the
extra banks were made mattered, though: a version that also randomly deleted fields and added decoy numbers got
*worse* (73% at one bank), because it learned "grab the nearest dollar amount".

**3. The safety checks came from failures, not from planning.** Each new held-out bank broke something:

- One listed fields in reverse order, and the model put the monthly payment in the loan-amount field. It was
  caught by checking against the bank's schedule, and by a rule that a payment must be a small fraction of the
  loan.
- One printed dates day-first (`06.04.2008` = 6 April). The model read them perfectly; **my own code** turned
  them into June 4th, and nothing flagged it. The fix was to learn each bank's date order from dates that can
  only be read one way, and to send ambiguous dates to a person until the order is known.

With those checks, every bank tested ended with **0 wrong values slipping through**, and a person reviewing
**about 2%** of values (12% at the hardest bank).

{% include figure.liquid path="assets/img/failed-bank-docai/powerapps-review.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">The review queue. The model read the monthly payment as the principal; the bank's own schedule says $1,051,000. The page, the model's reading, the reason it was flagged and the schedule sit side by side.</div>

**4. For free text, combine a careful model with a thorough one.** Simple text models (TF-IDF + logistic
regression) were never wrong but
missed half the flags at a new bank. An LLM (gpt-4.1-mini on Azure AI Foundry) caught every flag but raised
false alarms. Accepting what both
agree on, and sending the LLM's extra flags to a person, gave **zero wrong auto-accepts and every real flag
found**, with about half the flags reviewed. Every flag carries the sentence it came from, and the app checks
that the quote appears word-for-word on the page.

**5. On real documents, it reads the deal terms.** I ran the pipeline on 22 real purchase-and-assumption
agreements from 2009–2011 failures (60–200 scanned pages each) and checked it against the FDIC's published bid
summaries. Reading only 3% of the pages, it got the buyer and date right 22 out of 22 times and made **no wrong
readings** of the premium, discount or loss-sharing terms; its misses were blanks. Cost: about \\$1 of document
AI.

## A receiver sells loans, not fields

The first version of the review app looked like a form-processing tool: one field at a time. That fits an
insurance letter. It doesn't fit a loan file, where the note, the servicing history and the appraisal have to
agree with each other, and where the end product is a loan someone can bid on.

The FDIC's public material on loan sales describes how that works: loans are grouped into pools by type and
performance, sold by sealed bid, and bidders review sample loan files in a virtual data room. The FDIC sells them
without representations or warranties, so whatever the file says is what the buyer gets.

So the second screen shows the whole loan:

{% include figure.liquid loading="eager" path="assets/img/failed-bank-docai/loan_view.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">The loan view for one synthetic commercial loan, 347 days past due when the bank closed.</div>

- **The loan tape:** every field, the document and page it was read from, and the bank's schedule value next
  to it, with its status (auto-accepted, in review, or corrected by a reviewer).
- **Packet checks** that compare documents with each other: payment vs principal on the note, the servicing
  balance vs the original amount, loan-to-value from the appraisal.
- **Risk flags** from the comment log, letters and credit memo, each with its quote.
- **A proposed sale pool**: loan type × performance at closing (performing, 30–89 days delinquent, 90+ days).
- **A release decision.** *Release to data room* stays disabled while any value is in review or any check fails;
  *Hold* needs a note. Every decision is kept with who made it and when.

## Is it keeping up?

{% include figure.liquid path="assets/img/failed-bank-docai/1-trust.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Can we trust the loan tape? Accuracy and silent errors per held-out bank.</div>

{% include figure.liquid path="assets/img/failed-bank-docai/2-queue.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Is review keeping up? Queue size, age and escalations.</div>

{% include figure.liquid path="assets/img/failed-bank-docai/4-context.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Context: U.S. bank failures since 1934, from the FDIC's public failures data.</div>

## What I'd tell someone deploying this

- **Start every new bank at full human review**, and lower it only as accuracy is proven on that bank.
- **Measure silent errors, not accuracy.** A wrong number nobody looks at is the expensive one.
- **Reconcile against an independent source** (the bank's own schedule) whenever one exists. It caught most of
  the model's mistakes.
- **Keep every version.** The app never overwrites: the model's value, the reviewer's correction, who made it
  and when are all kept.

## Limits

Synthetic loan files are cleaner than real ones: no handwriting, coffee stains or 400-page files. Some risk flags
(fraud, property damage) had only a handful of examples. Two held-out banks were used to choose between models,
so a fresh bank is needed for a final, unbiased number. The real-agreement test covers 22 deals, not the whole
wave.

*An independent personal research project. Not affiliated with or endorsed by the FDIC or any other organization.
Loan files are synthetic (fictional banks and people); the public data and agreements are real.*
