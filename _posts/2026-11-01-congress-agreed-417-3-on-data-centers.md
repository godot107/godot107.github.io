---
layout: post
title: "Congress agreed 417–3 on data centers. What else do they agree on?"
date: 2026-11-01 08:00:00-0600
description: A non-partisan look at the U.S. House record before Election Day — which issues bring the parties together, who crosses party lines, and a dashboard to look up your own representative.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/congress-issues/cover.png
og_image: https://willieman.com/assets/img/og/congress-agreed-417-3-on-data-centers.png
---

*Democrats and Republicans split on most energy votes this term. Then, on September 16, they voted
417 to 3 on one. Here's what the House actually agrees on, who crosses party lines, and how to look up
your own representative before Tuesday.*

Energy is one of the most divided subjects in the House. Of the 29 recorded votes on energy bills in
this Congress, 83% split along party lines. In September 2025, the GRID Power Act, which tells
federal regulators to put "dispatchable" power plants (such as fossil-fuel plants) at the front of the
line to connect to the grid, passed 216–206. 2% of Democrats and 99% of Republicans voted yes.

Then came the Ratepayer Protection Act. It asks every state to consider a rule that makes very large
data centers (those drawing 100 megawatts or more) pay the full cost of the power lines and upgrades
built to serve them, so that cost is recovered from the data center rather than from other customers.
It passed **417–3**.

That made me want to know what else Congress agrees on. The answer is more than the headlines suggest.

I took every recorded vote in the House since January 2025 (674 of them) and the official topic the
Library of Congress assigns to each bill. Here's what the record shows.

## Nearly 4 in 10 votes on bills are bipartisan

Across 420 votes on bills (final passage, fast-tracked bills and amendments), **38% were bipartisan**:
the share of Democrats and the share of Republicans voting yes were within 25 points of each other.
**43% were party-line**: the parties were more than 80 points apart. The rest fell in between.

How a bill comes to the floor matters more than its subject:

- **Fast-tracked bills**, which need a two-thirds majority to pass, were bipartisan 87% of the time.
- **Regular bills** on final passage were party-line 80% of the time. These are the big, contested
  bills that make the news.

And these counts understate the agreement. Many bills pass by voice vote, with no recorded roll call,
and those are almost always uncontroversial.

## Where the parties agree, and where they split

{% include figure.liquid loading="eager" path="assets/img/congress-issues/04_issues.png" title="How far apart the two parties voted, by issue" class="img-fluid rounded z-depth-1" %}
<div class="caption">How far apart the two parties voted, by issue. Each bar is the typical gap between the share of Democrats and the share of Republicans voting yes.</div>

- **Among the most divided:** energy, environmental protection, immigration, labor, and armed forces
  and national security. On these, the typical vote had the two parties 84 to 95 points apart.
- **Most bipartisan:** science and technology, transportation, emergency management, commerce and
  international affairs. Here the typical vote had the parties within 10 points of each other.

One caution on taxes. The "Taxation" bar looks fully bipartisan because its seven votes were small,
specific bills, such as disaster filing extensions and help for fraud victims. The big 2025
tax-and-spending law (H.R. 1) is classified under "Economics and Public Finance". Both of its votes were
strictly party-line: 0% of Democrats and 99% of Republicans voted yes.

## Who crosses party lines?

On the 317 votes where most Democrats and most Republicans voted opposite ways, the typical member
sided with the other party about **2%** of the time. That's true in both parties: the median is 2.3%
for Democrats and 2.5% for Republicans. Only 41 of the 445 voting members crossed over more than 10% of
the time.

Here are the members of each party who crossed most often:

| Democrats | With the other party | Republicans | With the other party |
|---|---|---|---|
| Henry Cuellar (TX-28) | 48% | Brian Fitzpatrick (PA-1) | 30% |
| Don Davis (NC-1) | 42% | Mike Lawler (NY-17) | 14% |
| Marie Gluesenkamp Perez (WA-3) | 40% | Thomas Massie (KY-4) | 14% |
| Jared Golden (ME-2) | 39% | Don Bacon (NE-2) | 11% |
| Vicente Gonzalez (TX-34) | 37% | Andrew Garbarino (NY-2) | 11% |

There are two different kinds of crossing in that list:

- **Most cross from the middle.** Nearly all of these members belong to the Problem Solvers Caucus
  or the Blue Dog Coalition, and they vote yes on almost every bill both parties support (98–100%).
- **Massie crosses from the edge.** He votes yes on only 56% of the bills both parties back, against
  99% for the typical Republican. The members who cross from the middle sit at 98–100%.

My [previous post](/blog/2026/finding-the-factions-in-congress/) found that this second pattern,
voting no on bills both parties back, is the House's second dimension. It is also what sets the
Freedom Caucus apart.

Crossing party lines isn't good or bad in itself. It can reflect a district, a caucus, a principle or
a deal. These numbers describe what happened, not why.

## Look up your own representative

[**How your representative votes**](https://ideology-clusters-m3ky5ydmbkhxmwnmzri8tz.streamlit.app) is a free, non-partisan
dashboard built from the same data. It works the same way for all 445 voting members. Pick your state
and representative to see:

- how often they voted, and how often they sided with the other party;
- where they sit among every other member;
- their recent votes on bills, each linked to the bill on Congress.gov, with a filter by issue.

Don't know who your representative is? Enter your address at
[house.gov](https://www.house.gov/representatives/find-your-representative). You can also
[see every member on a map of the House](/assets/html/ideology-clusters/explorer.html).

## Then vote

**Election Day is Tuesday, November 3.** Every House seat is on the ballot. You can check your
registration, find your polling place and see what's on your ballot at [vote.gov](https://vote.gov).

The record is public so that voters can use it. Whoever you support, look at what your representative
did, then go vote.

## Methods

**Data.**

- *Votes:* [Voteview](https://voteview.com) (Lewis, Poole, Rosenthal, Boche, Rudkin & Sonnet). The
  files were downloaded on 2026-10-17 and cover the 119th House's 674 recorded votes, from January 3,
  2025 to September 16, 2026.
- *Topics:* the [Congress.gov API](https://api.congress.gov) (Library of Congress). The Congressional
  Research Service assigns every bill one policy area, plus subject terms and a summary. All 429 bills
  that received a roll call were found.
- Senate votes, voice votes and committee votes aren't included.

**Definitions.** Everything is computed directly from the votes, with no model.

- *Yes-rate:* the share of a party's members voting on a roll call who voted yes.
- *Gap:* the difference between the Democratic and Republican yes-rates (0 = voted alike, 1 = strict
  party line). *Bipartisan* means a gap under 0.25; *party-line* means a gap over 0.8.
- *Votes on bills* are final-passage, fast-track (suspension) and amendment votes. Procedural votes,
  such as the rule that sets up debate, are left out of the issue analysis. An amendment takes its
  bill's policy area.
- *With the other party:* on votes where the two parties' majorities voted opposite ways (317 votes,
  procedural rule votes excluded), the share where a member sided with the other party's majority.
- Delegates from DC and the territories are excluded from the comparisons, because they can vote on
  amendments but not on final passage.

**Limits.**

- Each bill gets only one policy area, so a broad bill sits under one heading.
- The data-center finding rests on a single bill. The bill's official summary is the only place that
  names data centers; no subject term does.
- Caucus labels come from Wikipedia's current member lists (retrieved 2026-10-17). The Freedom Caucus
  doesn't publish its roster.

Code and data: [github.com/godot107/ideology-clusters](https://github.com/godot107/ideology-clusters)
(`scripts/fetch_bills.py`, `scripts/issues.py`, `app/`).

*These are public officials' public votes, described the same way for every member of both parties.
This post doesn't endorse any candidate or party.*
