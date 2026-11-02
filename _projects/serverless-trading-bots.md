---
layout: page
title: Serverless Trading Bots on AWS
description: Three paper-trading bots running unattended as scheduled container Lambdas, defined in CloudFormation with least-privilege IAM, alarms, budget guards, and hard safety limits.
img: assets/img/serverless-trading-bots/bots-architecture.png
importance: 1
category: work
---

# Serverless trading bots on AWS

I run three trading bots against **paper** (simulated-money) brokerage accounts. Each one runs
unattended on AWS on a schedule, with no server to look after. Profit isn't the point. The point
is to practice building cloud systems that run on their own, fail safely, and tell me when
something is wrong.

| Bot | What it does |
|---|---|
| **AuraTrade** | Stock/ETF strategies on Alpaca, including a 70/30 core-satellite allocation, with a monthly report |
| **Crypto bot** | Low-frequency BTC/ETH rebalancing with a market-regime switch and a manipulation guard |
| **LLM agent research lab** | A team of LLM agents proposes trades, code filters them, and I approve each one |

## Shared architecture

{% include figure.liquid loading="eager" path="assets/img/serverless-trading-bots/bots-architecture.png" title="The deployment pattern the bots share" class="img-fluid rounded z-depth-1" %}

- **Compute:** each bot is a container image in ECR, run as a Lambda function on an EventBridge
  Scheduler cron. The bots are stateless between runs. The broker and S3 are the memory.
- **Secrets:** broker keys live in SSM Parameter Store as SecureString values and are read at run
  time. They never appear in code or in the template.
- **Infrastructure as code:** each bot's stack is a CloudFormation template with least-privilege
  IAM roles, deployed by scripts. On every infrastructure change, GitHub Actions statically scans
  the templates for cost risks, with no AWS credentials. Each bot has a pytest suite, and the
  crypto bot runs its suite in CI on every push.
- **Operations:** a CloudWatch alarm on the Lambda `Errors` metric sends an email through SNS.
  An AWS Budgets alert emails me if spend drifts. Run records and reports land in S3.

## Safety limits in code, not in hope

Every bot enforces hard limits in plain code. Depending on the bot, these include cash-only
trading (no margin or leverage), per-order and daily trade caps, a daily-loss circuit breaker,
limit orders instead of market orders, and a halt switch checked before every run. Halting any
or all of them from my phone is the job of the
[Bot Control Console](/projects/bot-control-console/).

## Using LLMs responsibly: agents propose, code decides, a human approves

The research-lab bot asks what an LLM trading team actually does when a human is the gatekeeper,
and what it costs to run.

{% include figure.liquid loading="lazy" path="assets/img/serverless-trading-bots/agent-flow.png" title="The daily run of the LLM agent bot" class="img-fluid rounded z-depth-1" %}

- Agents only **propose**. The critic can drop ideas but never add them.
- A **deterministic risk engine** in plain Python filters what survives, and it fails closed.
- **I approve or reject every order** from Telegram before anything is placed.
- An **S3 journal** records every step, including the tokens used and dollars spent per run.

## Stack

Python, Docker, AWS Lambda, EventBridge Scheduler, ECR, S3, SSM Parameter Store, CloudWatch, SNS,
AWS Budgets, CloudFormation, IAM, GitHub Actions; Alpaca API; LLM agents. Built with Claude Code.

The bot repositories are private, because they are wired to my own brokerage accounts. I'm happy
to walk through them on a call.

*Not financial advice. These bots trade simulated money.*
