---
layout: post
title: "I Turned Six Years of Data Science Textbooks Into a Knowledge Base My AI Can Reason Over"
date: 2026-06-18 12:00:00-0500
description: Building a private, local RAG system over my own library — and why I think almost everyone with a bookshelf of PDFs should do the same.
tags: machine-learning datascience deep-learning
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/textbook-to-knowledge-base/architecture.png
---

*Building a private, local RAG system over my own library — and why I think almost everyone with a bookshelf of PDFs should do the same.*

---

## The shelf problem

My data science journey started almost six years ago, in a master's program, with the usual stack of textbooks: *The Elements of Statistical Learning*, Bishop's *Pattern Recognition and Machine Learning*, Han's *Data Mining: Concepts and Techniques*, Wasserman's *All of Statistics*, Goodfellow's *Deep Learning*, and a long tail of others I collected as the field moved.

Six years later, those books have a strange status in my life. They taught me the foundations I use every day. They are, collectively, the most trustworthy reference material I own — written by the people who defined the field, reviewed to within an inch of their lives, far more reliable than a random blog post or a confident-but-wrong answer from a chatbot.

And I almost never open them.

{% include figure.liquid loading="eager" path="assets/img/textbook-to-knowledge-base/giphy.gif" title="My most trusted references, circa every day before this project. (via GIPHY)" class="img-fluid rounded z-depth-1" %}

The friction is too high. When I need to remember exactly how the bias–variance decomposition falls out, or the precise steps of the KDD process, or which distance metric Han recommends for mixed attribute types, I don't go digging through a 700-page PDF. I Google it. Or I ask an LLM and hope it isn't hallucinating. My best sources sit on disk, indexed by nothing, searchable only by my increasingly unreliable memory.

So I built the thing I actually wanted: a private knowledge base over my own library, with a vector database for **retrieval** and Claude Code as the layer that does the **reasoning** on top of it. Ask a question in plain English; get back the exact passages from *my* books, with citations, and an answer that reasons across them.

This post is about how it works, what surprised me building it, and why I think this pattern is badly underused.

---

## The idea: retrieval *and* reasoning over sources you trust

Most people now reach for a general-purpose chatbot when they have a question. That's great for a lot of things and genuinely bad for others: the model answers from a blurry average of the whole internet, it can't cite where an answer came from, and it will occasionally invent a formula with total confidence.

{% include figure.liquid loading="lazy" path="assets/img/textbook-to-knowledge-base/giphy_1.gif" title="An LLM confidently deriving a formula it doesn't actually know. (via GIPHY)" class="img-fluid rounded z-depth-1" %}

Retrieval-augmented generation (RAG) flips that. Instead of asking the model to recall facts, you:

1. **Retrieve** the most relevant passages from a corpus *you* chose and trust (a vector database does this by meaning, not keywords), and
2. **Reason** over those passages with an LLM, which now has the right source material in front of it.

The corpus is the part everyone underuses. People build RAG over company wikis and support tickets. Almost nobody points it at the canonical textbooks they already own — the highest-signal technical material most of us will ever have access to. That's the gap I wanted to close.

The reasoning layer matters just as much. I didn't want a search box that returns ten snippets and makes me read them. I wired the knowledge base directly into **Claude Code** as a native tool, so the AI can search my library mid-conversation, pull the passages it needs, and reason across three different books to answer one question — citing each as it goes. Retrieval gives it grounding; the model gives it synthesis. Neither half is enough alone.

---

## How it's built

The whole thing runs locally on a single machine with a consumer GPU (a 6 GB GTX 1660). No cloud, no API bills, nothing leaves the house. The pipeline:

{% include figure.liquid loading="eager" path="assets/img/textbook-to-knowledge-base/architecture.png" title="Ingest once: PDFs are cleaned, chunked, embedded with BGE-large, and stored in ChromaDB. On every query, Claude Code searches through an MCP server, and the retrieval pipeline applies a relevance floor, optional reranking, and MMR diversification before reasoning over the results." class="img-fluid rounded z-depth-1" %}

A few of the choices that mattered:

**Embeddings.** I use `BAAI/bge-large-en-v1.5` to turn each chunk of text into a 1,024-dimensional vector that captures its meaning. BGE has a quirk a lot of people miss: it's *asymmetric* — you're supposed to prepend a short instruction to **queries** but not to stored passages. Get that wrong and retrieval quietly degrades. That one detail is the difference between "this works" and "this is mediocre and I don't know why."

**Vector store.** ChromaDB with a cosine-similarity HNSW index. At my scale — about 600 books, ~78,000 chunks — the index lives comfortably in RAM at query time, so a question comes back in well under a second.

**The retrieval pipeline is more than nearest-neighbor.** Raw vector search is stage one. On top of it I added a relevance floor (so the system can honestly say "I found nothing relevant" instead of returning garbage), an optional cross-encoder reranker, and MMR diversification so three near-identical passages don't crowd out the answer. More on the reranker below, because it taught me a lesson.

**The integration is the payoff.** A small [Model Context Protocol](https://modelcontextprotocol.io) server exposes the knowledge base to Claude Code as tools — `search_textbooks`, `list_sources`, `get_toc`, `expand_context`. The embedding model loads once and stays resident, so there's no cold start. From my side it just feels like the AI suddenly *knows my library*: I ask a question, it searches, it reasons, it cites.

---

## The part nobody warns you about: your data is a mess

Here's the unglamorous truth of any real RAG project. The retrieval algorithm is maybe 20% of the work. The other 80% is discovering that your data is dirtier than you think.

{% include figure.liquid loading="lazy" path="assets/img/textbook-to-knowledge-base/giphy_2.gif" title="Auditing your own corpus for the first time. (via GIPHY)" class="img-fluid rounded z-depth-1" %}

When I actually audited my corpus, I found:

- **Duplicate books.** *The Elements of Statistical Learning* had been ingested twice under two different filenames — over 1,600 redundant chunks competing in every search. My first instinct, "just group by title," was naive: the same audit flagged a hundred-plus genuinely *different* files (per-section quiz PDFs that happened to share an embedded title). The fix was to detect duplicates by **shared chunk content**, not metadata — and to divide overlap by the *larger* document so a short file merely *contained* in a big compilation isn't mistaken for a copy. Correctness on a destructive operation is worth the extra care.

- **Garbled extraction.** One of my most important books — the pre-publication PDF of Goodfellow's *Deep Learning* — extracts as duplicated nonsense (`Deep Deep Deep Belief Belief Networks orks orks`). Another linear-algebra file was pure mojibake. Bad text in produces bad answers out, silently. I wrote a small heuristic to score each source for "looks broken," and it correctly surfaced the worst offender as #1.

- **Unreliable metadata.** Embedded PDF titles are frequently `Untitled`, duplicated, or shared across dozens of unrelated files. Trusting them for citations gives you nonsense provenance. I reconstruct clean titles from filenames instead.

None of this is exciting. All of it is the actual job. A knowledge base is only as trustworthy as the corpus underneath it, so I built the data-quality checks as first-class features — an `audit` command, a `dedup` tool, and a health check that runs automatically and warns me when the corpus drifts. If you take one engineering lesson from this post: **budget for data quality, and make it a running process, not a one-time cleanup.**

---

## The reranker that didn't help — and why I kept the result

I added a cross-encoder reranker because the literature says it's the single biggest precision win in RAG, and I believed it. Then I did something I think more people should do before shipping: I built an evaluation harness and actually measured it.

I wrote a small gold set of questions tied to the books that should answer them, and scored the pipeline with and without each stage (recall@k and mean reciprocal rank). The result was humbling:

| Configuration | recall@10 | MRR |
|---|---|---|
| Baseline (vector search) | 0.93 | 0.60 |
| + reranker | 0.93 | **0.53** |
| + diversification | 0.93 | 0.60 |

The reranker made things *worse* on my metric.

{% include figure.liquid loading="lazy" path="assets/img/textbook-to-knowledge-base/giphy_3.gif" title="Me, watching the 'biggest precision win in RAG' make things worse. (via GIPHY)" class="img-fluid rounded z-depth-1" %}

Now — that metric is imperfect. It checks whether the right *book* showed up, which is saturated and can't see whether a passage's *content* got more relevant (exactly what a reranker is for). So the honest reading isn't "rerankers are bad." It's "on the evidence I have, this reranker model isn't earning its place, and I will not turn it on by default and pretend it's an improvement." I left it implemented, off by default, one flag away, with a written plan to re-test it with a stronger model and a better gold set.

That discipline — *measure before you believe, and report what you find even when it's inconvenient* — is, to me, the whole point of doing this seriously. It's also the difference between a portfolio project and a demo.

---

## What it actually feels like to use

The abstract pitch is "local RAG over textbooks." The concrete experience is better than that sounds.

I ask, *"Summarize the first two chapters of Han's Data Mining."* The AI pulls the table of contents, retrieves the relevant passages from chapter 1 (the KDD process, data-mining functionalities) and chapter 2 (attribute types, similarity measures), and writes a grounded summary — citing the actual pages, from the actual book, with zero hallucination, because it's reading my copy.

I ask about the bias–variance tradeoff and get the passage from *Practical Statistics for Data Scientists* sitting next to the one from a model-selection chapter, and a synthesis across both. I ask about backpropagation and it spreads its answer across three books that each explain it differently — the intuition from one, the math from another, the code from a third.

It is, functionally, a conversation with my own bookshelf — except the bookshelf has read all of itself and can cross-reference instantly.

{% include figure.liquid loading="lazy" path="assets/img/textbook-to-knowledge-base/giphy_4.gif" title="Asking your bookshelf a question and watching it answer, with citations. (via GIPHY)" class="img-fluid rounded z-depth-1" %}

---

## Why this is underused — and the benefits

This pattern is mature technology now. Vector databases are a commodity, embedding models are excellent and free, and the tooling to wire it all into an AI assistant exists. And yet hardly anyone points it at their *own* trusted library. A few reasons it's worth doing:

- **Grounded, not guessed.** Every answer traces back to a specific page in a specific book you trust. Hallucination drops to near zero because the model is reading, not recalling.
- **Private by default.** It runs locally. My notes, my library, my questions never leave my machine. For anyone working with sensitive or proprietary material, that's not a nice-to-have.
- **You curate the truth.** A general chatbot averages the internet. This averages *nothing* — it answers from the canonical sources you deliberately chose. Signal over noise.
- **It compounds.** Every book I add makes it smarter. Six years of accumulated material stops being dead weight on a drive and becomes a living, queryable asset.
- **Retrieval *plus* reasoning.** Search alone gives you ten snippets to read. An LLM alone gives you confident guesses. Together they give you cited, synthesized answers — the actual thing you wanted.

The cost of entry keeps falling and the payoff is immediate. If you've got a folder of PDFs you "keep meaning to reference," you are one weekend away from never having to dig through them by hand again.

---

## Where it's going next

The natural next step is to lift the vector store off my desk and into the cloud behind a small service endpoint, so the knowledge base is reachable from anywhere and from other tools — not just the machine it lives on. Managed vector databases and a thin API layer make that straightforward, and it turns a personal project into something I could actually share.

But honestly, even as a local tool, it's already changed how I work. The books that taught me the field six years ago are finally pulling their weight again — not as decoration on a shelf, but as the grounded memory of an AI I can think alongside.

That's the part I find genuinely exciting. We spend a lot of energy asking what AI knows. It turns out the more useful question is: *what do you want it to know?* Point it at the right sources, give it a way to retrieve and reason over them, and the answer becomes — whatever you've spent your career learning to trust.

---

*Built with Python, ChromaDB, BGE embeddings, and Claude Code. Runs on a single consumer GPU. Code and design notes are on [GitHub](https://github.com/godot107/textbook-kb).*
