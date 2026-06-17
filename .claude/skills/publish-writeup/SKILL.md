---
name: publish-writeup
description: >
  Publish a project repo's writeup/article as a post on the godot107.github.io
  al-folio blog, with assets self-hosted and proper front matter. Use when the
  user wants to migrate, port, or publish a markdown writeup from another GitHub
  repo (e.g. a project's blog/ or reports/ article) onto this site. Triggers:
  "migrate this post over", "publish my <repo> writeup to the blog", "port the
  article from <repo> to godot107.github.io".
---

# Publish a project writeup to the al-folio blog

Turns a markdown writeup living in another GitHub repo into a properly
configured post on **godot107.github.io**, with every asset self-hosted (no
hotlinks). This is the repeatable version of the CWRU
(`predictive-maintenance-cwru`) migration. **Assist and stage a draft — do not
silently publish.** Always show the draft and get the user's OK before commit.

## Inputs to gather (ask only what's missing)

- **Source repo** — `OWNER/NAME` (e.g. `godot107/predictive-maintenance-cwru`).
- **Article path** in that repo (e.g. `blog/medium_article.md`). Don't assume a
  fixed filename — confirm it.
- **Branch/ref** — default `main`.
- Optional hints: publish date, tags/categories, preferred thumbnail.

Derive a **slug** for assets and the post (kebab-case, e.g.
`predictive-maintenance-cwru` or a title-based slug like
`teaching-a-neural-network-to-hear-a-failing-bearing`).

## Phase 1 — Fetch & localize assets (mechanical)

Run the helper from the **site root**. It downloads the article and every image
it references into `assets/img/<slug>/` and prints a `ref -> local path` map:

```bash
python3 .claude/skills/publish-writeup/scripts/localize_assets.py \
  --repo OWNER/NAME --article PATH/IN/REPO.md --slug SLUG \
  [--ref BRANCH] --save-article /tmp/writeup_src.md
```

Then `Read /tmp/writeup_src.md` for the full prose. Note anything the script
**skipped** (embeds, tracking pixels) or that **failed**.

## Phase 2 — Transform the body

Using the original markdown + the mapping, write the post body:

- **Images:** replace each `![..](url)` / `<img>` with an al-folio figure:
  ```liquid
  {% include figure.liquid loading="eager" path="assets/img/<slug>/<file>" title="<caption>" class="img-fluid rounded z-depth-1" %}
  ```
  Keep the original alt/caption text as the `title`.
- **Mermaid diagrams:** the script won't grab these (they're code, not images).
  Prefer a **pre-rendered PNG already in the repo** (look in `reports/`,
  `images/`, `assets/` for a matching export, e.g. `cnn_architecture.png`) and
  download it into `assets/img/<slug>/` for a guaranteed render. Native
  ```` ```mermaid ```` blocks are configured in `_config.yml` but render
  gem-side and can't be verified locally — use the PNG unless the user prefers
  native.
- **Math** works (`enable_math: true`): keep `$$ ... $$` and inline `$$x$$`.
- **Strip Medium-only artifacts:** remove HTML comments like
  `<!-- Publishing to Medium? ... -->` and any "clap"/follow CTAs.
- Keep external links (repo, dataset, live demos) as real URLs.

## Phase 3 — Front matter & filename

Filename: `_posts/YYYY-MM-DD-<slug>.md`. If it continues/precedes an existing
post, pick the date to keep the narrative order sensible.

```yaml
---
layout: post
title: "<Exact title>"          # quote if it contains a colon
date: YYYY-MM-DD 12:00:00-0500
description: <one-line dek>
tags: <space-separated lowercase>   # recent convention; reuse existing tags
categories: <project|tutorial|...>
giscus_comments: true
related_posts: true
thumbnail: assets/img/<slug>/<hero>.png
---
```

- **Reuse the existing taxonomy** rather than inventing tags. In use today:
  tags — `machine-learning`, `signal-processing`, `predictive-maintenance`,
  `deep-learning`, `math`, `datascience`, `healthcare`, `community`, `faith`;
  categories — `project`, `tutorial`, `slice-of-life`.
- **Thumbnail:** pick the most representative figure (or generate one with
  matplotlib for image-less posts, as done for the healthcare posts).
- **Cross-link** companion posts with `{% post_url YYYY-MM-DD-other-slug %}` and
  set `related_posts: true` on both.

### Title discipline (important — Medium round-trip)

The site imports the user's Medium feed via `external_sources`, and the user
publishes blog → Medium → the feed renders it back. `_plugins/external_post_thumbnails.rb`
drops the round-trip duplicate **by normalized title**, so the on-site title
must stay identical to what gets published on Medium, or a duplicate slips
through. Keep titles stable.

## Phase 4 — Review & publish

1. Summarize what you created (post path, asset count, thumbnail, tags) and show
   the front matter.
2. Sanity-check: every `path=` asset exists; `post_url` targets resolve; no
   `raw.githubusercontent` hotlinks remain in the body.
3. **Get the user's OK**, then commit only the new/changed files (the post, the
   `assets/img/<slug>/` images, any cross-linked post). End the commit message
   with the required `Co-Authored-By` trailer. Push only when the user says so —
   pushing to `main` auto-deploys via GitHub Actions.

## al-folio conventions reference

- Build: GitHub Actions `deploy.yml` → `bundle exec jekyll build` (no `--safe`),
  so custom `_plugins/*.rb` run. The `al_folio_core` gem is **not installed
  locally** — you can't `jekyll build` here; validate structurally instead.
- Permalink: `/blog/:year/:title/`.
- Responsive images: the `imagemagick` plugin generates 480/800/1400 variants
  for anything under `assets/img/` — always self-host post images there.
- Don't commit `.claude/settings.local.json` (personal/local).

## Gotchas

- Verify asset paths and `post_url` targets exist before committing (can't build
  locally to catch typos).
- A perfect first image isn't always the hero — sanity-check the thumbnail.
- Large image sets grow the repo; fine at this scale, but be deliberate.
- gem/theme upgrades can shift conventions — re-check the figure include
  signature and front-matter fields if a build regresses.
