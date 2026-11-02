---
layout: page
title: Bot Control Console
description: A serverless mobile web app on AWS to see and stop every trading bot I run, with Cognito sign-in and MFA, least-privilege IAM, and an audit trail.
img: assets/img/bot-control-console/console-light.png
importance: 1
category: work
---

# Bot Control Console

Several of my projects run unattended on AWS: paper-trading bots on weekday schedules, a crypto
bot on its own cadence, and more on the way. Each one has its own stop switch, but finding and
flipping the right one in the AWS console from a phone is slow. So I built one page that knows
all of them.

It is a mobile-first web app served from my own subdomain. One card per bot shows whether it is
running or halted and when it last ran, with **Halt**, **Halt buys**, **Resume** and **Report**
buttons, plus a single **Halt all bots** button.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/bot-control-console/console-light.png" title="Signed in: one card per bot." class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/bot-control-console/console-dark-halted.png" title="After Halt all bots, in dark mode." class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/bot-control-console/console-signin.png" title="Signed out." class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    The real page, rendered locally against mock API responses so no account data appears. Left:
    every bot running. Middle: right after <em>Halt all bots</em>, with the server's reply. Right:
    the signed-out view.
</div>

## Architecture

{% include figure.liquid loading="lazy" path="assets/img/bot-control-console/console-architecture.png" title="Bot Control Console architecture" class="img-fluid rounded z-depth-1" %}

- **Front end:** a single HTML page with plain JavaScript. It signs in through the Amazon
  Cognito hosted UI using OAuth2 with PKCE and an authenticator-app second factor, then calls a
  small REST API with the access token.
- **API:** an API Gateway HTTP API with a JWT authorizer, so unauthenticated requests never
  reach my code. Throttling and a small reserved concurrency cap what a flood of requests could
  cost.
- **Back end:** one Python Lambda. Each bot is an entry in a registry file that names its halt
  switch (an SSM parameter or an S3 key), where its status lives, and how to request a report.
  Adding a bot means adding a registry entry and its permissions.
- **Infrastructure as code:** the whole stack is a CloudFormation template with deploy scripts,
  and the test suite runs in GitHub Actions on every push, with no AWS account needed.

## Designed for the bad day

The console exists for the moment something goes wrong, so the design choices lean toward safety:

- **Stopping is easy, and starting again is not.** Halting takes one tap. Resuming also needs a
  fresh code from an authenticator app, so someone who got into my email or chat could stop
  trading but could not restart it.
- **It never holds broker keys.** Its IAM role names exactly the switches, status files and
  report functions it uses. It cannot read the trading API keys and cannot place an order.
- **Halt means "no new orders," never "sell everything."** A forced sale at the bottom of a bad
  day is its own risk.
- **A remote control, not the engine.** Each bot checks its own switch before every run. If the
  console breaks, the bots carry on, and every bot can still be stopped the old way.
- **Every command is logged** to CloudWatch for 90 days. Alert emails carry a halt link that
  opens a confirm button, so a mail scanner opening the link changes nothing.

## Stack

JavaScript, Python, AWS Lambda, API Gateway (HTTP API), Amazon Cognito, SSM Parameter Store, S3,
CloudWatch, CloudFormation, GitHub Actions. Built with Claude Code.

The source is in a private repository, because it is wired to my own accounts. I'm happy to walk
through it on a call.

Related: [Serverless trading bots on AWS](/projects/serverless-trading-bots/), the bots this
console controls.
