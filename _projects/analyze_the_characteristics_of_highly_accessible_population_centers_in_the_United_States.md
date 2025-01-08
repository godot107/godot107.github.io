---
layout: page
title: Analyze the characteristics of highly accessible population centers in the United States
description:  This project seeks to improve accessibility to jobs, entertainment, and shopping
img: assets/img/accessible_populations_walkability.jpg
importance: 1
category: work
related_publications: true
---

# Introduction

In the US, cars are the most utilized modes of transportation for every day activity and life. Compared to European countries like Amsterdam that use bicycles, Paris, France on subways, and Rome, Italy on high speed rails, US citizens for the most-part rely solely on cars. This raises concern on the scalability of urban planning and affordable housing to various areas in the US. Using government curated and publically accessible datasets, our hope to improve the daily lives of their citizens by increasing the accessibility of amenities such as jobs, entertainment, and shopping.

The outcome of this report is to identify the characteristics which makes a city more accessible than others to create models that predict the accessibility of a population center with those characteristics. Realizing that the scope is beyond the allotted time, we decided to focus on _walkability_ as our metric for accessibility.

# Related Work

1. [The Influence of Land Use on Travel Behavior](https://www.sciencedirect.com/science/article/abs/pii/S0965856400000197) (Boarnet and Crane 2001)
1. The Influence of Land Use on Travel Behavior (Boarnet and Crane 2001) seeks to identify key factors determining the likelihood of consumers using mass transit over single family automobiles. The study regresses trip behavior (number of trips by walking, mass transit and automobile) of Southern California residents with three classes of independent variables: 1) Price of travel and the income level of the individual household, 2) Socio-demographic "taste variables such as gender, education levels, age and number of people per household and 3) Land use and urban design characteristics (as regressed in previous similar studies)
1. Our project will incorporate social-demographic variables such as urban or not, access to food, and urban design such as road network density. However, instead of using income level of individual households, we will use housing prices by FIPS code.
1. [The economic value of neighborhoods: Predicting real estate prices from the urban environment](https://arxiv.org/abs/1808.02547)
1. Use home listings, openstreetmap, and census data on population, buildings, and industries to predict home value. In terms of differences, the research scope are individual property and neighborhood. Our research is scoped to census tracts.
1. [Neighborhood Walkability and Housing Prices: A Correlation Study](https://www.mdpi.com/2071-1050/12/2/593)
1. The study regresses housing prices using walkability score using OLS regression. Different categories were used to derive walkability. For example, the study uses access to restaurants, shopping, schools, and recreation. The study invokes a penalty based on pedestrian friendliness using intersection density and average block length.

# Data Sources

## Environmental Protection Agency's Smart Location Database (SLD)

The [EPA's Smart Location Database](https://edg.epa.gov/EPADataCommons/public/OA/SLD/SmartLocationDatabaseV3.zip) is an aggregation dataset, containing data from a variety of sources and timeframes, including [Longitudinal Employer Household Dynamics](https://lehd.ces.census.gov/) from 2017, the [Census 2019 Tiger/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2019.html#list-tab-790442341), [Census ACS 5 year](https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2018/5-year.html) from 2018, and [GTFS](https://gtfs.org/) data from providers such as "[TransitFeeds](https://transitfeeds.com/)" and "[TransitLand](https://www.transit.land/)" in 2020. The SLD was created to help facilitate efforts such as travel demand and transportation planning studies. It is composed of more than 90 different variables associated with employment, transportation, land use, and demographics. This dataset contained our dependent variable, the National Walkability Index (NWI).

## Zillow Home Value Index (ZHVI)

The [Zillow Home Value Index (ZHVI)](https://www.zillow.com/research/data/), which is made available as a csv file, contains time series data at the State/County FIPS grain for the "middle tier" (i.e. 35th to 65th percentile) typical home value with a monthly periodicity. The dataset ranges from Jan-01-2000 to Jul-01-2023, but due to missing values for small regions, especially in early years, we have decided to only use data from January 2012 or later. This dataset provided the "Home Value" feature for our analysis.

## U.S. Department of Agriculture's Food Access Research Atlas (Food Atlas)

The [USDA Food Access Research Atlas](https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data/) (hereafter referred to as "Food Atlas") is a data asset focused on identifying Census Tracts of low income and low accessibility to food resources, originally created to measure the impact of food deserts. It contains numerous features, but we concentrated on binary variables that define a Census Tract as Urban, Low Access to Food, Low Income, or Low Vehicle Accessibility. The Food Atlas was downloaded as a multi-sheet Excel file from their website, which was updated on 4/27/2021.

## Pre-Processing Steps for Data Sources

EPA SLD

- Converted the dataset from [ESRI GDB](https://desktop.arcgis.com/en/arcmap/latest/manage-data/administer-file-gdbs/file-geodatabases.htm) format using geopandas.
- Dropped shapefile columns that make the dataset excessively large.
- Removed records that are not states (US territories & holdings).
- Created Census Tract and county level FIPS codes to join against Zillow and Food Atlas.
- Dropped records where features are out-of-range from the study, for example all CBGs with population-weighted centroids that were further than three-quarter miles from a transit stop were assigned a value of "-99999.

Zillow ZHVI

- Combine StateCodeFIPS and MunicipalCodeFIPS to create a county level FIPS column.
- Melt the data by Year in order to transform the dataset from a wide structure to a long structure.
- Extract the years and months as independent variables from the date column for easy filtering.

USDA Food Atlas

- Created the county level FIPS from the Census Tract identifier to join against Zillow and EPA SLD.

# Feature Engineering

Feature engineering tasks were straightforward with these particular datasets, given the overall good hygiene of the data in general. Due to the size of the data, and the fact we were taking relatively few columns from large datasets, the [Apache Parquet](https://parquet.apache.org/) data format was utilized as part of the workflow, which is columnar optimized, features built in compression algorithms, and is well supported by the Pandas library.

For the Food Atlas dataset, we focused on the binary features for census tracts representing Urban, low access to food by distance, low income, or low vehicle accessibility to food. For these features, we grouped the tracts together by their county level FIPS identities, and then took the percentage representations for each of the binary features. For example, if a county level FIPS contained 4 census tracts with 3 tracts having the "Urban" variable set to 1, the resulting output would be 0.75 (3 Urban tracts / 4 total tracts).

There were two additional features derived from the Food Atlas, one of which was taking the mean of the PovertyRate feature, grouped by the county FIPS. The other additional feature was a binary flag created to identify potential food desert locations, applied at the tract level and then grouped to a percentage like the other binary features.

From Zillow, there were four features that were created. The first feature was a simple filter of the data to Jan-2023 observations for the supervised analysis. The other three features percent change indicators that were built by using annual percentage growth from [FRED Median Sales Price of Houses Sold for the United States](https://fred.stlouisfed.org/series/MSPUS) to identify years of high/medium/low macro home value trends and apply that to the Zillow dataset.

Please see [Appendix B - Full Feature List](#qwbpbmtpzp7t) for a listing of all features.

# Supervised Learning

## Objective

As part of the goal of understanding the characteristics of highly accessible population centers in the United States, we looked at the National Walkability Index (NWI) metric that was created by the US Environmental Protection Agency in their Smart Location Database (SLD). The NWI is a complex index that is a composite of four other metrics that are related to Employment (_D2A_Ranked_, _D2B_Ranked_), Transit Accessibility (_D3B_Ranked_), and Street Density (_D4A_Ranked_). It requires a great deal of data from a variety of sources that can be laborious to retrieve and recompose, if a researcher wanted to rebuild the Index themselves.

Our goal became to see if it was possible to approximate the NWI without directly using the same data resources that the SLD was built from (Census Demographics, Labor statistics, and Transit statistics). The NWI therefore became our dependent variable that we were trying to predict.

The workflow consisted of building a development environment for creating notebooks on a local server with 32 CPU Cores and an NVidia 3090 GPU. Using Anaconda, a virtual environment with Python 3.10 was created for this project, with Jupyter Lab and all additional libraries installed via pip. After notebooks were developed on the local server, the notebooks, data, hyperparameter objects, models, and visualizations were uploaded to a project space on Deepnote for review by the team. The data manipulation portions of the notebooks were not able to be directly executed on the Deepnote environment, due to memory limitations of the service when loading the original large datasets, but result sets were usable in the shared environment.

## Feature Representations

The Features used for this analysis are the ones in the " **Feature Engineering**" section of this report. With the exception of the Zillow _Home Value_ feature, all features were composed from the USDA Food Atlas dataset, and were aggregated from the Census Tract level to the county level. The aggregation method used was to take percentages of the binary features in all cases except for the _PovertyRate_, which took the mean. Final representations are continuous floats, ranging from 0 to 1, and 0 to100 for _PovertyRate_.

The Zillow _Home Value_ feature was built by filtering the Zillow dataset so that it was limited to January 2023 observations, and the 16 (out of 3078) observations missing the _Home Value_ data point were dropped from the analysis. This value was represented as a continuous variable with no limits.

## Method

Because the _NatWalkInd_ dependent variable is continuous within the range of 1 to 20, multiple regression modeling methods were selected for evaluation in approximating the National Walkability Index.

1. Ridge Regression - This is the baseline regression algorithm that was used to validate the other algorithms were performing adequately. Its primary advantages are that it is simple to use, is quick to execute, and that it should handle multicollinearity from the Food Atlas data fairly well.
2. Random Forest Regression - A tree ensemble algorithm, this modeling method leverages the concept of "bagging", where multiple subsets of the data source are sampled with replacement to train individual trees. The individual trees are how regularization is introduced to the model, as the various trees are then aggregated to produce a final output, which reduces overall variance. It is capable of handling missing values without requiring imputation, can also capture non-linear relationships, and is highly parallelizable.
3. XGBoost Regression - XGBoost is also a tree based algorithm, but unlike RandomForest, it builds each tree sequentially with the focus of correcting the errors of the previous tree. This method leverages the concept of using the gradient of the loss function to direct the construction of the next tree. It uses L1 and L2 regularization to prevent overfitting, and like RandomForest, it is insensitive to missing data and has some parallelism capabilities.
4. PyTorch Neural Net Regression - The PyTorch Neural Network (NN) that was used in this report was built from scratch, using only one hidden layer and ReLU Linear activation functions. An additional Dropout layer was included in each model architecture, along with an Early Stopping function to add a method of regularization and to prevent overfitting. The element of using Dropout layers makes the model inherently non-deterministic, due to the randomness introduced into the training process, despite setting a seed variable. The PyTorch NN was the only model that was trained on a GPU.

Each of the algorithms listed above utilized a hyperparameter tuning method, and leveraged 5 fold cross validation with 70/30 train/test split of data, using either Hyperopt, Scikit-Learn's HalvingGridSearchCV or ParamGrid. The selections for the hypertuning methods were quite deliberate, as explained below.

HalvingGridSearchCV was used for RandomForest models because of the independent nature of the tree ensembles. With 32 processors available, each processor could work on an independent tree with sample data, and each iteration would leverage larger samples of the data on the most successful of the models. The HalvingGridSearchCV hyperparameter tuning method evaluates a large number of model candidates using a small amount of sample data, then iteratively selecting the best candidates for training on larger samples over multiple rounds. This combination created a very efficient parameter search process.

The Hyperopt library with Tree-based Parzen Estimators (TPE) was selected for XGBoost as a result of XGBoost being not quite as parallelizable as RandomForest, due to its boosting process being sequential (though its node splitting process is parallelized). The Hyperopt TPE method implements an iterative Bayesian optimization process that was able to search through a grid space efficiently and determine the most effective model with substantially fewer iterations than HalvingGridSearchCV. This optimization process can be seen in Fig. 1 below, where promising hyperparameters are discovered early in the process, and the variability of MAE scores decreases as parameters are refined.

![](RackMultipart20231020-1-cxpey8_html_5623da23428abdfe.png)

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 1

The standard ParameterGrid method from Scikit-Learn was used for hypertuning the PyTorch model. This particular model required a large amount of fine tuning and tweaking of the parameter grid space for the number of hidden nodes, learning rate and dropout percentages, which meant it was more efficient to iterate over every permutation in the space to discover the optimal parameters, which is what the standard ParameterGrid method allowed. This model did have an advantage in that it could use GPU resources, which reduced the overall training time required. A [visualization](#_es9wik286it) is available in [Appendix E](#kipwtc1u6agx), showing the results of the 5-Fold cross validation used to generate the best Neural Net model, with the various spikes in each fold indicating the impact of dropout, and the differing number of epochs per fold illustrating the early stopping method preventing the model from hitting the maximum 1000 epoch limit, preventing overfitting.

## Evaluation

### Loss Function & Evaluation Metric

The Mean Absolute Error (MAE) method was used as the objective function and the evaluation metric in our analysis across all models. This selection was driven by the fact that the values returned by MAE are in the same unit of measure as the dependent variable, and were consequently easily interpreted against the NWI.

![Shape 2](RackMultipart20231020-1-cxpey8_html_407f4fc3ab78677b.gif)

Table 1

| **Model**        | **MAE of CV 5 Mean** | **Std Dev** | **Training Time (seconds)** | **Hyperparam Models** |
| ---------------- | -------------------- | ----------- | --------------------------- | --------------------- |
| Ridge (Baseline) | 1.1                  | ±0.25       | 1                           | 24                    |
| XGBoost          | 0.757                | ±0.026      | 1052                        | 1000                  |
| Random Forest    | 0.808                | ±0.060      | 2632                        | 15246                 |
| PyTorch NN       | 0.798                | ±0.050      | 240                         | 706                   |

### Model Evaluation and Determination

![Shape 2](RackMultipart20231020-1-cxpey8_html_1a69d0d5d4b03a0a.gif)

Table 1

Despite the variety of algorithms and hyperparameter training, the non-baseline models resulted in fairly similar scores (Table 1), with XGBoost having the slightly lower MAE and standard deviation overall, coming in at 0.757 ± 0.026 MAE. There were multiple important tradeoffs to consider for this model selection process, when comparing the top two performing models, XGBoost and PyTorch NN.

1. The training time for PyTorch models is significantly lower than the time required for XGBoost, but the accuracy of the XGBoost models is higher.
2. The PyTorch model utilized a modern GPU and there is additional substantial expense associated with this hardware. If standard CPUs are used instead, the amount of time to train complex models with more epochs would increase dramatically. The latest version of XGBoost (currently 2.0.0) can also leverage GPU hardware for training, but using it actually increased training times.
3. The explainability of XGBoost is substantially superior to that of PyTorch's NN through its "feature_importance\_" function, but NN can often more accurately model non-linear relationships.
4. The PyTorch model's architecture was extremely simple, and a more complex architecture could certainly surpass the existing XGBoost model. The tradeoff here is the amount of development time it takes to fine tune a Neural Network model to achieve those gains, versus quickly delivering a model that is sufficient for the purpose.
5. The XGBoost model is deterministic, whereas the PyTorch model is non-deterministic due to its use of dropout and early stopping. This makes XGBoost extremely repeatable, with only the parameters required to rebuild the model. For the PyTorch NN model, to recreate the results you would need to load the model's state dictionary, or a copy of the entire model itself. The model cannot be re-created by simply reusing the same parameters and architecture. The tradeoff here is therefore the storage space required to persist or recreate the model. For XGBoost, it would be measured in bytes, regardless of complexity, and for the NNs, it is measured in kilobytes for this simple model. Larger NN models would require substantially more storage, mega or gigabytes.

Considering the tradeoffs listed above, the XGBoost model was selected due to its better MAE score, its explainability, its deterministic and repeatable nature, and that it did not require additional time to refine.

### Feature Analysis ![](RackMultipart20231020-1-cxpey8_html_798e21508f1e1384.png)

Shapely Additive Explanations (SHAP) was used to calculate the overall importance of features and provide insights into some of the highest ranked.

The SHAP "Beeswarm" plot in Fig. 2 indicates that the _Urban_Pct_feature is by far the most important, followed by \_LATracts_half_Pct_ and _Home Value_.

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 2

Taking a closer look at the dependency plot for the _Urban_Pct_ feature (colored by _Home Value_ in Fig. 3), we can see that it has a non-linear impact on the SHAP values. For observations with small _Urban_Pct_ values, the impact to SHAP is nearly -1, which slowly increases to 0 when the values of the feature reach roughly 0.33. At this point, there is a plateau from ~0.33 to ~0.75, after which the impact to the SHAP value increases dramatically from 0 to 4+.

Per SHAP's interaction values, the feature that has the most interactive effects with _Urban_Pct_ is _LATracts_half_Pct_. Looking at the interactive effects dependency plot for those two features (Fig.4) indicates a negligible impact to the SHAP value from the combination until the values of both features reach roughly 0.7, which then results in a mostly positive, but slight (maximum 0.4+) increase to the SHAP value. This is the strongest interactive effect, for the most impactful feature, and it only accounts for a slight increase to the overall score, indicating that most of the

![](RackMultipart20231020-1-cxpey8_html_1b16e3f42763f3c6.png) ![](RackMultipart20231020-1-cxpey8_html_7c1e48bd2e97ef84.png)

###

### ![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif) ![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 4

Fig. 3

###

### Model Accuracy

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 5

The MAE results of 0.757 ± 0.026 indicated that the model should be capable of providing reasonable results at predicting the aggregated National Walkability Index (NWI), which has a possible range of 1 to 15.96 points. The scatterplot results in Fig. 5 has the dependent variable (_NatWalkInd_) on the X axis, the feature with the highest SHAP value (_Urban_Pct_) on the Y axis, and the plot is colored by the difference between the actual NWI values and our predicted values. The shape of the data is similar to a sigmoidal curve, and our model has clearly captured this non-linearity, as evidenced by observing the narrow band of green in the diagram, which represents a near zero difference in actuals versus predictions. ![](RackMultipart20231020-1-cxpey8_html_aa735820d6138971.png)

### Ablative Analysis of Top 5 Features

![Shape 2](RackMultipart20231020-1-cxpey8_html_12444bd0979d1a00.gif)

# Table 2

An ablative analysis was performed on the top 5 features as reported by SHAP in Figure 2. These features were removed from the training and test datasets in order to measure their MAE impact, using the XGBoost model. The MAE resulting from the ablation tests were compared against the baseline MAE, and the differences between the two are displayed in Table 3.

| **Feature**                | **Urban_Pct** | **LATracts_half_Pct** | **Home Value** | **LATracts10_Pct** | **LAhalfand10_Pct** |
| -------------------------- | ------------- | --------------------- | -------------- | ------------------ | ------------------- |
| **Importance per XGBoost** | 32%           | 21%                   | 10%            | 10%                | 6%                  |

While holding the XGBoost model parameters static, each feature(s) in the table below were dropped from the training and testing datasets, and another 5-Fold cross validation mean MAE was generated.

| **Ablated Tests**                                                         | **MAE (5-Fold CV)** | **Std Dev** | **Difference from Baseline MAE** | **Percent Difference from Baseline MAE** |
| ------------------------------------------------------------------------- | ------------------- | ----------- | -------------------------------- | ---------------------------------------- |
| None (XGBoost Baseline)                                                   | 0.7570              | ±0.0263     | 0                                | 0                                        |
| Urban_Pct                                                                 | 0.8132              | ±0.0267     | -0.0563                          | -7.43%                                   |
| Home Value                                                                | 0.7818              | ±0.0278     | -0.0248                          | -3.29%                                   |
| Urban_Pct, Home Value                                                     | 0.8727              | ±0.0290     | -0.1157                          | -15.29%                                  |
| Urban_Pct, Home Value, LATracts_half_Pct                                  | 0.8898              | ±0.0313     | -0.1328                          | -17.55%                                  |
| Urban_Pct, Home Value, LATracts_half_Pct, LATracts10_Pct                  | 0.9005              | ±0.0302     | -0.1435                          | -18.96%                                  |
| Urban_Pct, Home Value, LATracts_half_Pct, LATracts10_Pct, LAhalfand10_Pct | 1.1205              | ±0.0215     | -0.3635                          | -48.03%                                  |

![Shape 2](RackMultipart20231020-1-cxpey8_html_12444bd0979d1a00.gif)

# Table 3

Key Findings:

1. _Urban_Pct_ has significantly more impact on the MAE score than _Home Value_. This was not entirely unexpected given the SHAP analysis, but the magnitude of the difference was surprising, given the initial assumptions that _Home Value_ would tend to be more expensive in rural areas, causing Urban Percentage to be of secondary importance.
2. Despite the loss of both _Urban_Pct_ and _Home Value_, the model is still fairly resilient, with an accuracy drop of only -15.29%. The resulting mean MAE of 0.8727 is still better than the Ridge regression model's baseline score of 1.1 MAE with all of the features. This is an indication that there is likely a good amount of multicollinearity involved in this data.
3. It is not until the top 5 features (_Urban_Pct_, _Home Value_, _LATracts_half_Pct_, _LATracts10_Pct_, _LAhalfand10_Pct_), as reported by the XGBoost Feature Importance variable, until there is significant decay in the MAE score. It is at this point that the XGBoost model performance is worse than the Ridge Regression Baseline (MAE 1.1 ± 0.25).

### Hyperparameter Sensitivity ![](RackMultipart20231020-1-cxpey8_html_e26a937ea5e097e1.png)

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 6

With Hyperopt selecting the optimal parameters used for the training of the XGBoost model, it was important to look at how sensitive some parameters were to being changed. A model that is exceptionally sensitive to slight parameter changes indicates it might be over-fitted and would perform poorly when making predictions on unseen data. All other parameters were held constant when performing these tests.

![](RackMultipart20231020-1-cxpey8_html_b1a89e00aa49d271.png)

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 7

With regards to the L1 regularization parameter (reg_alpha), Hyperopt selected the value of "1" as being the most optimal value, but this indicates there is little Lasso regression occurring in our model. According to the tests (Fig. #), our model is moderately insensitive to changing the reg_alpha parameter from 1 to 100, resulting in a change from MAE 0.757 ± 0.03 to an MAE of 0.83 ± 0.03. Of course, since regularization by definition is making the model more generalizable, this result is not unexpected, and scaling from 1 to 100 is a fairly large change.

Performing a similar analysis on the max_depth hyperparameter (Fig. #) shows negligible changes from a depth of 2, which is the value selected for the best model, versus 12. The model_depth parameter is stable and is not significantly sensitive.

## Failures Analysis

1. Data leakage occurred during initial regression model development due to the time series nature of the Zillow data Observations for single FIPS codes were appearing in both Train and Test datasets, and the FIPS code categorical variable was included in the dataset as well. This caused exceptionally good MAE scores that were suspicious. Selecting a single month of observations (Jan 2023) and removing FIPS codes from training datasets remediated this issue.
2. The worst performing under prediction was for FIPS code 31043, which corresponds to the Sioux City metropolitan region in South Dakota. Looking at the SHAP force plot (Figure #) gives us an idea of the reasons for the prediction of 6.18, which is a 5.34 point miss from the actual NWI score of 11.51. The reasoning for this discrepancy comes down to issues with aggregating data up to the grain of State/County for the FIPS codes, so the Zillow _Home Value_ feature can be added to the analysis. The Smart Location Database (SLD) has very granular data, with their FIPS codes going down to the Census Block Group level, while the Food Atlas is slightly less granular at the Census Tract level. Both have to be aggregated upwards to accommodate the Zillow data.

![](RackMultipart20231020-1-cxpey8_html_cef40c36435169d6.png)

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig.8

In the case of FIPS 31043, it contains a large number of Census Block Groups in the SLD that have a very high National Walkability Index (8 out of 13 CBGs have an NWI \> 12), pushing the actual NWI mean number quite high. Looking at the features data, only two of the four Food Atlas Census Tracts for this FIPS are considered "Urban", so the critical _Urban_Pct_ feature produces a fairly low score of 0.5. This is further exacerbated by the fairly low _Home Value_ for a metropolitan area, as seen in the force plot, and a high score (0.75) for the Low Accessibility to grocery stores at 1 mile for Urban or 10 miles for Rural feature (_LA1and10_Pct_). These factors combined mean the prediction fails quite badly in this scenario.

In order to remediate this issue for future analysis, we would remove the _Home Value_ feature from Zillow, which would allow us to use the Census Tract grain of data. The feature ablation tests indicated that the _Home Value_ feature provides only nominal value, and the increased degree of accuracy gained by using a lower grain of data would most likely offset that loss.

1. The worst over prediction, in terms of percentage, was for FIPS code 51181. This particular region was quite rural (Surry County, VA), with 7 Census Block Groups in the SLD dataset, 2 of which had NWI ratings slightly above 5 points, and 3 groups had rankings in the 1 point range. This gave the county an aggregated NWI of 3.07, but the prediction was 5.42, an over prediction of 2.35 points. Reviewing the [force plot](#_i5lmqfpw6x1b) revealed that while the prediction score was pushed down from the base value of 6.5 by a lack of positive scores in the _Urban_Pct_ and _LATracts_half_Pct_, it wasn't very substantial, and no other features have enough power to push the prediction further down.

Unlike the situation for FIPS 31043, while using a lower grain of data should help in this situation, it is doubtful that this particular prediction can be remediated without the use of additional features. The most likely candidate features would be acreage of the tract and population & households. This would help identify physically large tracts with small populations that are truly rural, as well as differentiate physically large tracts with large populations that are suburbs.

1. The FIPS code with the highest over prediction by magnitude is 22087, which is the area east of New Orleans. The NWI aggregated mean value was 7.08, and our model's prediction was 10.77. Reviewing the [force plot](#_sdyxxsmqzx18) reveals the value is significantly impacted by _Urban_Pct_ and related features. Investigating this issue further, there are 17 Census Tracts within the county reported in the Food Atlas data source, with 16 listed as Urban. There are also 50 Census Block Groups in the SLD, with NWI values ranging from 1 to 16. While part of this problem comes down to the issue of aggregating the NWI and features, as previously mentioned, there also seems to be a data classification problem after reviewing maps of the region. As an example, tract 22087.0302.04 is predominantly swampland, but is classified as "Urban" with a single state road passing through it with a handful of auto salvage yards, scrap metal yards, and collision repair businesses. Additionally, the majority of the other tracts appear to be suburban or residential in nature, which would typically have poor NWI scores.

Additional features that would help with this problem would include the population and acreage, which were mentioned as part of the FIPS 51181 failure analysis, but also a count of Census Block Groups within a tract, whether or not the tract is within the boundaries of a Core Based Statistical Area (CBSA), and if they are within a Combined Statistical Area (CSA).

# Unsupervised Learning

## Motivation

As part of the unsupervised learning section of this project, we have decided to create several levels of clusters to understand how transit and food infrastructure intersect with the health of a housing market in a particular county.In order to do this, three k-means clustering models were created:

1. Clustering around transit infrastructure, walkability, and urban density
2. Clustering based around the availability of food in a particular county
3. Clustering based around the sensitivity of a county's housing market to macro-economic shifts.

After this, we examined how each group of clusters overlapped with one another to gain an understanding of the relationship between each domain.

## Methods description

### Hyperparameter Tuning

Initially, we set a specific number of clusters to create for each model (n = 5), but quickly discovered that those clusters were not well differentiated from one another. In fact, there was such an overlap in clusters that it was difficult to describe the differences between different centroids. This led us to conduct hyperparameter tuning with the objective of maximizing the silhouette score.

The Silhouette score is defined as: (b-a) / max(a,b) where:

a = the average euclidean distance between each point within a cluster

b = the average distance between clusters

Scores closer to one indicate a well differentiated model with clear definitions for clusters. Scores closer to -1 indicate overlapping and undifferentiated clusters. Silhouette scores were calculated for k-means models containing the following combinations of hyperparameters:

1. Algorithms (Lloyd and Elkan)- The Lloyd algorithm is the most common K-means optimization method and involves an iterative process of recalculating centroids as the mean over their closest data-points until the model reaches convergence. This has risk of getting stuck on a local optima (depending on initialization). Elkan uses a triangle inequality to speed up the performance of training the k-means algorithm. Because our feature space and observations for clustering is relatively low, all models were successfully trained with the Lloyd algorithm.
2. N-Clusters (3 to 10)- Because these clusters inform our exploratory data analysis, we did not want to create too many of them. It would be difficult to comprehend what each cluster means if we separated them into groups of more than ten. In addition, having too few (2 clusters) may create groups too large to perform any meaningful analysis. In fact, when we tried using 2 clusters, it merely split county into rural and urban counties (without differentiating between access to transit, walkability, etc).
3. Tolerance (1e-6, 1e-4, 1e-3, 1e-2)- represents the tolerance for when Scikit-learn declares convergence between two iterations. A smaller tolerance means that the same centroids would need to be closer to converge and stop iteration. A larger tolerance indicates the iterations of centroids could be further apart.

## Unsupervised evaluation

We evaluated each clustering model based off their individual silhouette scores. The transit and infrastructure model, housing market model, and food availability models scored .43, .24, and .3 respectively. Additionally, based on the visualizations described in the discussion section, we can easily see how defined each cluster is. For example, the transit and infrastructure model created well defined, easily decipherable clusters. This is reflected in the relatively high silhouette score. However, the housing market health model is less defined, both in the visualizations as well as the silhouette score. The scatter plots- across each pair of features contains many overlapping clusters in this case.

## Failure Analysis

The failure of the housing market model can be attributed to the reasons:

1. Feature engineering and selection- low growth, medium growth, and high growth periods were defined using single years provided in the Zillow dataset. For example, the low growth period was the year with the _lowest_ growth rate in the national housing market between 2010 and present (in this case, the year 2018. Medium and high growth periods were defined as the years 2013 and 2011, respectively. As such, 7 years of the Zillow dataset were excluded from the clustering model. Alternatively, we could have created thresholds defining low, medium, and high growth periods and categorized all available years within those buckets. This would have allowed us to utilize the entire time series in our model, and potentially given us a better understanding of regional housing market resilience compared to the national average.
2. In the above point, growth was defined as the average housing cost at the beginning of the year compared to the average housing cost at the end of the year. This ignored intra-year fluctuations, and potentially missed dramatic housing events. Calculating monthly growth periods would have allowed us to catch short lived housing spikes and depressions.
3. We primarily optimized this model using a discrete K-means algorithm. Potentially, a more robust clustering model could have been achieved by exploring alternative clustering approaches, such as fuzzy k-means, hierarchical clustering, or gaussian models

# Discussion

## Supervised

An early hypothesis was developed around using _Home Value_ to predict the National Walkability Index (NWI), with an initial assumption that homes in FIPS code regions with a higher NWI would see a substantial increase in home value during the past few years. Using Facebook's Prophet library, we created time series models for all 3000+ FIPS codes to generate trends and predictions, along with their respective confidence intervals to use as features in regression models to predict the NWI index for a FIPS State/County location.

This process produced mediocre results (MAE 1.253 ± 0.043), so we pivoted from leveraging time series to a classic regression approach, still using _Home Value_, but augmented with features built from the Food Atlas. The decision to pivot from the Prophet time series approach was ultimately correct, but that process consumed a considerable amount of time, manpower, and compute cycles; we should have decided to change tack earlier in the project.

A major complication to our analysis was the lack of alignment in the granularity of data between the Zillow ZHVI, SLD and Food Atlas data sources. Rolling up our dependent variable (NWI) by two levels inherently introduced a degree of inaccuracy into the predictions from the start. Despite this issue, the model was ![](RackMultipart20231020-1-cxpey8_html_e989d45976da4065.png)surprisingly successful in predicting the NWI, with a clear normalized curve in the predictions, and an overall mean of differences in NWI actuals versus predictions of 0.034 ± 0.967.

![Shape 2](RackMultipart20231020-1-cxpey8_html_7ca98a122de74044.gif)

Fig. 9

Another surprising aspect of this analysis was the exceptionally strong correlation (0.86) between the _Urban_Pct_ feature and the _D3B_Ranked_ variable from the SLD. _DB3_Ranked_ is a street intersection density ranking, and it is one of the 4 indexes that is used to build the NWI. These two data points come from completely different resources, where _D3B_Ranked_ is built based on mapping data from [HERE](https://www.here.com/)'s NAVSTREETS product, the Urban flag in the Food Atlas is determined by a simple calculation of whether or not the geographic centroid of the census tract contains more or less than 2500 people. The strength of this correlation that was the reason that _Urban_Pct_ was the most important feature, according SHAP.

After the feature ablation tests were performed, it was clear that the Zillow _Home Value_ feature was not providing enough value (3.29%) to justify the complexities caused by the aggregation, and that a finer grain of data could potentially provide better predictions. The NWI would still need to be rolled up, but only one step, from Census Block Group to Tract level, in order to be joined with the features from the Food Atlas This would only reduce the NWI range by a minimal amount, 1 to 19.83 (instead of the 1 to 15.96 caused by the two steps roll up), which is a more accurate reflection of the actual 1 to 20 range. That being said, model times would also increase as a result of the increased number of records available for training (roughly a 2,400% increase), so there is a potential tradeoff between time to train and accuracy to be considered.

Another factor to be considered is that resiliency of the MAE scores with respect to the Feature Ablation process indicates the features likely have high multicollinearity. Utilizing Principal Component Analysis (PCA) to perform dimensionality reduction would create orthogonal components that explain the maximum variance while simplifying the feature space.

And finally, building a slightly more complex PyTorch Neural Network would almost certainly achieve better MAE results, especially with the finer grain of data mentioned above, along with the additional features mentioned in the **Failures Analysis** section for Supervised Learning. A simple test on the existing data with two additional hidden layers using ReLU activators, and changing the dimension inputs to those layers through simple multiplication, produced a 5-fold CV mean MAE of 0.7153 ± 0.0251, which is a 6% improvement over the best XGBoost model. With more time, it would be interesting to more fully investigate the possibilities available with Neural Networks with more features and observations.

## Unsupervised

### Walkability and Transit Infrastructure

The first model's goal was to understand the different levels of transit infrastructure (such as availability to public transportation) and urban density amongst different U.S. counties. In order to do this, several factors were selected from the smart location database. Since many of the factors are highly correlated with the national walkability index (see figure below), we decided to keep the list of features low.

![Shape 2](RackMultipart20231020-1-cxpey8_html_c179342a5891d654.gif)

Fig. 10

![](RackMultipart20231020-1-cxpey8_html_ac6d65828063ed62.png)

![](RackMultipart20231020-1-cxpey8_html_760c89e01f26a6d5.png)

![Shape 2](RackMultipart20231020-1-cxpey8_html_6039852edb3bb6af.gif)

Fig. 11

This also helped us have a conceptual understanding of the unique characteristics of each cluster. The features on the model are: **Total county land acreage** , **D3B** (Street intersection density), the number of street intersections per square mile, which is a good proxy for understanding the urban density of a county, **D4BO50** , Proportion of CBG employment within a square mile of fixed-guideway transit stop, which provides a measure of the public transit availability in commercial centers, and **National Walkability Index.**

![](RackMultipart20231020-1-cxpey8_html_b64fb971e3aa933d.png) ![Shape 2](RackMultipart20231020-1-cxpey8_html_1a69d0d5d4b03a0a.gif)

Fig. 12

Based on the silhouette optimized model, the model parameters and centroids are defined below. Low acreage counties generally correspond to high transit availability and walkability (cluster 0). Clusters 1 and 2 differentiate high acreage counties between their unique transit characteristics. In this case, cluster 1 represents rural counties with limited walkability and transit availability where cluster 2 represents suburban counties that are connected to urban centers by transit infrastructure.

### Food Availability

The second model's goal is to understand how individuals within a specific county have access to food- either through vehicle travel or walking. This will be used to understand the impact that food availability has on housing prices and market stability in a regional context. The features we selected are less auto-correlated than the smart location dataset and do not necessarily require principal component analysis.

![Shape 2](RackMultipart20231020-1-cxpey8_html_1a69d0d5d4b03a0a.gif)

Fig. 13

![](RackMultipart20231020-1-cxpey8_html_3d90cbce416c4cdd.png)

![](RackMultipart20231020-1-cxpey8_html_88cb3e9464383ca5.png)

The features for clustering by food availability are as follows:

1. The aggregate percent of low income tracts within a county
2. The aggregate percent of census tracts that are categorized as a "food desert" by the FDA
3. The aggregate percent of urban tracts that are within a county
4. The aggregate percent of tracts that have low access to food and have low vehicle ownership. This is defined as tracts where \>= 100 of households do not have a vehicle, and beyond 1/2 mile from supermarket; or \>= 500 individuals are beyond 20 miles from supermarket ; or \>= 33% of individuals are beyond 20 miles from supermarkets
   ![Shape 2](RackMultipart20231020-1-cxpey8_html_1a69d0d5d4b03a0a.gif)

Fig. 14

Based on the silhouette optimized model, the model parameters and centroids are defined below. In this case, there are 8 clusters within the optimal model. There are several unique clusters of note. First, cluster 0 represents a high income, urban county with high accessibility to food. We may expect these areas to have more robust housing markets. On the contrary, cluster 1 consists of counties with a poorer population that have significantly limited accessibility to food. One interesting feature on the below clusters is that food availability related to vehicle ownership does not seem to be concentrated in poorer areas. In fact, certain wealthier counties seem to have low food accessibility and vehicle ownership.

### Housing Market Health

The goal of the 3rd model is to understand the health of housing markets within a respective county. Specifically, how regional housing markets react to price swings within the broader national housing environment. The Zillow home price dataset was used to create this set of clusters. The features for this model are listed below:

1. Home value- the average normalized home value within a specific county (most recent FYE)
2. pct \_change_diff_low- the average percent change in home value compared to the U.S. percent change in home value during periods of negative growth in the U.S. housing market (between 2013 and 2022)
3. pct \_change_diff_med- the average percent change in home value compared to the U.S. percent change in home value during periods of low to no growth in the U.S. housing market (between 2013 and 2022)
4. pct \_change_diff_high- the average percent change in home value compared to the U.S. percent change in home value during periods of high growth in the U.S. housing market (between 2013 and 2022) ![](RackMultipart20231020-1-cxpey8_html_2048babfee7e82e1.png)

We generally define healthy regional housing markets as those with resilient home values during periods of economic decline and perform on par with national trends during high and no growth periods. Additionally, we have reduced all the features above, using Principal Component Analysis to further understand where each cluster is separated visually. Based on the silhouette optimized model, the model parameters and centroids are defined below. Unlike the transit model, this model contains (n=7) clusters.

![Shape 2](RackMultipart20231020-1-cxpey8_html_1a69d0d5d4b03a0a.gif)

Fig. 15

**Cluster relatedness and takeaways**

After running the above models, we looked at the overlap between the housing stability, food availability, and transit cluster sets. Specifically, we looked to see if there are unique characteristics associated with stable housing markets that are present in other datasets. We will look at 3 housing stability clusters.

**Housing cluster 0** , a middle class price-stable dataset, has high overlap with transit clusters 1 (very rural, high acreage, low density, low transit availability) and 2 (Moderate acreage, high walkability, high accessibility). Additionally, this group overlaps heavily with food availability clusters 1 (moderately urban, low vehicle accessibility to food, many food deserts) This fits in line with middle-to-high class suburban and semi-rural communities that rely heavily on cars.

**Housing cluster 2** (very low income, underperforms the national housing market), however, tells a different story. In this case, the transit infrastructure is approximately the same as with transit cluster 0. However, there is much higher overlap with urban and suburban clusters clusters that have low food availability (in this case, food availability clusters 6 and 4). Not surprisingly, this indicates that the accessibility to food corresponds to higher instability in a regional housing market.

The **healthiest housing cluster, 1** (upper class, resistant to macroeconomic swings) has a very high (40%)overlap with food availability cluster 7, which is a group representing high income, low food desert, and high food availability. This is in line with our understanding that wealthier areas generally have high quality supermarkets and many local businesses that could support the population. It also has a very high overlap with transit cluster 3, representing high density, walkable, transit accessible regions. In general, this indicates that wealthy, stable housing markets are mostly in areas that have food and have a high degree of urban mobility.

We were surprised to see that in terms of transit infrastructure, middle and low class counties were not as differentiated as we hoped. In fact, housing cluster 0 (middle income) and housing cluster 2 (low income) both were represented by a mix of high walkability and low walkability clusters. This could potentially mean that transit does not do a good enough job of differentiating between class. This could be because larger cities contain a diverse mix of individuals and classes. Because the baseline of our analysis considered characteristics at the _county_ level, we may have missed certain nuanced class considerations between specific neighborhoods. In this case, if we had more time, we may have been able to find data sources at a census tract, or even census block level. This would allow us to differentiate between very different neighborhoods within the same county.

One challenge we faced was the fact that we needed to compare time series data, specifically, the Zillow home price dataset, with point-in-time data. This prevented us from merely joining the primary datasets together. We solved this by making an assumption that point-in-time regional housing market health can be defined in terms of its past performance. For example, the three features that were created (performance during low growth, medium growth, and high growth periods) were no longer time series data points, but rather, became point in time features that we could compare to our other datasets.

# Ethical considerations

For both supervised and unsupervised applications, we examined areas within:

1. Privacy: All data sources are publically accessible and aggregated by FIPS county codes and census tracts. Therefore, no individual names or addresses are expected to be identified based on home values or infrastructure characteristics.
2. Protected Classes such as race, religion, sex, and age were not used as part of analysis or model building. Only macro-economic features were used such as Urban Percentage, Food Access, and Home Values were used in model building and analysis
3. Transparency and reproducibility: source code and notebooks have been provided, along with feature importance via SHAP analysis. Aside from the random-forest regression and pytorch neural network, all other models are deterministic.
4. The Government of Canada Algorithm Impact Assessment has been performed and can be found in Appendix.

Impact consideration and unintended consequences

We acknowledge that our findings could have policy making implications for city planners and zoning that can affect individuals within the FIPS county. For those policy-making decisions, we recommend performing a disparate impact by merging census data that contains protected classes and evaluate disproportional impacts. Unfortunately, due to time and scope, we are unable to provide the analysis.
