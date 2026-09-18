# Blog taxonomy

How posts on willieman.com are classified, and the rules for changing it.
`docs/` is excluded from the Jekyll build (`_config.yml: exclude`), so this file
is versioned with the site but never published.

## Why this exists

The taxonomy had drifted into being useless. Before this document:

- `_config.yml: display_tags` still held al-folio's demo list
  (`formatting`, `images`, `links`, `math`, `code`, `blockquotes`). Five of those
  six tags matched no post, so the tag strip on `/blog/` was five dead links.
- `display_categories` was `["external-services"]`, which is Medium-importer
  plumbing, not a topic a reader would pick.
- 14 tags covered 17 posts and **8 of them appeared on exactly one post**. A tag
  page with one result is a dead end: the reader asks for "more like this" and
  is handed the post they just finished.
- `community` and `faith` sat on the *same six posts*, so one of them carried no
  information at all.
- Four posts had no tags and no category.

## The two axes

**Category — what kind of post it is. Exactly one per post.**

| category | meaning |
| --- | --- |
| `project` | something I built, normally with a repo behind it |
| `tutorial` | explains a technique rather than reporting a build |
| `essay` | commentary or analysis, nothing built |
| `slice-of-life` | personal, non-technical |

**Tag — what the post is about. One to three per post, from the closed list.**

| tag | posts | covers |
| --- | --- | --- |
| `faith` | 6 | the 2016 CSMP summer missions series |
| `machine-learning` | 5 | models, deep learning, signal processing, NLU |
| `data-science` | 3 | analysis and forecasting where no model is the point |
| `healthcare` | 2 | clinical and health-IT work |
| `cloud` | 1 | infrastructure, DNS, deployment — **provisional, see below** |

## Rules

1. **Every post gets exactly one category** from the four above.
2. **Tags come from the closed list.** Do not invent one while writing a post.
3. **A new tag needs two posts that would carry it.** One post is not a topic,
   it is a detail. Until the second exists, use the nearest tag on the list.
4. **No tag that is a subset of another.** `deep-learning`,
   `signal-processing` and `predictive-maintenance` were all folded into
   `machine-learning` for this reason; splitting them again needs rule 3 to be
   satisfied *and* the parent tag to stay useful without them.
5. **No tag that duplicates a category.** `project` is a category, never a tag.
6. **No two tags with the same membership.** That was the `community` / `faith`
   problem; `community` was dropped.
7. **Three places must agree.** The closed list lives in
   `_config.yml: display_tags`, is rendered by `_pages/tags.md`, and is repeated
   in `.claude/skills/publish-writeup/SKILL.md`. Change all three together.

### The provisional tag

`cloud` has one post (the Lightsail/DNS box) and so does not satisfy rule 3. It
is kept deliberately, because the cloud learning journey is active work and the
second post is expected. If a second cloud post has not appeared by the time the
tag is a year old, merge it rather than letting it sit as a dead end.

Record any other exception here rather than quietly breaking rule 3.

## Retired

- `community` — identical membership to `faith` (rule 6).
- `deep-learning`, `signal-processing`, `predictive-maintenance` — subsets of
  `machine-learning` (rule 4).
- `datascience` — respelled `data-science`.
- `aws`, `dns`, `devops` — single-post tags (rule 3), folded into `cloud`.
- `math` — single-post tag, folded into `machine-learning`.
- `comments`, `sample-posts`, `external-services` — existed only because two
  al-folio demo posts were still published. Those posts were deleted.

`external-posts` is **not** part of this taxonomy: `_config.yml` assigns it to
every Medium import, and `_plugins/external_post_thumbnails.rb` keys its
de-duplication off it. Leave it alone.
