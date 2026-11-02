---
layout: post
title: "The Great War was a family feud. I measured how close."
date: 2026-11-21 12:00:00-0600
description: How related were the monarchs who went to war in 1914? Kinship coefficients on eight generations of Wikidata ancestry, and Bayes' rule on Queen Victoria's haemophilia gene.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/family-tree/cousins_war_heatmap.png
og_image: https://willieman.com/assets/img/og/the-great-war-was-a-family-feud.png
---

*In August 1914, sixteen European monarchs had well-recorded family trees. Every one of the 120 pairs among
them was related, including all fifteen pairs whose countries fought each other.*

Everyone knows the First World War was a family quarrel. George V, Kaiser Wilhelm II and Tsar Nicholas II were
cousins, and Wilhelm and Nicholas signed their telegrams "Willy" and "Nicky". I wanted to know whether the story
holds up as a number. How related were the monarchs who went to war in 1914? Was it three famous cousins, or all of
them?

Code and data: [github.com/godot107/family-tree](https://github.com/godot107/family-tree).
There is also an [interactive version of this story](/assets/html/family-tree/family-feud.html).

## Building the family

I took the nineteen people who reigned in Europe in August 1914 and pulled eight generations of their ancestry
from Wikidata, the free database behind Wikipedia's infoboxes. Eight generations reach back to people born in the
1600s. Nineteen monarchs have 9,690 ancestor slots across those generations. Wikidata filled 7,591 of them with
only **1,816 different people**, so the average ancestor appears four times. Genealogists call this pedigree
collapse. In royal houses it is the norm.

That repetition is why a family "tree" is the wrong picture. It is a graph: each person points to two parents,
and cousin marriages join branches again further down. So I wrote the code as graph code. A relationship
is a pair of paths climbing from two people to a shared ancestor through two different children. The number of
generations on each side gives the name, so "second cousin once removed" is just a two-and-three climb with a
difference of one.

Before trusting it, I checked it against cases historians already know. Elizabeth II and Prince Philip come out as
third cousins through Queen Victoria and second cousins once removed through Christian IX of Denmark, which is
right. Victoria and Albert come out as first cousins. Isabella II of Spain has an inbreeding coefficient of exactly
1/8, which is correct because her parents were uncle and niece. (The inbreeding coefficient is the chance that a
person's two copies of a gene, one from each parent, are the same copy handed down from a shared ancestor.)

## A continent of cousins

{% include figure.liquid loading="eager" path="assets/img/family-tree/cousins_war_heatmap.png" title="Kinship among the monarchs of 1914. Darker squares share more ancestry." class="img-fluid rounded z-depth-1" %}
<div class="caption">Kinship among the monarchs of 1914. Darker squares share more ancestry.</div>

The darker a square, the more ancestry two monarchs share. The measure is the kinship coefficient: the chance
that a gene drawn at random from each of them is the same copy, inherited from a common ancestor. Siblings score
1/4, first cousins 1/16, second cousins 1/64.

The answer is all of them. Sixteen of the nineteen monarchs have well-recorded ancestry, and **every one of
the 120 pairs among them is related** within eight generations. That includes all fifteen pairs whose countries fought
on opposite sides. (Italy and Romania joined later, and Russia left in 1917.) The three exceptions are Serbia's Peter I, Montenegro's Nicholas I and the Ottoman sultan
Mehmed V. For them the hatched squares mean the records are thin, not that there is no relation.

## The nearest cousin understates it

The usual way to describe two relatives is the nearest line: "first cousins". Royal pedigrees fold back on
themselves so often that the nearest line is a poor summary. Wilhelm II and Nicholas II were second cousins once
removed by their nearest line. But **118 separate lines** connect them within eight generations. Added up, they make
the Kaiser and the Tsar about as related as first cousins once removed, and 1.6 times as related as ordinary second
cousins. George V and Wilhelm, first cousins through
Victoria, share 71 lines.

## Victoria's gene

The same graph tells a second story. Queen Victoria carried haemophilia B on one of her X chromosomes. A carrier
mother passes the gene to each child with even odds. Sons who get it bleed, and daughters who get it become carriers.
Nine of her male descendants are documented as affected. They include her son Leopold, Tsarevich Alexei, and two
sons of Alfonso XIII of Spain.

{% include figure.liquid loading="eager" path="assets/img/family-tree/victorias_gene.png" title="Victoria's daughters and granddaughters: the chance each carried the gene, from Mendel alone (grey) and after the evidence from their sons (purple)" class="img-fluid rounded z-depth-1" %}
<div class="caption">Victoria's daughters and granddaughters: the chance each carried the gene, from Mendel alone (grey) and after the evidence from their sons (purple)</div>

Mendel alone gives each of Victoria's daughters a 50% chance of being a carrier. The family's sons are
evidence. An affected son proves his mother was a carrier. A son who grows up healthy makes it less likely. Run
Bayes' rule over the whole line of descent and the daughters separate:

- **Alice and Beatrice: certain.** Each had an affected son, and through their daughters the gene reached
  the Romanovs and the Spanish Bourbons.
- **Vicky, the Kaiser's mother: 6%.** Two of her sons grew up healthy. That is why the German imperial line
  was spared.
- **Helena: 20%.** Louise had no children, so she stays at 50%.
- **Daughters of her healthy sons: 0%.** Edward VII, Alfred and Arthur were healthy, and a healthy father can't
  pass on an X-linked gene.
- **Leopold's daughter Alice: certain.** Leopold was the one affected son. A father gives his only X chromosome to
  every daughter, so Alice was a carrier, and her son Rupert was affected.

Could the gene still be out there? My first crawl stopped four generations below Victoria, so I went further.
I followed every line that could still carry it down to the present, six generations deep. Each healthy son found
further down lowered the odds for his mother's line: Infanta María Cristina of Spain fell from 50% to 29%, and her
sister Beatriz from 20% to 11%. Of the 61 living women in those lines, 14 still have odds above 1%, and the highest is
14.5%. I count them but don't name them, because a carrier probability is a statement about a real person's health.
The family tree can't settle it: the lines still open mostly end with women whose children aren't recorded, and only a
genetic test could answer it for any one person. No case has been recorded since Infante Gonzalo died in 1934.

## Method notes

- Data: Wikidata (CC0), crawled October 2026. Affected descendants: Potts & Potts, *Queen Victoria's Gene* (1995).
  The type was confirmed as haemophilia B from Romanov remains by Rogaev et al., *Science* (2009).
- Kinship: Wright (1922), Malécot (1948). Unknown parents count as unrelated, so every value is a lower bound.
- Carrier odds: exact belief propagation. People marrying in are assumed not to carry the gene. A son counts as
  healthy once he lived past 15, and Maurice of Battenberg's disputed case counts as unknown.
- The same code reads a GEDCOM export of your own family and keeps it on your machine.
