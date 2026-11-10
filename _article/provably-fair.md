---
layout: article
title: Provably fair results and verification
description: Understand hash-chain commitments and the data needed to independently verify a round.
categories:
- provably-fair
tags:
- provably fair
- verification
author: CrashTop Team
pinned: false
sitemap: true
toc: true
public: true
order: 102
---

## How verification works

In a hash-chain scheme, a public commitment is published before play, and data disclosed afterward allows results to be checked. Using a public input that is unknown at the time of commitment can make selective outcome generation more difficult.

## Verify a round

To verify a round, obtain its identifier, disclosed hash, public input, and algorithm version. Check both chain membership and the calculated multiplier. The verification tool should be executable independently of the result display page.

## What verification does not establish

This mechanism does not make the next round predictable and provides no guarantee of solvency or account security.

Use the [round verifier]({{ site.verifier_url }}) to check a finished round. The tool must match the round data and protocol version.

## Related guide

[How to verify a result]({{ url('/articles/provable-fairness/') }})

## Need help?

Contact [{{ site.support_email }}](mailto:{{ site.support_email }}). Include the round ID or transaction identifier when relevant. Never send passwords, one-time codes, or recovery keys.
