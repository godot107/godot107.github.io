---
layout: page
permalink: /books/
title: books
description: Books Reviews and Essays
nav: true
display_categories: [contemporate, fun]
horizontal: false
nav_order: 6
---

**Welcome to My Book Review Space**

Here, I share thoughts and reflections on books I've read, many of which are borrowed from the public library. For me, books are more than stories or lessons—they are conversations. They invite us to engage with new ideas, wrestle with different perspectives, and ultimately reach our own conclusions. As John Mark Comer beautifully puts it, "Reading a book invites the writer’s thoughts to your mind." I hope my reviews inspire you to explore, reflect, and discover your own insights through reading.



<!-- pages/books.md -->

{% if page.display_categories %}
<div class="books">
  <!-- Display categorized books -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_books = site.books | where: "category", category %}
  {% assign sorted_books = categorized_books | sort: "importance" %}
  <!-- Generate cards for each project -->
  {% if page.horizontal %}
  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_books %}
      {% include books_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_books %}
      {% include books.liquid %}
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}

{% else %}

<!-- Display books without categories -->

{% assign sorted_books = site.books | sort: "importance" %}

  <!-- Generate cards for each project -->

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_books %}
      {% include books_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_books %}
      {% include books.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>
