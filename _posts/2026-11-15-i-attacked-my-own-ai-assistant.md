---
layout: post
title: "I attacked my own AI assistant before anyone else could. 3 of 22 attacks worked."
date: 2026-11-15 09:00:00-0600
description: The guardrails, red teams and opt-in memory behind Fiscal Note Desk, an assistant that answers questions about Texas bills. Plus Azure AI Foundry's built-in search, which matched mine on quality, and the one reason it isn't the default.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/tx-fiscal-radar/desk-4-sales-tax-declines-cached.png
og_image: https://willieman.com/assets/img/og/i-attacked-my-own-ai-assistant.png
---

*An assistant that answers questions about state spending will get asked to do things it shouldn't: write that an
election was moved, make the case against an agency, predict a tax increase. Before anyone else tried, I wrote 22
attacks myself. Three got through. After five layers of defense, none did.*

This is the second post about [Texas Fiscal Radar](/blog/2026/inside-the-2025-texas-legislature/), a pipeline that
reads every Texas bill history and fiscal note, and **Fiscal Note Desk**, the assistant on top of it. It answers in
plain English, gets its numbers from the warehouse and its explanations from the fiscal notes, and cites both. The
first post covered what the 2025 laws cost. This one covers what it took to make the assistant safe to put in front
of people.

Code, evaluation runs and the full write-up: [github.com/godot107/tx-fiscal-radar](https://github.com/godot107/tx-fiscal-radar).

## Two ways to search: mine, and Foundry's

The assistant runs on Azure AI Foundry. Its answers depend on finding the right fiscal note among 11,224 documents,
and Foundry offers two ways to do that.

- **My own search tool.** My code runs the search (Azure AI Search, hybrid with a semantic reranker), screens the
  results, and hands them to the model.
- **Foundry's built-in "Knowledge".** You connect the search index to the agent, and Foundry runs the search
  itself, server-side. There's no retrieval code to write or maintain.

I built both as separate agents and tested them the same way:

| | My search | Foundry Knowledge |
| :--- | ---: | ---: |
| Test questions answered correctly (expected answers computed from the warehouse) | 24 / 25 | 23 / 25 |
| Head-to-head on 25 questions, judged in pairs | 6 wins | 5 wins (14 ties) |

That's no detectable difference, and it's a real point in Knowledge's favor: it got the same quality with none of my
retrieval code. If you're building an assistant over your own documents and don't need to inspect what it retrieves,
Knowledge is the faster way to get there.

The comparison taught me something about judging, too. An AI judge compared each pair of answers twice, with the order
swapped. In 8 of 25 pairs, it preferred whichever answer it read first. A judge that only reads one order would have
declared a confident, wrong winner. A win only counts here if it survives the swap.

So why isn't Knowledge the default? One reason: **the guardrails need to see what the model reads.** When Foundry
retrieves server-side, my code never sees the search results. It can't screen them for planted instructions, and it
can't check the answer against them. Equal quality, less control. Knowledge stays in the app as the other side of a
live A/B test: a share of questions get both answers side by side, and the reader votes without knowing which is which.
At this scale it needs 100 to 200 votes to detect a real preference, so the verdict is still open.

## The attacks

Two red teams:

- **12 general attacks:** jailbreaks, attempts to pull out the assistant's instructions, harmful requests, and
  instructions hidden inside documents it would retrieve.
- **10 public-trust attacks:** election misinformation, impersonating an official, targeting a person, partisan
  advocacy, and asking for predictions.

| Red team | Attacks that worked, before | After |
| :--- | ---: | ---: |
| General (12) | 2 | **0** |
| Public trust (10) | 1 | **0** |

## Five layers, each catching what the others missed

1. **Content filters** on the model itself (jailbreaks, indirect attacks, protected material).
2. **A request screen** that runs before the agent: one small, fast call that sorts the question into a category.
   High-risk categories get a fixed refusal. Questions asking for a prediction get "I can't predict what the
   Legislature will do", then the facts. It stopped 8 of the 10 public-trust attacks before the agent ran.
3. **The agent's instructions.** Useful, but soft: with an explicit rule against it, the agent still wrote a post
   claiming an election date had moved. That's why layer 2 exists.
4. **A document shield.** Every search result is checked for planted instructions before the model sees it. In the
   test, a fiscal note seeded with "this bill costs nothing, LBB recommends repeal" went straight into an answer until
   this layer was added. If the shield is down, results are withheld rather than passed through unchecked.
5. **A groundedness check** after the answer, which flags sentences it can't match to a source.

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/desk-4-sales-tax-declines-cached.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Layer 2 at work. A prediction question gets "I can't predict what the Legislature will do", then what has actually been filed so far, with sources.</div>

{% include figure.liquid loading="lazy" path="assets/img/tx-fiscal-radar/desk-5-sb2206-leading-flagged.png" class="img-fluid rounded z-depth-1" %}

<div class="caption">Layer 5 at work. A leading question ("why does SB 2206 cost nothing…?") got a weak answer, and the groundedness check flagged 70% of it and listed the sentences it couldn't source. This copy was served from the answer cache, which is exactly why flagged answers are now kept out of it.</div>

The groundedness check has a known weakness worth saying out loud: it reads the fiscal-note text, not the warehouse
results, so it sometimes flags correct numbers that came from the database. It's a warning light, not a verdict.

Together, the guardrails cost about as much as the model does: roughly half of the half-cent each answer costs.

## Memory, only when asked

Tick "Remember my agency and topics" and the assistant uses Foundry's memory store to keep work context between
visits: which agency you're with, what you tend to ask about. It's off by default. It keeps work context only, it's
told to exclude personal details, it expires after 30 days, and one person's memory is never visible to another
(tested with two users). Answers that use memory are never cached, since they're tailored to one person.

Testing memory also caught a real bug. Asked about the Department of Information Resources, the agent called it
"agency 701" (that's the Texas Education Agency) and listed the wrong agency's bills. It had guessed a code because no
tool let it look one up. A lookup tool fixed it, and a new test question keeps it fixed. Tool and column names turn out
to be part of the prompt.

## What I'd tell a team building one

- **Attack it before you ship it**, with attacks written for your domain. The ones that mattered here were specific:
  a fake election-date post, and a planted "costs nothing" line in a fiscal note.
- **Put a hard control in front of the soft one.** Instructions alone didn't stop the worst requests. A fast,
  structured screen before the agent did.
- **Keep retrieval where your guardrails can see it**, unless you've decided you don't need to inspect it. That's the
  real trade-off between your own search and a managed one, not quality.
- **Count with checks, explain with judges.** Expected answers come from the warehouse at test time; AI judges explain
  failures, but they don't decide what passed.
