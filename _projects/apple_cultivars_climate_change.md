---
layout: page
title: Apple cultivars and climate change in the Eastern Mountain region of the United States
description: Extensive research exists regarding the effects of climate change on agriculture. However, there is often a gap between researchers and decision makers, particularly in industries with limited resources. The apple industry is one such example. Though apples are the most consumed fruit in the United States, apple orchards occupy less than 1% of the 880 million acres of United States farmland (Industry at a Glance, n.d.; National Agricultural Statistics Service, 2024).
img: assets/img/apple_cultivars_thumbnail.png
importance: 1
category: work
related_publications: true

---

# Apple cultivars and climate change in the Eastern Mountain region of the United States
Extensive research exists regarding the effects of climate change on agriculture. However, there is often a gap between researchers and decision makers, particularly in industries with limited resources. The apple industry is one such example. Though apples are the most consumed fruit in the United States, apple orchards occupy less than 1% of the 880 million acres of United States farmland (Industry at a Glance, n.d.; National Agricultural Statistics Service, 2024). To bridge this gap, we have developed a proof of concept for an apple manufacturer, providing insight into the resilience of cultivars in the Eastern Mountain region of the United States. Our findings suggest that this region will shift into the next USDA Plant Hardiness Zone within ten years, and that two apple cultivars—Cortland and Franklin Cider—may no longer be viable. If valuable, these insights could pave the way for other regions and crops, expanding both the accessibility and relevance of essential climate data.

## Getting Started
### Source Repo:
<a href = 'https://github.com/godot107/UM-Apple-Cultivars-Climate-Change'>https://github.com/godot107/UM-Apple-Cultivars-Climate-Change</a>
### Requirements
See the `requirements/requirements.txt` file. GeoPandas, pandas, scikit-learn, and Xarray are used extensively.
### Installation
1. Clone the GitHub repository using `git clone https://github.com/FixCarbon/um-mads.git`.
2. Install dependencies using `pip install -r requirements/requirements.txt`.
3. Download a GeoTIFF file for a particular crop and region from <a href = "https://croplandcros.scinet.usda.gov/">https://croplandcros.scinet.usda.gov/</a>.
4. Run the [create_polygons.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/create_polygons.ipynb) notebook with the GeoTIFF file to define a geographic area.
5. Run the [get_climate_data.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/get_climate_data.ipynb) and [get_weather_data.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/get_weather_data.ipynb) notebooks to retrieve data for the geographic area.
6. Run the [transform_data.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/transform_data.ipynb) and [train_model.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/train_model.ipynb) notebooks to predict temperature.
7. Run the [map_cultivars.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/map_cultivars.ipynb) and [visualize_data.ipynb](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/blob/main/notebooks/visualize_data.ipynb) notebooks to create and save visuals.
## Requesting Data
To access climate data, you will need credentials for the FixCarbon Amazon S3 bucket. Similarly, to access weather data, you will need credentials for Oikolab. FixCarbon provided both sets of credentials for this project. If you have credentials, create a `hidden.py` file. An example template is provided below.

```
import os

os.environ['AWS_ACCESS_KEY_ID'] = 'YOUR_AWS_ACCESS_KEY_ID'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'YOUR_AWS_SECRET_ACCESS_KEY'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['OIKOLAB_API_KEY'] = 'YOUR_OIKOLAB_API_KEY'
```

## Interpreting Results
Results for the proof of concept are detailed in the `reports/report.pdf` file. Our model acheived an R<sup>2</sup> score of 0.89 and predicted shift in average USDA Plant Hardiness Zone from 6B to 8A. 

Assuming the USDA continues to use a 30-year rolling average for risk assessment, most apple cultivars will continue to be viable. However, two cultivars—Cortland and Franklin Cider—may no longer be viable past 2025, when the entire region shifts into 6A. Furthermore, the majority of the region will be in 7A just after 2030, jeopardizing an additional 13 cultivars, including Ben Davis, Empire, Enterprise, and Liberty, among others.

_USDA Plant Hardiness Zones in the Eastern Mountain Region from 2014 to 2050 based on Elastic Net Regression_

![plot](https://github.com/godot107/UM-Apple-Cultivars-Climate-Change/raw/main/reports/figures/fig4_weather_usda.gif)

### Resources
- {% cite hoplamazian2023 %}
- {% cite usappleindustry2024 %}
- {% cite mohammed2024 %}
- {% cite morton2017 %}
- {% cite openai2023 %}
- {% cite nass2024 %}
- {% cite peter2024 %}
- {% cite usda2023 %}
- {% cite weber2023 %}
