# godot107.github.io

Personal portfolio and creation space for **Willie Man** — data professional based in Greater Houston, Texas.

🌐 **Live site:** [godot107.github.io](https://godot107.github.io)

---

## About

This site is built with [Jekyll](https://jekyllrb.com/) using the [al-folio](https://github.com/alshedivat/al-folio) theme — forked in November 2024 and maintained as a personal portfolio covering data, AI, machine learning, and life outside work.

---

## Stack

| Layer                 | Technology                                              |
| --------------------- | ------------------------------------------------------- |
| Static site generator | Jekyll                                                  |
| Theme                 | [al-folio](https://github.com/alshedivat/al-folio) v1.0 |
| Hosting               | GitHub Pages                                            |
| CI                    | GitHub Actions                                          |

---

## What's here

| Section          | Description                                            |
| ---------------- | ------------------------------------------------------ |
| **About**        | Bio, featured projects carousel, X/Twitter feed        |
| **Blog**         | Posts on data science, ML, and personal topics         |
| **Projects**     | Write-ups for technical and personal projects          |
| **CV**           | Résumé — education, experience, certifications, skills |
| **Books**        | Reading log and reflections                            |
| **Repositories** | GitHub repo showcase                                   |

---

## Migration history

| Date     | Change                                            |
| -------- | ------------------------------------------------- |
| Nov 2024 | Forked al-folio (~v0.12.1), initial customization |
| May 2026 | Migrated to **al-folio v1.0** plugin architecture |

### v1.0 migration (May 2026)

al-folio v1.0 restructured from a monolithic theme repo to a **thin starter + plugin gem** model. The upgrade involved:

- Replacing all bundled runtime files (`_includes`, `_layouts`, `_sass`, `assets/js/css`) with plugin gems (`al_folio_core`, `al_folio_cv`, `al_search`, etc.)
- Removing 9 custom `_plugins/*.rb` scripts now provided by gems
- Porting personal config values to the v1.0 `_config.yml` schema
- Moving social links to `_data/socials.yml`
- Updating CI with CodeQL, upgrade-check, and integration test workflows
- Populating `_data/cv.yml` with actual CV data (was previously placeholder)

This migration was planned and executed with the assistance of **[Claude](https://claude.ai)** (Anthropic's AI), which analyzed the upstream changelog, identified customization conflicts, performed the file migrations, and iterated on CI failures until all checks passed.

---

## Local development

```bash
bundle install
bundle exec jekyll serve
```

Requires Ruby 3.3+ and ImageMagick.

---

## Upstream

Based on [alshedivat/al-folio](https://github.com/alshedivat/al-folio) — MIT License.
