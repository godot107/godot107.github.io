---
layout: page
title: NBA Daily Fantasy Sports (DFS) Project - Competing for Pocket Cash
description: Yahoo NBA Daily Fantasy Sports
img: assets/img/nba_daily_Fantasy.png
importance: 3
category: work
---
# My NBA Daily Fantasy Sports (DFS) Project: Competing for Pocket Cash

## Background

As someone who's followed the NBA for nearly two decades, the 2024–2025 NBA season presented a perfect opportunity to dive into the world of **Daily Fantasy Sports (DFS)**. Growing up in Houston, I’ve experienced the highs of the Kyle Lowry, Tracy McGrady (TMAC), and Yao Ming era, and I’ve always loved the strategy and excitement of basketball.

To add a bit of recreation and challenge to my routine, I decided to put my NBA knowledge to the test by entering DFS competitions. For the last few months, I've been participating daily, with a focus on **50/50 competitions** where you aim to place in the top 50% of players. So far, my results have been promising: I’ve earned about **130%** of my initial entry fees, which has made the experience even more rewarding.

---

## The Workflow

Here’s how I approach building a DFS lineup:

1. **Roster Review:** I start by analyzing the available roster of players for the day.
2. **Data Scraping or API Calls:** I gather relevant stats by scraping data or invoking APIs that provide updated player metrics.
3. **Scoring Algorithm:** I build a composite score that takes into account recent performances and other factors like Vegas odds and matchups.
4. **Player Value Scoring:** After calculating scores, I assign a **'value-score'** to each player, which helps me evaluate their potential relative to their salary.
5. **Lineup Building:** Using DFS optimizers, I assemble my final lineup, aiming to maximize value while fitting within the salary cap.

---

## Current Implementations

### Scoring System

- **Composite Score:** I apply a weighted average on the last five games of a player, but I bias it against their most recent performance. This helps mitigate the tendency to overvalue recent outliers.
- **Vegas Odds:** I integrate Vegas odds to gauge the overall expectations for a game. The higher the projected total points, the more opportunities players will have to accumulate fantasy points.
- **Home/Away Modifier:** I factor in whether a player is playing at home or on the road, as this can influence performance.
- **Alternative Value Scoring:** I use various stats—such as minutes played, rebounds, assists, and usage rate—as part of a more holistic value assessment.
- **Optimizers:** While optimizers provide a useful baseline, I fine-tune the lineup based on my scoring system and any last-minute changes like injuries or lineup shifts.

---

## What I’ve Learned

### It’s All About Value

While **superstars** like Jayson Tatum or Luka Dončić are always great players, they don’t always deliver good **value** in a DFS contest. These players typically come with a hefty price tag, and if they have an off-night, it can leave you at a disadvantage. It’s crucial to balance star power with lower-cost players who can provide solid fantasy points.

### Pace of Play Matters

In DFS, **pace** is king. A faster-paced game means more possessions, which translates to more opportunities for players to score, rebound, and assist. For example, a game between two fast-paced teams like the Brooklyn Nets and Golden State Warriors is likely to have more fantasy potential than a slow-paced game.

### Monitoring Salary Trends

In DFS, player salaries can change daily based on performance. If a player has a breakout game, their salary will increase, potentially making them less attractive for future contests. I track salary trends closely, as a player’s price can act as an **inflection point**—for example, a rookie like Brandon Boston Jr. may have been a good value at a low price, but as his salary rises, it becomes harder to justify selecting him.

### Embracing Risk

To win, you must accept some risk. Whether it’s betting on an underperforming player to bounce back or choosing a lesser-known rookie who might break out, risk is inherent in DFS, and **reward follows risk**. This concept extends beyond DFS and into life decisions—investing in education, business ventures, or even people requires taking chances.

### Depth Charts are Crucial

Injuries and roster changes are a constant in the NBA, and they present opportunities for value. When a starter is out, the backup player steps in and often offers great value at a lower price. Additionally, the matchups can shift in favor of the opponent, creating even more volatility. Monitoring team depth charts is vital for maximizing value.

---

## Challenges and Observations

### Emotional Bias

One of the hardest lessons I’ve learned is to **avoid becoming attached** to certain players. For instance, I’ve had Ivica Zubac in my lineups multiple times, and while he was a great value initially, his salary has risen, making him less of a bargain. Just because a player has been solid in the past doesn’t mean they’re worth their price in the present.

### The Unpredictability of NBA Games

NBA games are inherently unpredictable. Even when everything seems to align—like a favorable matchup and strong player stats—there are external factors beyond our control:
- **Travel schedules** and the impact of back-to-back games.
- **Player motivation** (e.g., contract years, playing against former teams).
- **Injuries** during games can completely alter a player’s performance.

---

## The Fun Side of DFS

Despite the challenges, DFS remains incredibly fun. It’s not just about the potential to earn money—it’s about the thrill of making informed decisions and **competing against other fans**. Beating the odds and outsmarting opponents in a game of skill is immensely rewarding. Plus, it enhances my enjoyment of NBA games, as every play feels like it could impact my DFS lineups.

---

## What’s Next for My DFS Strategy?

As I continue to refine my approach, there are a few things I plan to implement:

- **Strength of Schedule:** I want to incorporate strength of schedule metrics to assess the difficulty of upcoming matchups.
- **Advanced Scoring Models:** I aim to enhance my scoring algorithm to better account for situational factors like player fatigue and team dynamics.

Daily Fantasy Sports has opened a new way for me to engage with the NBA, and I’m excited to keep learning and improving my strategies as the season progresses.
