---
layout: post
title: "A/B testing my own dashboard, and the ways it tried to lie to me"
date: 2026-10-03 12:00:00-0500
description: An end-to-end A/B test on a dashboard tracking post-pandemic US hiring demand — and the six places it would have produced a confident, wrong answer.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/ab-lab/experiment_page.png
---

_An end-to-end A/B test on the Hiring Demand Monitor, a dashboard I built on [Indeed Hiring Lab](https://www.hiringlab.org/)'s public Job Postings Index. Work in progress: the method and the pipeline are done, and **no real-traffic result exists yet**. Source: [github.com/godot107/ab-lab](https://github.com/godot107/ab-lab)._

---

Running an A/B test is easy. Splitting traffic is a few lines of code. What's hard is
everything around it: making sure the two groups really are comparable, deciding in advance
what "better" means, and not fooling yourself when the numbers come in.

So I built the whole thing on a dashboard I'd already made, end to end: assignment,
logging, a written pre-registration, the analysis, and a stakeholder brief. This post is
mostly about the places where it would have produced a confident, wrong answer if I hadn't
caught them first.

---

## Why a hiring dashboard

I started with a question about the job market, not about A/B testing.

The US unemployment rate is low by historical standards: 4.2% in the
[September 2026 jobs report](https://www.bls.gov/news.release/empsit.nr0.htm). On that number
alone, it's a good time to be looking for work. It doesn't always feel that way, though, and
part of the reason is that unemployment and hiring measure different things. The unemployment
rate counts people who are looking for a job. Job postings count employers who are looking for
people. The two can move apart for a long time.

[Indeed Hiring Lab](https://www.hiringlab.org/), Indeed's economic research team, publishes the
second one openly: a daily
[Job Postings Index](https://data.indeed.com/) for the US and other countries, broken out by
occupational sector, set to 100 on February 1, 2020, and released on
[GitHub](https://github.com/hiring-lab/job_postings_tracker) under CC BY 4.0. It's one of the
best free views of labor demand there is, and nearly every number below comes from it.

The post-pandemic shape is striking once you plot it:

- **The drop.** US postings fell to about 62 by early May 2020, nearly 40% below the
  pre-pandemic baseline.
- **The boom.** They passed the baseline within a year and peaked at **161 on March 31, 2022**,
  when employers were advertising roughly 60% more openings than before the pandemic.
- **The long cool-down.** From there they eased back for more than four years: 143 at the start
  of 2023, 120 at the start of 2024, 111 at the start of 2025, and touching **100**, the
  pre-pandemic level, in June 2026. As of September 25, 2026, the index stands at 103.8.

The national number hides a split by sector. Healthcare is far above its 2020 baseline:
physicians & surgeons at about 199, therapy at 186. Much of tech and knowledge work sits well
below it: software development at 78, IT infrastructure at 69, and data & analytics, the field
I work in, at 62. Some of those are recovering (software development is up from 64 a year ago).
They are still below where they were before the pandemic.

So "the job market" is really several job markets. I wanted a tool that answers one question
for a weekly review: **where is employer hiring demand growing, and how broad is it?** That
became the [Hiring Demand Monitor](https://github.com/godot107/ab-lab/tree/main/monitor), a
Plotly Dash dashboard with a data-quality suite that checks the data before anything renders.
Each sector's move is compared against its own normal variation, so a +0.7% wobble doesn't get
the same bold color as a +37% jump.

Once it existed, I had a real product with a real design question about how its page should
be laid out. That is what the rest of this post is about.

---

## The question

The [Hiring Demand Monitor](https://github.com/godot107/ab-lab/tree/main/monitor) opens with
a headline, a row of four KPI tiles, then a national trend chart and a ranking of 47
occupational sectors. Almost every mark can be clicked to open a **drill-through**: the rows
behind the number, with the arithmetic shown.

The test asks one thing: **does putting the charts above the tiles get more people to drill
into the data?** Tiles answer "what's the number?" and can end the visit. A chart answers it
while raising "why?", and here "why?" is one click away. It could just as easily go the other
way: charts are slower to read, and someone who wanted a number might leave.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/ab-lab/variant_a_desktop.png" title="Version A (control): KPI tiles first." class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/ab-lab/variant_b_desktop.png" title="Version B (treatment): the trend chart and sector ranking first." class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Left: Version A (control), KPI tiles first. Right: Version B (treatment), the trend chart and sector ranking first. The first screen of each version on a desktop. Same components, same data, same styling — only two blocks swap places. A test serializes both layouts and checks that nothing else differs.
</div>

The decision metric is the share of visitors who open at least one drill-through. One
metric, chosen before any data arrived.

{% include figure.liquid loading="eager" path="assets/img/ab-lab/drill_through.png" title="A drill-through: the two rows behind a bar, highlighted, with the arithmetic. Opening one is the conversion." class="img-fluid rounded z-depth-1" %}
<div class="caption">
    A drill-through: the two rows behind a bar, highlighted, with the arithmetic. Opening one is the conversion.
</div>

---

## How it works, briefly

- **Assignment is a hash, not a coin flip.** `hash(visitor_id + salt) % 100 < 50` → A, else B.
  The same visitor gets the same version forever, with no lookup table, and the analysis can
  recompute every assignment to audit the server.
- **The server writes an explicit exposure row** at the moment it assigns a version. Splitting
  traffic at the proxy would have been tidier, but without that row a broken randomizer is
  undiagnosable.
- **One exposure per visitor is enforced by a database index**, not application code. A
  double-counted visitor silently corrupts the denominator of every rate.
- **The browser never says which version it's in.** Every event's version is recomputed on
  the server from the cookie.
- **The live stats endpoint returns counts, never a p-value.** More on why below.

All of it is a small package (`ablab`) that mounts on the dashboard's Flask server, so the
dashboard itself only asks "which version is this visitor in?"

---

## Where it tried to lie to me

### 1. My first treatment was a guaranteed null

My first idea was a colour test. The ranking colors a sector's bar only when its move is
beyond a ±3σ "normal variation" limit, and grey otherwise. Version B would colour every bar.

I wired it up, opened both versions side by side, and they looked almost identical. At the
default "compare to 1 year" setting, nearly every sector's move is beyond its limit, so
**the two versions differed by one grey bar out of twenty.**

That test would have run for a month and come back "no significant difference". The tempting
reading is "colour doesn't matter". The real reason would have been that I never changed
anything. I swapped it for the layout test before writing the pre-registration.

**Lesson:** look at the arms before you measure them.

### 2. The dashboard would have changed itself mid-test

Both versions have to show the same content for the whole test, so the daily data refresh is
switched off while an experiment runs. Simple enough.

But the dashboard also runs a data-quality suite, including a **blocking** freshness check:
data more than 14 days old turns the header badge red and tells every visitor to treat the
numbers as unverified. The original deploy restarted the app daily, re-running the checks.
So about two weeks into a 28-day test, the page would have changed under both versions at once, in a way that plausibly
affects whether anyone trusts the numbers enough to click into them.

The fix: while an experiment is live, the freshness check reports "frozen for experiment X"
instead of failing. It still shows the age; it just doesn't sound the alarm.

### 3. On a phone, A and B look the same

I took screenshots of both versions on desktop and mobile for reference, and the mobile pair
was a surprise.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/ab-lab/variant_a_mobile.png" title="Version A on a phone." class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/ab-lab/variant_b_mobile.png" title="Version B on a phone." class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Version A (left) and Version B (right) on a phone. On a 390×844 screen the filter panel fills the first screen, so A's tiles and B's chart both start right at its bottom edge.
</div>

The treatment is much weaker on phones. That isn't fixable inside this test without changing
the design, so it's written into the pre-registration as a known threat, and any per-device
result is labelled exploratory.

### 4. A true effect that came back "inconclusive"

The real experiment needs traffic a personal site won't get: at 250 visitors per version, the
smallest effect it can reliably detect is about 12 percentage points. So the method is checked
separately with **synthetic visitors whose true effect I set by hand**, sent through the real
site over real HTTP.

With a true lift of +12 points for B, one run measured **+12.05 points**, 95% CI
[+4.6, +19.5]: the pipeline recovers what it was given.

Another run, same settings, measured +5.6 points with p = 0.14: **inconclusive**. Nothing
was broken; the generator's own random draws just came up low. A third came in at +18.6. At
this sample size the test has about 80% power, so roughly one run in five misses a real
+12-point effect, and the ones that catch it can overshoot it by half.

That's the most important thing the project says, so the readout says it explicitly: *not
significant* means *not measurable below this size*, **not** "no effect".

### 5. Peeking turns 5% into 28%

The obvious way to run a test is to check it every day and stop when it looks significant. The
simulation measures what that does to the false-positive rate when there is no real effect at
all:

```
checks   false positive rate
     1                  5.2%
     4                 12.5%
    14                 20.3%
    28                 27.6%
```

Checking daily for a month and stopping at the first p < 0.05 makes a false win about five
times as likely. Hence the fixed stopping rule (250 visitors per version or 28 days, analyzed
once), an endpoint that never shows a p-value, and a stakeholder brief that **refuses to
compare A and B** until the rule is met. Mid-test, it only reports progress, data health and
pooled usage.

The live status page follows the same rule. Here it is partway through a demo run, with 202
visitors, 200 of them synthetic and labelled as such:

{% include figure.liquid loading="eager" path="assets/img/ab-lab/experiment_page.png" title="The live experiment status page, mid-test: visitors, pooled drill-through rate, time on page and quick exits, progress to the stopping rule, and a sealed Which version is ahead box." class="img-fluid rounded z-depth-1" %}
<div class="caption">
    The public <code>/experiment</code> page mid-test. Everything is pooled across both versions; the one question a scoreboard would answer, "which version is ahead?", is deliberately sealed until both versions reach 250 visitors or day 28. Anonymous totals only.
</div>

The same simulation caught a bug in my own sample-size formula: a missing factor of 2 that had
every power calculation understating the traffic needed by half.

### 6. The smaller ones

- **A test that started failing on a date.** The dashboard's smoke test checked data freshness
  against the real clock, and its synthetic data ended on a fixed date. It passed for two weeks
  after that date, then failed every day after. It now pins "today".
- **Two claims I had to take back.** My own code comment said a drill-through was "a click the
  browser can't fabricate". It can, for its own cookie; what it can't do is choose its version.
  And an inherited line said first-time visitors were reported separately. They weren't.
  Both are corrected rather than quietly left in.
- **The first cloud deploy failed** with "command not found". The EC2 instance registered with
  AWS Systems Manager while its own setup script was still running, before it had written the
  deploy script it was about to be asked to run. A one-line wait fixed it.

---

## What "better" means here

Written down before any data, in this order:

1. **Check the split.** Visitors should divide about 50/50. If they don't (p < 0.001), the
   pipeline is broken and nothing is read.
2. **One decision metric: drill-through rate.** B wins only if it's higher and the 95%
   interval for the difference stays above zero. Anything else is inconclusive, and A stays.
3. **Supporting numbers that never decide:** time on page (median seconds the tab was
   visible), quick exits, repeat drill-throughs, which chart people clicked first.

What isn't measured yet: page-load time and JavaScript errors. Until they are, a "win" can't
rule out a version that's slower or broken, and the readout says so.

---

## Where it stands

The method, the pipeline and the deploy are done and tested, including a live demo on AWS. The real 28-day run hasn't happened. If it does, it will most
likely come back inconclusive, and the write-up will say exactly that, with the size of effect
it could have detected.

The full pre-registration, the sample stakeholder briefs and the code are in the
[repository](https://github.com/godot107/ab-lab).

---

## Data and credit

All job-postings data comes from **Indeed Hiring Lab's Job Postings Index**
([hiringlab.org](https://www.hiringlab.org/) ·
[data.indeed.com](https://data.indeed.com/) ·
[github.com/hiring-lab/job_postings_tracker](https://github.com/hiring-lab/job_postings_tracker)),
licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source: Indeed Hiring Lab.
Thanks to the Hiring Lab team for publishing it openly. The unemployment figure is from the
U.S. Bureau of Labor Statistics'
[Employment Situation release for September 2026](https://www.bls.gov/news.release/empsit.nr0.htm).
This is an independent project, not affiliated with or endorsed by Indeed.
