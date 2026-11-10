---
layout: article
title: How to verify a result
description: Learn which round data and algorithm specifications are needed to independently check a result.
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
order: 116
---

## What to check

Valid verification requires raw round data and a public algorithm specification. Compare an independently calculated result with the recorded result, and also check the commitment published before play.

Use the [round verifier]({{ site.verifier_url }}) to check a finished round. The tool must match the round data and protocol version.

## Related guide

[Provably fair results and verification]({{ url('/articles/provably-fair/') }})

## Need help?

Contact [{{ site.support_email }}](mailto:{{ site.support_email }}). Include the round ID or transaction identifier when relevant. Never send passwords, one-time codes, or recovery keys.
