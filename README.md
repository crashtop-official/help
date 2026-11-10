# CrashTop Help Center

سایت راهنما و مستندات CrashTop؛ یک سایت استاتیک که از فایل‌های مارک‌داون همین ریپازیتوری ساخته و با GitHub Actions روی GitHub Pages منتشر می‌شود.

## راه‌اندازی (یک بار)

1. محتویات این پوشه را در یک ریپازیتوری گیت‌هاب، روی شاخهٔ `main`، قرار دهید.
2. در گیت‌هاب: **Settings → Pages → Build and deployment → Source** را روی **GitHub Actions** بگذارید.
3. هر `push` به `main` سایت را می‌سازد و منتشر می‌کند (فایل `.github/workflows/pages.yml`).
4. دامنهٔ اختصاصی (مثلاً `help.crashtop.com`): در همان صفحهٔ Pages دامنه را وارد کنید. آدرس و مسیر پایه خودکار تشخیص داده می‌شود و لازم نیست چیزی در کد عوض شود.

## ساختار پوشه‌ها

| مسیر | کاربرد |
| --- | --- |
| `site.yml` | **تنظیمات و متغیرهای مرکزی** (ایمیل، آدرس‌ها، منو، موضوع‌ها، متن‌های ثابت) |
| `_article/` | مقاله‌های راهنما → `/articles/<slug>/` |
| `_posts/` | پست‌ها و اطلاعیه‌ها → `/posts/<slug>/` |
| `_page/` | صفحه‌های معمولی → `/<slug>/` |
| `_layouts/`، `_includes/` | قالب‌های HTML |
| `assets/` | CSS، جاوااسکریپت و تصویرها |
| `build.py` | سازندهٔ سایت |
| `.github/workflows/pages.yml` | اکشن ساخت و انتشار |

## افزودن محتوا

یک فایل `.md` در پوشهٔ مربوط بسازید. **نام فایل همان slug و آدرس است**: حروف کوچک انگلیسی، بدون فاصله، کلمه‌ها با `-` جدا می‌شوند.

```
_posts/new-post-in-help.md      →  help.crashtop.com/posts/new-post-in-help/
_article/how-a-round-works.md   →  help.crashtop.com/articles/how-a-round-works/
_page/contact.md                →  help.crashtop.com/contact/
```

بالای هر فایل، مشخصات آن بین دو خط `---` نوشته می‌شود:

```yaml
---
layout: "article"            # post | page | article  (پیش‌فرض: بر اساس پوشه)
title: "How a round works"   # عنوان
description: "…"             # توضیح کوتاه؛ در فهرست‌ها و موتورهای جست‌وجو
date: 2026-11-10             # اختیاری؛ اگر نباشد خودکار است (پایین را ببینید)
categories: [playing-a-round]  # slug موضوع‌ها از site.yml
tags: [round, bet, payout]   # کلیدواژه‌ها؛ در meta keywords و صفحهٔ تگ
author: "John Smith"         # پیش‌فرض: default_author در site.yml
pinned: true                 # سنجاق در صفحهٔ اصلی
sitemap: true                # درج در sitemap.xml و sitemap_index.xml
toc: true                    # فهرست «On this page» از تیترهای h2 و h3
public: true                 # false = پیش‌نویس؛ منتشر نمی‌شود
---
```

فیلدهای اختیاری دیگر:

| فیلد | کار |
| --- | --- |
| `updated` | تاریخ آخرین به‌روزرسانی (پیش‌فرض: آخرین کامیت فایل) |
| `order` | ترتیب در منوی کناری و فهرست‌ها (عدد کوچک‌تر، بالاتر) |
| `stage` | عدد ۱ تا ۵؛ مقاله را به همان کارت مرحلهٔ راند در صفحهٔ اصلی وصل می‌کند |
| `noindex` | `true` = صفحه ساخته می‌شود ولی از موتور جست‌وجو و سایت‌مپ پنهان است |
| `image` | تصویر اشتراک‌گذاری (Open Graph) |

**تاریخ خودکار:** اگر `date` ننویسید، تاریخ اولین کامیتی که فایل را اضافه کرده استفاده می‌شود؛ یعنی لحظهٔ انتشار. `updated` هم از آخرین کامیت می‌آید.

## متغیرهای مرکزی

همه‌چیز در `site.yml` است. در هر فایل مارک‌داون یا قالب:

```
{{ site.support_email }}    {{ site.min_bet }}    {{ site.main_site_url }}
```

یک مقدار را در `site.yml` عوض کنید؛ همهٔ صفحه‌ها در بیلد بعدی به‌روز می‌شوند.

**بدون کامیت هم می‌شود:** در گیت‌هاب، **Settings → Secrets and variables → Actions → Variables** یک متغیر با نام `SITE_<نام کلید با حروف بزرگ>` بسازید، مثلاً `SITE_SUPPORT_EMAIL`. این مقدار روی `site.yml` اولویت دارد. بعد اکشن را دوباره اجرا کنید (Actions → Deploy help center → Run workflow).

## اجزای آماده داخل مارک‌داون

| کد | خروجی |
| --- | --- |
| `{{ chip(2.4) }}` | چیپ ضریب؛ رنگ خودکار (زیر ۲×، ۲× تا ۱۰×، ۱۰× به بالا) |
| `{{ badge("waiting") }}` | نشان وضعیت راند: `waiting`، `live`، `crashed` |
| `{{ stats({"Bet": "10.00", "Profit": "+14.00"}) }}` | جدول آمار؛ مقدار با `+` سبز و با `−` قرمز |
| `{{ url('/articles/slug/') }}` | لینک داخلی که با هر دامنه و مسیری درست کار می‌کند |
| `!!! note "Title"` و خط بعد با ۴ فاصله | کادر توضیح (`note`، `tip`، `warning`، `danger`) |

نمونهٔ همهٔ این‌ها در `_page/style-guide.md` هست (آدرس `/style-guide/`).

اگر لازم شد خودِ `{{ … }}` را به‌صورت متن نشان دهید، آن را بین `{% raw %}` و `{% endraw %}` بگذارید.

## موضوع‌ها، منو و نقشهٔ راند

- **موضوع‌ها (`topics`)**: فهرست دسته‌ها با عنوان، توضیح و آیکون. موضوع بدون محتوا خودکار پنهان می‌شود.
- **منو (`nav`) و لینک‌های فوتر (`footer_links`)**: در `site.yml`.
- **مراحل راند (`round_stages`)**: پنج کارت صفحهٔ اصلی؛ هر کدام به مقاله‌ای با همان `stage` لینک می‌شود.

## پیش‌نمایش روی کامپیوتر خودتان

```bash
pip install -r requirements.txt
python build.py --serve      # http://localhost:8000
python build.py --drafts     # همراه با فایل‌های public: false
```

## خروجی‌های خودکار

`sitemap_index.xml` (فهرست سایت‌مپ‌ها)، `sitemap.xml` (همهٔ صفحه‌ها)، `sitemap-articles.xml`، `sitemap-posts.xml`، `sitemap-pages.xml`، `feed.xml` (Atom برای پست‌ها)، `robots.txt` و `404.html`. سایت‌مپ‌ها در مرورگر با ظاهر خوانا باز می‌شوند (`sitemap.xsl`).

## خطاهای بیلد

اکشن با `--strict` اجرا می‌شود: فایلی که عنوان یا توضیح ندارد، یا نام آن حروف بزرگ یا فاصله دارد، بیلد را متوقف می‌کند و نام فایل را در لاگ اکشن می‌نویسد.
