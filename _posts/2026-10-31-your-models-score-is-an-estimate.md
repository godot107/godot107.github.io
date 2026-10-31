---
layout: post
title: "Your model's score is an estimate. Here's how wrong it can be."
date: 2026-10-31 09:00:00-0500
description: Eight experiments on simulated data where the true score is known, grading every common evaluation shortcut — metrics, cross-validation, leakage, tuning, model comparison.
tags: data-science
categories: project
giscus_comments: true
related_posts: true
thumbnail: assets/img/eval-lab/l1_classification.png
---

*Eight experiments where the right answer is known, so every evaluation shortcut can be graded.*

Every machine-learning model arrives with a number attached: 92% accuracy, an AUC of 0.85, an R² of 0.3. Teams
ship on that number, budgets get set by it, and model A beats model B because of it. But the number is an
*estimate* of how the model will do on data it hasn't seen, and nobody usually checks how good that estimate is,
because on real data you can't: the future isn't in the dataset.

So I built a lab where you can. Every dataset in it comes from a simulation whose rules I wrote, which means that,
besides the usual evaluation, every model can also be scored on 100,000 fresh examples from the same rules. That
fresh-data score is the truth. The gap between it and what the evaluation reported is the thing each experiment
measures. Code, results and an executed notebook: [github.com/godot107/eval-lab](https://github.com/godot107/eval-lab).

## 1. Accuracy can't tell your model from doing nothing

Take a problem where 1 case in 100 is positive: fraud, a machine failure, a disease. My model scored **99.0%
accuracy**. So did a "model" that answers "no" to everything.

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l1_classification.png" title="Lesson 1: metrics as positives get rarer, calibration of a class-weighted model, and cost by threshold." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 1: metrics as positives get rarer, calibration of a class-weighted model, and cost by threshold.</div>

As positives get rarer (left panel), ROC AUC stays roughly flat (0.84 to 0.87), because it only asks whether positives rank
above negatives. The precision-recall score falls from 0.84 to 0.14, because it asks how many flagged cases are
real, and with rare events most flags are false alarms. For rare events, look at precision and recall.

The middle panel shows a subtler trap. A common fix for imbalance is to weight the rare class more
(`class_weight="balanced"`). Its ROC AUC is identical to the plain model's (0.861 vs 0.862), so a ranking metric
sees nothing wrong. But it now says "34% chance" for events that happen 10% of the time. Every probability is
inflated. Only scores that grade the probabilities themselves (log loss, Brier score) and a calibration plot catch
it.

That matters as soon as a decision is made. If missing a positive costs 5 and a false alarm costs 1, the right
rule is to act when the probability is above 1/(1+5) = 0.167, not 0.5. On fresh data that rule cost 0.292 per
case, within 0.007 of the best possible; the default 0.5 cost 0.398. The same 0.167 rule applied to the "balanced"
model cost **0.560**, the worst option tested, because its numbers only look like probabilities.

On a real dataset, German credit (1,000 loans, 30% go bad, a bad approval costs five times a wrongly rejected
good customer), both models at the default 0.5 threshold cost more per loan than simply **rejecting every
applicant**. At the cost-based threshold the logistic model cost 0.54 per loan, against 0.70 for rejecting everyone.
Same model; better decision rule.

## 2. In regression, the metric picks the winner

On a skewed target like house prices or sales, I trained five models, each aimed at a different metric, and scored
all of them on all metrics:

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l2_regression.png" title="Lesson 2: each metric crowns its own model; interval coverage by noise level." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 2: each metric crowns its own model; interval coverage by noise level.</div>

Each metric crowned the model built for it (left). Absolute error rewards predicting the median. Percentage error
(MAPE) rewards predicting *below* the median: it treats a 10% miss on a $5 item like a 10% miss on a $5,000 one,
and pays you to forecast low. Only the squared-error model was unbiased on average; the median-type models,
including the common habit of fitting log(price) and converting back, under-predicted by about 11%. Fine for a
typical house; a problem if the forecasts are added up into an inventory order or a budget.

One result went against the textbook: the squared-error model should have won on RMSE, and it tied with the median
model instead. The best possible mean and median predictions differ by only 3% in RMSE here, and 5,000 rows of a
skewed target aren't enough to estimate the mean that precisely. RMSE is dominated by a few huge values.

Two more traps. **R² is not a property of the model**: the same model with the same error scored R² 0.57 or 0.92,
depending only on how spread out the inputs were in the sample. And **an "80% prediction interval" can be 80% on
average and wrong everywhere** (right panel): the usual "prediction plus or minus 1.28 standard errors" contained
99% of outcomes where things were calm and only 64% where they were volatile, exactly where the interval matters.
Conformalized quantile regression came closest to the true interval at every level of noise.

## 3. Even honest cross-validation is noisy

Cross-validation is the standard answer to "how good is my model?". I trained the same simple model on 200
independent datasets of 200 rows and compared each cross-validation score with the truth:

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l3_estimators.png" title="Lesson 3: cross-validation estimates against the true error over 200 datasets." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 3: cross-validation estimates against the true error over 200 datasets.</div>

On average, 10-fold CV is almost exactly right. For any one dataset, it is typically 3.6 percentage points off,
and a single train/test split is about 1.7 times as noisy. Most surprising is the right panel: whether the CV score was high
or low barely related to whether *that particular model* was good or bad (correlation 0.18). This is a known result
(Hastie, Tibshirani and Friedman, *Elements of Statistical Learning*, 7.12): cross-validation tells you how good the
*recipe* is on average, not the one cake you baked. A 27% error estimate means "roughly 20% to 34%".

## 4. Leakage: three ways to fool yourself

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l4_leakage.png" title="Lesson 4: three kinds of leakage, each against the truth." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 4: three kinds of leakage, each against the truth.</div>

- **Choosing features before cross-validating.** Fifty examples, 5,000 random features, labels that are coin
  flips: no model can beat 50% error. Pick the 100 features most related to the label using all the data, then
  cross-validate, and the error comes out at **1.3%**. The selection had already seen the test answers. Done inside
  each fold, the estimate is 48.7%.
- **The same patient in training and test.** With ten records per patient, ordinary cross-validation said AUC 0.73;
  on genuinely new patients the model scored 0.68. Splitting by patient said 0.66.
- **Overlapping time windows.** On a price series with nothing to predict, each target covered the next 20 days, so
  neighbouring rows were near-copies. Shuffled cross-validation reported a small positive R² (+0.02), a model that
  seems to have an edge. On fresh data it scored -0.20: it loses. Splitting by time got it right (-0.22).

A detour worth admitting: my first check of when "purging" (removing training rows whose time windows overlap the
test period) matters gave absurd numbers, R² of -7. The bug was the metric, not the data. Averaging R² fold by fold
fails when test blocks are short, because overlapping targets barely vary inside a block. Scored on all
predictions together, the answer is sensible: purging barely matters with 5 folds and matters with many folds and
long windows.

## 5. Tuning makes the winning score optimistic

Try 100 settings and keep the one with the best cross-validation score. That score is the winner of 100 noisy
estimates, so it's lucky by construction:

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l5_tuning.png" title="Lesson 5: the winning score after tuning, against nested cross-validation and the truth." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 5: the winning score after tuning, against nested cross-validation and the truth.</div>

On pure noise (true error 50%), the best of 100 settings claimed **39.9%**. On a problem with real signal, the winner claimed
34.9% and truly scored 43.0%, no better than the winner of 10. *Nested* cross-validation, which wraps the whole
tuning process in an outer loop, reported 48.3% and 43.2%: honest both times.

The same thing happens when the validation set is a single group. In an earlier project I tuned a machine-fault
detector on one machine and tested it on another, and a 0.96 validation score became 0.61. Here, choosing on one
held-out group claimed 27.5% error against a true 40.2%. Cross-validating across all groups claimed 35.4% against
a true 38.0%, and chose better.

## 6. "B beats A" is usually not established

Two models that are equally good by construction, compared with five common statistical tests on 500 datasets.
A test at the 5% level should declare a winner at most 5% of the time:

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l6_compare.png" title="Lesson 6: how often each test declares a winner, when the models are equal and when B is better." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 6: how often each test declares a winner, when the models are equal and when B is better.</div>

The t-test on repeated random train/test splits declared a winner **45% of the time**. The splits share most of
their training data, so their results aren't independent, and the test thinks it has far more evidence than it
does (Dietterich, 1998). The corrected version (Nadeau and Bengio, 2003), the 5x2 cross-validation test and
McNemar's test all kept their promise (5%); a paired t-test on 10-fold CV was mildly over (8%). The sobering part is the right panel: when B really was 6 points better,
the tests that kept their promise detected it only 12% to 23% of the time with 300 rows. On small data,
"no significant difference" is the expected outcome even when there is one.

## 7. Will more data help?

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l7_curves.png" title="Lesson 7: learning curves for a high-bias and a high-variance model, and a validation curve." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 7: learning curves for a high-bias and a high-variance model, and a validation curve.</div>

Learning curves answer this before you pay for more data. A straight-line model on a circular boundary (left) has
training and cross-validation error meeting at about 50%, far above the best possible 11.6%: more data won't help, a
better model will. A nearest-neighbour model (second) memorises the training data (error 0) and keeps improving
as data grows: more data helps. And the validation curve (right) shows cross-validation picking the right tree
depth, while the training error would have picked the most complex tree.

## 8. Putting it together

The last lesson is a reusable report for any scikit-learn classifier, in the spirit of the "model quality" report
AWS's AutoML service produces. It sets aside an untouched holdout first, builds a leaderboard with a do-nothing
baseline, proper scores, calibration, the expected cost of decisions and uncertainty intervals, then scores the
winner once on the holdout. On German credit, the random forest won the leaderboard at 0.515 cost per loan and
cost 0.550 on the holdout: lesson 5's optimism, small here, but there.

{% include figure.liquid loading="eager" path="assets/img/eval-lab/l8_german_credit_report.png" title="Lesson 8: the model-quality report on German credit." class="img-fluid rounded z-depth-1" %}
<div class="caption">Lesson 8: the model-quality report on German credit.</div>

## What I'd tell a team

1. **Start from the decision, not the metric.** Write down what a miss and a false alarm cost; let that pick the
   metric and the threshold. Accuracy and the 0.5 threshold are almost never the right defaults.
2. **Check probabilities, not just rankings.** Log loss, Brier score and a calibration plot; recalibrate if needed.
3. **Treat every score as an estimate with an error bar.** A few points of noise is normal; differences smaller
   than that need a proper paired test.
4. **Split the way the model will be used.** New patients, new machines, the future: the split should look like
   that.
5. **Keep one set of data that no decision has touched**, and use it once.

## References

- Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning*, 2nd ed. (2009), sections 7.10-7.12.
- Harrell, *Regression Modeling Strategies*, ch. 5 (bootstrap validation, proper scoring rules).
- Witten, Frank, Hall, Pal, *Data Mining: Practical Machine Learning Tools and Techniques*, ch. 5 (nested CV).
- Lopez de Prado, *Advances in Financial Machine Learning* (2018), ch. 7 (purged K-fold).
- Romano, Patterson, Candes, "Conformalized Quantile Regression", NeurIPS 2019.
- Dietterich, "Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms", *Neural
  Computation* (1998).
- Nadeau and Bengio, "Inference for the Generalization Error", *Machine Learning* (2003).
