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

<div id="carousel" style="position:relative; width:300px; height:200px;">
  <img class="carousel-img" src="https://plus.unsplash.com/premium_photo-1736437251499-9b5d6f0a9a53?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Image 1" style="width:100%; height:100%; position:absolute; display:block;">
  <img class="carousel-img" src="https://images.unsplash.com/photo-1736131660777-8b7aa6bb0efe?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Image 2" style="width:100%; height:100%; position:absolute; display:none;">
  <img class="carousel-img" src="https://images.unsplash.com/photo-1736437381508-9f19d2936f7c?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Image 3" style="width:100%; height:100%; position:absolute; display:none;">
  <a href="https://www.reddit.com/r/nba/" target="_blank" style="position:absolute; width:100%; height:100%; top:0; left:0;"></a>
</div>

<script>
  let images = document.querySelectorAll('.carousel-img');
  let currentIndex = 0;

  function rotateCarousel() {
    images[currentIndex].style.display = 'none';
    currentIndex = (currentIndex + 1) % images.length;
    images[currentIndex].style.display = 'block';
  }

  setInterval(rotateCarousel, 3000); // Rotate every 3 seconds
</script>

<!---
Write your biography here. Tell the world about yourself. Link to your favorite [subreddit](http://reddit.com). You can put a picture in, too. The code is already in, just name your picture `prof_pic.jpg` and put it in the `img/` folder.

Put your address / P.O. box / other info right below your picture. You can also disable any of these elements by editing `profile` property of the YAML header of your `_pages/about.md`. Edit `_bibliography/papers.bib` and Jekyll will render your [publications page](/al-folio/publications/) automatically.

Link to your social media connections, too. This theme is set up to use [Font Awesome icons](https://fontawesome.com/) and [Academicons](https://jpswalsh.github.io/academicons/), like the ones below. Add your Facebook, Twitter, LinkedIn, Google Scholar, or just disable all of them.

-->
