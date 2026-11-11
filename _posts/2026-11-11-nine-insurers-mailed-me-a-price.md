---
layout: post
title: "Nine insurers mailed me a price for my house. Reading them took AI, and knowing when not to trust it."
date: 2026-11-11 09:00:00-0600
description: Azure Document Intelligence, a human review app and Power BI on home-insurance letters, tested on layouts the model never saw. The confidence score lied; silent errors were the number that mattered.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/insurance-docai/1-should-i-switch.png
og_image: https://willieman.com/assets/img/og/nine-insurers-mailed-me-a-price.png
---

*My renewal said about \\$7,200 a year. Nine other insurers had mailed me "personalized quotes" between roughly
\\$1,000 and \\$3,000. Picking the cheap one looked easy. It wasn't.*

No two letters were alike. One says "Dwelling Protection", another "Dwelling Coverage". One prints a wind/hail
deductible, eight don't. Two letters for the same house disagreed by almost 20% on how much dwelling coverage it needs. Two had my square footage wrong. To compare
them you have to read every letter, pull out the same dozen numbers, and notice which ones can't be compared at all.

## The question: should I switch?

This is the page I wanted at the end: every quote lined up against the current policy, and a plain answer to
whether each one is a real comparison.

{% include figure.liquid loading="eager" path="assets/img/insurance-docai/1-should-i-switch.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">The "Should I switch?" page of the Power BI report, shown with a simulated household (not my numbers).</div>

A quote only counts as **comparable** when it has the same dwelling coverage, the same deductible and the same
wind/hail percentage as the current policy. Anything else gets a reason in the last column ("dwelling differs",
"wind/hail 5%"). Price per \\$1,000 of dwelling coverage puts different-sized quotes on one scale.

For my real letters the answer was blunt: **none of the nine mailers was comparable**, because none of them stated a
deductible. So the action wasn't "pick the cheapest letter". It was: request binding quotes on my exact coverage,
deductible and wind/hail terms, and decide before the renewal date. The gap was large enough to be worth the calls.

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

{% include figure.liquid loading="eager" path="assets/img/insurance-docai/synthetic-letters.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">Two of the 96 synthetic letters: a clean declarations page from one fictional insurer, and a "scanned" renewal notice (tilted, blurred, grayscale) from another, in a layout held back for testing. Names and addresses are fake; every number is planted, so the right answer is known.</div>

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

Here's one of them, end to end: a quote mailer that arrived as a phone-quality scan, with my details blacked out.

{% include figure.liquid path="assets/img/insurance-docai/real-mailer-redacted.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">A real quote mailer, redacted: names, addresses and the agent's contact details, plus the amounts that describe my house (dwelling, other structures, contents) and the quoted premium. Liability and medical limits are standard round numbers and stay visible.</div>

| On the letter | What the model read | Confidence | What happened |
| :--- | :--- | :--- | :--- |
| Dwelling *(hidden)* | read exactly | 0.94 | accepted automatically |
| Other structure *(hidden)* | read exactly | 0.90 | accepted automatically |
| Personal property *(hidden)* | read exactly | 0.96 | accepted automatically |
| Liability \\$300,000 | \\$300,000 | 0.94 | accepted automatically |
| Guest medical \\$1,000 | \\$1,000 | 0.92 | accepted automatically |
| Annual premium *(hidden)* | read exactly | 0.94 | accepted automatically |
| Additional living expense "Included" | "Included" (no amount) | 0.40 | **sent to a person** |

Six of seven values were read exactly and went straight through. The seventh is the interesting one. The letter
prints "Included" instead of an amount, and the two versions of the model handled it differently:

- The **first model** filled in **\\$300,000**, the liability number from the line above, at a fairly confident
  0.83. Confidence alone would have let that through. What caught it was a simple rule: living-expense coverage
  is normally 5–50% of the dwelling amount, and \\$300,000 was well over half of it.
- The **retrained model** read the word "Included", reported low confidence, and sent it to a person, who marks
  it "not on the document".

Either way, the wrong number never reached the comparison. And note that the mailer doesn't state a deductible
at all, which is why no mailer could be compared like for like with my actual policy.

### A smarter router isn't automatically better

On Databricks I trained a model to predict which extracted values are wrong. It ranked errors far better than the
raw confidence score (AUC 0.91 vs 0.53, where 0.5 is a coin flip), yet at the same review workload it didn't beat
a calibrated threshold plus simple rules. With eight insurers, the simple policy wins. Negative results are results.

## The person in the loop

The review step is a deliberately simple app, built in Microsoft Power Apps (part of Microsoft's Power
Platform) and hosted there, reading and writing the review queue in Azure SQL. No web server to run: the
reviewer opens it in a browser, sees one flagged value at a time, and clicks Accept, Save Correction or Not on
document. The app itself is kept as code and deployed from the command line, so it's versioned like everything
else.

{% include figure.liquid loading="eager" path="assets/img/insurance-docai/review-app.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">The review app: the page, what the model read, its confidence, why it was flagged, and a hint. Synthetic letter from a fictional insurer.</div>

Every decision is stored with who made it and when, which turns the review queue into a free model monitor.
Replaying the project's history through it: under the rules, almost every flagged value needed **correcting**. When
the first custom model went live, the share marked **"not on the document"** jumped from 0% to 59% (it was making
values up). After the "bad documents" retraining it fell to 29%. In production, that spike is the alarm that says
retrain.

## The dashboard

The same Power BI report has pages for operations and finance next to the homeowner's page above, all built as code.

{% include figure.liquid path="assets/img/insurance-docai/2-operations.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">Operations: accuracy, silent errors, and how much review each cutoff costs.</div>

{% include figure.liquid path="assets/img/insurance-docai/3-review-feedback.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">Review decisions by week: the "not on the document" spike is the drift alarm.</div>

## Why not just upload the letters to ChatGPT?

Fair question. For nine letters, once, a chat assistant would probably do fine, and I'd use one too. This project
isn't really about my nine letters. They're a small, checkable stand-in for a problem that looks very different at
work:

- **Volume and repetition.** An insurer, bank or agency gets thousands of documents a day, every day. That needs a
  pipeline that runs unattended, not a person pasting files into a chat window.
- **A measured error rate.** A chat answer looks equally sure whether it's right or wrong. Here every value has a
  confidence score that was checked against known answers, and the rate of silent errors is a number you can
  report and manage.
- **A person in the loop, on record.** Uncertain values go to a reviewer, and every decision is stored with who
  made it and when. When an auditor asks "where did this number come from?", there's an answer.
- **The data stays inside your own cloud account.** Documents full of names, addresses and account numbers never
  go to a consumer chat service; access is controlled with the organization's own sign-in.
- **It plugs into everything else.** Results land in a database, feed a dashboard, and can feed any other system,
  instead of living in a chat transcript.
- **It extends to other paperwork.** Nothing here is specific to insurance. Swap the field list and retrain the
  custom model, and the same pipeline reads claims forms, invoices, loan files, benefit applications or permits.
- **It scales and has a known price.** The cloud services scale with volume, and the cost per page is known up
  front: at list price, reading a page with a custom model costs about 3 cents. Building and testing this whole
  project cost **under a dollar** on Azure's bill so far, because almost everything ran on free tiers (Document
  Intelligence free tier, the Azure SQL free offer, Databricks Free Edition, the Power Apps developer plan).

The skill on show isn't "getting an AI to read a letter". It's building the system around the AI so that an
organization can trust, check and run it.

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

## How it fits together

What was actually built: one Azure resource group, deployed from Bicep templates, signed in with Microsoft
Entra ID, no passwords or keys.

{% include figure.liquid path="assets/img/insurance-docai/architecture.png" class="img-fluid rounded z-depth-1" %}
<div class="caption">How a letter moves through the system. Values the checks trust go straight to Azure SQL; anything unsure goes to a person in the Power Apps review app first.</div>

For a production version (private networking, no public endpoints, separate dev/test/prod), the repo has a
reference architecture: [docs/ARCHITECTURE.md](https://github.com/godot107/insurance-docai/blob/main/docs/ARCHITECTURE.md).

*Stack: Azure AI Document Intelligence (layout + custom neural), Azure AI Language, Power Apps, Azure SQL,
Power BI, Databricks (Unity Catalog, MLflow), Azure AI Foundry, Bicep, Python, GitHub Actions.*

## Glossary

- **Layout**: how a letter is arranged on the page (a table, a postcard, a two-column notice). The same facts
  can sit in very different places.
- **Custom (neural) model**: a Document Intelligence model trained on my own labeled examples, instead of the
  general-purpose one that only reads text and tables.
- **Confidence score**: the model's own estimate, from 0 to 1, of how sure it is about a value.
- **Calibrated**: a confidence score that means what it says: of values scored 0.9, about 90% are right.
- **Silent error**: a wrong value that no check flagged, so no person ever looked at it.
- **Precision**: of the values the model returned, the share that were right. Low precision means it makes
  things up.
- **Cutoff (threshold)**: the confidence below which a value goes to a person.
- **Augmentation**: making extra, deliberately varied training examples (harder layouts, worse scans) so the
  model learns the general pattern rather than one look.
- **AUC**: how well a score ranks wrong values above right ones; 1.0 is perfect, 0.5 is a coin flip.
- **Drift**: when the documents (or the model's behavior on them) change over time, so accuracy measured
  earlier no longer holds. Here, a jump in "not on the document" decisions is the early warning.
- **PII**: personally identifiable information: names, addresses, phone numbers, policy and loan numbers.
- **Bronze / silver / gold**: raw data as received → cleaned and checked → ready for reports.
- **Infrastructure as code (Bicep)**: the cloud resources are described in files and created by a script, so
  they can be rebuilt or torn down exactly.
