---
layout: page
permalink: /blog/tags/
title: tags
description: Every topic on the blog, with the posts filed under it.
nav: false
---

<!--
  A browsable index of the whole tag vocabulary. Rendered from `site.tags`
  rather than from a hand-written list, so it can never drift out of step with
  what the posts actually carry. The curated vocabulary and the rules for
  changing it are in docs/TAXONOMY.md.

  `site.tags` is a Hash, and Liquid's `sort` wraps a Hash in a one-element array
  rather than sorting its pairs (see InputIterator in standardfilters.rb), so
  `site.tags | sort` silently yields one empty entry. Collect the names into a
  real array first, sort that, and look each tag up by key.
-->

{% assign tag_names = "" | split: "," %}
{% for tag in site.tags %}
{% assign tag_names = tag_names | push: tag[0] %}
{% endfor %}
{% assign tag_names = tag_names | sort %}

<p>
  {{ tag_names.size }} topic{% if tag_names.size != 1 %}s{% endif %} across
  {{ site.posts.size }} post{% if site.posts.size != 1 %}s{% endif %}.
</p>

<div class="tag-index-jump">
  {% for name in tag_names %}
    <a href="#{{ name | slugify }}"><i class="fa-solid fa-hashtag fa-sm"></i>{{ name }} ({{ site.tags[name].size }})</a>
  {% endfor %}
</div>

{% for name in tag_names %}
{% assign tagged = site.tags[name] | sort: "date" | reverse %}

  <h2 id="{{ name | slugify }}" class="tag-index-heading">
    <a href="{{ name | slugify | prepend: '/blog/tag/' | relative_url }}">{{ name }}</a>
    <span class="tag-index-count">{{ tagged.size }}</span>
  </h2>

  <ul class="tag-index-posts">
    {% for post in tagged %}
      <li>
        {% if post.redirect contains '://' %}
          <a href="{{ post.redirect }}" target="_blank" rel="noopener noreferrer">{{ post.title }}</a>
        {% elsif post.redirect %}
          <a href="{{ post.redirect | relative_url }}">{{ post.title }}</a>
        {% else %}
          <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        {% endif %}
        <span class="tag-index-date">{{ post.date | date: "%b %-d, %Y" }}</span>
      </li>
    {% endfor %}
  </ul>
{% endfor %}
