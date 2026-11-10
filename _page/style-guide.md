---
layout: "page"
title: "Writing style guide"
description: "Every element you can use in a Markdown file, shown as it renders. For editors; hidden from search engines."
sitemap: false
toc: true
---

## Text

Plain paragraph with **bold**, *italic*, `inline code` and a [link]({{ url('/') }}).

> A quotation or an aside.

## Lists

- Bullet one
- Bullet two

1. Step one
2. Step two

## Variables from site.yml

Support email: {{ site.support_email }} · Bet limits: {{ site.min_bet }} to {{ site.max_bet }} {{ site.currency }}

## Game components

Chips: {{ chip(1.24) }} {{ chip(3.1) }} {{ chip(14.52) }}

Badges: {{ badge("waiting") }} {{ badge("live") }} {{ badge("crashed") }}

{{ stats({"Bet": "10.00", "Cashed out at": "2.40×", "Profit": "+14.00"}) }}

## Callouts

!!! note "Note"
    Neutral information.

!!! tip "Tip"
    A helpful shortcut.

!!! warning "Warning"
    Something to be careful about.

## Table

| Column | Value |
| --- | --- |
| One | 1.00 |
| Two | 2.00 |

## Code block

```
payout = bet × multiplier
```

### A third-level heading

Headings at level 2 and 3 appear in "On this page" when `toc: true`.
