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

Welcome to my website! I created this space to share my journey in data, AI, and machine learning through blogs and projects, while also offering a glimpse into my life outside of work. Whether you're in the industry exploring my professional skills or someone curious about my hobbies—like baking, traveling, or stories about my dog—I hope you find something here that resonates. Thank you for taking the time to visit and learn more about me!


---
layout: default
title: About
permalink: /about/

---

## About Me

Welcome to my GitHub Page! Here's a carousel of featured web pages:

<div id="carousel" style="position:relative; width:300px; height:200px; overflow:hidden;">
  <div class="carousel-container" style="display:flex; transition: transform 0.5s ease; width: 300%; height: 100%;">
    <!-- First Image with Link -->
    <a href="https://en.wikipedia.org/wiki/Houston_Astros" target="_blank" style="width: 300px; height: 200px; display: block;">
      <img class="carousel-img" src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Houston-Astros-Logo.svg/150px-Houston-Astros-Logo.svg.png" alt="Image 1" style="width: 100%; height: 100%; object-fit: cover;">
    </a>
    <!-- Second Image with Link -->
    <a href="https://en.wikipedia.org/wiki/Houston_Texans" target="_blank" style="width: 300px; height: 200px; display: block;">
      <img class="carousel-img" src="https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Texans_logo.svg/150px-Houston_Texans_logo.svg.png" alt="Image 2" style="width: 100%; height: 100%; object-fit: cover;">
    </a>
    <!-- Third Image with Link -->
    <a href="https://en.wikipedia.org/wiki/Houston_Rockets" target="_blank" style="width: 300px; height: 200px; display: block;">
      <img class="carousel-img" src="https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Rockets.svg/255px-Houston_Rockets.svg.png" alt="Image 3" style="width: 100%; height: 100%; object-fit: cover;">
    </a>
  </div>
  
  <!-- Left and Right Navigation Buttons -->
  <button class="carousel-nav left" onclick="navigateCarousel(-1)" style="position:absolute; top:50%; left:0; transform:translateY(-50%); background-color: rgba(0, 0, 0, 0.5); color: white; border: none; padding: 10px; cursor: pointer;">←</button>
  <button class="carousel-nav right" onclick="navigateCarousel(1)" style="position:absolute; top:50%; right:0; transform:translateY(-50%); background-color: rgba(0, 0, 0, 0.5); color: white; border: none; padding: 10px; cursor: pointer;">→</button>
</div>

<script>
  let container = document.querySelector('.carousel-container');
  let images = document.querySelectorAll('.carousel-img');
  let currentIndex = 0;
  let carouselInterval;

  // Function to rotate the carousel
  function rotateCarousel() {
    currentIndex = (currentIndex + 1) % images.length;
    container.style.transform = `translateX(-${currentIndex * 100 / images.length}%)`;
  }

  // Function to navigate the carousel with buttons
  function navigateCarousel(direction) {
    currentIndex = (currentIndex + direction + images.length) % images.length;
    container.style.transform = `translateX(-${currentIndex * 100 / images.length}%)`;
  }

  // Start the carousel interval
  function startCarousel() {
    carouselInterval = setInterval(rotateCarousel, 3000); // Rotate every 3 seconds
  }

  // Pause the carousel on hover
  function pauseCarousel() {
    clearInterval(carouselInterval);
  }

  // Resume the carousel when the mouse leaves the carousel
  function resumeCarousel() {
    startCarousel();
  }

  // Add hover event listeners
  document.getElementById('carousel').addEventListener('mouseenter', pauseCarousel);
  document.getElementById('carousel').addEventListener('mouseleave', resumeCarousel);

  // Start the carousel when the page loads
  startCarousel();
</script>




<!---
Write your biography here. Tell the world about yourself. Link to your favorite [subreddit](http://reddit.com). You can put a picture in, too. The code is already in, just name your picture `prof_pic.jpg` and put it in the `img/` folder.

Put your address / P.O. box / other info right below your picture. You can also disable any of these elements by editing `profile` property of the YAML header of your `_pages/about.md`. Edit `_bibliography/papers.bib` and Jekyll will render your [publications page](/al-folio/publications/) automatically.

Link to your social media connections, too. This theme is set up to use [Font Awesome icons](https://fontawesome.com/) and [Academicons](https://jpswalsh.github.io/academicons/), like the ones below. Add your Facebook, Twitter, LinkedIn, Google Scholar, or just disable all of them.

-->
