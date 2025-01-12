---
layout: about
title: about
permalink: /
subtitle: <a href='https://linktr.ee/williemaize'>Affiliations</a>. <a href='https://hihello.me/p/e51e021a-872b-4c2c-9c66-88bd9e69c354'>Contacts</a>. All Things Data

#profile:
#  align: right
#  image: prof_pic.jpg
#  image_circular: false # crops the image to make it circular
#  more_info: >
#    <p>Greater Houston, Texas</p>

news: true # includes a list of news items
selected_papers: true # includes a list of papers marked as "selected={true}"
social: true # includes social icons at the bottom of the page
---

Welcome to my website! I created this space to share my journey in data, AI, and machine learning through blogs and projects, while also offering a glimpse into my life outside of work. Whether you're in the industry exploring my professional skills or someone curious about my hobbies—like baking, traveling, or stories about my dog—I hope you find something here that resonates. Thank you for taking the time to visit and learn more about me!


---
layout: default
title: About
permalink: /about/
---

## About Me

Welcome to my GitHub Page! Here's a carousel of featured web pages:

<!-- Carousel HTML -->
<div class="carousel">
  <div class="carousel-container">
    <a href="https://godot107.github.io/projects/" target="_blank">
      <img src="https://godot107.github.io/assets/img/prof_pic.jpg?348b15b90c8f71a6ed1d4582b1192884" alt="Featured Page 1" class="carousel-item">
    </a>
    <a href="https://en.wikipedia.org/wiki/Houston_Rockets" target="_blank">
      <img src="https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Rockets.svg/255px-Houston_Rockets.svg.png" alt="Featured Page 2" class="carousel-item">
    </a>
    <a href="https://en.wikipedia.org/wiki/Houston_Texans" target="_blank">
      <img src="https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Texans_logo.svg/150px-Houston_Texans_logo.svg.png" alt="Featured Page 3" class="carousel-item">
    </a>
  </div>
  <button class="carousel-control prev" onclick="moveCarousel(-1)">&#10094;</button>
  <button class="carousel-control next" onclick="moveCarousel(1)">&#10095;</button>
</div>

<!-- Carousel CSS -->
<style>
.carousel {
  position: relative;
  max-width: 80%;
  margin: 20px auto;
  overflow: hidden;
}

.carousel-container {
  display: flex;
  transition: transform 0.5s ease-in-out;
  width: 300%; /* Adjust based on the number of images */
}

.carousel-item {
  width: 100%;
  object-fit: cover;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  cursor: pointer;
  padding: 10px;
  font-size: 18px;
  z-index: 1;
}

.carousel-control.prev {
  left: 10px;
}

.carousel-control.next {
  right: 10px;
}

.carousel-control:focus {
  outline: none;
}
</style>

<!-- Carousel JavaScript -->
<script>
let currentIndex = 0;

function moveCarousel(direction) {
  const container = document.querySelector('.carousel-container');
  const items = document.querySelectorAll('.carousel-item');
  const totalItems = items.length;

  currentIndex += direction;

  if (currentIndex < 0) {
    currentIndex = totalItems - 1;
  } else if (currentIndex >= totalItems) {
    currentIndex = 0;
  }

  const offset = -currentIndex * 100; // Shift container based on index
  container.style.transform = `translateX(${offset}%)`;
}
</script>



<!---
Write your biography here. Tell the world about yourself. Link to your favorite [subreddit](http://reddit.com). You can put a picture in, too. The code is already in, just name your picture `prof_pic.jpg` and put it in the `img/` folder.

Put your address / P.O. box / other info right below your picture. You can also disable any of these elements by editing `profile` property of the YAML header of your `_pages/about.md`. Edit `_bibliography/papers.bib` and Jekyll will render your [publications page](/al-folio/publications/) automatically.

Link to your social media connections, too. This theme is set up to use [Font Awesome icons](https://fontawesome.com/) and [Academicons](https://jpswalsh.github.io/academicons/), like the ones below. Add your Facebook, Twitter, LinkedIn, Google Scholar, or just disable all of them.

-->
