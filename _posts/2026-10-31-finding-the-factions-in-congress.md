---
layout: post
title: "Finding the factions in Congress from votes alone"
date: 2026-10-31 12:00:00-0500
description: PCA, logistic PCA and Bayesian ideal points on US House roll calls, graded against a synthetic Congress, and five clustering methods checked against caucus membership.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/ideology-clusters/02_fig1.png
og_image: https://willieman.com/assets/img/og/finding-the-factions-in-congress.png
---

*Every recorded vote in the House is public. How much can you learn about who stands where, and which
methods can you trust?*

The standard data-science tutorial on this goes: download Congress's roll-call votes, run PCA or
k-means, and watch the Democrats and Republicans fall into two neat clouds. It looks impressive, and it
proves almost nothing. Any method separates the two parties. The interesting questions are *inside*
each party: who sits where, how sure can we be, and are there real factions or just a smooth spread?

I compared three ways of placing members on a map and five ways of finding groups, and checked each one
against answers the votes never saw. Code, results and executed notebooks:
[github.com/godot107/ideology-clusters](https://github.com/godot107/ideology-clusters).

## The trap: "it separates the parties" proves little

Lay the votes out as a table, one row per member, one column per vote, yes or no in each cell. Plain PCA
on the 118th House (2023-24) matches DW-NOMINATE, political science's standard scores, at a correlation
of **0.97**. That sounds like a near-perfect result.

Now score it *within* each party, the way you'd need it to work if you wanted to know which Democrats are
more progressive or which Republicans are more hard-line. The agreement drops to **0.52** among Democrats
and **0.82** among Republicans. Almost all of that 0.97 came from the two parties being far apart. So
every method in this project is scored within party, and splitting the parties counts for nothing.

## Grading against a Congress I built

The catch with real votes is that nobody knows members' "true" positions. DW-NOMINATE is a useful
comparison, but it's a model too: it pools each member's whole career. So I also built a synthetic
Congress: 440 members in six factions, with positions I chose, noisy votes and realistic absences
(chronic absentees, members who joined late). There, every method can be graded exactly.

| Method | Ordering within party (D / R) | Full 2-D map recovered |
|---|---|---|
| PCA | 0.88 / 0.90 | 0.61 |
| **Logistic PCA** | **0.99 / 0.99** | **0.95** |

The difference is how they handle missed votes. PCA treats yes/no as numbers and fills each missing vote
with an average, which drags absentees toward the middle. Logistic PCA models the *chance* of a yes and
simply skips votes that weren't cast.

## How many dimensions does Congress have?

On real votes there's no answer key, so I hid a random 10% of the 118th House's votes and predicted them.
The rival to beat is trivial: "every member votes with their party's majority".

| Predictor | Hidden votes right |
|---|---|
| Vote with your party | 92.8% |
| Logistic PCA, 1 dimension | 95.5% |
| 2 / 3 dimensions | 96.1% / 96.3% |

The party rule alone gets 93%. One left-right scale adds less than 3 points, and extra dimensions add
less than one more. That matches decades of political science: modern Congress is close to
one-dimensional.

## Error bars, and when they lie

A position without an error bar hides how much the data actually supports it. So I fitted the standard
Bayesian ideal-point model (Clinton, Jackman & Rivers, 2004) in NumPyro, which gives every member a
*range*.

{% include figure.liquid loading="eager" path="assets/img/ideology-clusters/01_fig3.png" title="Every member of the 118th House, ordered by position, with a 90% range" class="img-fluid rounded z-depth-1" %}
<div class="caption">Every member of the 118th House, ordered by position, with a 90% range</div>

The wide ranges make sense once you look at who has them: members sworn in late after a special
election, members who left early, and members at the far edge of their party, where no vote separates
them from their neighbours. Within party, this model agrees best with DW-NOMINATE: **0.90** among
Republicans and **0.72** among Democrats (0.89 and 0.75 in the current House).

But the synthetic Congress caught something. For five of the six factions, the 90% ranges contained the
true position 77-91% of the time, close to the promised 90%. For the sixth, a faction I'd made different on
a *second* dimension (voting against its own leadership), they contained it only **25%** of the time. A
one-dimensional model has nowhere to put that difference, so it squeezes those members onto the
left-right line and reports narrow ranges around the wrong spot. Error bars are only as honest as the
model behind them.

The fix is to give the model somewhere to put it. With a second dimension, the same faction's ranges
contain the truth **93%** of the time on left-right (95% on the second dimension), and the other five stay at 82-97%. Getting there took one more
lesson: these models only loosely fix where the axes point, so the sampler's runs slowly drift and
rotate, and the raw diagnostics looked like total failure. Lining every draw up on a common map (a
rotation that moves nobody relative to anybody else) showed the runs had agreed all along.

## Factions: five methods, one trade-off

Next, clustering. I compared k-means with a Gaussian mixture (soft membership: "70% this group"),
HDBSCAN (dense regions, with members in between as noise), Ward hierarchical clustering, and community
detection on a co-voting network. Each picked its own number of groups by its standard rule.

On the synthetic Congress, the honest finding was this: k-means, the mixture and Ward all found three
groups (Democrats, Republicans and the faction that differs *in kind*). The factions that differed only
*by degree* (a wing, a mainstream, moderates) formed a continuum with no gap between them, so there was
nothing to find. Telling k-means the "right" answer of six groups made it score *worse*, because it then
cuts the continuum at arbitrary points.

On the current 119th House, I checked each method against caucus membership, which the votes never saw.
F1 measures how well one cluster captures a caucus within its party (1 = exactly). Stability is how
similar the clustering stays when the roll calls are resampled (1 = identical).

| Method | Groups | Freedom Caucus | Progressive Caucus | Blue Dogs | Stability |
|---|---|---|---|---|---|
| k-means | 3 | 0.55 | 0.63 | 0.63 | 0.95 |
| Gaussian mixture | 5 | 0.59 | 0.66 | 0.31 | 0.75 |
| HDBSCAN | 2 | 0.24 | 0.62 | 0.05 | 0.97 |
| Ward | 3 | **0.70** | 0.61 | 0.09 | 0.87 |
| Network communities | 5 | 0.61 | **0.82** | 0.15 | 0.68 |

{% include figure.liquid loading="eager" path="assets/img/ideology-clusters/02_fig1.png" title="119th House on two dimensions, coloured by Gaussian-mixture group, with Freedom Caucus and Progressive Caucus members marked" class="img-fluid rounded z-depth-1" %}
<div class="caption">119th House on two dimensions, coloured by Gaussian-mixture group, with Freedom Caucus and Progressive Caucus members marked</div>

Explore the map yourself: [hover over any member, highlight a caucus, or search by name](/assets/html/ideology-clusters/explorer.html).

**The methods that find the most faction structure are the least stable.** HDBSCAN is rock-steady
because it mostly just returns the two parties. Network communities isolate most of the Progressive
Caucus but reshuffle the most between resamples. There's no single best method. The useful habit is to
report clusters together with their stability, and to use soft membership for the 86 members who don't belong more than 80% to
any one group.

## So what is the second dimension?

In the map, Freedom Caucus members sit at the bottom of the Republican cloud. The axis has no label of
its own, so I went back to the votes. For every roll call where at least 5% of a party broke with its
majority, I asked which dimension predicts *who* broke away.

Among Republicans, left-right barely does (correlation 0.07). Dimension 2 does (0.36), and most clearly
on "suspension" bills, the fast-tracked, two-thirds-majority bills that are in practice the bipartisan
ones (0.61). One reading fits both parties: dimension 2 tracks **how often a member votes yes on bills
that both parties' majorities support**. Across the 80 such votes in the current House, the rank
correlation is 0.88 among Democrats and 0.88 among Republicans.

The median Freedom Caucus member voted yes on 53% of those bipartisan bills. Other Republicans: 99%.
The Progressive Caucus sits lower than other Democrats too (88% vs 97%), but nowhere near as far.

One caution: the positions were estimated from these same votes, so this *describes* the axis rather
than proving anything about it. The independent part is the caucus comparison, since the caucus lists
never went into the model. This is also exactly the kind of group the synthetic Congress warned about:
one that differs on a second dimension, where a one-dimensional model's error bars miss.

So I fitted the two-dimensional Bayesian model to the current House too, to get error bars on both
axes. On dimension 2, **30 of the 31** Freedom Caucus members have a 90% range lying entirely below the
median of other Republicans. That isn't automatic: only a third of the other Republicans do. Their ranges
are also narrow (half as wide as other Republicans'), so the gap isn't a few noisy members.

The second axis also changes the first. Among Republicans, the one-dimensional scale and DW-NOMINATE's
first dimension both largely *are* the bipartisan-bills pattern (rank correlation with the yes-rate
-0.85 and -0.76). Once the model has a separate axis for it, its left-right scale barely relates to that
pattern (-0.16), and agrees much less with DW-NOMINATE among Republicans (0.54, down from 0.89). The
median Freedom Caucus member moves from the 93rd percentile of Republicans on the one-dimensional scale
to the 66th on the two-dimensional left-right axis.

In other words, much of what puts them at the far end of a one-dimensional scale is voting no on bills
both parties back. A caveat: a two-dimensional model doesn't fix which way its axes point. I lined them
up with logistic PCA's map, so this split is one reading of the same positions, not the only one.

## Polarisation since 1973

Finally I fitted every Congress from 1973 to 2025 separately and measured the gap between the party
medians in "typical party widths". It's a scale-free measure, so different years can be compared.

{% include figure.liquid loading="eager" path="assets/img/ideology-clusters/03_fig1.png" title="Separation, overlap and party-line voting in the House and Senate, 1973-2025" class="img-fluid rounded z-depth-1" %}
<div class="caption">Separation, overlap and party-line voting in the House and Senate, 1973-2025</div>

In the House the gap grew from 1.9 party widths in 1973 to about 7 today. My series tracks
DW-NOMINATE's closely (correlation 0.98 in the House, 0.89 in the Senate), and so does the share of
party-line votes taken straight from the raw data with no model at all. Since the early 2000s
essentially no member is closer to the other party's median than to their own.

The two models disagree about the 1970s: about 1 member in 5 overlapped the other party by my
one-dimensional fit, but 1 in 20 by DW-NOMINATE. That era's cross-party votes (notably Southern
Democrats) ran partly along a second dimension, and a one-dimensional fit squeezes them onto
left-right. It's the same failure the synthetic Congress showed, appearing in real history.

## What I'd tell someone running this analysis

1. **Score within party.** The party split is free. Report the 0.52, not the 0.97.
2. **Build an answer key.** A simulation with known positions is the only place a method can be graded
   exactly. DW-NOMINATE is a comparison, not the truth.
3. **Beat the party rule.** "Vote with your party" already predicts 93% of votes, so a model has to
   clear that.
4. **Don't trust error bars from a model that can't represent the thing you're measuring.**
5. **Report clusters with their stability.** A clustering that changes when you resample isn't a finding
   yet.

## Methods

For readers who want to check the work or repeat it. Everything is in the
[repository](https://github.com/godot107/ideology-clusters), and one command re-runs each stage.

**Data.** Every roll-call vote comes from [Voteview](https://voteview.com) (Lewis, Poole, Rosenthal,
Boche, Rudkin & Sonnet), the standard public database of congressional votes. For each Congress and
chamber, it provides three files: the members (with their DW-NOMINATE scores), every member's vote on
every roll call, and a description of each roll call. The files were downloaded on 2026-10-17, so the
119th House covers votes from January 3, 2025 to September 16, 2026. Caucus membership comes from
Wikipedia's current member lists, retrieved the same day. The Freedom Caucus doesn't publish its roster,
so that list covers publicly identified members. Members were matched to the lists by state and district,
then checked by surname so that a seat that changed hands isn't credited to the wrong person. The caucus
lists were used only to grade the results, never as an input.

**Pre-processing.**

- Each vote becomes a 1 (any kind of yes), a 0 (any kind of no), or blank (present, not voting, or not
  yet in office).
- Voteview also records the President's announced positions as if he were a member, so I removed them.
- Following DW-NOMINATE's conventions, I dropped near-unanimous roll calls, where the losing side had
  under 2.5% of the votes (naming a post office tells you nothing about ideology). I also dropped members
  with fewer than 20 remaining votes.
- That left 451 members and 1,119 roll calls in the 118th House (of 1,235), and 448 members and 573 roll
  calls in the 119th (of 674). About 7% of the cells are blank.

**Placing members.**

- *PCA* fills each blank with that roll call's average yes-rate, then finds the directions of greatest
  variation.
- *Logistic PCA* models the probability of a yes as a logistic function of a few member and roll-call
  coordinates. It fits only the votes that were cast, using L-BFGS with an L2 penalty on the coordinates.
- *Bayesian ideal points* are the Clinton–Jackman–Rivers model in NumPyro, sampled with NUTS. The priors
  are Normal(0, 1) for positions and Normal(0, 5) for each roll call's cut point and direction.
  - One-dimensional fits: two chains of 1,000 warm-up and 1,000 kept draws for the 119th House, and one
    chain of 500 + 500 for the 118th.
  - Two-dimensional fits: two chains of 1,000 + 500. The most party-line vote is held to dimension 1 to
    fix the rotation.
  - Because these models only loosely pin where the axes sit, each draw is standardised (1-D) or rotated
    onto the logistic-PCA map (2-D) before scoring. After that, R-hat is at most 1.04, with no divergent
    transitions.
- In every method, the axes are flipped if needed so that Republicans come out on the positive side.

**Choosing settings (hyperparameters).** No setting was tuned against DW-NOMINATE or the caucus lists,
since those are what the results are graded on.

- *Logistic PCA* has two settings: the number of dimensions and the penalty strength. Both were chosen by
  hiding a random 10% of the 118th House's votes and predicting them. I tried 1, 2 and 3 dimensions with
  penalties of 0.3, 1, 3 and 10.
  - A penalty of 1 was within 0.05 points of the best and was used throughout.
  - Two dimensions were used for the maps and clusters. A third added only 0.2 points (96.1% vs 96.3%).
- *Clustering* methods each chose their own number of groups by their standard rule, so none was told
  the answer:

| Method | Settings | How the number of groups was chosen |
|---|---|---|
| k-means | 10 random starts | best silhouette score, k from 2 to 8 |
| Gaussian mixture | full covariance, 5 starts | lowest BIC, k from 1 to 8 |
| HDBSCAN | minimum cluster size 10 | found by the algorithm; members between groups are left unassigned |
| Ward (hierarchical) | Ward linkage | best silhouette score, k from 2 to 8 |
| Network communities | each member linked to the 15 colleagues they agree with most | Louvain modularity |

The embedding-based methods ran on the standardised two-dimensional logistic-PCA positions. The network
method ran on the raw votes. To show what a hand-picked k does, I also ran k-means with k fixed at the
synthetic Congress's true 6. It scored worse than letting the silhouette choose (adjusted Rand index 0.42
vs 0.58).

**Checks.**

- *Synthetic Congress:* 440 members in six factions, 1,000 roll calls, and one Republican faction set
  apart on a second dimension. Most members miss 3% of votes, a few chronic absentees miss 20-50%, and
  12 members arrive late or leave early. Positions are scored by within-party rank correlation, and
  clusters by the adjusted Rand index against the true factions.
- *Caucus F1:* for each caucus, the cluster that best matches its members within their party.
- *Stability:* resample the roll calls with replacement 20 times, re-fit and re-cluster each time, and
  take the median adjusted Rand index against the full-data clustering.
- *Error bars:* 90% ranges from the posterior draws, checked for coverage on the synthetic Congress.

**Polarisation.**

- For each Congress from the 93rd (1973) to the 119th, I fitted a one-dimensional logistic PCA to each
  chamber separately.
- *Separation* is the gap between the party medians divided by the average within-party standard
  deviation.
- *Overlap* is the share of members closer to the other party's median than to their own.
- *Party-line share* is the share of roll calls where the two parties' majorities voted opposite ways.
  It is computed straight from the votes, with no model.

*These are public officials' public votes, described with the methods' own neutral terms.*
