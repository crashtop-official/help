---
layout: "article"
title: "How a round works"
description: "A round has three phases: a betting window, a rising multiplier and a crash. This guide walks through each one and shows how a payout is worked out."
categories: [playing-a-round]
tags: [round, bet, cash out, payout, multiplier]
author: "CrashTop Team"
pinned: true
sitemap: true
toc: true
stage: 1
order: 1
---

## The betting window

Between rounds there is a short pause. While it lasts, the badge above the chart reads:

{{ badge("waiting") }}

1. Enter a bet amount in the bet panel. Limits are {{ site.min_bet }} to {{ site.max_bet }} {{ site.currency }}.
2. Optionally set an auto cash-out target (see [Set an auto cash-out]({{ url('/articles/set-an-auto-cash-out/') }})).
3. Press the main button to place the bet.

If a round is already running, the bet is queued for the next round instead.

## The multiplier climbs

The round starts at `1.00×` and the multiplier rises until the round crashes. The crash point is fixed before the round starts, so nothing on screen can tell you when it will come.

!!! note "Good to know"
    {{ site.honesty_note }} A run of low rounds does not make a high one more likely.

## Cash out

While the round is live you can cash out at any moment. The payout is your bet times the multiplier at that moment.

```
payout = bet × multiplier
profit = payout − bet
```

### Worked example

{{ stats({"Bet": "10.00", "Cashed out at": "2.40×", "Payout": "24.00", "Profit": "+14.00"}) }}

With an auto cash-out target set, the game cashes out for you the moment the multiplier reaches it. You can still cash out by hand earlier.

## The crash

When the round crashes, every bet that has not been cashed out is lost. The badge changes to:

{{ badge("crashed") }}

### Same bet, target not reached

{{ stats({"Bet": "10.00", "Auto target": "3.00×", "Crashed at": "1.84×", "Result": "−10.00"}) }}

## What to read next

- [Reading the history chips]({{ url('/articles/reading-the-history-chips/') }}) explains the colours of past rounds.
- [Verify a finished round]({{ url('/articles/verify-a-finished-round/') }}) shows how to check a result yourself at [{{ site.verifier_url | replace('https://', '') }}]({{ site.verifier_url }}).
