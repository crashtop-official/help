---
layout: "article"
title: "Verify a finished round"
description: "Every round publishes a hash before betting closes and reveals its server seed after the crash. Here is how to check any round yourself."
categories: [provably-fair]
tags: [provably fair, hash, verify, fairness, server seed]
author: "CrashTop Team"
pinned: true
sitemap: true
toc: true
stage: 5
order: 1
---

## Why a round can be checked

Each round publishes a **round hash** before betting closes. That hash is a commitment to the round's **server seed**, which stays hidden until the round ends. After the crash the seed is revealed, and anyone can confirm two things:

- hashing the revealed seed gives back the round hash that was published in advance, so the result was fixed before bets were placed;
- the round hash walks back, hash by hash, to a **chain anchor** that was published before the first round of that chain was played.

## The round verifier

The check runs on a separate public page: [{{ site.verifier_url | replace('https://', '') }}]({{ site.verifier_url }}).

It rebuilds the hash chain and replays the results entirely in your browser. It has no database, no login and no connection to the game server, and nothing you paste is sent anywhere.

## Check a round

1. Open **Round info** in the game and copy the round hash and the round number.
2. Open the [round verifier]({{ site.verifier_url }}) and paste them in. Pressing **Verify hash** in the game does the same thing and opens the page already filled in.
3. Optionally add the revealed **server seed**. Without it the table starts one round earlier.
4. Press **Verify**.

## Read the result

A green **Verified** verdict means the hash walks back to the published chain anchor and every row replays from the chain. Under it, the page lists three checks:

| Check | What it proves |
| --- | --- |
| Hashing the revealed seed reproduces the published round hash | The seed was chosen before betting closed. |
| Hashing this round back reaches the chain anchor | The round belongs to a chain committed before its first round. |
| The result shown for this round replays from its seed | The multiplier you saw is the one the seed produces. |

Compare the rows in **Replayed rounds** with the results the game showed.

## A real example

[Round #37191 on chain #207]({{ site.verifier_example_url }}) opens the verifier with a finished round filled in. Its replayed result is {{ chip(1.56) }}, and the round before it, #37190, replays as {{ chip(157.19) }}.

!!! note "Questions about a specific round"
    Send the round number to [{{ site.support_email }}](mailto:{{ site.support_email }}) and support will look at that exact round.
