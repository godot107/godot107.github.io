---
layout: post
title: "Applied Math for Engineers: Deconstructing the FFT and CNNs"
date: 2026-06-16 12:00:00-0500
description: A deep dive into the math behind CNNs and the FFT using the AGY CLI.
tags: machine-learning math signal-processing
categories: tutorial
giscus_comments: true
related_posts: false
---

*This post is a direct continuation of my work on the [CWRU Predictive Maintenance pipeline](https://github.com/godot107/predictive-maintenance-cwru). While I successfully built a CNN that scored 100% accuracy, writing the code and actually understanding the deep applied mathematics behind it are two very different things.*

---

When building my predictive maintenance pipeline, I hit the classic data science milestone: my Convolutional Neural Network (CNN) scored 100% accuracy. After investigating, I realized the dataset itself was exceptionally clean under specific conditions, and the signal processing techniques I used (like the Fast Fourier Transform) had perfectly isolated the faults. 

But what was the FFT *actually* doing mathematically? Why did I need to use imaginary numbers in my Python code? And how do the layers of a CNN actually connect without causing matrix multiplication errors?

To break this down, I fired up the **AGY CLI** (Anti-Gravity CLI) for an interactive pair-programming session. I wanted to step out of pure software engineering and dive into the domain of applied math. What followed was an incredibly fun journey that transformed those complex "black box" algorithms into pure, visual intuition. 

Here is a transcript of my session with Anti-Gravity.

## 1. The CNN "Matrix Mismatch" Error

**Me:** *I'm new to CNN architecture. How does one design the inputs of one layer and the outputs of the next to be compatible? If I do it by hand, I get a lot of matrix multiplication errors. How do I build intuition for this?*

**Anti-Gravity:** This is the exact hurdle everyone faces when learning deep learning! To build intuition, separate your tensor into two concepts: **Channels** and **Spatial Dimensions (Height x Width)**.

1. **The Plumbing Rule (Channels):** When stacking Convolutional layers (`Conv2d`), you only need to worry about the channels. If Layer 1 outputs 16 pipes, Layer 2 *must* have exactly 16 intakes. PyTorch handles the spatial dimensions shrinking underneath.
2. **The Danger Zone (Flattening):** 99% of shape mismatch errors happen when transitioning from Convolutional blocks to `Linear` (Dense) blocks, which only accept a flat 1D list of numbers. 

To avoid the nightmare of manually calculating grid sizes (which breaks if your input image size changes), use the **"Cheat Code"**: `AdaptiveAvgPool2d`.

By inserting `nn.AdaptiveAvgPool2d((4, 4))` right before flattening, you tell PyTorch: *"I don't care what the height and width of the image are at this point. Mathematically squish whatever you have into a 4x4 grid."* This permanently locks your flattened size to exactly `Channels * 4 * 4`, completely eliminating shape mismatch errors!

*(Note: The math that makes Adaptive Pooling possible was pioneered by Kaiming He et al. in the 2014 paper [Spatial Pyramid Pooling](https://arxiv.org/abs/1406.4729), and Global Average Pooling was introduced by Lin et al. in [Network In Network](https://arxiv.org/abs/1312.4400). Credit to academia!)*

## 2. What actually *is* the FFT?

**Me:** *Can you attempt to explain the math behind the Fast Fourier Transform (FFT)? Start simple.*

**Anti-Gravity:** Imagine your messy vibration wave is drawn on a long, straight piece of string. Now, imagine taking that string and **wrapping it around a circle**. 

Most of the time, the string is distributed evenly around the circle, so its "Center of Mass" stays right dead in the middle at `(0, 0)`. But, if you wind the string at a speed that *exactly matches* a hidden frequency inside the wave (let's say 107 Hz), every single time the wave hits a peak, it lands on the **exact same side of the circle**. The string bulges massively to one side, and the Center of Mass shoots outward!

The mathematical equation for this is:

$$ \hat{f}(\xi) = \int_{-\infty}^{\infty} f(t) \cdot e^{-2\pi i \xi t} dt $$

*   **$$2\pi$$**: One full rotation around a circle.
*   **$$\xi$$**: The frequency (e.g., 107 Hz).
*   **$$t$$**: Time.
*   **$$i$$**: The imaginary number (which triggers 2D rotation).

The equation simply says: *"Spin the wave around a circle at frequency $$\xi$$. Does the center of mass bulge outward? If yes, draw a spike on the graph."*

## 3. Why the "Imaginary" Number?

**Me:** *What is the imaginary number $$i$$? Technically the square root of a negative number is underdetermined and errors out.*

**Anti-Gravity:** You are exactly right! You cannot multiply a number by itself and get a negative number on a standard ruler. 

But think about a 1D number line. If you multiply `1` by `-1`, it flips 180 degrees to `-1`. But what if you only want to rotate exactly half-way (90 degrees)? You need a number that, if you multiply it *twice*, gives you `-1`. That number is $$i$$! 

If you multiply `1` by $$i$$, it rotates 90 degrees off the number line, pointing straight up into a brand new 2nd Dimension. This creates the **Complex Plane**, which has an X-axis (Real numbers) and a Y-axis (Imaginary numbers). It shouldn't be called "imaginary"; it should be called a "Rotational Number."

**Me:** *Right, because it's complex math, you're mapping the imaginary number (rotation) back to the original dimension, the x-axis.*

**Anti-Gravity:** Exactly! The FFT does its rotation math and says, *"At 107 Hz, the center of mass shifted to the coordinate $$3 + 4i$$."*

But your Machine Learning model can't read `3 + 4i`. So, in Python, we use `np.abs()`. Under the hood, this calculates the actual physical distance from the center `(0,0)` to the dot `(3, 4)` using the Pythagorean theorem: $$\sqrt{3^2 + 4^2} = 5$$.

It takes the 2D rotational math, collapses it back down to a single real number (`5`), and plots that number on your Y-axis. That number `5` is exactly what your CNN or Random Forest looks at to determine if the motor is breaking.

## Conclusion

Math gets a bad reputation because it's usually taught as a bunch of disconnected equations to memorize. But when you realize that things like the imaginary number $$i$$ or the `AdaptiveAvgPool2d` layer are just incredibly clever "hacks" invented to solve real-world geometry and engineering problems, it completely changes the perspective. It stops being "black magic" and starts feeling like a superpower.

Wow, math is fun.
