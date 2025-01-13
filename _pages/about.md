---
layout: about
title: about
permalink: /
subtitle: <a href='https://linktr.ee/williemaize'>Affiliations</a>. <a href='https://hihello.me/p/e51e021a-872b-4c2c-9c66-88bd9e69c354'>Contacts</a>. All Things Data

profile:
  align: right
  image: prof_pic.jpg
  image_circular: false # crops the image to make it circular
  more_info: >
    <p>Greater Houston, Texas</p>

news: true # includes a list of news items
selected_papers: true # includes a list of papers marked as "selected={true}"
social: true # includes social icons at the bottom of the page
---

Welcome to my creation space where I share my journey in data, AI, and machine learning through blogs and projects, while also offering a glimpse into my life outside of work. Whether you're in the industry exploring my professional skills or someone curious about my hobbies—like baking, traveling, or stories about my dog—I hope you find something here that resonates. Thank you for taking the time to visit and learn more about me!

<h2>Featured</h2>

<div id="carousel" style="position:relative; width:300px; height:200px; overflow:hidden;">
  <div class="carousel-container" style="display:flex; transition: transform 0.5s ease; width: 300%; height: 100%;">
    <a href="https://godot107.github.io/projects/apple_cultivars_climate_change/" style="width: 300px; height: 200px;">
      <img src="https://godot107.github.io/assets/img/apple_cultivars_thumbnail.png" alt="Image 1" style="width: 100%; height: 100%; object-fit: cover;">
    </a>
    <a href="https://medium.com/@manwill/dogs-vs-cats-audio-classification-56175ce58429" style="width: 300px; height: 200px;">
      <img src="https://miro.medium.com/v2/resize:fit:720/format:webp/0*waJB0GOUm-sjj_C8" alt="Image 2" style="width: 100%; height: 100%; object-fit: cover;">
    </a>
    <a href="https://www.instagram.com/ladybirdbakingcompany/" style="width: 300px; height: 200px;">
      <img src="https://raw.githubusercontent.com/godot107/godot107.github.io/refs/heads/main/assets/img/carousel/LB_thumbnail.jpg" alt="Image 3" style="width: 100%; height: 100%; object-fit: cover;">
    </a>
  </div>
  <button class="carousel-nav left" onclick="navigateCarousel(-1)">←</button>
  <button class="carousel-nav right" onclick="navigateCarousel(1)">→</button>
</div>
<div id="text-banner" style="text-align: center; margin-top: 10px;">Apple Cultivars and Climate Change</div>

<script>
  const banners = [
      "Apple Cultivars and Climate Change",
      "Dogs vs Cats Audio Classification",
      "Lady Bird Baking Co.",
  ];
  let container = document.querySelector('.carousel-container');
  let images = document.querySelectorAll('.carousel-container a');
  let currentIndex = 0;
  let carouselInterval;

  function rotateCarousel() {
      currentIndex = (currentIndex + 1) % images.length;
      container.style.transform = `translateX(-${currentIndex * 100}%)`;
      document.getElementById('text-banner').textContent = banners[currentIndex];
  }

  function navigateCarousel(direction) {
      currentIndex = (currentIndex + direction + images.length) % images.length;
      container.style.transform = `translateX(-${currentIndex * 100}%)`;
      document.getElementById('text-banner').textContent = banners[currentIndex];
  }

  function startCarousel() {
      carouselInterval = setInterval(rotateCarousel, 3000);
  }

  function pauseCarousel() {
      clearInterval(carouselInterval);
  }

  document.getElementById('carousel').addEventListener('mouseenter', pauseCarousel);
  document.getElementById('carousel').addEventListener('mouseleave', startCarousel);

  startCarousel();
</script>





<!---
Write your biography here. Tell the world about yourself. Link to your favorite [subreddit](http://reddit.com). You can put a picture in, too. The code is already in, just name your picture `prof_pic.jpg` and put it in the `img/` folder.

Put your address / P.O. box / other info right below your picture. You can also disable any of these elements by editing `profile` property of the YAML header of your `_pages/about.md`. Edit `_bibliography/papers.bib` and Jekyll will render your [publications page](/al-folio/publications/) automatically.

Link to your social media connections, too. This theme is set up to use [Font Awesome icons](https://fontawesome.com/) and [Academicons](https://jpswalsh.github.io/academicons/), like the ones below. Add your Facebook, Twitter, LinkedIn, Google Scholar, or just disable all of them.

-->
