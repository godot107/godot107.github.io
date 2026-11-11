---
layout: post
title: "Nine insurers mailed me a price for my house. Reading them took AI, and knowing when not to trust it."
date: 2026-11-11 09:00:00-0600
description: Azure Document Intelligence, a human review app and Power BI on home-insurance letters, tested on layouts the model never saw. The confidence score lied; silent errors were the number that mattered.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/insurance-docai/2-operations.png
og_image: https://willieman.com/assets/img/og/nine-insurers-mailed-me-a-price.png
---

*My renewal said about $7,200 a year. Nine other insurers had mailed me "personalized quotes" between roughly
$1,000 and $3,000. Picking the cheap one looked easy. It wasn't.*

No two letters were alike. One says "Dwelling Protection", another "Dwelling Coverage". One prints a wind/hail
deductible, eight don't. One quotes $440k of coverage, another $529k. Two had my square footage wrong. To compare
them you have to read every letter, pull out the same dozen numbers, and notice which ones can't be compared at all.

That's a small version of a common problem. Insurers, banks and government offices receive piles of documents
in inconsistent formats, and they need structured data they can trust, with a person checking whatever the
machine is unsure about. So I built that, on Microsoft Azure, and tested it the way I'd want a vendor to test it
for me. Code, results and runbooks:
[github.com/godot107/insurance-docai](https://github.com/godot107/insurance-docai).

## What I built

1. **Read the documents** with Azure AI Document Intelligence (scans and digital PDFs).
2. **Map every insurer's wording to one standard list of fields**: the six coverages (dwelling, contents,
   liability…), premium, deductibles, property facts.
3. **Check each value**: the model's confidence, a plausible range, and ratios (contents coverage is usually
   25–75% of dwelling coverage, for example). Anything suspicious goes to a person.
4. **Have a person review** the flagged values in a small Power Apps app.
5. **Remove personal information** before anything is shared.
6. **Serve the results** through Azure SQL to a Power BI dashboard, and through a Databricks lakehouse for analysis.

Everything is infrastructure as code, uses no passwords or API keys, and costs about nothing while idle.

## Testing it honestly

Ten real letters can't tell you how accurate a system is. So I generated **96 synthetic letters** from 8
fictional insurers in 6 different layouts, about half degraded to look like cheap scans. Because I made them, I
know every correct value exactly. Two layouts (a postcard and a renewal notice) were held back completely: no
model or rule saw them before the test. That's the question that matters for any document system: how does it
do on the format nobody planned for?

The number I care about most is the **silent error**: a value that's wrong *and* nobody was asked to check it.
Those are the ones that end up in a report.

### The confidence score can lie

Hand-written rules on top of Document Intelligence's general-purpose model read **96% of fields correctly on
familiar layouts, but only 78% on the unfamiliar ones**. Worse, the wrong values came with the same confidence
(about 0.99) as the right ones. The score means "I read these characters correctly", not "this number belongs in
this field". A policy of "send low-confidence values to a person" would have let every error through.

### A custom model generalizes, and knows when it's unsure

I trained a custom extraction model on 72 labeled synthetic letters. On the two layouts it had never seen:

| | Rules | Custom model |
| :--- | :--- | :--- |
| Printed fields read correctly | 78% | **93%** |
| Wrong values | 27 | 6 |
| Errors caught by the review step | 70% | **95%** |
| Silent errors | 8 | **2** |

Its new weakness: it sometimes fills in a field the letter doesn't print. But it does that at low confidence, and
its confidence actually means something: values above 0.95 were all correct, values below 0.8 only about 30%.

### Training on "bad" documents fixed most of that

I generated 150 deliberately difficult training letters: fields left off the page, misleading extra numbers
("last term you paid…"), labels above values instead of beside them, fax-quality and upside-down scans. Made-up
values dropped from 30 to 5, and precision rose from 76% to 92%.

### The review threshold didn't transfer, and that's the real lesson

Every review threshold trades work against risk: review more, and fewer errors slip through. On the test letters
the new model looked like it needed only **6.5%** of values reviewed. But I'd chosen that cutoff on the same letters
I measured it on. So I checked it properly: choose the cutoff on one unseen layout, apply it to the other. On the
easy postcard the model barely erred, so the cutoff said "review almost nothing", and on the harder renewal notice
that let **9% of values through wrong**.

The fix is a process, not a better statistic: when a new layout shows up, a person reviews its first documents in
full, the cutoff is set from those reviews, and only then does the system start trusting confidence scores.

### It transfers to real mail

On my own letters, the model trained only on synthetic data read **about 97% of printed fields correctly, with no
silent errors**, at the cost of flagging more fields for review. (These numbers are provisional while I finish
double-checking the hand labels.)

### A smarter router isn't automatically better

On Databricks I trained a model to predict which extracted values are wrong. It ranked errors far better than the
raw confidence score (AUC 0.91 vs 0.53, where 0.5 is a coin flip), yet at the same review workload it didn't beat
a calibrated threshold plus simple rules. With eight insurers, the simple policy wins. Negative results are results.

## The person in the loop

{% include figure.liquid loading="eager" path="assets/img/insurance-docai/review-app.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">The review app: the page, what the model read, its confidence, why it was flagged, and a hint. Synthetic letter from a fictional insurer.</div>

Every decision is stored with who made it and when, which turns the review queue into a free model monitor.
Replaying the project's history through it: under the rules, almost every flagged value needed **correcting**. When
the first custom model went live, the share marked **"not on the document"** jumped from 0% to 59% (it was making
values up). After the "bad documents" retraining it fell to 29%. In production, that spike is the alarm that says
retrain.

## The dashboard

One Power BI report for three audiences (the homeowner, operations, finance), built entirely as code. The
household page uses a simulated household.

{% include figure.liquid path="assets/img/insurance-docai/1-should-i-switch.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">Should I switch? Each quote against the current policy, and whether it's actually comparable (simulated household).</div>

{% include figure.liquid path="assets/img/insurance-docai/2-operations.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">Operations: accuracy, silent errors, and how much review each cutoff costs.</div>

{% include figure.liquid path="assets/img/insurance-docai/3-review-feedback.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">Review decisions by week: the "not on the document" spike is the drift alarm.</div>

## What I'd tell anyone deploying document AI

- **Test on the layouts you didn't design for.** Familiar-layout accuracy (96%) hid the real number (78%).
- **Don't route on raw confidence.** Check what it actually predicts first; it may predict nothing.
- **Count silent errors, not just accuracy.**
- **Choose the review workload deliberately**, with the trade-off in front of you.
- **Check the threshold on data it wasn't chosen on.** Every new layout needs a full-review burn-in.
- **Generic privacy tools miss domain IDs.** Azure's PII detector found names and addresses but missed policy and
  loan numbers; a simple "whatever follows *Policy Number*" rule caught them.

## And for homeowners

Mailers are estimates, not offers. Before comparing prices, match the dwelling coverage, the deductible **and the
wind/hail percentage**, and ask how the roof is paid on a claim. Get binding quotes on the same terms, switch on the
renewal date, and repeat every year.

*Stack: Azure AI Document Intelligence (layout + custom neural), Azure AI Language, Power Apps, Azure SQL,
Power BI, Databricks (Unity Catalog, MLflow), Azure AI Foundry, Bicep, Python, GitHub Actions.*
